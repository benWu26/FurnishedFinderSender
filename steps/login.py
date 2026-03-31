from playwright.sync_api import Browser, Page
import os


def login(browser: Browser) -> Page:
    email = os.getenv("EMAIL")

    if not email:
        raise ValueError("EMAIL environment variable must be set.")

    context = browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    )
    context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    page = context.new_page()

    # goes directly to favorites page
    page.goto("https://www.furnishedfinder.com/members/favorites")
    page.wait_for_load_state("load")

    # Enter email
    page.locator("#username").click()
    page.locator("#username").fill(email)

    # Submit email — code is automatically sent to the email address
    page.locator("button[type='submit']").filter(has_text="Login").click()
    page.wait_for_load_state("load")

    # Prompt for the code sent to email
    code = input("Enter the login code sent to your email: ").strip()

    # Enter the code then submit
    page.locator("[data-testid='code']").fill(code)
    page.wait_for_load_state("load")

    if "login" in page.url:
        raise RuntimeError("Login failed. Please check the code and try again.")

    print("Login successful!")
    return page
