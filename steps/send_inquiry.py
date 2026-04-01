from playwright.sync_api import Page
from datetime import datetime
import os
import re

# helper
def _get_bedroom_count(page: Page) -> str:
    for el in page.locator(".font-semibold.text-black").all():
        text = el.inner_text().strip()
        match = re.search(r"(\d+)\s*(?:bedroom|bed|br)\b", text, re.IGNORECASE)
        if match:
            return match.group(1)
    return "1"

# helper
def _pick_date_in_open_calendar(page: Page, date_str: str) -> None:
    """Navigate the open calendar to the right month and click the day. date_str: MM/DD/YYYY"""
    dt = datetime.strptime(date_str, "%m/%d/%Y")
    target_day_attr = dt.strftime("%Y-%m-%d")
    target_month_label = dt.strftime("%B %Y")  # e.g. "May 2026"

    calendar = page.locator("[role='dialog'][aria-label='Select date range']")

    for _ in range(24):
        captions = calendar.locator("[data-animated-caption] span[role='status']").all_inner_texts()
        if target_month_label in captions:
            break
        calendar.locator("button[aria-label='Go to next month']").click()
        page.wait_for_timeout(300)

    disabled_cell = calendar.locator(f"td[data-day='{target_day_attr}'][data-disabled='true']")
    if disabled_cell.count() > 0:
        print(f"  [warning] Date {date_str} is disabled in the calendar, skipping click.")
        return

    calendar.locator(f"td[data-day='{target_day_attr}']:not([data-hidden='true']):not([data-disabled='true']) button").click()


# helper
def _pick_date_with_retry(page: Page, trigger_testid: str, date_str: str) -> None:
    """Click the date trigger, pick the date, verify it stuck, retry up to 5 times."""
    dt = datetime.strptime(date_str, "%m/%d/%Y")
    expected_text = f"{dt.strftime('%b')} {dt.day}, {dt.year}"  # e.g. "Aug 16, 2026"
    trigger = page.locator(f"[data-testid='{trigger_testid}']")

    is_to_date = "to" in trigger_testid

    for attempt in range(1, 6):
        print(f"  [{trigger_testid}] Attempt {attempt}: clicking trigger for {date_str}")
        trigger.click()

        calendar = page.locator("[role='dialog'][aria-label='Select date range']")
        calendar.wait_for(state="visible", timeout=5000)
        print(f"  [{trigger_testid}] Calendar opened")

        _pick_date_in_open_calendar(page, date_str)
        print(f"  [{trigger_testid}] Date clicked in calendar")

        if is_to_date:
            # After selecting the end date, wait for the calendar to auto-close
            print(f"  [{trigger_testid}] Waiting for calendar to auto-close...")
            try:
                calendar.wait_for(state="hidden", timeout=3000)
                print(f"  [{trigger_testid}] Calendar auto-closed")
            except Exception:
                # If it didn't auto-close, press Tab to move focus away
                print(f"  [{trigger_testid}] Calendar did not auto-close, pressing Tab")
                page.keyboard.press("Tab")
                page.wait_for_timeout(500)
        else:
            page.keyboard.press("Escape")
            print(f"  [{trigger_testid}] Pressed Escape to close calendar")

        page.wait_for_timeout(300)
        actual_text = trigger.locator("span").first.inner_text().strip()
        print(f"  [{trigger_testid}] Trigger text: '{actual_text}' (expected: '{expected_text}')")
        if actual_text == expected_text:
            print(f"  [{trigger_testid}] Date set successfully")
            break
        print(f"  [{trigger_testid}] [retry {attempt}/5] Date mismatch")
    else:
        raise RuntimeError(f"Failed to set date '{date_str}' after 5 attempts.")


# helper
def _select_combobox(page: Page, aria_label: str, value: str) -> None:
    """Click a Radix UI combobox and select an option by text."""
    btn = page.locator(f"button[aria-label='{aria_label}']")
    btn.scroll_into_view_if_needed()
    btn.wait_for(state="visible", timeout=10000)
    btn.click()
    page.get_by_role("option", name=value).click()


def send_inquiry(page: Page, listing_url: str) -> None:
    move_in = os.getenv("MOVE_IN_DATE", "05/01/2026")
    move_out = os.getenv("MOVE_OUT_DATE", "")
    num_people_env = os.getenv("NUM_PEOPLE", "").strip()
    contact_method = os.getenv("CONTACT_METHOD", "Email")
    travel_reason = os.getenv("TRAVEL_REASON", "Other")
    has_pets = os.getenv("HAS_PETS", "No")
    message = os.getenv("MESSAGE", "")

    if not message:
        raise ValueError("MESSAGE environment variable must be set.")

    page.goto(listing_url)
    page.wait_for_load_state("load")

    # Default num_people to bedroom count if not explicitly set
    if num_people_env:
        num_people = num_people_env
    else:
        num_people = _get_bedroom_count(page)
        print(f"  Defaulting num people to {num_people} (bedrooms)")

    # Map to valid dropdown options: 1, 2, 3, 4, 5+
    try:
        num_people = "5+" if int(num_people) >= 5 else str(int(num_people))
    except ValueError:
        num_people = "1"

    # Open the inquiry form
    print(f"  Opening inquiry form...")
    page.locator("[data-testid='send-booking-request']").click()
    page.wait_for_load_state("load")
    print(f"  Inquiry form loaded")

    # Select move-in and move-out dates with retry verification
    print(f"  Setting move-in: {move_in}, move-out: {move_out}")
    _pick_date_with_retry(page, "ff-day-picker-trigger-from", move_in)
    _pick_date_with_retry(page, "ff-day-picker-trigger-to", move_out)

    # Occupants (Radix combobox)
    print(f"  Setting occupants: {num_people}")
    _select_combobox(page, "occupants", num_people)

    # Best way to contact (Radix combobox)
    print(f"  Setting contact method: {contact_method}")
    _select_combobox(page, "best-way-to-contact-you", contact_method)

    # Reason for travel (Radix combobox)
    print(f"  Setting travel reason: {travel_reason}")
    _select_combobox(page, "reason-for-travel", travel_reason)

    # Traveling with pets (radio)
    print(f"  Setting pets: {has_pets}")
    if has_pets.strip().lower() == "yes":
        page.locator("input[type='radio'][name='travelingWithPets'][value='on']").check()
    else:
        page.locator("input[type='radio'][name='travelingWithPets'][value='off']").check()

    # Message to landlord
    print(f"  Filling message ({len(message)} chars)")
    page.locator("#aboutYou").fill(message)

    # Submit
    print(f"  Submitting inquiry...")
    page.locator("button[type='submit']").filter(has_text="Submit").click()

    # Wait for "Inquiry sent!" dialog then dismiss it
    page.locator("text=Inquiry sent!").wait_for(state="visible", timeout=10000)
    print(f"  Success confirmation received: Inquiry sent!")
    page.keyboard.press("Escape")

    print(f"  Inquiry sent for: {listing_url}")
