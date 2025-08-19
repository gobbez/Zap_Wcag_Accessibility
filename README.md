# Zap WCAG Accessibility
## WCAG Accessibility Scanner (ZAP + Selenium + axe-core)

This script allows you to automatically scan the accessibility (WCAG) of web pages discovered by **OWASP ZAP**, using **Selenium** and **axe-core**.

## Features
- Accepts an exported file from ZAP (`.json`, `.xml`, `.html`, `.txt`) containing URLs.
- Extracts and deduplicates the list of web pages.
- Runs **axe-core** accessibility tests on each page via Selenium (headless Chrome by default).
- Computes an accessibility score from **0 to 100** for each page and an overall average score.
- Generates detailed reports in **JSON** and **Markdown**, including:
  - The score per page
  - Violations grouped by impact (minor, moderate, serious, critical)
  - Top accessibility issues with links to documentation

## Requirements
- Python 3.8+
- Google Chrome installed

### Install dependencies
```bash
pip install selenium webdriver-manager axe-selenium-python beautifulsoup4 lxml
