import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pdfkit
import argparse
import time

def get_links_from_sitemap(sitemap_url):
    r = requests.get(sitemap_url)
    soup = BeautifulSoup(r.text, "xml")
    
    links = []
    
    for loc in soup.find_all("loc"):
        links.append(loc.text)
        
    for url in soup.find_all("url"):
        links.append(url.loc.text)
    
    return links

def render_and_convert_to_pdf(url):
    options = {
        'quiet': ''
    }
    rendered_content = pdfkit.from_url(url, False, options=options)
    return rendered_content

def main():
    parser = argparse.ArgumentParser(description='Convert links from sitemap.xml to PDF.')
    parser.add_argument('sitemap_url', type=str, help='URL of the sitemap.xml')
    parser.add_argument('output_filename', type=str, help='Name of the output PDF file')
    parser.add_argument('--num_links', type=int, default=10, help='Number of links to convert')
    parser.add_argument('--start_offset', type=int, default=0, help='Starting offset of links to convert')

    args = parser.parse_args()

    links = get_links_from_sitemap(args.sitemap_url)
    
    start_time = time.time()
    with open(args.output_filename, 'wb') as f:
        for index, link in enumerate(links[args.start_offset:args.start_offset + args.num_links]):
            pdf_content = render_and_convert_to_pdf(link)
            f.write(pdf_content)
            
            elapsed_time = time.time() - start_time
            estimated_time = elapsed_time / (index + 1) * args.num_links - elapsed_time
            progress = (index + 1) / args.num_links * 100
            
            print(f"{index + 1} of {args.num_links} ({progress:.2f}%) completed, Remaining {estimated_time:.2f} seconds, getting {link}")

if __name__ == "__main__":
    main()

