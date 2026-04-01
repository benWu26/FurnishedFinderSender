from steps import login, get_favorites, send_inquiry, unsave_listing, DateUnavailableError
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import os

def validate_env():
    if not os.getenv("SLOW_MO"):
        raise ValueError("SLOW_MO environment variable must be set. Please edit your .env file.")   
    
    if not os.getenv("EMAIL"):
        raise ValueError("EMAIL environment variable must be set. Please edit your .env file.")

    if not os.getenv("MESSAGE"):
        raise ValueError("MESSAGE environment variable must be set. Please edit your .env file.")

    if not os.getenv("MOVE_IN_DATE"):
        raise ValueError("MOVE_IN_DATE environment variable must be set. Please edit your .env file.")

    if not os.getenv("MOVE_OUT_DATE"):
        raise ValueError("MOVE_OUT_DATE environment variable must be set. Please edit your .env file.")

    valid_contact_methods = {"Email", "Any", "Text", "Phone"}
    contact_method = os.getenv("CONTACT_METHOD", "")
    if contact_method not in valid_contact_methods:
        raise ValueError(f"CONTACT_METHOD must be one of: {', '.join(sorted(valid_contact_methods))}. Got: '{contact_method}'")

    valid_travel_reasons = {"Other", "Digital Nomad", "Insurance Housing", "Traveling Healthcare", "Long Term Housing", "Business/Work", "Military", "Student", "Relocation/Transition"}
    travel_reason = os.getenv("TRAVEL_REASON", "")
    if travel_reason not in valid_travel_reasons:
        raise ValueError(f"TRAVEL_REASON must be one of: {', '.join(sorted(valid_travel_reasons))}. Got: '{travel_reason}'")


def main():
    load_dotenv()
    validate_env()


    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=int(os.getenv("SLOW_MO", 0)),
            args=["--disable-blink-features=AutomationControlled"],
        )
        try:
            page = login(browser)
            
            favorites = get_favorites(page)

            succeeded = []
            skipped = []
            failed = []

            for i, url in enumerate(favorites, 1):
                print(f"[{i}/{len(favorites)}] Sending inquiry to: {url}")
                try:
                    send_inquiry(page, url)
                    unsave_listing(page, url)
                    succeeded.append(url)
                except DateUnavailableError as e:
                    print(f"  Skipped: {e}")
                    skipped.append((url, str(e)))
                except Exception as e:
                    print(f"  Failed: {e}")
                    failed.append((url, str(e)))
        finally:
            browser.close()

        # Summary
        print(f"\n{'='*50}")
        print(f"Results: {len(succeeded)} succeeded, {len(skipped)} skipped, {len(failed)} failed out of {len(favorites)} total")
        if succeeded:
            print(f"\nSucceeded:")
            for url in succeeded:
                print(f"  {url}")
        if skipped:
            print(f"\nSkipped (dates unavailable):")
            for url, reason in skipped:
                print(f"  {url}")
                print(f"    Reason: {reason}")
        if failed:
            print(f"\nFailed:")
            for url, error in failed:
                print(f"  {url}")
                print(f"    Error: {error}")
        print(f"{'='*50}")


if __name__ == "__main__":
    main()
