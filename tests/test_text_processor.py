import unittest
import os
import sys
import tempfile
import shutil

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.text_processor import TextProcessor

class TestTextProcessor(unittest.TestCase):
    """Test cases for the TextProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.text_processor = TextProcessor()
        
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Create a test file with sample content
        self.test_file = os.path.join(self.test_dir, "test_document.txt")
        with open(self.test_file, "w") as f:
            f.write("""
            Bridgeland Orchestra Newsletter
            
            Upcoming Events:
            
            1. Spring Concert - April 15, 2025
            Join us for our annual spring concert featuring works by Mozart and Beethoven.
            
            2. Summer Workshop - June 10
            Our summer workshop will focus on string techniques and ensemble playing.
            
            3. Fall Auditions - 9/5/2025
            Auditions for the 2025-2026 season will be held on September 5th.
            
            Recent News:
            
            The orchestra performed at the district competition on March 3rd and received
            superior ratings. Congratulations to all our musicians!
            
            Contact Information:
            
            Email: info@bridgelandorchestra.com
            Phone: 555-123-4567
            """)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)
    
    def test_load_document(self):
        """Test loading a document."""
        # Load the test document
        result = self.text_processor.load_document(self.test_file, "Test Document")
        
        # Check that the document was loaded successfully
        self.assertTrue(result)
        self.assertEqual(len(self.text_processor.documents), 1)
        self.assertEqual(len(self.text_processor.document_metadata), 1)
        self.assertEqual(self.text_processor.document_metadata[0]['name'], "Test Document")
    
    def test_extract_dates(self):
        """Test extracting dates from text."""
        # Load the test document
        self.text_processor.load_document(self.test_file, "Test Document")
        
        # Check that dates were extracted correctly
        dates = self.text_processor.document_metadata[0]['dates']
        
        # There should be at least 3 dates in the test document
        self.assertGreaterEqual(len(dates), 3)
        
        # Check specific dates
        date_texts = [date['original'] for date in dates]
        self.assertIn("April 15, 2025", date_texts)
        self.assertIn("June 10", date_texts)
        self.assertIn("9/5/2025", date_texts)
        
        # Check that dates were normalized
        normalized_dates = [date['normalized'] for date in dates]
        self.assertIn("2025-04-15", normalized_dates)  # April 15, 2025
        
        # Check that dates without years were handled correctly
        for date in dates:
            if date['original'] == "June 10":
                self.assertFalse(date['has_year'])
                # Should use current year
                self.assertTrue(date['normalized'].startswith("2025-06-10"))
    
    def test_search(self):
        """Test searching for documents."""
        # Load the test document
        self.text_processor.load_document(self.test_file, "Test Document")
        
        # Search for a term that should be in the document
        results = self.text_processor.search("concert")
        
        # Check that the search returned results
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['name'], "Test Document")
        
        # Search for a term that should not be in the document
        results = self.text_processor.search("basketball")
        
        # Check that the search returned no results
        self.assertEqual(len(results), 0)
    
    def test_get_context_for_query(self):
        """Test getting context for a query."""
        # Load the test document
        self.text_processor.load_document(self.test_file, "Test Document")
        
        # Get context for a query
        contexts = self.text_processor.get_context_for_query("When is the spring concert?")
        
        # Check that contexts were returned
        self.assertGreater(len(contexts), 0)
        
        # Check that the context contains relevant information
        context_text = contexts[0]['context']
        self.assertIn("Spring Concert", context_text)
        self.assertIn("April 15", context_text)
    
    def test_get_date_ordered_events(self):
        """Test getting events ordered by date."""
        # Load the test document
        self.text_processor.load_document(self.test_file, "Test Document")
        
        # Get date-ordered events
        events = self.text_processor.get_date_ordered_events()
        
        # Check that events were returned
        self.assertGreater(len(events), 0)
        
        # Check that events are ordered by date
        for i in range(1, len(events)):
            self.assertLessEqual(events[i-1]['date'], events[i]['date'])

if __name__ == "__main__":
    unittest.main()
