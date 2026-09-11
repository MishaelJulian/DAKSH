"""Browser lifecycle management and page automation interactions for eCourts Karnataka.

Provides get_browser_page for context management and ECourtsBrowser for cascading
drop-down inputs, CAPTCHA wait, and results validation.
"""
from __future__ import annotations
import logging
from contextlib import contextmanager
from typing import Generator
from playwright.sync_api import sync_playwright, Page, Dialog
from ecourts_scraper import config
from ecourts_scraper.models import (
    CaseSummary,
    CaseDetail,
    ActEntry,
    ProcessEntry,
    HearingRecord,
    OrderEntry,
    TransferEntry,
)
from ecourts_scraper.parser import parse_case_detail_text

logger = logging.getLogger("ecourts_scraper")

class DropdownSelectionError(Exception):
    """Exception raised when selection on a dropdown element fails."""
    pass

class CaptchaError(Exception):
    """Exception raised when an invalid CAPTCHA is entered."""
    pass

class ECourtsPortalError(Exception):
    """Exception raised when eCourts returns an application-level failure page ('Oops, something happened', 'Invalid Request')."""
    pass

def _matches_with_aliases(configured: str, option_text: str) -> bool:
    """Checks if a configured value matches an option text, ignoring case/whitespace
    and supporting common equivalent aliases (like Bengaluru/Bangalore).
    """
    conf_norm = " ".join(configured.lower().split())
    opt_norm = " ".join(option_text.lower().split())
    
    aliases = {
        "bengaluru": "bangalore",
        "bangalore": "bengaluru",
    }
    
    if conf_norm == opt_norm or conf_norm in opt_norm or opt_norm in conf_norm:
        return True
        
    conf_alias = conf_norm
    for src, dst in aliases.items():
        conf_alias = conf_alias.replace(src, dst)
        
    opt_alias = opt_norm
    for src, dst in aliases.items():
        opt_alias = opt_alias.replace(src, dst)
        
    if conf_alias == opt_alias or conf_alias in opt_alias or opt_alias in conf_alias:
        return True
        
    return False

