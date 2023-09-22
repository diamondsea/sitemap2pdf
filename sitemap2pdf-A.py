import requests
import sys
import time
from bs4 import BeautifulSoup
from PyPDF2 import PdfMerger
from selenium import webdriver
from selenium.webdriver.common.by import By

def parse_sitemap(sitemap_url):
    resp = requests.get(sitemap_url)
    soup = BeautifulSoup(resp.content, 'xml')
    urls = [loc.text for loc in soup.find_all('loc')]
    if not urls:
        urls = [link.get('href') for link in soup.find_all('link') if link.get('href')]
    return urls

def convert_links_to_pdf(urls, output_filename, hide_classes=None, num_links=None, start_offset=0):
    if hide_classes is None:
        hide_classes = []

    merged_pdf = PdfMerger()
    total_urls = len(urls)
    num_links = num_links or total_urls
    end_offset = start_offset + num_links
    urls_subset = urls[start_offset:end_offset]

    chrome_options = webdriver.ChromeOptions()

    with webdriver.Chrome(options=chrome_options) as driver:
        for index, url in enumerate(urls_subset, 1):
            start_time = time.time()
            print(f"{index + start_offset} of {total_urls} ({(index/num_links)*100:.2f}%) completed, getting {url}")
            try:
                driver.get(url)
                for cls in hide_classes:
                    elements = driver.find_elements(By.CLASS_NAME, cls)
                    for elem in elements:
                        driver.execute_script("arguments[0].style.display = 'none';", elem)

                pdf_path = url.replace("https://", "").replace("http://", "").replace("/", "_") + ".pdf"
                
                # Set the Chrome print options
                chrome_options.add_experimental_option('prefs', {
                    "printing.print_preview_sticky_settings.appState": {
                        "recentDestinations": [{
                            "id": "Save as PDF",
                            "origin": "local",
                            "account": ""
                        }],
                        "selectedDestinationId": "Save as PDF",
                        "printing.print_preview_sticky_settings.printerType": "pdf",
                        "printType": "pdf"
                    },
                    "printing.printer_preferences": {
                        "recentDestinations": [{
                            "id": "Save as PDF",
                            "origin": "local",
                            "account": ""
                        }],
                        "selectedDestinationId": "Save as PDF",
                        "version": 2,
                        "printing.print_preview_sticky_settings.printerType": "pdf",
                        "printType": "pdf"
                    },
                    "savefile.filename": pdf_path
                })
                
                driver.execute_script('window.print();')
                merged_pdf.append(pdf_path)

            except Exception as e:
                print(f"Error processing {url}: {e}")

            elapsed_time = time.time() - start_time
            estimated_remaining = (num_links - index) * elapsed_time
            print(f"Remaining {estimated_remaining/60:.2f} minutes")

    merged_pdf.write(output_filename)
    merged_pdf.close()

if __name__ == '__main__':
    sitemap_url = sys.argv[1]
    output_filename = sys.argv[2]
    num_links = int(sys.argv[3])
    start_offset = int(sys.argv[4])
    hide_classes = sys.argv[5:]

    urls = parse_sitemap(sitemap_url)
    convert_links_to_pdf(urls, output_filename, hide_classes=hide_classes, num_links=num_links, start_offset=start_offset)

