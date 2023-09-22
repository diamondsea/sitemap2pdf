import asyncio
import sys
from bs4 import BeautifulSoup
import requests
from PyPDF2 import PdfMerger
from pyppeteer import launch

async def convert_url_to_pdf(url, pdf_path):
    browser = await launch()
    page = await browser.newPage()
    
    # Navigate to the URL
    await page.goto(url)
    
    # Convert the page to PDF
    await page.pdf({'path': pdf_path, 'format': 'A4', 'printBackground': True})
    
    await browser.close()

def parse_sitemap(sitemap_url):
    resp = requests.get(sitemap_url)
    soup = BeautifulSoup(resp.content, 'xml')
    urls = [loc.text for loc in soup.find_all('loc')]
    if not urls:
        urls = [link.get('href') for link in soup.find_all('link') if link.get('href')]
    return urls

def main(sitemap_url, output_filename, limit=None):
    urls = parse_sitemap(sitemap_url)

    # If a limit is provided, truncate the URLs list
    if limit:
        urls = urls[:limit]

    merged_pdf = PdfMerger()

    total_urls = len(urls)

    for index, url in enumerate(urls, 1):
        pdf_path = url.replace("https://", "").replace("http://", "").replace("/", "_") + ".pdf"
        print(f"Processing {index} of {total_urls}: {url}")
        asyncio.get_event_loop().run_until_complete(convert_url_to_pdf(url, pdf_path))
        merged_pdf.append(pdf_path)

    merged_pdf.write(output_filename)
    merged_pdf.close()

if __name__ == '__main__':
    sitemap_url = sys.argv[1]
    output_filename = sys.argv[2]
    limit = None
    
    if len(sys.argv) > 3:
        limit = int(sys.argv[3])

    main(sitemap_url, output_filename, limit)
