from playwright.sync_api import Page


def unsave_listing(page: Page, listing_url: str) -> None:
    """Unfavorite a listing if the heart is currently filled (saved)."""
    # Navigate to the listing if we're not already there
    if page.url != listing_url:
        page.goto(listing_url)
        page.wait_for_load_state("load")

    save_btn = page.locator("button").filter(has_text="Save").first
    save_btn.scroll_into_view_if_needed()
    save_btn.wait_for(state="visible", timeout=5000)

    # Check if the heart SVG has a fill (saved) — filled path means it's currently saved
    filled_heart = save_btn.locator("path[class*='fill-accent-color']")
    if filled_heart.count() > 0:
        print(f"  Listing is saved, clicking to unsave...")
        save_btn.click()
        page.wait_for_timeout(500)
        print(f"  Unsaved: {listing_url}")
    else:
        print(f"  Listing is already unsaved, skipping")
