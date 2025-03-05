import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

def fetch_chart_image(scid, exchange_id, ex='NSE', screenshot_path='chart.png'):
    """
    Fetches a stock chart image from Moneycontrol for the given parameters.
    
    Args:
        scid (str): The scrip ID for the stock.
        exchange_id (str): The exchange ID for the stock.
        ex (str): Exchange code (default 'NSE').
        screenshot_path (str): Optional file path to save the screenshot.
        
    Returns:
        str: Base64-encoded image string of the chart.
    """
    # Configure headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-features=DirectComposition")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36")
    # Optional: Use incognito mode to avoid caching issues
    chrome_options.add_argument("--incognito")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Construct the URL with the given parameters
        url = f"https://www.moneycontrol.com/mc/stock/chart?scId={scid}&exchangeId={exchange_id}&ex={ex}"
        driver.get(url)
        
        # Wait for the chart element to load
        # Adjust the CSS selector below to match the actual element containing the chart.
        wait = WebDriverWait(driver, 60) # Increase timeout for slow loads
        print("Current working directory:", os.getcwd())
        iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[id^='tradingview_']")))
        driver.switch_to.frame(iframe)

        print("Current working directory2:", os.getcwd())
        # Save a full-page screenshot for debugging purposes 
        # Enable if need to debug for any issues
        img_folder = os.path.join(os.getcwd(), 'img')
        full_page_screenshot = driver.get_screenshot_as_png()
        with open(os.path.join(img_folder, 'full_page_debug.png'), "wb") as f:
            f.write(full_page_screenshot)
        print("Full page screenshot saved as 'full_page_debug.png'")

        chart_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".chart-gui-wrapper")))

        # Take a screenshot of the chart element
        chart_png = chart_element.screenshot_as_png
        
        # Optionally, save the screenshot to a file
        img_folder = os.path.join(os.getcwd(), 'img')
        file_suffix = time.strftime("%Y%m%d-%H%M%S")
        img_file_name = f"{scid}_{exchange_id}_{file_suffix}.png"
        screenshot_path = os.path.join(img_folder, img_file_name)
        with open(screenshot_path, "wb") as f:
            f.write(chart_png)
        
        # Convert the PNG data to a base64-encoded string
        b64_string = base64.b64encode(chart_png).decode("utf-8")
        return b64_string
        
    except Exception as e:
        print(f"Error fetching chart image: {e}")
        return None
        
    finally:
        driver.quit()

# Example usage:
if __name__ == "__main__":
    # Replace these parameters with actual values for a specific scrip.
    scid = "ICI02"          # Example scrip ID
    exchange_id = "ICICIBANK"  # Example exchange ID
    image_b64 = fetch_chart_image(scid, exchange_id)
    
    if image_b64:
        print("Successfully fetched chart image.")
        # You can now use the base64 string to display the image in your Flask app or save it.
    else:
        print("Failed to fetch chart image.")