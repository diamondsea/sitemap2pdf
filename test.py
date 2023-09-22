from selenium import webdriver

with webdriver.Chrome() as driver:
    driver.get("https://www.google.com")
    elements = driver.find_element(By.CSS_SELECTOR,"a")
    print(f"Found {len(elements)} 'a' tags on Google's homepage.")

