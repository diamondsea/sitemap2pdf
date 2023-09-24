import asyncio
from bs4 import BeautifulSoup
import requests
from PyPDF2 import PdfMerger
from pyppeteer import launch
import argparse
import time
import os

async def convert_url_to_pdf(url, pdf_path, hide_classes):
    browser = await launch()
    page = await browser.newPage()
    
    await page.goto(url)
    
    for cls in hide_classes:
        elements = await page.querySelectorAll(f".{cls}")
        for elem in elements:
            await page.evaluate('(elem) => elem.style.display = "none"', elem)
    
    await page.pdf({'path': pdf_path, 'format': 'A4', 'printBackground': True})
    
    await browser.close()

def parse_sitemap(sitemap_url, all_urls=None):
    if all_urls is None:
        all_urls = []

    resp = requests.get(sitemap_url)
    soup = BeautifulSoup(resp.content, 'xml')
    urls = [loc.text for loc in soup.find_all('loc')]
    
    # Display details of the current sitemap being processed
    print(f"Reading sitemap: {sitemap_url}")
    print(f"Number of URLs found: {len(urls)}")
    
    sitemap_links = [url for url in urls if 'sitemap' in url.lower()]
    if sitemap_links:
        for link in sitemap_links:
            parse_sitemap(link, all_urls)
    else:
        all_urls.extend(urls)

    return all_urls

def main(sitemap_url, output_filename, limit, hide_classes, no_cache):
    all_urls = parse_sitemap(sitemap_url)
    if limit:
        all_urls = all_urls[:limit]

    merged_pdf = PdfMerger()
    total_urls = len(all_urls)
    start_time = time.time()
    avg_time_per_url = None

    for index, url in enumerate(all_urls, 1):
        current_time = time.time()
        elapsed_time = current_time - start_time
        pdf_path = url.replace("https://", "").replace("http://", "").replace("/", "_") + ".pdf"

        if os.path.exists(pdf_path) and not no_cache:
            print(f"Using cached {pdf_path}")
            merged_pdf.append(pdf_path)
            continue

    # ... rest of your code ...
        if avg_time_per_url:
            eta_seconds = avg_time_per_url * (total_urls - index)
            eta_minutes = int(eta_seconds // 60)
            eta_seconds = int(eta_seconds % 60)
            eta = f"{eta_minutes}m {eta_seconds}s"
        else:
            eta = "Calculating..."

        percentage_complete = (index / total_urls) * 100
        print(f"[{percentage_complete:.2f}% - ETA: {eta}] Processing {index} of {total_urls}: {url}")
        asyncio.get_event_loop().run_until_complete(convert_url_to_pdf(url, pdf_path, hide_classes))
        merged_pdf.append(pdf_path)

        if index == 5:
            avg_time_per_url = elapsed_time / index

    merged_pdf.write(output_filename)
    merged_pdf.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert sitemap URLs to a merged PDF.")
    parser.add_argument('--sitemap_url', required=True, help="URL of the sitemap to process.")
    parser.add_argument('--output_filename', required=True, help="Filename for the merged PDF output.")
    parser.add_argument('--limit', type=int, default=None, help="Limit the number of URLs processed.")
    parser.add_argument('--start_offset', type=int, default=0, help="Starting offset for the URLs.")
    parser.add_argument('--hide_classes', nargs='*', default=[], help="List of classes to hide in the PDF.")
    parser.add_argument('--no-cache', action='store_true', help="If set, the script will not use cached PDFs and will regenerate them.")

    args = parser.parse_args()
    urls = parse_sitemap(args.sitemap_url)[args.start_offset:]
    if args.limit:
        urls = urls[:args.limit]

    main(args.sitemap_url, args.output_filename, len(urls), args.hide_classes, args.no_cache)





