import unittest
import os
import sys
import tempfile
import shutil

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_integrator import DataIntegrator
from src.text_processor import TextProcessor

class TestDataIntegrator(unittest.TestCase):
    """Test cases for the DataIntegrator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.data_integrator = DataIntegrator()
        
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.text_files_dir = os.path.join(self.test_dir, "text_files")
        self.web_data_dir = os.path.join(self.test_dir, "web_data")
        
        os.makedirs(self.text_files_dir, exist_ok=True)
        os.makedirs(self.web_data_dir, exist_ok=True)
        
        # Create test text file
        self.text_file = os.path.join(self.text_files_dir, "newsletter.txt")
        with open(self.text_file, "w") as f:
            f.write("""
            Bridgeland Orchestra Newsletter
            
            Upcoming Events:
            
            1. Spring Concert - April 15, 2025
            Join us for our annual spring concert featuring works by Mozart and Beethoven.
            
            2. Summer Workshop - June 10
            Our summer workshop will focus on string techniques and ensemble playing.
            
            Contact Information:
            
            Email: info@bridgelandorchestra.com
            Phone: 555-123-4567
            """)
        
        # Create test web data file
        self.web_file = os.path.join(self.web_data_dir, "website.txt")
        with open(self.web_file, "w") as f:
            f.write("""
            URL: https://www.bridgelandorchestra.com/events
            Title: Events - Bridgeland Orchestra
            
            HEADINGS:
            # Upcoming Events
            ## Spring Concert
            ## Summer Workshop
            
            CONTENT:
            Join us for our exciting events this season.
            
            Date: April 15, 2025
            Location: Bridgeland Auditorium
            
            Date: June 10, 2025
            Location: Bridgeland Community Center
            
            IMAGES:
            - Concert Hall (https://www.bridgelandorchestra.com/images/hall.jpg)
            """)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)
    
    def test_add_text_file(self):
        """Test adding a text file to the data sources."""
        # Add the text file
        result = self.data_integrator.add_text_file(self.text_file, "Newsletter")
        
        # Check that the file was added successfully
        self.assertTrue(result)
        self.assertEqual(len(self.data_integrator.data_sources['text_files']), 1)
        self.assertEqual(self.data_integrator.data_sources['text_files'][0]['name'], "Newsletter")
    
    def test_add_web_data(self):
        """Test adding web data from a directory."""
        # Add the web data
        files_added = self.data_integrator.add_web_data(self.web_data_dir)
        
        # Check that the files were added successfully
        self.assertEqual(files_added, 1)
        self.assertEqual(len(self.data_integrator.data_sources['web_pages']), 1)
    
    def test_get_response(self):
        """Test generating a response to a query."""
        # Add both data sources
        self.data_integrator.add_text_file(self.text_file, "Newsletter")
        self.data_integrator.add_web_data(self.web_data_dir)
        
        # Get a response for a query
        response = self.data_integrator.get_response("When is the spring concert?")
        
        # Check that a response was generated
        self.assertIsNotNone(response)
        self.assertIn('answer', response)
        self.assertIn('sources', response)
        self.assertIn('confidence', response)
        
        # Check that the response contains relevant information
        self.assertIn("April 15", response['answer'])
        
        # Check that the sources are included
        self.assertGreater(len(response['sources']), 0)
    
    def test_fallback_response(self):
        """Test fallback response when no relevant information is found."""
        # Add both data sources
        self.data_integrator.add_text_file(self.text_file, "Newsletter")
        self.data_integrator.add_web_data(self.web_data_dir)
        
        # Get a response for a query with no relevant information
        response = self.data_integrator.get_response("What is the ticket price?")
        
        # Check that a fallback response was generated
        self.assertIn("please ask the directors for further details", response['answer'])
        
        # Check that the confidence is low
        self.assertLess(response['confidence'], 0.5)
    
    def test_additional_information(self):
        """Test providing additional information beyond what was asked."""
        # Add both data sources
        self.data_integrator.add_text_file(self.text_file, "Newsletter")
        self.data_integrator.add_web_data(self.web_data_dir)
        
        # Get a response with additional information
        response = self.data_integrator.get_response("Tell me about the spring concert", include_additional_info=True)
        
        # Check that the response contains additional information
        self.assertIn("You might also be interested to know", response['answer'])

if __name__ == "__main__":
    unittest.main()
