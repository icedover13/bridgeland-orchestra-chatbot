import unittest
import os
import sys
import tempfile
import shutil
import requests_mock

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web_scraper import WebScraper

class TestWebScraper(unittest.TestCase):
    """Test cases for the WebScraper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scraper = WebScraper(base_url="https://www.bridgelandorchestra.com")
        
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Sample HTML content
        self.sample_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bridgeland Orchestra</title>
        </head>
        <body>
            <h1>Welcome to Bridgeland Orchestra</h1>
            <p>We are a community orchestra dedicated to musical excellence.</p>
            
            <h2>Upcoming Events</h2>
            <ul>
                <li>Spring Concert - April 15, 2025</li>
                <li>Summer Workshop - June 10, 2025</li>
            </ul>
            
            <h2>About Us</h2>
            <p>Founded in 2010, the Bridgeland Orchestra has been serving the community for over 15 years.</p>
            
            <div class="links">
                <a href="/events">Events</a>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
                <a href="https://www.example.com">External Link</a>
            </div>
            
            <img src="/images/orchestra.jpg" alt="Orchestra performing">
        </body>
        </html>
        """
        
        # Sample HTML for a subpage
        self.events_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Events - Bridgeland Orchestra</title>
        </head>
        <body>
            <h1>Upcoming Events</h1>
            <p>Join us for our exciting events this season.</p>
            
            <h2>Spring Concert</h2>
            <p>Date: April 15, 2025</p>
            <p>Location: Bridgeland Auditorium</p>
            
            <h2>Summer Workshop</h2>
            <p>Date: June 10, 2025</p>
            <p>Location: Bridgeland Community Center</p>
        </body>
        </html>
        """
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)
    
    @requests_mock.Mocker()
    def test_scrape_page(self, m):
        """Test scraping a single page."""
        # Mock the HTTP request
        m.get("https://www.bridgelandorchestra.com", text=self.sample_html)
        
        # Scrape the page
        page = self.scraper.scrape_page("https://www.bridgelandorchestra.com")
        
        # Check that the page was scraped successfully
        self.assertIsNotNone(page)
        self.assertEqual(page['url'], "https://www.bridgelandorchestra.com")
        self.assertEqual(page['title'], "Bridgeland Orchestra")
        
        # Check that the content was extracted correctly
        self.assertIn("We are a community orchestra dedicated to musical excellence.", page['content']['text'])
        self.assertEqual(len(page['content']['headings']), 3)  # h1, h2, h2
        self.assertEqual(len(page['content']['images']), 1)
        self.assertEqual(len(page['content']['lists']), 1)
        
        # Check that links were extracted correctly
        self.assertEqual(len(page['links']), 3)  # 3 internal links, 1 external link filtered out
    
    @requests_mock.Mocker()
    def test_crawl(self, m):
        """Test crawling multiple pages."""
        # Mock the HTTP requests
        m.get("https://www.bridgelandorchestra.com", text=self.sample_html)
        m.get("https://www.bridgelandorchestra.com/events", text=self.events_html)
        m.get("https://www.bridgelandorchestra.com/about", text="<html><body><h1>About</h1></body></html>")
        m.get("https://www.bridgelandorchestra.com/contact", text="<html><body><h1>Contact</h1></body></html>")
        
        # Crawl the website with a limit of 3 pages
        pages = self.scraper.crawl(max_pages=3, delay=0)
        
        # Check that pages were crawled successfully
        self.assertEqual(len(pages), 3)
    
    @requests_mock.Mocker()
    def test_save_to_files(self, m):
        """Test saving scraped content to files."""
        # Mock the HTTP request
        m.get("https://www.bridgelandorchestra.com", text=self.sample_html)
        
        # Scrape the page
        self.scraper.scrape_page("https://www.bridgelandorchestra.com")
        
        # Save to files
        saved_files = self.scraper.save_to_files(self.test_dir)
        
        # Check that a file was saved
        self.assertEqual(len(saved_files), 1)
        
        # Check that the file exists
        self.assertTrue(os.path.exists(saved_files[0]))
        
        # Check the content of the file
        with open(saved_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Bridgeland Orchestra", content)
            self.assertIn("Welcome to Bridgeland Orchestra", content)
    
    def test_is_valid_url(self):
        """Test URL validation."""
        # Valid URLs (same domain)
        self.assertTrue(self.scraper.is_valid_url("https://www.bridgelandorchestra.com/events"))
        self.assertTrue(self.scraper.is_valid_url("/about"))  # Relative URL
        
        # Invalid URLs (different domain)
        self.assertFalse(self.scraper.is_valid_url("https://www.example.com"))
        self.assertFalse(self.scraper.is_valid_url("https://bridgelandorchestra.org"))  # Different TLD
    
    def test_normalize_url(self):
        """Test URL normalization."""
        # Test joining relative URLs with base URL
        self.assertEqual(
            self.scraper.normalize_url("/events"),
            "https://www.bridgelandorchestra.com/events"
        )
        
        # Test removing fragments
        self.assertEqual(
            self.scraper.normalize_url("https://www.bridgelandorchestra.com/events#schedule"),
            "https://www.bridgelandorchestra.com/events"
        )
        
        # Test removing query parameters
        self.assertEqual(
            self.scraper.normalize_url("https://www.bridgelandorchestra.com/events?date=2025-04-15"),
            "https://www.bridgelandorchestra.com/events"
        )

if __name__ == "__main__":
    unittest.main()
