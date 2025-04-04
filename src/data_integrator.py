import os
import sys
import pandas as pd
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.text_processor import TextProcessor
from src.web_scraper import WebScraper

class DataIntegrator:
    """
    A class for integrating data from multiple sources (text files and web data)
    and providing unified access for the chatbot.
    """
    
    def __init__(self, text_processor=None):
        """
        Initialize the data integrator.
        
        Args:
            text_processor (TextProcessor, optional): An existing TextProcessor instance
        """
        self.text_processor = text_processor if text_processor else TextProcessor()
        self.data_sources = {
            'text_files': [],
            'web_pages': []
        }
        self.events_timeline = []
        self.topic_index = {}
    
    def add_text_file(self, file_path, source_name=None):
        """
        Add a text file to the data sources.
        
        Args:
            file_path (str): Path to the text file
            source_name (str, optional): Name to identify the source
            
        Returns:
            bool: True if file was added successfully, False otherwise
        """
        if source_name is None:
            source_name = os.path.basename(file_path)
            
        # Load the document into the text processor
        success = self.text_processor.load_document(file_path, source_name)
        
        if success:
            self.data_sources['text_files'].append({
                'path': file_path,
                'name': source_name,
                'added_at': datetime.now()
            })
            
            # Update the events timeline and topic index
            self._update_events_timeline()
            self._update_topic_index()
            
        return success
    
    def add_web_data(self, web_data_dir, base_url=None):
        """
        Add web data from a directory of scraped web pages.
        
        Args:
            web_data_dir (str): Directory containing scraped web pages
            base_url (str, optional): Base URL of the website
            
        Returns:
            int: Number of files added successfully
        """
        if not os.path.isdir(web_data_dir):
            return 0
            
        files_added = 0
        
        # Get all text files in the directory
        for filename in os.listdir(web_data_dir):
            if filename.endswith('.txt'):
                file_path = os.path.join(web_data_dir, filename)
                
                # Load the document into the text processor
                success = self.text_processor.load_document(file_path, filename)
                
                if success:
                    self.data_sources['web_pages'].append({
                        'path': file_path,
                        'name': filename,
                        'added_at': datetime.now()
                    })
                    files_added += 1
        
        if files_added > 0:
            # Update the events timeline and topic index
            self._update_events_timeline()
            self._update_topic_index()
            
        return files_added
    
    def _update_events_timeline(self):
        """Update the events timeline from all data sources."""
        self.events_timeline = self.text_processor.get_date_ordered_events()
    
    def _update_topic_index(self):
        """
        Update the topic index by extracting key topics from all documents.
        This creates a mapping of topics to relevant document sections.
        """
        # Reset the topic index
        self.topic_index = {}
        
        # Process each document to extract key topics
        for doc in self.text_processor.document_metadata:
            # Extract potential topics from headings, capitalized phrases, etc.
            content = doc['raw_content']
            
            # Look for capitalized phrases (potential topics)
            capitalized_phrases = re.findall(r'\b[A-Z][A-Z\s]+\b', content)
            
            # Add each potential topic to the index
            for phrase in capitalized_phrases:
                topic = phrase.strip()
                if len(topic) > 3:  # Ignore very short topics
                    if topic not in self.topic_index:
                        self.topic_index[topic] = []
                    
                    # Find the sentence containing this topic
                    for sentence in doc['sentences']:
                        if topic in sentence:
                            self.topic_index[topic].append({
                                'document_name': doc['name'],
                                'sentence': sentence
                            })
                            break
    
    def get_response(self, query, max_contexts=3, include_additional_info=True):
        """
        Generate a comprehensive response to a query based on all data sources.
        
        Args:
            query (str): The user's query
            max_contexts (int): Maximum number of context snippets to include
            include_additional_info (bool): Whether to include additional related information
            
        Returns:
            dict: Response data including answer text and sources
        """
        # Check if any data is loaded
        if not self.text_processor.documents:
            return {
                'answer': "I don't have any information loaded yet. Please upload some text files or load website data.",
                'sources': [],
                'confidence': 0.0
            }
        
        # Get relevant contexts for the query
        contexts = self.text_processor.get_context_for_query(query, max_contexts=max_contexts)
        
        if not contexts:
            # Fallback response
            return {
                'answer': "I have some information on this topic, but please ask the directors for further details.",
                'sources': [],
                'confidence': 0.1
            }
        
        # Construct a response based on the contexts
        response_text = ""
        sources = []
        
        # Add information from each context
        for i, context in enumerate(contexts):
            if i == 0:
                response_text += f"{context['context']}\n\n"
            else:
                response_text += f"Additionally, {context['context'].lower()}\n\n"
            
            sources.append(context['document_name'])
        
        # Look for additional related information if requested
        if include_additional_info:
            additional_info = self._find_additional_information(query, contexts)
            
            if additional_info:
                response_text += "\nYou might also be interested to know that:\n"
                for info in additional_info:
                    response_text += f"- {info['text']}\n"
                    if info['source'] not in sources:
                        sources.append(info['source'])
        
        # Calculate a confidence score based on context relevance
        confidence = min(0.9, max([c['relevance_score'] for c in contexts]))
        
        # Add a note about the source
        response_text += f"\nThis information comes from {', '.join(sources)}.\n\n"
        
        # Add fallback message for low confidence responses
        if confidence < 0.5:
            response_text += "If you need more specific details, please ask the directors for further information."
        
        return {
            'answer': response_text,
            'sources': sources,
            'confidence': confidence
        }
    
    def _find_additional_information(self, query, existing_contexts, max_items=2):
        """
        Find additional information related to the query that wasn't included in the main response.
        
        Args:
            query (str): The user's query
            existing_contexts (list): Contexts already included in the response
            max_items (int): Maximum number of additional info items to include
            
        Returns:
            list: Additional information items
        """
        additional_info = []
        
        # Extract potential topics from the query
        query_terms = self.text_processor._preprocess_text(query).split()
        
        # Check the events timeline for related events
        for event in self.events_timeline:
            # Skip if this event is already in the existing contexts
            if any(event['event_text'] in context['context'] for context in existing_contexts):
                continue
                
            # Check if the event is related to the query
            event_text = self.text_processor._preprocess_text(event['event_text'])
            if any(term in event_text for term in query_terms):
                additional_info.append({
                    'text': event['event_text'],
                    'source': event['document_name'],
                    'date': event['normalized_date']
                })
                
                if len(additional_info) >= max_items:
                    break
        
        # If we still need more items, check the topic index
        if len(additional_info) < max_items:
            for topic, mentions in self.topic_index.items():
                # Skip if this topic is already in the existing contexts or additional info
                if any(topic in context['context'] for context in existing_contexts) or \
                   any(topic in info['text'] for info in additional_info):
                    continue
                    
                # Check if the topic is related to the query
                if any(term in topic.lower() for term in query_terms):
                    for mention in mentions:
                        additional_info.append({
                            'text': mention['sentence'],
                            'source': mention['document_name']
                        })
                        
                        if len(additional_info) >= max_items:
                            break
                            
                if len(additional_info) >= max_items:
                    break
        
        return additional_info

# Import re module which was missing
import re
