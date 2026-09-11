"""Checkpoint and resume system for the eCourts scraper.

Saves progress every N cases so interrupted runs can resume
from the last successfully scraped case instead of restarting.
"""
from __future__ import annotations
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger("ecourts_scraper")


def _checkpoint_path(year: str, output_dir: Path) -> Path:
    """Returns the checkpoint file path for a given year."""
    return output_dir / f"checkpoint_{year}.json"


def save_checkpoint(
    cases: list[dict[str, Any]],
    year: str,
    output_dir: Path,
    last_page: int = 0,
    completed_cnrs: set[str] | None = None,
    failed_case_count: int = 0,
    current_case: str = "",
    current_result_index: int = 0,
    search_parameters: dict[str, str] | None = None,
) -> Path:
    """Saves current scraping progress to a checkpoint file.

    Args:
        cases: List of canonical case records scraped so far.
        year: The year being scraped.
        output_dir: Directory to save the checkpoint file in.
        last_page: The last pagination page that was fully processed.
        completed_cnrs: Set of CNR numbers already scraped.
        failed_case_count: Number of cases that failed extraction.
        current_case: Case number currently being processed.
        current_result_index: Index within the current results page.
        search_parameters: The search parameters used for this run.

    Returns:
        Path to the saved checkpoint file.
    """
    checkpoint_file = _checkpoint_path(year, output_dir)

    last_case = cases[-1] if cases else {}
    last_cnr = last_case.get("cnr", "")
    last_case_number = last_case.get("case_number", "")

    checkpoint_data = {
        "year": year,
        "last_completed_case": last_case_number,
        "last_completed_cnr": last_cnr,
        "cases_processed": len(cases),
        "last_page": last_page,
        "completed_cnrs": sorted(completed_cnrs) if completed_cnrs else [],
        "timestamp": datetime.now().isoformat(),
        # Enhanced checkpoint fields (spec §14)
        "failed_case_count": failed_case_count,
        "current_case": current_case,
        "current_result_index": current_result_index,
        "search_parameters": search_parameters or {},
        "completed_case_count": len(cases),
        "cases": cases,
    }

    # Write atomically: write to temp file first, then rename
    temp_file = checkpoint_file.with_suffix(".tmp")
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
        # Replace checkpoint file atomically (on Windows, need to remove first)
        if checkpoint_file.exists():
            checkpoint_file.unlink()
        temp_file.rename(checkpoint_file)
        logger.info(
            f"Checkpoint saved: {len(cases)} cases, last CNR={last_cnr}, "
            f"page={last_page} → {checkpoint_file}"
        )
    except Exception as e:
        logger.error(f"Failed to save checkpoint: {e}")
        # Clean up temp file on failure
        if temp_file.exists():
            try:
                temp_file.unlink()
            except Exception:
                pass
        raise

    # Also save the incremental cases.json at the same time
    json_path = output_dir / "cases.json"
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(cases, f, indent=4, ensure_ascii=False)
        logger.info(f"Incremental cases.json saved: {len(cases)} cases → {json_path}")
    except Exception as e:
        logger.error(f"Failed to save incremental cases.json: {e}")

    return checkpoint_file


def load_checkpoint(
    year: str, output_dir: Path
) -> tuple[list[dict[str, Any]], int, set[str]]:
    """Loads an existing checkpoint for resume.

    Args:
        year: The year to resume.
        output_dir: Directory containing the checkpoint file.

    Returns:
        Tuple of (cases_list, last_page, completed_cnrs_set).
        Returns ([], 0, set()) if no checkpoint exists.
    """
    checkpoint_file = _checkpoint_path(year, output_dir)

    if not checkpoint_file.exists():
        logger.info(f"No checkpoint found at {checkpoint_file}. Starting fresh.")
        return [], 0, set()

    try:
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        cases = data.get("cases", [])
        last_page = data.get("last_page", 0)
        completed_cnrs = set(data.get("completed_cnrs", []))

        # If completed_cnrs is empty but we have cases, rebuild from cases
        if not completed_cnrs and cases:
            completed_cnrs = {c.get("cnr", "") for c in cases if c.get("cnr")}

        logger.info(
            f"Checkpoint loaded: {len(cases)} cases, "
            f"{len(completed_cnrs)} CNRs, last_page={last_page}, "
            f"last_case={data.get('last_completed_case', 'N/A')}"
        )
        return cases, last_page, completed_cnrs

    except json.JSONDecodeError as e:
        logger.error(f"Corrupt checkpoint file {checkpoint_file}: {e}")
        logger.warning("Starting fresh due to corrupt checkpoint.")
        return [], 0, set()
    except Exception as e:
        logger.error(f"Error loading checkpoint: {e}")
        return [], 0, set()


def clear_checkpoint(year: str, output_dir: Path) -> None:
    """Removes the checkpoint file after successful completion.

    Args:
        year: The year whose checkpoint to clear.
        output_dir: Directory containing the checkpoint file.
    """
    checkpoint_file = _checkpoint_path(year, output_dir)
    if checkpoint_file.exists():
        checkpoint_file.unlink()
        logger.info(f"Checkpoint cleared: {checkpoint_file}")
    else:
        logger.info(f"No checkpoint to clear for year {year}.")
