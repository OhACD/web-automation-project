from playwright.sync_api import sync_playwright, TimeoutError

def run_automation():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False) # Set to True for production
            page = browser.new_page()
            
            # Go to site
            page.goto("https://www.saucedemo.com/", timeout=10000)
            
            # Log in
            page.fill("#user-name", "standard_user")
            page.fill("#password", "secret_sauce")
            page.click('[id="login-button"]')
            
            # Validate if login was correct
            if page.locator('[data-test="error"]').count() > 0:
                raise Exception("Login failed: Invalid credentials")
            
            # Wait for inventory page
            page.wait_for_selector(".inventory_list", timeout=10000)
            
            # Find the product and its price
            item = page.locator(".inventory_item", has_text="Sauce Labs Backpack")
            if item.count() == 0:
                raise Exception("Product not found!")
            price = item.locator(".inventory_item_price").inner_text()
            
            # Output
            print(f"Success! Product Sauce Labs Backpack price: {price}")
            browser.close()
            
    except TimeoutError:
        print("Failed: Page took too long to load")
    except Exception as e:
        print(f"Failed: {str(e)}")
        
if __name__ == "__main__":
    run_automation()