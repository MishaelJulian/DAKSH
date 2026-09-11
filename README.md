# eCourts Karnataka Case Scraper

An enterprise-grade automation system and parsing pipeline for extracting disposed case records from the Indian eCourts portal for Karnataka.

## Overview
This scraper uses Playwright to drive search interactions, handles human-in-the-loop CAPTCHA entry, parses the AJAX-loaded DOM structures with BeautifulSoup4, and exports case data to structured JSON files, a combined CSV, and Excel document.

## Architecture
- `config.py`: Environment-aware settings, navigation constants, timeouts, and directories.
- `models.py`: Strongly typed dataclass representation of the parsed case schema.
- `browser.py`: Playwright lifecycle management.
- `scraper.py`: Stateful browser navigation flow.
- `parser.py`: Pure function parses HTML snippets using BeautifulSoup4.
- `exporter.py`: Atomically serializes case records and compiles spreadsheet outputs.
- `utils.py`: Setup for rotating logs and exponential backoff retry wrappers.

## Setup
1. Install Python 3.12+.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browser engines:
   ```bash
   playwright install chromium
   ```

## Execution
Run the orchestrator:
```bash
python ecourts_scraper/main.py
```
