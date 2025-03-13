from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import time
from PIL import Image

def trigger_download_with_keys(scid, exchange_id, ex='NSE'):
    # Set up download preferences if you want to capture the downloaded file.
    download_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_dir, exist_ok=True)

    chrome_options = Options()
    # For debugging, consider disabling headless mode initially.
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-features=DirectComposition")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    chrome_options.add_argument("--incognito")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 30)
    
    try:
        url = f"https://www.moneycontrol.com/mc/stock/chart?scId={scid}&exchangeId={exchange_id}&ex={ex}"
        driver.get(url)
        
        # Switch to the iframe if needed.
        #iframe = wait.until(lambda d: d.find_element_by_css_selector("iframe[id^='tradingview_']"))
        iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[id^='tradingview_']")))
        driver.switch_to.frame(iframe)
        
        # Ensure the chart is loaded.
        # Wait for all relevant elements to ensure the chart is fully loaded
        #tv_container = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".tradingview-container")))
        gui_wrapper = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".chart-gui-wrapper")))
        #chart_container = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".chart-container.active")))

        print("Chart container step done")
        wait = WebDriverWait(driver, 100)
        element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.chart-container.active')))
        #element= wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".chart-gui-wrapper")))
        wait = WebDriverWait(driver, 100)
        print("printing after element step done")
        


        file_suffix = time.strftime("%Y%m%d-%H%M%S")
        img_file_name = f"{scid}_{exchange_id}_{file_suffix}.png"
        screenshot_path = os.path.join(download_dir, img_file_name)

        chart_png = element.screenshot_as_png
        #element.screenshot(screenshot_path)

        with open(screenshot_path, "wb") as f:
            f.write(chart_png)
        


        #Image.open(img)

        # Click on the body or chart area to ensure it has focus.
        #driver.find_element_by_tag_name("body").click()
        #print("body clicked")

        # Simulate the key combination Ctrl+Alt+S
 #       actions = ActionChains(driver)
 #       actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys("s").key_up(Keys.ALT).key_up(Keys.CONTROL).perform()
 #       print("actions clicked")
 #       # Wait for the download to start (monitor the downloads folder)
        time.sleep(5)  # adjust sleep as necessary
        
        # List files in download directory
#       files = os.listdir(download_dir)
#       if files:
#           downloaded_file = os.path.join(download_dir, files[0])
#           print(f"Downloaded file: {downloaded_file}")
#           return downloaded_file
#       else:
#           print("No file downloaded.")
#           return None

    except Exception as e:
        print("Error triggering download:", e)
        return None

    finally:
        driver.quit()

# Example usage:
if __name__ == "__main__":
    scid = "PGC"  # replace with actual scrip id
    exchange_id = "ICICIBANK"  # replace with actual exchange id
    trigger_download_with_keys(scid, exchange_id)
