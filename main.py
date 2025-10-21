import requests
import os
import json
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def run_automation():
    """
    Automates login to SauceDemo and retrieves the price of the Sauce Labs Backpack product.

    Uses Playwright to interact with the SauceDemo website, logging in with provided credentials
    and extracting the price of the specified product for the Web Automation Project.

    Environment Variables:
        SAUCE_USER (str): Username for login (default: "standard_user").
        SAUCE_PASS (str): Password for login (default: "secret_sauce").
        HEADLESS (str): Run browser in headless mode if "true" (default: "true").

    Returns:
        dict: A dictionary containing:
            - status (str): "success" or "error".
            - product (str, optional): Name of the product if successful.
            - price (str, optional): Price of the product if successful.
            - message (str, optional): Error message if failed.
    """
    username = os.getenv("SAUCE_USER", "standard_user")
    password = os.getenv("SAUCE_PASS", "secret_sauce")
    headless = os.getenv("HEADLESS", "true").lower() == "true"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        try:
            # Go to site
            page.goto("https://www.saucedemo.com/", timeout=10000)

            # Log in
            page.fill("#user-name", username)
            page.fill("#password", password)
            page.click('[id="login-button"]')

            # Check for login error
            if page.locator('[data-test="error"]').is_visible():
                raise Exception("Login failed: Invalid credentials")

            # Wait for inventory page
            page.wait_for_selector(".inventory_list", timeout=10000)

            # Find the product and its price
            item = page.locator(".inventory_item", has_text="Sauce Labs Backpack")
            if item.count() == 0:
                raise Exception("Product not found")

            price = item.locator(".inventory_item_price").inner_text()

            return {
                "status": "success",
                "product": "Sauce Labs Backpack",
                "price": price
            }

        except PlaywrightTimeoutError:
            return {"status": "error", "message": "Page took too long to load"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

        finally:
            browser.close()

if __name__ == "__main__":
    result = run_automation()
    print(json.dumps(result))