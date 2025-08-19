#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import sys
from typing import List, Dict, Any

from utilities.extractions import extract_urls_from_file
from utilities.reports import make_reports
from utilities.drivers import build_driver, run_axe_on_page


def ask_for_input_if_needed(args: argparse.Namespace) -> str:
    if args.input:
        return args.input
    try:
        return input("Path to the ZAP file (or .txt with URLs): ").strip()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="WCAG scan with axe starting from a ZAP file")
    parser.add_argument("--input", "-i", type=str, help="Path to the file (ZAP JSON/XML/HTML or TXT with URLs)")
    parser.add_argument("--max-pages", type=int, default=100, help="Maximum number of pages to scan")
    parser.add_argument("--headless/--no-headless", dest="headless", default=True, action=argparse.BooleanOptionalAction,
                        help="Run the browser in headless mode")
    parser.add_argument("--page-wait", type=int, default=5, help="Seconds to wait after the page is loaded")
    parser.add_argument("--implicit-wait", type=int, default=2, help="Selenium implicit wait (seconds)")
    parser.add_argument("--out-prefix", type=str, default="report_accessibility", help="Output file prefix")
    args = parser.parse_args()

    path = ask_for_input_if_needed(args)

    print(f"\n[1/5] Reading file: {path}")
    urls = extract_urls_from_file(path)
    if not urls:
        print("No URL found in the provided file.")
        sys.exit(2)

    # Deduplicate and cut to max-pages
    urls = list(dict.fromkeys(urls))
    if args.max_pages:
        urls = urls[: args.max_pages]

    print(f"[2/5] URLs to scan: {len(urls)}")

    print("[3/5] Starting browser…")
    driver = build_driver(headless=args.headless, implicit_wait=args.implicit_wait)

    results: List[Dict[str, Any]] = []
    try:
        for idx, url in enumerate(urls, start=1):
            print(f"- ({idx}/{len(urls)}) {url}")
            res = run_axe_on_page(driver, url=url, wait_seconds=args.page_wait)
            results.append(res)
    finally:
        driver.quit()

    print("[4/5] Generating report…")
    html_path = make_reports(results, out_prefix=args.out_prefix)

    print("[5/5] Done!\n")
    print(f"HTML report: {html_path}")


if __name__ == "__main__":
    main()
