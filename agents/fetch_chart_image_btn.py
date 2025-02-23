import os
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def capture_snapshot(scid, exchange_id, ex='NSE', screenshot_path='img/snapshot.png'):
    # Setup Chrome options
    chrome_options = Options()
    # For debugging, you can disable headless mode
    chrome_options.add_argument("--headless")  # Remove for visual debugging
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-features=DirectComposition")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 30)
    
    try:
        # Construct the URL and open it
        url = f"https://www.moneycontrol.com/mc/stock/chart?scId={scid}&exchangeId={exchange_id}&ex={ex}"
        driver.get(url)
        
        # Switch to the iframe (assuming chart is inside an iframe with dynamic ID)
        iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[id^='tradingview_']")))
        driver.switch_to.frame(iframe)
        
        # Wait for the chart container to load inside the iframe
        chart_container = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".chart-gui-wrapper")))
        
        # OPTIONAL: If you want to see the full page before snapshotting, capture a debug screenshot
        debug_full_path = os.path.join(os.getcwd(), "img", "debug_full_page.png")
        os.makedirs(os.path.dirname(debug_full_path), exist_ok=True)
        with open(debug_full_path, "wb") as f:
            f.write(driver.get_screenshot_as_png())
        print(f"Debug full page screenshot saved to {debug_full_path}")
        
        # Locate the "Take a Snapshot" button.
        # You may need to adjust the XPath/CSS selector based on the actual button text or attributes.
        snapshot_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'snapshot')]")))
        snapshot_button.click()
        
        # After clicking, wait for the snapshot to be processed.
        # It might update the same chart container, or a new element might appear.
        # Adjust the selector and wait condition based on what changes on the page.
        snapshot_container = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".chart-gui-wrapper")))
        
        # Capture screenshot of the snapshot container
        snapshot_png = snapshot_container.screenshot_as_png
        
        # Ensure the directory exists
        snapshot_full_path = os.path.join(os.getcwd(), "img", "snapshot.png")
        os.makedirs(os.path.dirname(snapshot_full_path), exist_ok=True)
        with open(snapshot_full_path, "wb") as f:
            f.write(snapshot_png)
        print(f"Snapshot saved to {snapshot_full_path}")
        
        # Optionally, return the Base64-encoded image string
        b64_string = base64.b64encode(snapshot_png).decode("utf-8")
        return b64_string

    except Exception as e:
        print(f"Error capturing snapshot: {e}")
        error_screenshot_path = os.path.join(os.getcwd(), "img", "error_debug.png")
        with open(error_screenshot_path, "wb") as f:
            f.write(driver.get_screenshot_as_png())
        print(f"Error screenshot saved to {error_screenshot_path}")
        return None

    finally:
        driver.quit()

# Example usage:
if __name__ == "__main__":
    # Replace these with the actual values for your scrip.
    scid = "PGC"
    exchange_id = "POWERGRID"
    b64_img = capture_snapshot(scid, exchange_id)
    if b64_img:
        print("Snapshot captured and saved successfully.")
    else:
        print("Failed to capture snapshot.")
