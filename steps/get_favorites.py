from playwright.sync_api import Page


def get_favorites(page: Page) -> list[str]:
    urls = []
    seen = set()
    current_page = 1

    # wait for pages to load after login before scraping
    page.wait_for_selector("[data-testid^='property-card-']", timeout=15000)

    while True:
        links = page.locator("a[href*='/property/']").all()
        page_urls = []
        for link in links:
            href = link.get_attribute("href")
            if href and href not in seen:
                seen.add(href)
                full_url = href if href.startswith("http") else "https://www.furnishedfinder.com" + href
                page_urls.append(full_url)

        if not page_urls:
            break

        urls.extend(page_urls)
        print(f"Page {current_page}: found {len(page_urls)} listings (total: {len(urls)})")

        next_btn = page.locator("[data-testid='pagination-next']").first
        if next_btn.count() == 0 or next_btn.is_disabled():
            break

        next_btn.click()
        page.wait_for_selector("[data-testid^='property-card-']", timeout=15000)
        current_page += 1

    print(f"Found {len(urls)} favorite listings across {current_page} page(s).")
    return urls
