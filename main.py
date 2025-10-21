import os
import json
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


"""
Runs the SauceDemo login and product price check.
Returns a structured result dictionary.
"""
def run_automation():
    
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