@contextmanager
def get_browser_page(
    headless: bool = config.HEADLESS,
    timeout: int = config.DEFAULT_TIMEOUT
) -> Generator[Page, None, None]:
    """Context manager to initialize and cleanup Playwright browser, context, and page.

    It configures a Chromium instance with specific viewport sizes, sets default timeouts,
    and handles graceful teardown on exit or exception.

    Args:
        headless: Whether to run the browser in headless mode.
        timeout: Default timeout in milliseconds for Playwright navigation and selector actions.

    Yields:
        A page instance ready to perform navigation.
    """
    logger.info("Initializing Playwright sync API...")
    with sync_playwright() as p:
        logger.info(f"Launching Chromium browser (headless={headless})...")
        browser = p.chromium.launch(
            headless=headless,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        try:
            logger.info("Creating browser context...")
            # Maximized viewport is cleaner for headful human CAPTCHA solving
            context = browser.new_context(
                no_viewport=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # Set page timeouts
            context.set_default_timeout(timeout)
            context.set_default_navigation_timeout(config.PAGE_LOAD_TIMEOUT)
            
            page = context.new_page()
            logger.info("Browser page successfully instantiated.")
            yield page
        except Exception as e:
            logger.exception(f"Exception encountered during browser execution: {e}")
            raise
        finally:
            logger.info("Closing browser context and instance...")
            try:
                context.close()
            except Exception:
                pass
            try:
                browser.close()
            except Exception:
                pass
            logger.info("Browser teardown complete.")

class ECourtsBrowser:
    """Reusable browser automation layer for eCourts Karnataka."""

    def __init__(self, page: Page):
        self.page = page
        self.dialog_text: str | None = None
        # Register dialog handler for invalid CAPTCHA alerts
        self.page.on("dialog", self._handle_dialog)

    def _handle_dialog(self, dialog: Dialog) -> None:
        self.dialog_text = dialog.message
        logger.warning(f"Browser Alert Dialog detected: {dialog.message}")
        dialog.dismiss()

    def navigate_to_home(self, retries: int = 3) -> None:
        """Navigates to eCourts India page with two-step session initialization."""
        for attempt in range(1, retries + 1):
            logger.info(f"Opening eCourts website (attempt {attempt}/{retries}): {config.BASE_URL}")
            try:
                # Step 1: Initialize session on base v6 URL
                base_home_url = "https://services.ecourts.gov.in/ecourtindia_v6/"
                logger.info(f"Step 1: Initializing session on {base_home_url}...")
                self.page.goto(base_home_url, wait_until="domcontentloaded", timeout=60000)
                self.page.wait_for_timeout(1000)

                # Step 2: Navigate to Case Status search page
                logger.info(f"Step 2: Navigating to Case Status URL {config.BASE_URL}...")
                self.page.goto(config.BASE_URL, wait_until="domcontentloaded", timeout=60000)
                self.page.wait_for_timeout(3000)
                logger.info("Waiting for #sess_state_code dropdown to become visible...")
                self.page.wait_for_selector("#sess_state_code", timeout=15000)
                logger.info("eCourts India Case Status page successfully loaded with #sess_state_code!")
                return
            except Exception as e:
                logger.warning(f"Homepage navigation attempt {attempt} failed: {e}")
                logger.warning(f"Page URL on failure: {self.page.url}")
                try:
                    bt = self.page.inner_text('body')[:300].replace('\n', ' ')
                    logger.warning(f"Body text on failure: {bt}")
                except Exception:
                    pass
                if attempt < retries:
                    self.page.wait_for_timeout(3000)
        raise Exception(f"Failed to navigate to eCourts home after {retries} attempts.")


    def _wait_and_get_dropdown_options(
        self, selector: str, target_text: str | None = None, timeout: int = 15000
    ) -> list[str]:
        """Waits for a dropdown to be populated and returns all option texts.

        If target_text is provided, waits until target_text is present in one of the options
        (case-insensitive substring match), or until the timeout is reached.
        Otherwise, waits until the dropdown contains more than 1 option.
        """
        import time
        logger.debug(f"Waiting for dropdown {selector} to populate (target_text={target_text})...")
        start_time = time.time()
        
        while (time.time() - start_time) * 1000 < timeout:
            try:
                # Evaluate option texts in-browser
                options = self.page.eval_on_selector(
                    selector,
                    "el => Array.from(el.options).map(o => o.text.trim())"
                )
                
                # Check population conditions
                if len(options) > 1:
                    if target_text:
                        matched = any(_matches_with_aliases(target_text, opt) for opt in options)
                        if matched:
                            return options
                    else:
                        return options
            except Exception:
                pass
            self.page.wait_for_timeout(200) # Small polling interval
            
        # Final attempt to get whatever is there
        try:
            return self.page.eval_on_selector(
                selector,
                "el => Array.from(el.options).map(o => o.text.trim())"
            )
        except Exception:
            return []

    def _select_dropdown_option(self, selector: str, value_to_select: str, dropdown_name: str) -> None:
        """Selects a dropdown option by value and asserts success."""
        logger.info(f"Selecting option value '{value_to_select}' in dropdown {selector} ({dropdown_name})...")
        self.page.select_option(selector, value_to_select)
        
        # Verify selection
        selected_val = self.page.eval_on_selector(selector, "el => el.value")
        if selected_val != value_to_select:
            # Retry via direct JS evaluation if standard select_option fails
            logger.warning(f"Standard select_option failed to stick (got '{selected_val}'). Attempting JS selection...")
            self.page.evaluate(
                f"""() => {{
                    const el = document.querySelector('{selector}');
                    if (el) {{
                        el.value = '{value_to_select}';
                        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                }}"""
            )
            selected_val = self.page.eval_on_selector(selector, "el => el.value")
            if selected_val != value_to_select:
                raise DropdownSelectionError(
                    f"Failed to set dropdown {selector} to value '{value_to_select}'. Current value: '{selected_val}'."
                )

    def select_state(self, state: str, retries: int = 3) -> None:
        """Selects State dropdown option robustly."""
        for attempt in range(1, retries + 1):
            logger.info(f"Selecting State: {state} (Attempt {attempt}/{retries})...")
            try:
                options = self._wait_and_get_dropdown_options("#sess_state_code", target_text=state)
                
                opt_pairs = self.page.eval_on_selector(
                    "#sess_state_code",
                    "el => Array.from(el.options).map(o => ({ text: o.text.trim(), value: o.value }))"
                )
                
                target_value = None
                matched_text = None
                for pair in opt_pairs:
                    text = pair["text"]
                    val = pair["value"]
                    if _matches_with_aliases(state, text):
                        target_value = val
                        matched_text = text
                        break
                        
                if target_value:
                    logger.info(f"Matched configured State '{state}' to website option '{matched_text}' (value: {target_value})")
                    self._select_dropdown_option("#sess_state_code", target_value, "State")
                    self.page.wait_for_timeout(3000)  # Allow AJAX to populate district dropdown
                    return
            except Exception as e:
                logger.warning(f"State selection attempt {attempt} failed: {e}")
            self.page.wait_for_timeout(2000)
            
        raise DropdownSelectionError(f"Failed to find or select State '{state}' in available options.")

    def select_district(self, district: str, retries: int = 5) -> None:
        """Selects District dropdown option robustly."""
        for attempt in range(1, retries + 1):
            logger.info(f"Selecting District: {district} (Attempt {attempt}/{retries})...")
            try:
                options = self._wait_and_get_dropdown_options("#sess_dist_code", target_text=district, timeout=30000)
                
                opt_pairs = self.page.eval_on_selector(
                    "#sess_dist_code",
                    "el => Array.from(el.options).map(o => ({ text: o.text.trim(), value: o.value }))"
                )
                
                # Log available options for debugging
                opt_texts = [p["text"] for p in opt_pairs if p["text"]]
                logger.info(f"District dropdown has {len(opt_texts)} options: {opt_texts[:10]}")
                
                target_value = None
                matched_text = None
                for pair in opt_pairs:
                    text = pair["text"]
                    val = pair["value"]
                    if _matches_with_aliases(district, text):
                        target_value = val
                        matched_text = text
                        break
                        
                if target_value:
                    logger.info(f"Matched configured District '{district}' to website option '{matched_text}' (value: {target_value})")
                    self._select_dropdown_option("#sess_dist_code", target_value, "District")
                    self.page.wait_for_timeout(1000)
                    return
                else:
                    logger.warning(f"District '{district}' not found in available options: {opt_texts}")
            except Exception as e:
                logger.warning(f"District selection attempt {attempt} failed: {e}")
            self.page.wait_for_timeout(5000)  # Longer wait between retries for AJAX
            
        raise DropdownSelectionError(f"Failed to find or select District '{district}' in available options.")

    def select_court_complex(self, complex_name: str, retries: int = 3) -> None:
        """Selects Court Complex dropdown option robustly."""
        for attempt in range(1, retries + 1):
            logger.info(f"Selecting Court Complex: {complex_name} (Attempt {attempt}/{retries})...")
            try:
                options = self._wait_and_get_dropdown_options("#court_complex_code", target_text=complex_name)
                
                opt_pairs = self.page.eval_on_selector(
                    "#court_complex_code",
                    "el => Array.from(el.options).map(o => ({ text: o.text.trim(), value: o.value }))"
                )
                
                target_value = None
                matched_text = None
                for pair in opt_pairs:
                    text = pair["text"]
                    val = pair["value"]
                    if _matches_with_aliases(complex_name, text):
                        target_value = val
                        matched_text = text
                        break
                        
                if target_value:
                    logger.info(f"Matched configured Court Complex '{complex_name}' to website option '{matched_text}' (value: {target_value})")
                    self._select_dropdown_option("#court_complex_code", target_value, "Court Complex")
                    self.page.wait_for_timeout(1000)
                    return
            except Exception as e:
                logger.warning(f"Court Complex selection attempt {attempt} failed: {e}")
            self.page.wait_for_timeout(2000)
            
        raise DropdownSelectionError(f"Failed to find or select Court Complex '{complex_name}' in available options.")

    def select_establishment(self, establishment: str, retries: int = 3) -> None:
        """Selects Establishment dropdown option robustly."""
        for attempt in range(1, retries + 1):
            logger.info(f"Selecting Establishment: {establishment} (Attempt {attempt}/{retries})...")
            try:
                options = self._wait_and_get_dropdown_options("#court_est_code", target_text=establishment)
                
                opt_pairs = self.page.eval_on_selector(
                    "#court_est_code",
                    "el => Array.from(el.options).map(o => ({ text: o.text.trim(), value: o.value }))"
                )
                
                target_value = None
                matched_text = None
                for pair in opt_pairs:
                    text = pair["text"]
                    val = pair["value"]
                    if _matches_with_aliases(establishment, text):
                        target_value = val
                        matched_text = text
                        break
                        
                if target_value:
                    logger.info(f"Matched configured Establishment '{establishment}' to website option '{matched_text}' (value: {target_value})")
                    self._select_dropdown_option("#court_est_code", target_value, "Establishment")
                    self.page.wait_for_timeout(1000)
                    return
            except Exception as e:
                logger.warning(f"Establishment selection attempt {attempt} failed: {e}")
            self.page.wait_for_timeout(2000)
            
        raise DropdownSelectionError(f"Failed to find or select Establishment '{establishment}' in available options.")

    def select_case_type_tab(self) -> None:
        """Clicks the 'Case Type' search tab link."""
        logger.info("Choosing Search Type: Case Type...")
        self.dismiss_validation_modal()
        self.page.wait_for_selector("#casetype-tabMenu")
        try:
            self.page.click("#casetype-tabMenu", no_wait_after=True, force=True)
        except Exception as e:
            logger.warning(f"Direct click on #casetype-tabMenu failed: {e}. Executing programmatic JS click...")
            self.page.evaluate("() => { const el = document.querySelector('#casetype-tabMenu'); if (el) el.click(); }")
        # Let tab menu animation/DOM transition complete
        self.page.wait_for_timeout(2000)
        self.dismiss_validation_modal()


    def fill_case_type(self, case_type_label: str, retries: int = 3) -> None:
        """Finds the visible Case Type select element and selects the matching option."""
        for attempt in range(1, retries + 1):
            logger.info(f"Selecting Case Type: {case_type_label} (Attempt {attempt}/{retries})...")
            try:
                # Detect which dropdown is visible (case_type, case_type_1, or case_type_2)
                dropdown_selectors = ["#case_type_2", "#case_type_1", "#case_type"]
                visible_sel = None
                for sel in dropdown_selectors:
                    el = self.page.query_selector(sel)
                    if el and el.is_visible():
                        visible_sel = sel
                        break
                        
                if not visible_sel:
                    raise DropdownSelectionError("No visible Case Type select dropdown found under Case Type tab.")
                    
                options = self._wait_and_get_dropdown_options(visible_sel, target_text=case_type_label)
                
                opt_pairs = self.page.eval_on_selector(
                    visible_sel,
                    "el => Array.from(el.options).map(o => ({ text: o.text.trim(), value: o.value }))"
                )
                
                target_value = None
                matched_text = None
                for pair in opt_pairs:
                    text = pair["text"]
                    val = pair["value"]
                    if _matches_with_aliases(case_type_label, text):
                        target_value = val
                        matched_text = text
                        break
                        
                if target_value:
                    logger.info(f"Matched configured Case Type '{case_type_label}' to website option '{matched_text}' (value: {target_value})")
                    self._select_dropdown_option(visible_sel, target_value, "Case Type")
                    self.page.wait_for_timeout(1000)
                    return
            except Exception as e:
                logger.warning(f"Case Type selection attempt {attempt} failed: {e}")
            self.page.wait_for_timeout(2000)
            
        raise DropdownSelectionError(f"Failed to find or select Case Type '{case_type_label}' in available options.")


    def fill_year(self, year: str) -> None:
        """Fills the free-text Year input field."""
        logger.info(f"Selecting Year: {year}...")
        self.page.wait_for_selector("#search_year")
        self.page.locator("#search_year").fill(year)

    def select_disposed(self) -> None:
        """Chooses Case Status Disposed radio button."""
        logger.info("Selecting Case Status: Disposed...")
        self.page.wait_for_selector("#radDCT")
        self.page.locator("#radDCT").click()

    def click_go(self) -> None:
        """Submits the search form by clicking the Go button inside #frm_casetype."""
        logger.info("Clicking GO...")
        self.dialog_text = None # Clear any previous dialog alerts
        
        go_selectors = [
            "#frm_casetype button:has-text('Go')",
            "#frm_casetype input[type='button'][value='Go']",
            "#frm_casetype input[type='submit'][value='Go']",
            "button:has-text('Go'):visible"
        ]
        
        clicked = False
        for sel in go_selectors:
            el = self.page.query_selector(sel)
            if el and el.is_visible():
                el.click()
                clicked = True
                break
                
        if not clicked:
            raise Exception("Failed to locate or click the Go button inside the Case Type form.")


    def verify_results_table(self, timeout: int = 15000) -> None:
        """Waits for the search results table to load and verifies its existence.
        
        If a captcha error alert message was triggered, raises CaptchaError.
        """
        logger.info("Waiting for search results table to load...")
        
        # Check if dialog was popped up (which occurs synchronously or right after click)
        self.page.wait_for_timeout(1000)
        if self.dialog_text and "captcha" in self.dialog_text.lower():
            err_msg = self.dialog_text
            self.dialog_text = None # Reset
            raise CaptchaError(f"Invalid CAPTCHA alert: {err_msg}")
            
        # Check for visible error banner or alert divs on the page (in case no browser dialog was fired)
        captcha_err_div = self.page.query_selector("#captcha_error") # common error block name if present
        if captcha_err_div and captcha_err_div.is_visible():
            err_text = captcha_err_div.inner_text().strip()
            raise CaptchaError(f"Invalid CAPTCHA page error: {err_text}")

        # Wait for the results table or list container
        results_selectors = [
            "table#dispTable",
            "#dispTable",
            "table#showListTable",
            "#showListTable",
            "#showCaseList table",
            "table:has-text('Petitioner Name versus Respondent Name')"
        ]
        
        found = False
        last_err = None
        for sel in results_selectors:
            try:
                self.page.wait_for_selector(sel, state="visible", timeout=timeout)
                logger.info(f"Results table detected using selector: {sel}")
                found = True
                break
            except Exception as e:
                last_err = e
                continue
                
        if not found:
            # Check dialog text again in case alert fired late
            if self.dialog_text and "captcha" in self.dialog_text.lower():
                err_msg = self.dialog_text
                self.dialog_text = None
                raise CaptchaError(f"Invalid CAPTCHA alert: {err_msg}")
            raise Exception(f"Search results table did not render. Details: {last_err}")

    def _capture_failure_screenshot(self, prefix: str) -> None:
        """Captures a screenshot of the browser window on failure and saves it to log/data directory."""
        try:
            import time
            from pathlib import Path
            import shutil
            
            timestamp = int(time.time())
            path = config.LOGS_DIR / f"{prefix}_{timestamp}.png"
            self.page.screenshot(path=str(path))
            logger.info(f"Failure screenshot captured and saved to: {path}")
            
            # Copy to workspace artifacts directory
            artifacts_dest = Path(r"C:\Users\misha\.gemini\antigravity-ide\brain\7e103581-574e-4e9b-b59c-b903f27af732")
            if artifacts_dest.exists():
                shutil.copy(path, artifacts_dest / f"{prefix}_{timestamp}.png")
                logger.info(f"Failure screenshot copied to artifacts: {artifacts_dest / f'{prefix}_{timestamp}.png'}")
        except Exception as e:
            logger.error(f"Failed to capture failure screenshot: {e}")

    def dismiss_validation_modal(self) -> None:
        """Robustly dismisses the validation error modal #validateError if it is visible/blocking."""
        modal_selector = "#validateError"
        try:
            modal = self.page.locator(modal_selector)
            if modal.count() > 0 and modal.is_visible():
                logger.warning("Validation error modal (#validateError) detected! Starting dismissal flow...")
                
                # 1. Click .btn-close if present and wait until hidden
                close_btn = modal.locator(".btn-close")
                if close_btn.count() > 0 and close_btn.is_visible():
                    logger.info("Found .btn-close. Clicking it...")
                    close_btn.click()
                    self.page.wait_for_timeout(500)
                
                # 2. If still present/visible, execute bootstrap programmatic hide
                if modal.count() > 0 and modal.is_visible():
                    logger.info("Modal still visible. Calling bootstrap.Modal.getInstance().hide()...")
                    self.page.evaluate("""() => {
                        const el = document.getElementById("validateError");
                        if (el) {
                            if (window.bootstrap && bootstrap.Modal) {
                                const modalInstance = bootstrap.Modal.getInstance(el);
                                if (modalInstance) {
                                    modalInstance.hide();
                                }
                            }
                        }
                    }""")
                    self.page.wait_for_timeout(500)
                
                # 3. If still present/visible, remove modal-backdrops, classes, style, and element itself
                if modal.count() > 0 and modal.is_visible():
                    logger.info("Modal still visible. Force destroying elements in DOM...")
                    self.page.evaluate("""() => {
                        document.querySelectorAll(".modal-backdrop").forEach(e => e.remove());
                        document.body.classList.remove("modal-open");
                        document.body.style.overflow = "";
                        const el = document.getElementById("validateError");
                        if (el) el.remove();
                    }""")
                    self.page.wait_for_timeout(500)
            else:
                logger.info("No visible validation error modal (#validateError) detected.")
        except Exception as e:
            logger.error(f"Error while dismissing validation modal: {e}", exc_info=True)

    def log_state_investigation(self, label: str) -> None:
        """Performs a comprehensive DOM and page state investigation for debugging.

        Logs CAPTCHA fields, image status, validation modal, navigation entries,
        and target View link onclick attributes.
        """
        logger.info(f"=== STATE INVESTIGATION [{label}] ===")
        try:
            # 1. Inspect CAPTCHA input field
            captcha_val = self.page.evaluate("""() => {
                const el = document.querySelector('#ct_captcha_code') || document.querySelector('#captcha_code');
                return el ? el.value : 'NOT_FOUND';
            }""")
            logger.info(f"  CAPTCHA Input Value: '{captcha_val}'")
            
            # 2. Inspect CAPTCHA image
            img_info = self.page.evaluate("""() => {
                const el = document.querySelector('#captcha_image') || document.querySelector('#captcha_img') || document.querySelector("img[src*='captcha']");
                return el ? { present: true, src: el.src } : { present: false, src: '' };
            }""")
            logger.info(f"  CAPTCHA Image Present: {img_info['present']}, src: '{img_info['src']}'")
            
            # 3. Inspect Validation Modal status
            modal_info = self.page.evaluate("""() => {
                const el = document.querySelector('#validateError');
                return el ? { present: true, visible: el.offsetHeight > 0, text: el.innerText.trim() } : { present: false, visible: false, text: '' };
            }""")
            logger.info(f"  Validation Modal Present: {modal_info['present']}, Visible: {modal_info['visible']}")
            if modal_info['visible']:
                logger.info(f"  Validation Modal Text: '{modal_info['text']}'")
                
            # 4. Get the onclick attribute of the first View link in the results
            first_onclick = self.page.evaluate("""() => {
                const table = document.querySelector("table#dispTable") || document.querySelector("table#showListTable");
                if (!table) return 'NO_TABLE';
                const anchor = table.querySelector("a[onclick*='viewHistory']");
                return anchor ? anchor.getAttribute('onclick') : 'NO_ANCHOR_FOUND';
            }""")
            logger.info(f"  First View link onclick attribute: '{first_onclick}'")
            
            # 5. Check browser navigation type using performance API
            nav_type = self.page.evaluate("""() => {
                const entries = performance.getEntriesByType("navigation");
                return entries.length > 0 ? entries[0].type : 'unknown';
            }""")
            logger.info(f"  Browser Navigation Type (from performance API): '{nav_type}'")
            
        except Exception as e:
            logger.error(f"  Error executing state investigation [{label}]: {e}")
        logger.info("=========================================")

    def _log_pre_click_diagnostics(self, locator, case_summary) -> None:
        """Logs comprehensive pre-click diagnostics of the browser page and the View element."""
        logger.info("=== PRE-CLICK DIAGNOSTICS ===")
        try:
            url = self.page.url
            title = self.page.title()
            
            # Evaluate browser state
            state = self.page.evaluate("""() => {
                const active = document.activeElement;
                const hiddenInputs = Array.from(document.querySelectorAll("input[type='hidden']")).map(el => ({ name: el.name || el.id, value: el.value }));
                
                const captchaInput = document.querySelector('#ct_captcha_code') || document.querySelector('#captcha_code');
                const captchaVal = captchaInput ? captchaInput.value : 'NOT_FOUND';
                
                const captchaImg = document.querySelector('#captcha_image') || document.querySelector('#captcha_img') || document.querySelector("img[src*='captcha']");
                const captchaSrc = captchaImg ? captchaImg.src : 'NOT_FOUND';
                
                const entries = performance.getEntriesByType("navigation");
                const navType = entries.length > 0 ? entries[0].type : 'unknown';
                
                return {
                    readyState: document.readyState,
                    href: window.location.href,
                    activeElement: active ? `${active.tagName}#${active.id || ''}.${active.className || ''}` : 'none',
                    hiddenInputs: hiddenInputs,
                    captchaVal: captchaVal,
                    captchaSrc: captchaSrc,
                    navType: navType
                };
            }""")
            
            # Element properties
            attached = locator.count() > 0
            visible = locator.is_visible() if attached else False
            enabled = locator.is_enabled() if attached else False
            box = locator.bounding_box() if visible else None
            onclick = locator.get_attribute("onclick") if attached else None
            href = locator.get_attribute("href") if attached else None
            
            logger.info(f"  Current URL: '{url}'")
            logger.info(f"  Page Title: '{title}'")
            logger.info(f"  Document readyState: '{state['readyState']}'")
            logger.info(f"  window.location.href: '{state['href']}'")
            logger.info(f"  Navigation Type: '{state['navType']}'")
            logger.info(f"  Active Element: '{state['activeElement']}'")
            logger.info(f"  CAPTCHA Textbox Value: '{state['captchaVal']}'")
            logger.info(f"  CAPTCHA Image Src: '{state['captchaSrc']}'")
            logger.info(f"  Hidden Inputs Count: {len(state['hiddenInputs'])}")
            
            logger.info(f"  View Element:")
            logger.info(f"    Case Number: {case_summary.case_number}")
            logger.info(f"    Serial Number: {case_summary.serial_number}")
            logger.info(f"    Row Index (view_index): {case_summary.view_index}")
            logger.info(f"    onclick: '{onclick}'")
            logger.info(f"    href: '{href}'")
            logger.info(f"    is_attached: {attached}")
            logger.info(f"    is_visible: {visible}")
            logger.info(f"    is_enabled: {enabled}")
            logger.info(f"    bounding_box: {box}")
            
        except Exception as e:
            logger.error(f"  Error capturing pre-click diagnostics: {e}")
        logger.info("=============================")

    def _log_post_click_diagnostics(
        self,
        locator,
        pre_url: str,
        pre_title: str,
        requests: list[dict],
        responses: list[dict],
        failures: list[dict]
    ) -> None:
        """Logs post-click diagnostics of the browser state and network traffic."""
        logger.info("=== POST-CLICK DIAGNOSTICS ===")
        try:
            post_url = self.page.url
            post_title = self.page.title()
            
            url_changed = pre_url != post_url
            title_changed = pre_title != post_title
            
            # Check if View anchor is still present or visible
            anchor_visible = False
            try:
                anchor_visible = locator.is_visible()
            except Exception:
                pass
                
            # Check modal
            modal_selector = "#validateError"
            modal = self.page.locator(modal_selector)
            modal_exists = modal.count() > 0
            modal_visible = modal.is_visible() if modal_exists else False
            modal_text = modal.inner_text().strip() if modal_visible else ""
            
            logger.info(f"  URL Changed: {url_changed} (from '{pre_url}' to '{post_url}')")
            logger.info(f"  Title Changed: {title_changed} (from '{pre_title}' to '{post_title}')")
            logger.info(f"  View Anchor Still Visible: {anchor_visible}")
            logger.info(f"  Validation Modal Detected: {modal_visible} (Exists: {modal_exists})")
            if modal_visible:
                logger.info(f"  Validation Modal Message: '{modal_text}'")
                
            logger.info(f"  Network Activity:")
            logger.info(f"    Total requests: {len(requests)}")
            logger.info(f"    Total responses: {len(responses)}")
            logger.info(f"    Failed requests: {len(failures)}")
            for idx, req in enumerate(requests, start=1):
                logger.info(f"      Request {idx}: {req['method']} '{req['url']}' ({req['resource_type']})")
            for idx, res in enumerate(responses, start=1):
                logger.info(f"      Response {idx}: status {res['status']} for '{res['url']}'")
            for idx, fail in enumerate(failures, start=1):
                logger.warning(f"      Failed Request {idx}: '{fail['url']}' - Error: '{fail['error_text']}'")
                
        except Exception as e:
            logger.error(f"  Error capturing post-click diagnostics: {e}")
        logger.info("==============================")

    def click_view(self, case_summary: CaseSummary) -> None:
        """Clicks the View button for the given CaseSummary using its view_index or case_number."""
        logger.info(f"Selecting View link for Case {case_summary.case_number} (index: {case_summary.view_index})...")
        
        # 1. Before any click, call dismiss_validation_modal()
        self.dismiss_validation_modal()
        
        # 2. Verify modal is hidden/absent before clicking View
        modal = self.page.locator("#validateError")
        if modal.count() > 0 and modal.is_visible():
            raise Exception("Cannot click View: #validateError modal is still blocking pointer events.")
            
        # Locate the table first
        table_locator = self.page.locator("table#dispTable, table#showListTable, table:has-text('Petitioner Name versus Respondent Name')").first
        
        # Try to locate by case number first
        row_locator = table_locator.locator("tr").filter(has_text=case_summary.case_number)
        marked_temp = False
        
        if row_locator.count() != 1:
            logger.warning(f"Could not uniquely locate row by case number '{case_summary.case_number}'. Falling back to view_index: {case_summary.view_index}")
            js_find_row = f"""() => {{
                const tables = Array.from(document.querySelectorAll("table"));
                let table = null;
                for (const t of tables) {{
                    if (t.innerText.includes("Petitioner Name versus Respondent Name") || 
                        t.innerText.includes("Case Type/Case Number/Case Year")) {{
                        table = t;
                        break;
                    }}
                }}
                if (!table) return false;
                const rows = Array.from(table.rows);
                let currentIdx = 0;
                for (let i = 0; i < rows.length; i++) {{
                    const row = rows[i];
                    const cells = Array.from(row.cells);
                    if (cells.length < 3) continue;
                    if (row.querySelector("th") || cells.some(c => c.colSpan > 1)) continue;
                    const srNo = cells[0].innerText.trim();
                    if (!/^\\d+$/.test(srNo)) continue;
                    
                    if (currentIdx === {case_summary.view_index}) {{
                        row.setAttribute("data-scrape-target", "true");
                        return true;
                    }}
                    currentIdx++;
                }}
                return false;
            }}"""
            marked = self.page.evaluate(js_find_row)
            if marked:
                row_locator = self.page.locator("tr[data-scrape-target='true']")
                marked_temp = True
            else:
                raise ValueError(f"Could not locate row for case number '{case_summary.case_number}' or index {case_summary.view_index}")
                
        # Scope the View link lookup to only inside this row
        locator = row_locator.locator("a[onclick*='viewHistory'], a:has-text('View')")
        
        # Verify View link is attached and scroll into view if needed
        locator.wait_for(state="attached", timeout=10000)
        locator.scroll_into_view_if_needed()
        
        # Double check modal again just in case scrolling/focus triggered anything
        self.dismiss_validation_modal()
        if modal.count() > 0 and modal.is_visible():
            raise Exception("Cannot click View: #validateError modal is still blocking pointer events.")
            
        # Capture pre-click state
        pre_url = self.page.url
        pre_title = self.page.title()
        
        # Log pre-click diagnostics
        self._log_pre_click_diagnostics(locator, case_summary)
        
        # Setup network event listeners
        requests_logged = []
        responses_logged = []
        failures_logged = []
        
        def on_request(req):
            requests_logged.append({
                "url": req.url,
                "method": req.method,
                "resource_type": req.resource_type
            })
        def on_response(res):
            responses_logged.append({
                "url": res.url,
                "status": res.status,
                "ok": res.ok
            })
        def on_request_failed(req):
            failures_logged.append({
                "url": req.url,
                "error_text": req.failure if req.failure else "Unknown error"
            })
            
        self.page.on("request", on_request)
        self.page.on("response", on_response)
        self.page.on("requestfailed", on_request_failed)
        
        # Log window.location.href before opening the case
        current_href = self.page.url
        logger.info(f"Opening Case. Current window.location.href: '{current_href}'")
        if "?p=casestatus/index" not in current_href:
            raise Exception(f"Current page URL '{current_href}' does not contain '?p=casestatus/index'. Aborting to prevent invalid navigation state.")
            
        try:
            # Retrieve the onclick attribute of the View anchor
            onclick = locator.get_attribute("onclick")
            if not onclick:
                raise ValueError("View anchor does not contain an 'onclick' attribute.")
            logger.info(f"Executing View anchor onclick action directly via JS evaluation: {onclick}")
            
            # Execute the JavaScript directly
            self.page.evaluate(f"() => {{ {onclick} }}")
            
            # Wait briefly for AJAX request/response to trigger or UI to change
            self.page.wait_for_timeout(1000)
            
            # Log post-click diagnostics
            self._log_post_click_diagnostics(
                locator, pre_url, pre_title, requests_logged, responses_logged, failures_logged
            )
            
            # Check for validation error modal AFTER the click
            modal_selector = "#validateError"
            modal = self.page.locator(modal_selector)
            if modal.count() > 0 and modal.is_visible():
                message_text = modal.inner_text().strip()
                logger.error(f"Post-click validation error modal detected: '{message_text}'")
                
                # Take screenshot
                self._capture_failure_screenshot(f"validation_modal_after_click_{case_summary.serial_number}")
                
                # Dismiss modal
                self.dismiss_validation_modal()
                
                raise Exception(f"Validation error modal displayed after clicking View: {message_text}")
                
            # Clean up attribute if temporary
            if marked_temp:
                self.page.evaluate("() => { const el = document.querySelector('tr[data-scrape-target]'); if (el) el.removeAttribute('data-scrape-target'); }")
                
        except Exception as e:
            logger.error(f"Failed to click or process View link for case {case_summary.case_number}: {e}")
            self._capture_failure_screenshot(f"view_click_failure_{case_summary.serial_number}")
            if marked_temp:
                self.page.evaluate("() => { const el = document.querySelector('tr[data-scrape-target]'); if (el) el.removeAttribute('data-scrape-target'); }")
            raise
        finally:
            # Always unsubscribe network listeners
            self.page.remove_listener("request", on_request)
            self.page.remove_listener("response", on_response)
            self.page.remove_listener("requestfailed", on_request_failed)

    def wait_for_case_detail_page(self, timeout: int = 15000) -> None:
        """Waits until the case details section is loaded and visible.

        Uses multiple fallback selectors to detect a successful load.
        """
        import time
        logger.info("Waiting for case details page to load...")
        
        # Immediately dump complete DOM to logs/after_view.html for diagnostic review
        try:
            html_content = self.page.content()
            after_view_path = config.LOGS_DIR / "after_view.html"
            with open(after_view_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"Complete DOM dumped to: {after_view_path}")
        except Exception as e:
            logger.error(f"Failed to dump DOM to after_view.html: {e}")

        # Check for application-level portal failure messages ("Oops! ... Invalid Request", "Session timeout")
        try:
            body_text = self.page.inner_text("body")
            # Spec §13: Explicit session timeout detection
            if "Session timeout" in body_text or "session timeout" in body_text:
                err_msg = "SESSION_TIMEOUT: eCourts portal returned 'Session timeout'. Scraper MUST stop and checkpoint."
                logger.critical(err_msg)
                self._capture_failure_screenshot("session_timeout")
                raise ECourtsPortalError(err_msg)
            if "Oops!" in body_text or "Invalid Request" in body_text or "something wrong" in body_text or "Welcome User Search Page not Found" in body_text:
                err_msg = "eCourts portal returned application error ('Oops! There is something wrong... Invalid Request')."
                logger.error(err_msg)
                self._capture_failure_screenshot("portal_oops_error")
                raise ECourtsPortalError(err_msg)
        except ECourtsPortalError:
            raise
        except Exception:
            pass

        # Unique indicators that exist ONLY on the detail view page
        indicators = [
            "text=Case Details",
            "text=History of Case Hearing",
            "text=Petitioner and Advocate",
            "text=Respondent and Advocate",
            "text=Acts",
            "#caseHistory",
            ".case_details_table"
        ]
        
        start_time = time.time()
        found = False
        last_err = None
        
        while (time.time() - start_time) * 1000 < timeout:
            for selector in indicators:
                try:
                    # Check if at least one indicator is visible
                    el = self.page.locator(selector).first
                    if el.is_visible():
                        logger.info(f"Case details page detected using indicator: '{selector}'")
                        found = True
                        break
                except Exception as e:
                    last_err = e
            if found:
                break
            self.page.wait_for_timeout(200)
            
        if not found:
            self._capture_failure_screenshot("case_detail_load_failure")
            raise TimeoutError(f"Case detail page failed to load within {timeout}ms. Last error: {last_err}")

    def get_minimal_case_details(self) -> CaseDetail:
        """Extracts case details and populates CaseDetail model from the loaded detail view.

        Scopes the extraction to the active detail container to avoid document-wide conflicts.
        """
        container_selector = "div[id^='CS']:has(table.case_details_table)"
        
        # Wait for container to be attached/visible
        self.page.locator(container_selector).wait_for(state="visible", timeout=15000)
        
        # 1. Log the selector used for the detail container
        container_id = self.page.locator(container_selector).evaluate("el => el.id")
        logger.info(f"Using detail container selector: '{container_selector}' (Resolved ID: '{container_id}')")
        
        # 2. Log the first 20 lines of text extracted from that container before parsing
        container_text = self.page.locator(container_selector).inner_text()
        lines = [line.strip() for line in container_text.splitlines() if line.strip()]
        logger.info("=== FIRST 20 LINES OF EXTRACTED DETAIL CONTAINER TEXT ===")
        for idx, line in enumerate(lines[:20], start=1):
            logger.info(f"{idx}: {line}")
        logger.info("=========================================================")
        
        # 3. Perform robust label-value extraction using pure python parser
        details = parse_case_detail_text(container_text)
        
        # 4. Evaluate structured JS extractor for repeatable tables and ajax pdf links
        js_extract_details = """async () => {
            const data = {
                label_values: {},
                petitioners: [],
                respondents: [],
                acts: [],
                processes: [],
                history: [],
                orders: [],
                transfers: []
            };

            const clean = (txt) => (txt || "").trim().replace(/\\s+/g, " ");

            // 1. Case Details Table
            const detailsTable = document.querySelector("table.case_details_table");
            if (detailsTable) {
                const rows = Array.from(detailsTable.querySelectorAll("tr"));
                rows.forEach(r => {
                    const cells = Array.from(r.querySelectorAll("td, th"));
                    for (let i = 0; i < cells.length; i += 2) {
                        if (i + 1 < cells.length) {
                            const lbl = clean(cells[i].innerText).replace(/:+$/, "").trim().toLowerCase();
                            const val = clean(cells[i+1].innerText);
                            if (lbl) data.label_values[lbl] = val;
                        }
                    }
                });
            }

            // 2. Case Status Table
            const statusTable = document.querySelector("table.case_status_table");
            if (statusTable) {
                const rows = Array.from(statusTable.querySelectorAll("tr"));
                rows.forEach(r => {
                    const cells = Array.from(r.querySelectorAll("td, th"));
                    if (cells.length >= 2) {
                        const lbl = clean(cells[0].innerText).replace(/:+$/, "").trim().toLowerCase();
                        const val = clean(cells[1].innerText);
                        if (lbl) data.label_values[lbl] = val;
                    }
                });
            }

            // 3. Parties lists
            const parsePartiesList = (ulSelector) => {
                const ul = document.querySelector(ulSelector);
                if (!ul) return [];
                const parties = [];
                const lis = Array.from(ul.querySelectorAll("li"));
                lis.forEach(li => {
                    const lines = li.innerText.split("\\n").map(clean).filter(Boolean);
                    for (let i = 0; i < lines.length; i++) {
                        const line = lines[i];
                        if (/^advocate/i.test(line)) {
                            let adv = line.replace(/^advocate\\b[-:\\s]*/i, "").trim();
                            adv = adv.replace(/^[-:\\s]+/, "").trim();
                            if (parties.length > 0) {
                                parties[parties.length - 1].advocate = adv;
                            }
                        } else {
                            const name = line.replace(/^\\d+[\\)\\.]\\s*/, "").trim();
                            parties.push({ name: name, advocate: null });
                        }
                    }
                });
                return parties;
            };
            data.petitioners = parsePartiesList("ul.Petitioner_Advocate_table");
            data.respondents = parsePartiesList("ul.Respondent_Advocate_table");

            // 4. Acts Table
            const actTable = document.querySelector("table.acts_table, table#act_table");
            if (actTable) {
                const rows = Array.from(actTable.querySelectorAll("tr"));
                rows.forEach(r => {
                    if (r.querySelector("th")) return;
                    const cells = Array.from(r.querySelectorAll("td")).map(td => clean(td.innerText));
                    if (cells.length >= 2) {
                        data.acts.push({
                            act_name: cells[0],
                            sections: cells[1]
                        });
                    }
                });
            }

            // 5. Processes Table
            const procTable = document.querySelector("table.FIR_details_table, table#process");
            if (procTable) {
                const rows = Array.from(procTable.querySelectorAll("tr"));
                rows.forEach(r => {
                    if (r.querySelector("th")) return;
                    const cells = Array.from(r.querySelectorAll("td")).map(td => clean(td.innerText));
                    if (cells.length >= 3) {
                        data.processes.push({
                            process_id: cells[0],
                            process_title: cells[1],
                            process_date: cells[2]
                        });
                    }
                });
            }

            // 6. Case History Table
            const histTable = document.querySelector("table.history_table");
            if (histTable) {
                const rows = Array.from(histTable.querySelectorAll("tr"));
                rows.forEach(r => {
                    if (r.querySelector("th")) return;
                    const cells = Array.from(r.querySelectorAll("td"));
                    if (cells.length >= 4) {
                        const dateLinkEl = cells[1].querySelector("a");
                        let businessDateLink = "";
                        if (dateLinkEl) {
                            businessDateLink = dateLinkEl.getAttribute("onclick") || "";
                        }
                        data.history.push({
                            judge: clean(cells[0].innerText),
                            business_date: clean(cells[1].innerText),
                            hearing_date: clean(cells[2].innerText),
                            purpose: clean(cells[3].innerText),
                            business_date_link: businessDateLink
                        });
                    }
                });
            }

            // 7. Orders Table
            const ordTable = document.querySelector("table.order_table");
            if (ordTable) {
                const rows = Array.from(ordTable.querySelectorAll("tr"));
                rows.forEach(r => {
                    if (r.querySelector("th")) return;
                    const cells = Array.from(r.querySelectorAll("td"));
                    if (cells.length >= 3) {
                        const orderNum = clean(cells[0].innerText);
                        const orderDate = clean(cells[1].innerText);
                        const linkEl = cells[2].querySelector("a");
                        let orderLink = "";
                        let ajaxParams = null;
                        let onclick = "";
                        
                        if (linkEl) {
                            onclick = linkEl.getAttribute("onclick") || "";
                            const match = onclick.match(/displayPdf\\s*\\(([^)]+)\\)/);
                            if (match) {
                                ajaxParams = match[1].split(",").map(s => s.trim().replace(/^['"]|['"]$/, ""));
                            } else {
                                const href = linkEl.getAttribute("href") || "";
                                if (href && href !== "#" && !href.startsWith("javascript")) {
                                    orderLink = href;
                                }
                            }
                        }
                        data.orders.push({
                            order_number: orderNum,
                            order_date: orderDate,
                            order_link: orderLink,
                            ajaxParams: ajaxParams,
                            onclick: onclick
                        });
                    }
                });
            }

            // 8. Transfers Table
            const transTable = document.querySelector("table.transfer_table");
            if (transTable) {
                const rows = Array.from(transTable.querySelectorAll("tr"));
                rows.forEach(r => {
                    if (r.querySelector("th")) return;
                    const cells = Array.from(r.querySelectorAll("td")).map(td => clean(td.innerText));
                    if (cells.length >= 4) {
                        data.transfers.push({
                            registration_number: cells[0],
                            transfer_date: cells[1],
                            from_court: cells[2],
                            to_court: cells[3]
                        });
                    }
                });
            }

            const resolvePdf = (params) => {
                return new Promise((resolve) => {
                    if (!params || typeof ajaxCall === 'undefined') {
                        resolve("");
                        return;
                    }
                    const [normal_v, case_val, court_code, filename, appFlag] = params;
                    const postdata = "&normal_v=" + normal_v + "&case_val=" + case_val + "&court_code=" + court_code + "&filename=" + filename + "&appFlag=" + (appFlag || "");
                    ajaxCall({
                        url: 'home/display_pdf',
                        postdata: postdata,
                        callback: (res) => {
                            if (res && res.status && res.order) {
                                resolve("https://services.ecourts.gov.in/ecourtindia_v6/" + res.order);
                            } else {
                                resolve("");
                            }
                        }
                    });
                });
            };

            for (let i = 0; i < data.orders.length; i++) {
                const order = data.orders[i];
                if (order.ajaxParams) {
                    try {
                        const pdfUrl = await resolvePdf(order.ajaxParams);
                        order.order_link = pdfUrl;
                    } catch (e) {
                        // ignore
                    }
                    delete order.ajaxParams;
                }
            }

            return data;
        }"""
        try:
            extracted = self.page.evaluate(js_extract_details)
            logger.info("Successfully evaluated JS detail extractor.")
            
            # Map JS lists to dataclasses
            
            if extracted.get("acts"):
                details.acts = [ActEntry(act_name=a["act_name"], sections=a["sections"]) for a in extracted["acts"]]
            if extracted.get("processes"):
                details.processes = [ProcessEntry(process_id=p["process_id"], process_title=p["process_title"], process_date=p["process_date"]) for p in extracted["processes"]]
            if extracted.get("history"):
                details.history = [HearingRecord(judge=h["judge"], business_date=h["business_date"], hearing_date=h["hearing_date"], purpose=h["purpose"], business_date_link=h.get("business_date_link")) for h in extracted["history"]]
            if extracted.get("orders"):
                details.orders = [OrderEntry(order_number=o["order_number"], order_date=o["order_date"], order_link=o["order_link"], business=o.get("business"), nature_of_disposal=o.get("nature_of_disposal"), disposal_date=o.get("disposal_date"), order_text=o.get("order_text"), metadata=o.get("metadata")) for o in extracted["orders"]]
            if extracted.get("transfers"):
                details.transfers = [TransferEntry(registration_number=t["registration_number"], transfer_date=t["transfer_date"], from_court=t["from_court"], to_court=t["to_court"]) for t in extracted["transfers"]]
                
            # If parties are parsed by JS, update
            if extracted.get("petitioners"):
                details.petitioners = [(p["name"], p["advocate"]) for p in extracted["petitioners"]]
            if extracted.get("respondents"):
                details.respondents = [(r["name"], r["advocate"]) for r in extracted["respondents"]]
                
            # Merge all label values from JS extractor (which is more robust as it has HTML layout)
            lv = extracted.get("label_values", {})
            
            def get_val(keys: list[str]) -> str | None:
                for key in keys:
                    if key in lv:
                        return lv[key]
                return None
                
            if get_val(["case type"]) is not None:
                details.case_type = get_val(["case type"])
            if get_val(["filing number"]) is not None:
                details.filing_number = get_val(["filing number"])
            if get_val(["filing date"]) is not None:
                details.filing_date = get_val(["filing date"])
            if get_val(["registration number"]) is not None:
                details.registration_number = get_val(["registration number"])
            if get_val(["registration date"]) is not None:
                details.registration_date = get_val(["registration date"])
            if get_val(["e-filing number", "efiling number"]) is not None:
                details.efiling_number = get_val(["e-filing number", "efiling number"])
            if get_val(["e-filing date", "efiling date"]) is not None:
                details.efiling_date = get_val(["e-filing date", "efiling date"])
            if get_val(["cnr number"]) is not None:
                raw_cnr = get_val(["cnr number"])
                if raw_cnr:
                    details.cnr_number = raw_cnr.split()[0]
            if get_val(["first hearing date"]) is not None:
                details.first_hearing_date = get_val(["first hearing date"])
            if get_val(["decision date"]) is not None:
                details.decision_date = get_val(["decision date"])
            if get_val(["case status"]) is not None:
                details.case_status = get_val(["case status"])
            if get_val(["nature of disposal"]) is not None:
                details.nature_of_disposal = get_val(["nature of disposal"])
            if get_val(["court number and judge"]) is not None:
                details.court_number_and_judge = get_val(["court number and judge"])
                    
        except Exception as e:
            logger.error(f"Error executing JS detail extractor: {e}", exc_info=True)
            
        logger.info(f"Extracted CaseDetail: {details}")

        # Save per-case HTML DOM snapshot reference
        try:
            snapshot_dir = config.DATA_DIR / "snapshots"
            snapshot_dir.mkdir(parents=True, exist_ok=True)
            safe_num = (details.case_number or "unknown").replace("/", "_").replace("\\", "_")
            snapshot_path = snapshot_dir / f"EX_{safe_num}.html"
            page_content = self.page.content()
            with open(snapshot_path, "w", encoding="utf-8") as f:
                f.write(page_content)
            logger.info(f"Saved per-case HTML snapshot to {snapshot_path}")
        except Exception as snap_err:
            logger.warning(f"Could not save HTML snapshot: {snap_err}")

        return details

    def follow_orders_and_business(self, details: CaseDetail) -> None:
        """Clicks each Case History link and Final Orders link to extract details and PDFs."""
        from pathlib import Path
        logger.info(f"Following business and order links for case {details.case_number}")
        
        # 1. Process Case History Business Date links
        history_orders = {}
        for r_idx, record in enumerate(details.history):
            if not record.business_date_link:
                continue
            
            logger.info(f"Clicking history link for date {record.business_date}: {record.business_date_link}")
            try:
                # Click programmatically
                self.page.evaluate(f"() => {{ {record.business_date_link} }}")
                
                # Wait for Case Business Div to be visible and populated
                self.page.wait_for_selector("#caseBusinessDiv_caseType:visible", timeout=12000)
                self.page.wait_for_timeout(1000)
                
                # Extract business page details
                js_extract_business = """() => {
                    const container = document.getElementById("caseBusinessDiv_caseType");
                    if (!container) return null;
                    const clean = (txt) => (txt || "").trim().replace(/\\s+/g, " ");
                    
                    const labelValues = {};
                    const tables = Array.from(container.querySelectorAll("table"));
                    tables.forEach(table => {
                        const rows = Array.from(table.querySelectorAll("tr"));
                        rows.forEach(r => {
                            const cells = Array.from(r.querySelectorAll("td, th"));
                            if (cells.length === 2) {
                                const lbl = clean(cells[0].innerText).replace(/:+$/, "").trim().toLowerCase();
                                const val = clean(cells[1].innerText);
                                if (lbl) labelValues[lbl] = val;
                            } else if (cells.length === 4) {
                                for (let i = 0; i < cells.length; i += 2) {
                                    if (i + 1 < cells.length) {
                                        const lbl = clean(cells[i].innerText).replace(/:+$/, "").trim().toLowerCase();
                                        const val = clean(cells[i+1].innerText);
                                        if (lbl) labelValues[lbl] = val;
                                    }
                                }
                            }
                        });
                    });
                    
                    // Search for any documents/PDF links inside the business container
                    const docs = [];
                    const anchors = Array.from(container.querySelectorAll("a"));
                    anchors.forEach(a => {
                        const href = a.getAttribute("href") || "";
                        const onclick = a.getAttribute("onclick") || "";
                        const text = clean(a.innerText);
                        if (href || onclick) {
                            docs.push({ text: text, href: href, onclick: onclick });
                        }
                    });
                    
                    // Fallback search for business text
                    let businessText = labelValues["business"] || labelValues["business on date"] || labelValues["business of the day"] || "";
                    if (!businessText) {
                        const tds = Array.from(container.querySelectorAll("td"));
                        for (const td of tds) {
                            const text = clean(td.innerText);
                            if (text.toLowerCase().includes("business") || text.toLowerCase().includes("order")) {
                                businessText = text;
                                break;
                            }
                        }
                    }
                    if (!businessText) {
                        businessText = clean(container.innerText);
                    }
                    
                    return {
                        full_text: clean(container.innerText),
                        label_values: labelValues,
                        business_text: businessText,
                        documents: docs
                    };
                }"""
                
                business_data = self.page.evaluate(js_extract_business)
                if business_data:
                    # Save details
                    lbls = business_data.get("label_values", {})
                    history_orders[record.business_date] = {
                        "business": business_data.get("business_text"),
                        "nature_of_disposal": lbls.get("nature of disposal", lbls.get("disposal", "")),
                        "disposal_date": lbls.get("disposal date", record.business_date),
                        "judge": lbls.get("judge", lbls.get("court number and judge", "")),
                        "order_text": business_data.get("full_text"),
                        "metadata": lbls,
                        "documents": business_data.get("documents", [])
                    }
                    logger.info(f"Extracted history details for date {record.business_date}.")
                
            except Exception as e:
                logger.error(f"Failed to follow business link for date {record.business_date}: {e}")
            
            # Programmatically return
            try:
                self.page.evaluate("""() => {
                    document.getElementById("caseBusinessDiv_caseType").style.display = "none";
                    const pFir = document.getElementById("printDiv_fir");
                    if (pFir) pFir.style.display = "none";
                    document.getElementById("history").style.display = "block";
                    document.getElementById("CScaseType").style.display = "block";
                    const mBack = document.getElementById("main_back_caseType");
                    if (mBack) mBack.style.display = "block";
                }""")
                self.page.wait_for_selector("#history:visible", timeout=10000)
            except Exception as e:
                logger.error(f"Failed programmatically returning from business view: {e}")
                # Fallback return
                try:
                    self.return_to_results()
                    self.wait_for_results_table()
                    logger.warning("Attempting fallback view click...")
                    self.click_view(details)
                    self.wait_for_case_detail_page()
                except Exception:
                    pass
        
        # 2. Match and update details.orders with layer tracking (spec §10, §24)
        updated_orders = []
        matched_dates = set()
        
        for ord_idx, o in enumerate(details.orders):
            matched = history_orders.get(o.order_date)
            docs = []
            
            # Layer D: Track whether a downloadable document/PDF link is exposed
            has_pdf_url = bool(o.order_link and o.order_link.strip())
            o.document_link_found = has_pdf_url
            o.document_url = o.order_link if has_pdf_url else None
            
            # Try to resolve PDF link
            pdf_url = o.order_link
            pdf_text = ""
            dest_path = None
            
            if pdf_url:
                filename = Path(pdf_url).name
                if not filename.lower().endswith(".pdf"):
                    filename = f"order_{details.case_number.replace('/', '_')}_{o.order_number}.pdf"
                dest_path = config.ORDERS_DIR / filename
                
                logger.info(f"Downloading PDF: {pdf_url} to {dest_path}")
                try:
                    res = self.page.request.get(pdf_url)
                    if res.status == 200:
                        dest_path.write_bytes(res.body())
                        logger.info(f"Downloaded PDF successfully: {dest_path}")
                        
                        # Extract PDF text
                        try:
                            import pypdf
                            reader = pypdf.PdfReader(str(dest_path))
                            txt_pages = []
                            for pg in reader.pages:
                                txt_pages.append(pg.extract_text() or "")
                            pdf_text = "\n".join(txt_pages).strip()
                            logger.info(f"Extracted {len(pdf_text)} characters from PDF.")
                        except Exception as pdf_err:
                            logger.error(f"Failed extracting PDF text: {pdf_err}")
                            
                        docs.append({
                            "url": pdf_url,
                            "link_text": "Orders",
                            "filename": filename,
                            "local_path": str(dest_path)
                        })
                except Exception as dl_err:
                    logger.error(f"Failed downloading PDF order {pdf_url}: {dl_err}")
            
            if matched:
                matched_dates.add(o.order_date)
                # Layer B: Order/business page was successfully opened
                o.order_page_found = True
                
                # Download any documents found in business details page too
                for doc in matched.get("documents", []):
                    doc_url = doc.get("href")
                    if doc_url and doc_url != "#":
                        if doc_url.startswith("/"):
                            doc_url = "https://services.ecourts.gov.in" + doc_url
                        elif not doc_url.startswith("http"):
                            doc_url = "https://services.ecourts.gov.in/ecourtindia_v6/" + doc_url
                        
                        # Update Layer D if we find a document link in business page
                        if not o.document_link_found:
                            o.document_link_found = True
                            o.document_url = doc_url
                        
                        doc_filename = Path(doc_url).name or f"doc_{o.order_date}.pdf"
                        doc_dest = config.ORDERS_DIR / doc_filename
                        try:
                            res = self.page.request.get(doc_url)
                            if res.status == 200:
                                doc_dest.write_bytes(res.body())
                                docs.append({
                                    "url": doc_url,
                                    "link_text": doc.get("text", "Document"),
                                    "filename": doc_filename,
                                    "local_path": str(doc_dest)
                                })
                        except Exception:
                            pass
                
                o.business = matched.get("business")
                o.nature_of_disposal = matched.get("nature_of_disposal")
                o.disposal_date = matched.get("disposal_date")
                o.order_text = pdf_text or matched.get("order_text")
                o.metadata = matched.get("metadata")
                
                # Layer C: Order text found if we have any text
                o.order_text_found = bool(o.order_text and o.order_text.strip())
            else:
                o.order_text = pdf_text
                # Layer B: No matching business page was opened for this order
                o.order_page_found = False
                # Layer C: Only PDF text if available
                o.order_text_found = bool(pdf_text and pdf_text.strip())
                
            o.local_path = str(dest_path) if pdf_url and dest_path and dest_path.exists() else None
            o.metadata = o.metadata or {}
            o.metadata["documents"] = docs
            
            updated_orders.append(o)
            
        # Add unmatched history orders as new order entries
        for date, details_dict in history_orders.items():
            if date in matched_dates:
                continue
            
            order_text_val = details_dict.get("order_text")
            has_docs = any(
                d.get("href") and d.get("href") != "#"
                for d in details_dict.get("documents", [])
            )
            
            new_ord = OrderEntry(
                order_number=f"H-{date}",
                order_date=date,
                order_link="",
                local_path=None,
                business=details_dict.get("business"),
                nature_of_disposal=details_dict.get("nature_of_disposal"),
                disposal_date=details_dict.get("disposal_date"),
                order_text=order_text_val,
                metadata=details_dict.get("metadata") or {},
                # Layer tracking
                order_page_found=True,  # We opened the business page
                order_text_found=bool(order_text_val and order_text_val.strip()),
                document_link_found=has_docs,
                document_url=None,
            )
            new_ord.metadata["documents"] = details_dict.get("documents", [])
            updated_orders.append(new_ord)
            
        details.orders = updated_orders
        logger.info(f"Total order details matched/created: {len(details.orders)}")

    def return_to_results(self) -> None:
        """Returns to the search results page by clicking the correct Back button or triggering JS state transition.

        Forces the transition specifically for CScaseType (Case Type search results).
        """
        import time
        start_total = time.perf_counter()
        logger.info("Starting return to search results...")
        
        # 1. Before any click, dismiss validation modal
        self.dismiss_validation_modal()
        
        # Save before_return.html DOM dump
        try:
            logger.info("Saving DOM dump before return...")
            with open(config.LOGS_DIR / "before_return.html", "w", encoding="utf-8") as f:
                f.write(self.page.content())
            logger.info("Saved DOM to before_return.html")
        except Exception as e:
            logger.error(f"Failed to save before_return.html: {e}")
            
        clicked = False
        
        # 2. Directly target #main_back_caseType first
        back_selector = "#main_back_caseType"
        back_btn = self.page.locator(back_selector)
        if back_btn.count() > 0 and back_btn.is_visible():
            logger.info(f"Directly clicking Back button using selector: '{back_selector}'")
            try:
                start_click = time.perf_counter()
                back_btn.click()
                logger.info(f"Direct click on '{back_selector}' completed in {time.perf_counter() - start_click:.4f}s")
                clicked = True
            except Exception as e:
                logger.exception(f"Direct click on '{back_selector}' failed: {e}")
                
        # 3. If direct button wasn't clicked/visible, programmatically trigger the JS state transition
        if not clicked:
            logger.info("Back button #main_back_caseType was not visible or not clicked. Programmatically executing main_back('CScaseType')...")
            try:
                start_js = time.perf_counter()
                self.page.evaluate("main_back('CScaseType')")
                logger.info(f"Programmatic JS transition main_back('CScaseType') completed in {time.perf_counter() - start_js:.4f}s")
                clicked = True
            except Exception as e:
                logger.error(f"Programmatic JS transition main_back('CScaseType') failed: {e}")
                
        # Save after return attempt
        try:
            with open(config.LOGS_DIR / "after_return.html", "w", encoding="utf-8") as f:
                f.write(self.page.content())
            logger.info("Saved DOM to after_return.html")
        except Exception as e:
            logger.error(f"Failed to save after_return.html: {e}")
            
        # Verify typeof viewHistory and wait until available
        start_verify = time.time()
        while time.time() - start_verify < 15:
            vh_type = self.page.evaluate("typeof viewHistory")
            logger.info(f"Diagnostics post-return: typeof viewHistory = '{vh_type}'")
            if vh_type == "function":
                break
            self.page.wait_for_timeout(500)
            
        if self.page.evaluate("typeof viewHistory") != "function":
            logger.error("viewHistory is not a function after back navigation!")
            
        logger.info(f"Return method completed in {time.perf_counter() - start_total:.4f}s total.")

    def wait_for_results_table(self, timeout: int = 15000) -> None:
        """Waits until the search results table is fully restored, visible, and has active rows."""
        import time
        logger.info("Waiting for search results table to reappear and stabilize...")
        start_time = time.time()
        
        while (time.time() - start_time) * 1000 < timeout:
            has_rows = self.page.evaluate("""() => {
                const tables = Array.from(document.querySelectorAll("table"));
                let table = null;
                for (const t of tables) {
                    if (t.innerText.includes("Petitioner Name versus Respondent Name") || 
                        t.innerText.includes("Case Type/Case Number/Case Year")) {
                        table = t;
                        break;
                    }
                }
                if (!table) return false;
                const rows = Array.from(table.rows).filter(r => {
                    const cells = Array.from(r.cells);
                    if (cells.length < 3) return false;
                    if (r.querySelector("th")) return false;
                    return Array.from(r.querySelectorAll("a")).some(a => (a.getAttribute("onclick") || "").includes("viewHistory") || a.innerText.trim() === "View");
                });
                return rows.length > 0;
            }""")
            
            if has_rows:
                logger.info("Search results table successfully found with active rows.")
                self.page.wait_for_timeout(1000)
                return
                
            self.page.wait_for_timeout(500)
            
        raise TimeoutError(f"Results table did not reappear within {timeout}ms.")

    # -----------------------------------------------------------------------
    # Pagination Support
    # -----------------------------------------------------------------------

    def get_pagination_info(self) -> dict:
        """Reads the pagination bar to determine current page, total pages, and navigation state.

        Returns:
            Dict with keys: current_page, total_pages, has_next, has_prev, total_records.
        """
        js_pagination = """() => {
            const result = {
                current_page: 1,
                total_pages: 1,
                has_next: false,
                has_prev: false,
                total_records: 0,
                page_links: []
            };

            // Look for text like "Showing 1-25 of 312"
            const allText = document.body.innerText;
            const showingMatch = allText.match(/Showing\\s+(\\d+)\\s*[-\\u2013to]+\\s*(\\d+)\\s+of\\s+(\\d+)/i);
            if (showingMatch) {
                result.total_records = parseInt(showingMatch[3]);
            }

            // Check for "Total Records: N"
            const totalMatch = allText.match(/Total\\s+Records?\\s*[:\\s]+(\\d+)/i);
            if (totalMatch) {
                result.total_records = parseInt(totalMatch[1]);
            }

            // Look for page links
            const pageAnchors = document.querySelectorAll(
                'a[onclick*="dispPaging"], a[onclick*="paging"], ' +
                'a[onclick*="gotoPage"], a[onclick*="nextPage"], ' +
                '.pagination a, .paging a'
            );

            if (pageAnchors.length > 0) {
                const pages = new Set();

                pageAnchors.forEach(a => {
                    const text = a.innerText.trim();
                    const onclick = a.getAttribute('onclick') || '';

                    if (/next|>>|\\u00bb|\\u203a/i.test(text)) {
                        const isDisabled = a.classList.contains('disabled') ||
                                           (a.parentElement && a.parentElement.classList.contains('disabled')) ||
                                           a.getAttribute('aria-disabled') === 'true';
                        result.has_next = !isDisabled;
                    }

                    if (/prev|<<|\\u00ab|\\u2039/i.test(text)) {
                        const isDisabled = a.classList.contains('disabled') ||
                                           (a.parentElement && a.parentElement.classList.contains('disabled')) ||
                                           a.getAttribute('aria-disabled') === 'true';
                        result.has_prev = !isDisabled;
                    }

                    const pageNum = parseInt(text);
                    if (!isNaN(pageNum)) {
                        pages.add(pageNum);
                        const isActive = a.classList.contains('active') ||
                                         (a.parentElement && a.parentElement.classList.contains('active')) ||
                                         a.getAttribute('aria-current') === 'page';
                        if (isActive) {
                            result.current_page = pageNum;
                        }
                    }

                    result.page_links.push({
                        text: text,
                        onclick: onclick.substring(0, 200)
                    });
                });

                if (pages.size > 0) {
                    result.total_pages = Math.max(...pages);
                }
            }

            return result;
        }"""

        try:
            info = self.page.evaluate(js_pagination)
            logger.info(
                f"Pagination info: page {info['current_page']}/{info['total_pages']}, "
                f"has_next={info['has_next']}, total_records={info['total_records']}"
            )
            return info
        except Exception as e:
            logger.error(f"Failed to read pagination info: {e}")
            return {
                "current_page": 1, "total_pages": 1,
                "has_next": False, "has_prev": False,
                "total_records": 0, "page_links": []
            }

    def has_next_page(self) -> bool:
        """Returns True if there is a next page of results available."""
        info = self.get_pagination_info()
        return info.get("has_next", False)

    def click_next_page(self) -> bool:
        """Clicks the Next page link and waits for the results table to refresh.

        Returns:
            True if successfully navigated to the next page, False otherwise.
        """
        logger.info("Attempting to navigate to next results page...")

        js_click_next = """() => {
            const pageAnchors = document.querySelectorAll(
                'a[onclick*="dispPaging"], a[onclick*="paging"], ' +
                'a[onclick*="gotoPage"], a[onclick*="nextPage"], ' +
                '.pagination a, .paging a'
            );

            for (const a of pageAnchors) {
                const text = a.innerText.trim();
                if (/^(next|>>|\\u00bb|\\u203a)$/i.test(text)) {
                    const isDisabled = a.classList.contains('disabled') ||
                                       (a.parentElement && a.parentElement.classList.contains('disabled'));
                    if (!isDisabled) {
                        const onclick = a.getAttribute('onclick');
                        if (onclick) {
                            eval(onclick);
                            return { clicked: true, method: 'onclick_eval', text: text };
                        } else {
                            a.click();
                            return { clicked: true, method: 'direct_click', text: text };
                        }
                    }
                }
            }
            return { clicked: false, method: 'not_found', text: '' };
        }"""

        try:
            result = self.page.evaluate(js_click_next)

            if not result.get("clicked"):
                logger.warning("No clickable Next page link found.")
                return False

            logger.info(f"Next page clicked via {result['method']} (link text: '{result['text']}')")
            self.page.wait_for_timeout(2000)
            self.wait_for_results_table(timeout=20000)
            logger.info("Next page results loaded successfully.")
            return True

        except Exception as e:
            logger.error(f"Failed to navigate to next page: {e}")
            return False

    def get_total_case_count(self) -> int:
        """Extracts the total case count displayed by the portal."""
        info = self.get_pagination_info()
        return info.get("total_records", 0)

    def save_search_results_snapshot(self, page_num: int) -> "Path | None":
        """Saves an HTML snapshot of the current search results page."""
        try:
            from pathlib import Path as PathLib
            snapshot_path = config.SNAPSHOTS_DIR / f"search_results_page_{page_num}.html"
            html_content = self.page.content()
            with open(snapshot_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"Search results snapshot saved: {snapshot_path}")
            return snapshot_path
        except Exception as e:
            logger.error(f"Failed to save search results snapshot for page {page_num}: {e}")
            return None

    # -----------------------------------------------------------------------
    # Session Recovery
    # -----------------------------------------------------------------------

    def is_session_expired(self) -> bool:
        """Detects if the eCourts session has expired."""
        try:
            current_url = self.page.url
            if "casestatus" not in current_url.lower() and "ecourtindia" in current_url.lower():
                logger.warning(f"Session may be expired: URL is '{current_url}'")
                return True
            if self.dialog_text and ("session" in self.dialog_text.lower() or
                                     "expired" in self.dialog_text.lower() or
                                     "timeout" in self.dialog_text.lower()):
                logger.warning(f"Session expiry dialog detected: '{self.dialog_text}'")
                return True
            return False
        except Exception as e:
            logger.error(f"Error checking session status: {e}")
            return True

    def recover_session(self, year: str | None = None) -> bool:
        """Re-authenticates with eCourts after a session expiry.

        Re-navigates, re-fills the form, prompts for CAPTCHA, re-submits.

        Returns:
            True if session was recovered successfully, False otherwise.
        """
        target_year = year or config.YEAR
        logger.info(f"Attempting session recovery for year {target_year}...")

        try:
            self.navigate_to_home()
            self.select_state(config.STATE)
            self.select_district(config.DISTRICT)
            self.select_court_complex(config.COURT_COMPLEX)
            self.select_establishment(config.ESTABLISHMENT)
            self.select_case_type_tab()
            self.fill_case_type(config.CASE_TYPE)
            self.fill_year(target_year)
            self.select_disposed()

            max_retries = config.MAX_CAPTCHA_RETRIES
            for attempt in range(1, max_retries + 1):
                print("\n" + "=" * 60)
                print("SESSION EXPIRED -- Please solve the CAPTCHA to continue.")
                print(f"Press [ENTER] after solving (Attempt {attempt}/{max_retries})...")
                print("=" * 60 + "\n")
                input()

                try:
                    self.click_go()
                    self.verify_results_table()
                    logger.info("Session recovered successfully.")
                    return True
                except CaptchaError as e:
                    logger.warning(f"CAPTCHA failed on recovery attempt {attempt}: {e}")
                    print(f"\n[!] CAPTCHA error: {e}. Please try again.")
                except Exception as e:
                    logger.error(f"Unexpected error during session recovery: {e}")
                    raise

            logger.error(f"Session recovery failed after {max_retries} attempts.")
            return False

        except Exception as e:
            logger.error(f"Session recovery failed: {e}")
            return False

