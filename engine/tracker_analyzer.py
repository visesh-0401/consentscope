from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import json
import os
import tldextract
import pandas as pd

# Category mapping dictionary
CATEGORY_MAPPING = {
    "doubleclick.net": "ads",
    "googletagmanager.com": "analytics",
    "google-analytics.com": "analytics",
    "facebook.net": "social",
    "twitter.com": "social",
    "hotjar.com": "analytics",
    "adnxs.com": "ads",
    "cloudflareinsights.com": "performance"
}

def analyze_website(url, action="accept", wait_time=5, log_dir="logs"):
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--remote-debugging-port=9222")

    # Setup ChromeDriver service
    service = Service(executable_path="/usr/bin/chromedriver")  # Update if installed elsewhere

    try:
        print(f"Launching Chrome for URL: {url} | Action: {action}")
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(url)
        time.sleep(wait_time)

        # Attempt to find and click cookie banner button
        try:
            if action == "accept":
                buttons = driver.find_elements("xpath", "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]")
            else:
                buttons = driver.find_elements("xpath", "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'reject')]")

            if buttons:
                print(f"[{action.upper()}] Clicking cookie button.")
                buttons[0].click()
                time.sleep(wait_time)
            else:
                print(f"[{action.upper()}] No cookie button found.")
        except Exception as e:
            print(f"[{action.upper()}] Error handling cookie banner: {e}")

        # Collect network requests
        requests_data = []
        for request in driver.requests:
            if request.response:
                requests_data.append({
                    "url": request.url,
                    "method": request.method,
                    "status": request.response.status_code,
                    "headers": dict(request.headers)
                })

        driver.quit()

        filename = os.path.join(log_dir, f"{url.replace('https://','').replace('/','_')}_{action}.json")
        with open(filename, "w") as f:
            json.dump(requests_data, f, indent=2)

        print(f"[{action.upper()}] Analysis complete. Saved to {filename}")
        return filename

    except Exception as e:
        print(f"[{action.upper()}] Error during analysis: {e}")
        return None

def is_third_party(main_domain, request_url):
    request_domain = tldextract.extract(request_url).registered_domain
    return request_domain and request_domain != main_domain

CATEGORY_MAPPING = {
    "doubleclick.net": "ads",
    "googletagmanager.com": "analytics",
    "google-analytics.com": "analytics",
    "facebook.net": "social",
    "twitter.com": "social",
    "hotjar.com": "analytics",
    "adnxs.com": "ads",
    "cloudflareinsights.com": "performance"
}

def classify_trackers(log_path, main_domain):
    """
    Classify trackers found in the log into categories like 'ads', 'analytics', etc.
    """
    with open(log_path) as f:
        data = json.load(f)

    categorized_trackers = {
        "ads": [],
        "analytics": [],
        "social": [],
        "performance": []
    }

    for req in data:
        url = req['url']
        domain = tldextract.extract(url).domain
        
        # Only classify third-party trackers (those not from the main domain)
        if domain != main_domain:
            # Classify based on the CATEGORY_MAPPING dictionary
            for key, category in CATEGORY_MAPPING.items():
                if key in url:
                    categorized_trackers[category].append(url)
                    break  # No need to check other categories once a match is found

    return categorized_trackers


def save_csv(categorized_trackers, filename):
    all_trackers = []
    for category, trackers in categorized_trackers.items():
        all_trackers.extend(trackers)
    
    df = pd.DataFrame({"Tracker URL": all_trackers})
    df.to_csv(filename, index=False)
