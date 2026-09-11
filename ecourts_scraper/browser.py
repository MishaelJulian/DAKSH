"""Browser lifecycle management and page automation interactions for eCourts Karnataka.

Provides get_browser_page for context management and ECourtsBrowser for cascading
drop-down inputs, CAPTCHA wait, and results validation.
"""
from __future__ import annotations
import logging
import re
from contextlib import contextmanager
from typing import Generator
from playwright.sync_api import sync_playwright, Page, Dialog
from ecourts_scraper import config
from ecourts_scraper.models import (
    CaseSummary,
    CaseDetail,
    RawCaseDetail,
    ActEntry,
    ProcessEntry,
    HearingRecord,
    DailyStatusRecord,
    OrderEntry,
    TransferEntry,
)
from ecourts_scraper.parser import (
    parse_case_detail_text,
    parse_case_details_page,
    parse_daily_status_html,
    check_portal_session_error,
    parse_search_results_rows
)

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
                    self.page.wait_for_timeout(2000)
                    return
            except Exception as e:
                logger.warning(f"Establishment selection attempt {attempt} failed: {e}")
            self.page.wait_for_timeout(2000)
            
        raise DropdownSelectionError(f"Failed to find or select Establishment '{establishment}' in available options.")

    def select_case_type_tab(self) -> None:
        """Clicks the 'Case Type' search tab link and ensures tab activation."""
        logger.info("Choosing Search Type: Case Type...")
        self.dismiss_validation_modal()
        self.page.wait_for_selector("#casetype-tabMenu")
        
        # 1. Try standard click on tab selector
        tab_selectors = [
            "#casetype-tabMenu a",
            "#casetype-tabMenu",
            "button#casetype-tabMenu",
            "a[href='#casetype']",
            "button[data-bs-target='#casetype']"
        ]
        clicked = False
        for sel in tab_selectors:
            try:
                if self.page.locator(sel).count() > 0:
                    self.page.locator(sel).first.click(no_wait_after=True, force=True, timeout=3000)
                    clicked = True
                    break
            except Exception:
                pass

        if not clicked:
            try:
                self.page.click("#casetype-tabMenu", no_wait_after=True, force=True)
            except Exception as e:
                logger.warning(f"Direct click on #casetype-tabMenu failed: {e}")

        # 2. Programmatic tab show fallback (Bootstrap / jQuery / JS click)
        self.page.evaluate("""() => {
            const el = document.querySelector('#casetype-tabMenu a, #casetype-tabMenu, button#casetype-tabMenu, a[href="#casetype"], button[data-bs-target="#casetype"]');
            if (el) {
                if (window.bootstrap && bootstrap.Tab) {
                    try {
                        const tab = bootstrap.Tab.getOrCreateInstance(el);
                        tab.show();
                    } catch(e) {}
                }
                if (window.jQuery && typeof jQuery(el).tab === 'function') {
                    try {
                        jQuery(el).tab('show');
                    } catch(e) {}
                }
                const link = (el.tagName === 'LI') ? (el.querySelector('a') || el) : el;
                link.click();
            }
        }""")
        
        # Let tab menu animation/DOM transition complete
        self.page.wait_for_timeout(2000)
        self.dismiss_validation_modal()

    def log_case_type_diagnostics(self) -> None:
        """Logs comprehensive diagnostics before fill_case_type."""
        try:
            url = self.page.url
            active_tabs = self.page.evaluate("""() => {
                const els = Array.from(document.querySelectorAll('.nav-link.active, .nav-tabs li.active, .nav-item.active, [aria-selected="true"]'));
                return els.map(e => ({
                    tag: e.tagName,
                    id: e.id,
                    className: e.className,
                    text: (e.innerText || e.textContent || '').trim()
                }));
            }""")
            casetype_tabmenu_count = self.page.locator("#casetype-tabMenu").count()
            case_type_2_count = self.page.locator("#case_type_2").count()
            case_type_2_visible = False
            if case_type_2_count > 0:
                try:
                    case_type_2_visible = self.page.locator("#case_type_2").first.is_visible()
                except Exception:
                    pass

            casetype_tabmenu_html = self.page.evaluate("""() => {
                const el = document.querySelector('#casetype-tabMenu');
                return el ? el.outerHTML : 'NOT_FOUND';
            }""")

            casetype_container_html = self.page.evaluate("""() => {
                const el = document.querySelector('#casetype, #casestatus-casetype, #caseType, #frm_casetype, #case_type_2');
                if (!el) return 'NOT_FOUND';
                const container = el.closest('.tab-pane, form, div') || el;
                return container.outerHTML.substring(0, 500);
            }""")

            visible_selects = self.page.evaluate("""() => {
                const selects = Array.from(document.querySelectorAll('select'));
                return selects.map(s => ({
                    id: s.id,
                    name: s.name,
                    visible: (s.offsetParent !== null && window.getComputedStyle(s).display !== 'none' && window.getComputedStyle(s).visibility !== 'hidden'),
                    optionsCount: s.options ? s.options.length : 0,
                    optionsSample: s.options ? Array.from(s.options).slice(0, 5).map(o => o.text.trim()) : []
                })).filter(s => s.visible);
            }""")

            logger.info("=== CASE TYPE DIAGNOSTICS ===")
            logger.info(f"Current URL: {url}")
            logger.info(f"Active Tab(s): {active_tabs}")
            logger.info(f"Count of #casetype-tabMenu: {casetype_tabmenu_count}")
            logger.info(f"Count of #case_type_2: {case_type_2_count}")
            logger.info(f"Visibility of #case_type_2: {case_type_2_visible}")
            logger.info(f"OuterHTML of #casetype-tabMenu: {casetype_tabmenu_html}")
            logger.info(f"OuterHTML of Case Type container: {casetype_container_html}")
            logger.info(f"Visible select elements: {visible_selects}")

            # Save screenshot
            diag_screenshot_dir = config.DATA_DIR / "screenshots"
            diag_screenshot_dir.mkdir(parents=True, exist_ok=True)
            diag_screenshot_path = diag_screenshot_dir / "case_type_diagnostics.png"
            self.page.screenshot(path=str(diag_screenshot_path))
            logger.info(f"Diagnostics screenshot saved to: {diag_screenshot_path}")
            logger.info("=============================")
        except Exception as e:
            logger.warning(f"Error while capturing Case Type diagnostics: {e}")

    def fill_case_type(self, case_type_label: str, retries: int = 5) -> None:
        """Finds the visible Case Type select element and selects the matching option."""
        self.log_case_type_diagnostics()

        dropdown_selectors = ["#case_type_2", "#case_type_1", "#case_type"]

        for attempt in range(1, retries + 1):
            logger.info(f"Selecting Case Type: {case_type_label} (Attempt {attempt}/{retries})...")
            try:
                # Detect which dropdown is visible (case_type, case_type_1, or case_type_2)
                visible_sel = None
                for sel in dropdown_selectors:
                    el = self.page.query_selector(sel)
                    if el and el.is_visible():
                        visible_sel = sel
                        break
                        
                if not visible_sel:
                    logger.info(f"No visible Case Type dropdown detected on attempt {attempt}. Re-triggering tab activation...")
                    self.select_case_type_tab()
                    self.page.wait_for_timeout(1000)
                    for sel in dropdown_selectors:
                        el = self.page.query_selector(sel)
                        if el and el.is_visible():
                            visible_sel = sel
                            break

                if not visible_sel:
                    # Also try waiting up to 5s for #case_type_2 to become visible
                    try:
                        self.page.locator("#case_type_2").wait_for(state="visible", timeout=5000)
                        visible_sel = "#case_type_2"
                    except Exception:
                        pass

                if not visible_sel:
                    raise DropdownSelectionError("No visible Case Type select dropdown found under Case Type tab.")
                    
                options = self._wait_and_get_dropdown_options(visible_sel, target_text=case_type_label, timeout=15000)
                
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
                else:
                    logger.warning(f"Case Type '{case_type_label}' not found in {len(opt_pairs)} options of {visible_sel}: {[p['text'] for p in opt_pairs[:10]]}")
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
            # Clear previous detail view to prevent stale data / cross-case contamination
            self.page.evaluate("() => { const el = document.getElementById('CScaseType'); if (el) el.innerHTML = ''; }")
            
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

    def get_minimal_case_details(
        self,
        expected_case_number: str = "EX/2/2023",
        expected_cnr: str = "KABC010342242022"
    ) -> RawCaseDetail:
        """Extracts case details and populates RawCaseDetail model using the scoped parser.
        
        Performs identity validation against expected_case_number and expected_cnr.
        Raises ValueError("CROSS_CASE_IDENTITY_MISMATCH") if mismatched.
        """
        container_selector = "#CScaseType"
        self.page.locator(f"{container_selector} table.case_details_table").wait_for(state="visible", timeout=20000)

        # Check for session error
        content = self.page.content()
        session_err = check_portal_session_error(content)
        if session_err:
            raise ECourtsPortalError(session_err)

        # Parse with zero-hallucination BeautifulSoup parser
        details = parse_case_details_page(content, expected_case_number=expected_case_number)
        logger.info(f"Extracted Case Details for: {details.case_number}, CNR: {details.cnr_number}")

        # FIRST-CASE IDENTITY CHECK (Requirement §7)
        if expected_case_number:
            actual_norm = details.case_number.replace("/", "").replace(" ", "").lower()
            expected_norm = expected_case_number.replace("/", "").replace(" ", "").lower()
            if actual_norm != expected_norm:
                logger.critical(f"CROSS_CASE_IDENTITY_MISMATCH: Expected case '{expected_case_number}', but loaded page showed '{details.case_number}'")
                raise ValueError(f"CROSS_CASE_IDENTITY_MISMATCH: Expected '{expected_case_number}', got '{details.case_number}'")

        if expected_cnr and details.cnr_number:
            if details.cnr_number.strip().upper() != expected_cnr.strip().upper():
                logger.critical(f"CROSS_CASE_IDENTITY_MISMATCH: Expected CNR '{expected_cnr}', but loaded page showed '{details.cnr_number}'")
                raise ValueError(f"CROSS_CASE_IDENTITY_MISMATCH: Expected CNR '{expected_cnr}', got '{details.cnr_number}'")

        # Save HTML snapshot
        try:
            snapshot_dir = config.DATA_DIR / "snapshots"
            snapshot_dir.mkdir(parents=True, exist_ok=True)
            safe_num = (details.case_number or "unknown").replace("/", "_").replace("\\", "_")
            snapshot_path = snapshot_dir / f"case_{safe_num}.html"
            snapshot_path.write_text(content, encoding="utf-8")
            logger.info(f"Saved case HTML snapshot to {snapshot_path}")
        except Exception as snap_err:
            logger.warning(f"Could not save HTML snapshot: {snap_err}")

        return details

    def extract_daily_statuses_and_orders(
        self,
        details: RawCaseDetail,
        output_dir: Path | None = None
    ) -> None:
        """Extracts each Daily Status entry from Case History and resolves Final Orders.
        
        Zero cross-case contamination: every daily status block is validated for CNR and Case Number.
        Uses built-in back_fun('CScaseType') to return cleanly without page reload.
        """
        import time
        from pathlib import Path
        
        logger.info(f"Extracting Daily Statuses and Orders for case {details.case_number}...")
        daily_status_dir = (output_dir / "daily_status") if output_dir else (config.DATA_DIR / "daily_status")
        daily_status_dir.mkdir(parents=True, exist_ok=True)
        orders_dir = (output_dir / "orders") if output_dir else config.ORDERS_DIR
        orders_dir.mkdir(parents=True, exist_ok=True)
        screenshots_dir = (output_dir / "screenshots") if output_dir else (config.DATA_DIR / "screenshots")
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        # 1. Iterate through Case History Business Date links
        for r_idx, record in enumerate(details.history):
            if not record.business_date_link:
                continue

            clean_date = record.business_date.replace("/", "-")
            logger.info(f"[{r_idx+1}/{len(details.history)}] Opening Daily Status for {record.business_date}...")

            # Clear previous daily status container
            try:
                self.page.evaluate("() => { const el = document.getElementById('caseBusinessDiv_caseType'); if (el) el.innerHTML = ''; }")
            except Exception:
                pass

            # Execute viewBusiness onclick
            try:
                self.page.evaluate(f"() => {{ {record.business_date_link} }}")
            except Exception as click_err:
                logger.error(f"Failed clicking business link for {record.business_date}: {click_err}")
                continue

            # Wait for Daily Status container to be visible and populated
            try:
                self.page.locator("#caseBusinessDiv_caseType:visible").wait_for(state="visible", timeout=15000)
                self.page.locator("#caseBusinessDiv_caseType table").wait_for(state="visible", timeout=10000)
            except Exception as wait_err:
                logger.error(f"Daily Status container failed to become visible for {record.business_date}: {wait_err}")
                try:
                    self.page.evaluate("back_fun('CScaseType')")
                except Exception:
                    pass
                continue

            # Check session timeout
            cur_html = self.page.content()
            session_err = check_portal_session_error(cur_html)
            if session_err:
                raise ECourtsPortalError(session_err)

            # Save snapshot
            snap_file = daily_status_dir / f"daily_status_{clean_date}.html"
            try:
                snap_file.write_text(cur_html, encoding="utf-8")
            except Exception:
                pass

            # Capture screenshot for first and last entries
            if r_idx == 0 or r_idx == len(details.history) - 1:
                try:
                    self.page.screenshot(path=str(screenshots_dir / f"daily_status_{clean_date}.png"))
                except Exception:
                    pass

            # Extract Daily Status Record
            daily_rec = parse_daily_status_html(cur_html)
            
            # IDENTITY VALIDATION (Requirement §16)
            cnr_match = bool(daily_rec.cnr and details.cnr_number and daily_rec.cnr.strip().upper() == details.cnr_number.strip().upper())
            
            case_num_clean = re.sub(r'[^a-zA-Z0-9]', '', daily_rec.case_number or '').lower()
            details_case_num_clean = re.sub(r'[^a-zA-Z0-9]', '', details.case_number or '').lower()
            case_num_clean_stripped = re.sub(r'0+', '', case_num_clean)
            details_case_num_stripped = re.sub(r'0+', '', details_case_num_clean)
            num_match = bool(case_num_clean_stripped and details_case_num_stripped and case_num_clean_stripped == details_case_num_stripped)

            if not cnr_match and not num_match:
                logger.critical(f"CROSS_CASE_CONTAMINATION: Daily status block for {record.business_date} showed CNR '{daily_rec.cnr}' / Case '{daily_rec.case_number}', expected '{details.cnr_number}' / '{details.case_number}'. REJECTING RECORD.")
                daily_rec.validation_status = "REJECTED_IDENTITY_MISMATCH"
            else:
                daily_rec.validation_status = "VALIDATED"
                details.daily_status.append(daily_rec)
                logger.info(f"Attached validated Daily Status for {record.business_date}: Purpose='{daily_rec.next_purpose}', Disposal='{daily_rec.nature_of_disposal}'")

            # Clean return back to Case Details page via back_fun('CScaseType')
            try:
                back_btn = self.page.locator("#caseBusinessDiv_back")
                if back_btn.count() > 0 and back_btn.is_visible():
                    back_btn.click()
                else:
                    self.page.evaluate("back_fun('CScaseType')")
                self.page.locator("#caseBusinessDiv_caseType").wait_for(state="hidden", timeout=10000)
                self.page.locator("#CScaseType").wait_for(state="visible", timeout=10000)
            except Exception as back_err:
                logger.warning(f"Error returning from daily status: {back_err}. Retrying back_fun...")
                try:
                    self.page.evaluate("back_fun('CScaseType')")
                    self.page.wait_for_timeout(500)
                except Exception:
                    pass

        # 2. Final Orders Resolution (Requirement §21 & §22)
        for ord_idx, o in enumerate(details.orders):
            onclick = o.metadata.get("onclick", "") if o.metadata else ""
            if "displayPdf" in onclick:
                o.order_details_present = True
                try:
                    js_resolve_pdf = """(onclickStr) => {
                        const m = onclickStr.match(/displayPdf\\s*\\(([^)]+)\\)/);
                        if (!m || typeof ajaxCall === 'undefined') return null;
                        const params = m[1].split(',').map(s => s.trim().replace(/^['"]|['"]$/g, ''));
                        return new Promise((resolve) => {
                            const [normal_v, case_val, court_code, filename, appFlag] = params;
                            const postdata = '&normal_v=' + normal_v + '&case_val=' + case_val + '&court_code=' + court_code + '&filename=' + filename + '&appFlag=' + (appFlag || '');
                            ajaxCall({
                                url: 'home/display_pdf',
                                postdata: postdata,
                                callback: (res) => {
                                    if (res && res.status && res.order) {
                                        resolve('https://services.ecourts.gov.in/ecourtindia_v6/' + res.order);
                                    } else {
                                        resolve(null);
                                    }
                                }
                            });
                            setTimeout(() => resolve(null), 5000);
                        });
                    }"""
                    pdf_url = self.page.evaluate(js_resolve_pdf, onclick)
                    if pdf_url:
                        o.order_pdf_available = True
                        o.order_pdf_url = pdf_url
                        o.order_link = pdf_url
                        safe_case = details.case_number.replace("/", "_")
                        pdf_path = orders_dir / f"order_{safe_case}_{o.order_number}.pdf"
                        res = self.page.request.get(pdf_url)
                        if res.status == 200:
                            pdf_path.write_bytes(res.body())
                            o.local_path = str(pdf_path)
                            try:
                                import pypdf
                                reader = pypdf.PdfReader(str(pdf_path))
                                txts = [pg.extract_text() or "" for pg in reader.pages]
                                o.order_text = "\n".join(txts).strip() or None
                            except Exception:
                                pass
                except Exception as ord_err:
                    logger.warning(f"Could not resolve order PDF for order {o.order_number}: {ord_err}")

        logger.info(f"Finished extracting Daily Statuses ({len(details.daily_status)} records) and Orders ({len(details.orders)} rows).")

    follow_orders_and_business = extract_daily_statuses_and_orders

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

