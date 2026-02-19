from playwright.sync_api import sync_playwright
import sys

html_path = sys.argv[1]
out_path = sys.argv[2]

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1200, "height": 1050})
    page.goto(f"file://{html_path}")
    page.locator(".card").screenshot(path=out_path)
    browser.close()
    print(f"Saved: {out_path}")
