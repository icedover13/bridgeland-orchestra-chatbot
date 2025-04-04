import unittest
import os
import sys

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
from tests.test_text_processor import TestTextProcessor
from tests.test_web_scraper import TestWebScraper
from tests.test_data_integrator import TestDataIntegrator

def run_tests():
    """Run all tests for the chatbot application."""
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestTextProcessor))
    test_suite.addTest(unittest.makeSuite(TestWebScraper))
    test_suite.addTest(unittest.makeSuite(TestDataIntegrator))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
