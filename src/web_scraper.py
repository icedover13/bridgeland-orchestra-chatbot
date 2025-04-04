import requests
from bs4 import BeautifulSoup
import re
import os
import time
from urllib.parse import urljoin, urlparse

class WebScraper:
    """
    A web scraper for extracting content from the Bridgeland Orchestra website
    and all its linked pages.
    """
    
    def __init__(self, base_url="https://www.bridgelandorchestra.com"):
        """
        Initialize the web scraper with the base URL.
        
        Args:
            base_url (str): The base URL of the website to scrape
        """
        self.base_url = base_url
        self.visited_urls = set()
        self.pages = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def is_valid_url(self, url):
        """
        Check if a URL is valid and belongs to the same domain.
        
        Args:
            url (str): URL to check
            
        Returns:
            bool: True if the URL is valid, False otherwise
        """
        parsed_url = urlparse(url)
        parsed_base = urlparse(self.base_url)
        
        # Check if the URL belongs to the same domain
        return parsed_url.netloc == parsed_base.netloc or not parsed_url.netloc
    
    def normalize_url(self, url):
        """
        Normalize a URL by joining it with the base URL if it's relative.
        
        Args:
            url (str): URL to normalize
            
        Returns:
            str: Normalized URL
        """
        # Remove fragments from URLs
        url = url.split('#')[0]
        
        # Remove query parameters
        url = url.split('?')[0]
        
        # Join with base URL if it's a relative URL
        return urljoin(self.base_url, url)
    
    def scrape_page(self, url):
        """
        Scrape a single page and extract its content.
        
        Args:
            url (str): URL of the page to scrape
            
        Returns:
            dict: Page content and metadata
        """
        try:
            # Normalize the URL
            url = self.normalize_url(url)
            
            # Skip if already visited
            if url in self.visited_urls:
                return None
            
            # Mark as visited
            self.visited_urls.add(url)
            
            # Make the request
            response = requests.get(url, headers=self.headers)
            
            # Check if the request was successful
            if response.status_code != 200:
                print(f"Failed to fetch {url}: Status code {response.status_code}")
                return None
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract page title
            title = soup.title.string if soup.title else url
            
            # Extract main content (this may need to be adjusted based on the website structure)
            content = self._extract_main_content(soup)
            
            # Extract links for further crawling
            links = self._extract_links(soup, url)
            
            # Create page object
            page = {
                'url': url,
                'title': title,
                'content': content,
                'links': links
            }
            
            # Add to pages list
            self.pages.append(page)
            
            print(f"Successfully scraped: {url}")
            return page
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
    
    def _extract_main_content(self, soup):
        """
        Extract the main content from a BeautifulSoup object.
        This method is customized for the Bridgeland Orchestra website structure.
        
        Args:
            soup (BeautifulSoup): BeautifulSoup object of the page
            
        Returns:
            dict: Extracted content
        """
        content = {
            'text': [],
            'headings': [],
            'images': [],
            'lists': []
        }
        
        # Extract all text paragraphs
        for p in soup.find_all('p'):
            if p.text.strip():
                content['text'].append(p.text.strip())
        
        # Extract headings
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                if heading.text.strip():
                    content['headings'].append({
                        'level': i,
                        'text': heading.text.strip()
                    })
        
        # Extract images with alt text and src
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src:
                content['images'].append({
                    'src': urljoin(self.base_url, src),
                    'alt': img.get('alt', '')
                })
        
        # Extract lists
        for list_tag in soup.find_all(['ul', 'ol']):
            list_items = []
            for item in list_tag.find_all('li'):
                if item.text.strip():
                    list_items.append(item.text.strip())
            
            if list_items:
                content['lists'].append({
                    'type': list_tag.name,
                    'items': list_items
                })
        
        return content
    
    def _extract_links(self, soup, current_url):
        """
        Extract links from a BeautifulSoup object.
        
        Args:
            soup (BeautifulSoup): BeautifulSoup object of the page
            current_url (str): URL of the current page
            
        Returns:
            list: List of extracted links
        """
        links = []
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            
            # Normalize the URL
            full_url = self.normalize_url(href)
            
            # Check if it's a valid URL to follow
            if self.is_valid_url(full_url):
                links.append({
                    'url': full_url,
                    'text': a.text.strip() or full_url
                })
        
        return links
    
    def crawl(self, max_pages=50, delay=1):
        """
        Crawl the website starting from the base URL.
        
        Args:
            max_pages (int): Maximum number of pages to crawl
            delay (float): Delay between requests in seconds
            
        Returns:
            list: List of scraped pages
        """
        # Start with the base URL
        urls_to_visit = [self.base_url]
        
        while urls_to_visit and len(self.pages) < max_pages:
            # Get the next URL to visit
            url = urls_to_visit.pop(0)
            
            # Scrape the page
            page = self.scrape_page(url)
            
            if page:
                # Add new links to the queue
                for link in page['links']:
                    link_url = link['url']
                    if link_url not in self.visited_urls and link_url not in urls_to_visit:
                        urls_to_visit.append(link_url)
            
            # Delay to be respectful to the server
            time.sleep(delay)
        
        return self.pages
    
    def save_to_files(self, output_dir):
        """
        Save the scraped content to text files.
        
        Args:
            output_dir (str): Directory to save the files
            
        Returns:
            list: List of saved file paths
        """
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        saved_files = []
        
        for i, page in enumerate(self.pages):
            # Create a filename based on the page title
            filename = f"{i+1:03d}_{self._sanitize_filename(page['title'])}.txt"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                # Write the URL and title
                f.write(f"URL: {page['url']}\n")
                f.write(f"Title: {page['title']}\n\n")
                
                # Write the headings
                if page['content']['headings']:
                    f.write("HEADINGS:\n")
                    for heading in page['content']['headings']:
                        f.write(f"{'#' * heading['level']} {heading['text']}\n")
                    f.write("\n")
                
                # Write the main text content
                if page['content']['text']:
                    f.write("CONTENT:\n")
                    for paragraph in page['content']['text']:
                        f.write(f"{paragraph}\n\n")
                
                # Write the lists
                if page['content']['lists']:
                    f.write("LISTS:\n")
                    for lst in page['content']['lists']:
                        f.write(f"{lst['type'].upper()}:\n")
                        for i, item in enumerate(lst['items']):
                            f.write(f"{i+1}. {item}\n")
                        f.write("\n")
                
                # Write image information
                if page['content']['images']:
                    f.write("IMAGES:\n")
                    for img in page['content']['images']:
                        f.write(f"- {img['alt']} ({img['src']})\n")
            
            saved_files.append(filepath)
            print(f"Saved: {filepath}")
        
        return saved_files
    
    def _sanitize_filename(self, filename):
        """
        Sanitize a string to be used as a filename.
        
        Args:
            filename (str): String to sanitize
            
        Returns:
            str: Sanitized filename
        """
        # Replace invalid characters with underscores
        sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
        
        # Limit the length
        if len(sanitized) > 50:
            sanitized = sanitized[:47] + '...'
        
        return sanitized
