# WCAG Accessibility Scanner (ZAP + Selenium + axe-core)

This script allows you to automatically scan the accessibility (WCAG) of web pages discovered by **OWASP ZAP**, 
using **Selenium** and **axe-core**.

## Features
- Accepts an exported file from ZAP (`.json`, `.xml`, `.html`, `.txt`) containing URLs.
- Extracts and deduplicates the list of web pages.
- Runs **axe-core** accessibility tests on each page via Selenium (headless Chrome by default).
- Computes an accessibility score from **0 to 100** for each page and an overall average score.
- Generates detailed reports on a new **HTML page**, including:
  - The score per page
  - Violations grouped by impact (minor, moderate, serious, critical)
  - Top accessibility issues with links to documentation

## Requirements
- Python 3.8+
- Google Chrome installed

### Install dependencies
```bash
pip install selenium webdriver-manager axe-selenium-python beautifulsoup4 lxml
```

## Usage

### Basic
```bash
python zap_wcag_accessibility.py
```
You will be prompted to provide the path to the ZAP output file.

### With options
```bash
python zap_wcag_accessibility.py --input zap_report.json --max-pages 50
```

#### Common arguments
- `--input, -i` → Path to ZAP report or `.txt` file with URLs  
- `--max-pages` → Maximum number of pages to scan (default: 100)  
- `--headless/--no-headless` → Run browser in headless mode (default: headless)  
- `--page-wait` → Seconds to wait after page load (default: 5)  
- `--implicit-wait` → Selenium implicit wait in seconds (default: 2)  
- `--out-prefix` → Prefix for generated report files (default: `report_accessibilita`)  

## Output
A website will be opened and the html file will be saved:
- `accessibility_report_YYYYMMDD_HHMMSS.html` → structured HTML page with scores and violations

---

🚀 Useful for quick accessibility checks on large sets of pages discovered by ZAP.
