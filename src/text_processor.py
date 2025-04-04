import re
import os
import pandas as pd
import numpy as np
from datetime import datetime
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class TextProcessor:
    """
    A class for processing text files with varying formats, especially handling dates.
    This processor is designed to work with newsletter content that may have inconsistent formatting.
    """
    
    def __init__(self):
        """Initialize the text processor with necessary resources."""
        # Ensure NLTK resources are available
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))
        self.documents = []
        self.document_metadata = []
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = None
        
    def load_document(self, file_path, document_name=None):
        """
        Load a document from a file path and process it.
        
        Args:
            file_path (str): Path to the text file
            document_name (str, optional): Name to identify the document. Defaults to filename.
        
        Returns:
            bool: True if document was loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return False
                
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if document_name is None:
                document_name = os.path.basename(file_path)
                
            # Process the document
            processed_content = self._preprocess_text(content)
            
            # Extract dates from the content
            dates = self._extract_dates(content)
            
            # Store the document and its metadata
            doc_id = len(self.documents)
            self.documents.append(processed_content)
            self.document_metadata.append({
                'id': doc_id,
                'name': document_name,
                'path': file_path,
                'dates': dates,
                'raw_content': content,
                'processed_content': processed_content,
                'sentences': sent_tokenize(content)
            })
            
            # Update the TF-IDF matrix
            self._update_tfidf_matrix()
            
            return True
            
        except Exception as e:
            print(f"Error loading document {file_path}: {str(e)}")
            return False
    
    def _preprocess_text(self, text):
        """
        Preprocess text by removing special characters, converting to lowercase,
        and removing stop words.
        
        Args:
            text (str): Raw text content
            
        Returns:
            str: Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stop words
        filtered_tokens = [word for word in tokens if word not in self.stop_words]
        
        # Join tokens back into text
        processed_text = ' '.join(filtered_tokens)
        
        return processed_text
    
    def _extract_dates(self, text):
        """
        Extract dates from text, handling various formats and missing information.
        
        Args:
            text (str): Text to extract dates from
            
        Returns:
            list: List of extracted date objects with original text and normalized form
        """
        dates = []
        
        # Pattern for dates with various formats
        # This handles formats like:
        # - April 15, 2025
        # - Apr 15, 2025
        # - 4/15/2025
        # - 15 April 2025
        # - April 15
        # - 15th of April
        # - etc.
        
        # Full date patterns (with year)
        full_date_patterns = [
            r'(?P<month>[A-Za-z]+)\s+(?P<day>\d{1,2})(?:st|nd|rd|th)?,?\s+(?P<year>\d{4})',  # April 15, 2025
            r'(?P<day>\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?(?P<month>[A-Za-z]+),?\s+(?P<year>\d{4})',  # 15th of April, 2025
            r'(?P<month>\d{1,2})[/-](?P<day>\d{1,2})[/-](?P<year>\d{4})',  # 4/15/2025 or 4-15-2025
            r'(?P<month>\d{1,2})[/-](?P<day>\d{1,2})[/-](?P<year>\d{2})'  # 4/15/25 or 4-15-25
        ]
        
        # Partial date patterns (missing year)
        partial_date_patterns = [
            r'(?P<month>[A-Za-z]+)\s+(?P<day>\d{1,2})(?:st|nd|rd|th)?',  # April 15
            r'(?P<day>\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?(?P<month>[A-Za-z]+)',  # 15th of April
            r'(?P<month>\d{1,2})[/-](?P<day>\d{1,2})'  # 4/15 or 4-15
        ]
        
        # Process full date patterns
        for pattern in full_date_patterns:
            for match in re.finditer(pattern, text):
                try:
                    date_info = match.groupdict()
                    
                    # Convert month name to number if it's a string
                    if date_info['month'].isalpha():
                        try:
                            month_num = datetime.strptime(date_info['month'], '%B').month
                        except ValueError:
                            try:
                                month_num = datetime.strptime(date_info['month'], '%b').month
                            except ValueError:
                                continue
                        date_info['month'] = month_num
                    
                    # Convert to integers
                    month = int(date_info['month'])
                    day = int(date_info['day'])
                    year = int(date_info['year'])
                    
                    # Handle two-digit years
                    if year < 100:
                        if year < 50:  # Assume 20xx for years less than 50
                            year += 2000
                        else:  # Assume 19xx for years 50 and above
                            year += 1900
                    
                    # Create datetime object
                    date_obj = datetime(year, month, day)
                    
                    dates.append({
                        'original': match.group(0),
                        'normalized': date_obj.strftime('%Y-%m-%d'),
                        'datetime': date_obj,
                        'has_year': True
                    })
                except (ValueError, KeyError) as e:
                    # Skip invalid dates
                    continue
        
        # Process partial date patterns (missing year)
        current_year = datetime.now().year
        for pattern in partial_date_patterns:
            for match in re.finditer(pattern, text):
                try:
                    date_info = match.groupdict()
                    
                    # Convert month name to number if it's a string
                    if date_info['month'].isalpha():
                        try:
                            month_num = datetime.strptime(date_info['month'], '%B').month
                        except ValueError:
                            try:
                                month_num = datetime.strptime(date_info['month'], '%b').month
                            except ValueError:
                                continue
                        date_info['month'] = month_num
                    
                    # Convert to integers
                    month = int(date_info['month'])
                    day = int(date_info['day'])
                    
                    # Use current year as default
                    year = current_year
                    
                    # Create datetime object
                    date_obj = datetime(year, month, day)
                    
                    dates.append({
                        'original': match.group(0),
                        'normalized': date_obj.strftime('%Y-%m-%d'),
                        'datetime': date_obj,
                        'has_year': False
                    })
                except (ValueError, KeyError) as e:
                    # Skip invalid dates
                    continue
        
        return dates
    
    def _update_tfidf_matrix(self):
        """Update the TF-IDF matrix with all current documents."""
        if not self.documents:
            self.tfidf_matrix = None
            return
            
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
    
    def search(self, query, top_n=5):
        """
        Search for documents relevant to the query.
        
        Args:
            query (str): Search query
            top_n (int): Number of top results to return
            
        Returns:
            list: List of top matching document metadata
        """
        if not self.documents or self.tfidf_matrix is None:
            return []
            
        # Preprocess the query
        processed_query = self._preprocess_text(query)
        
        # Transform the query using the same vectorizer
        query_vector = self.vectorizer.transform([processed_query])
        
        # Calculate cosine similarity between query and all documents
        cosine_similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Get indices of top N similar documents
        top_indices = cosine_similarities.argsort()[-top_n:][::-1]
        
        # Return metadata for top documents
        results = []
        for idx in top_indices:
            if cosine_similarities[idx] > 0:  # Only include relevant results
                doc_meta = self.document_metadata[idx].copy()
                doc_meta['similarity_score'] = float(cosine_similarities[idx])
                results.append(doc_meta)
                
        return results
    
    def get_context_for_query(self, query, max_contexts=3, context_size=3):
        """
        Get relevant context snippets for a query from all documents.
        
        Args:
            query (str): The query to find context for
            max_contexts (int): Maximum number of context snippets to return
            context_size (int): Number of sentences before and after the matching sentence
            
        Returns:
            list: List of context snippets with document metadata
        """
        # First, find the most relevant documents
        relevant_docs = self.search(query, top_n=max_contexts)
        
        if not relevant_docs:
            return []
            
        contexts = []
        
        for doc in relevant_docs:
            doc_sentences = doc['sentences']
            
            # Find sentences that might contain the answer
            query_terms = set(self._preprocess_text(query).split())
            
            # Score each sentence based on term overlap with query
            sentence_scores = []
            for i, sentence in enumerate(doc_sentences):
                sentence_terms = set(self._preprocess_text(sentence).split())
                overlap = len(query_terms.intersection(sentence_terms))
                if overlap > 0:
                    sentence_scores.append((i, overlap))
            
            # Sort by score and get top sentences
            sentence_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Get context around top sentences
            for sent_idx, score in sentence_scores[:2]:  # Get contexts for top 2 matching sentences
                start_idx = max(0, sent_idx - context_size)
                end_idx = min(len(doc_sentences), sent_idx + context_size + 1)
                
                context = ' '.join(doc_sentences[start_idx:end_idx])
                
                contexts.append({
                    'document_name': doc['name'],
                    'context': context,
                    'relevance_score': score * doc['similarity_score']
                })
                
                if len(contexts) >= max_contexts:
                    break
            
            if len(contexts) >= max_contexts:
                break
                
        # Sort contexts by relevance score
        contexts.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return contexts
    
    def get_date_ordered_events(self):
        """
        Get all events from documents ordered by date.
        
        Returns:
            list: List of events with dates, ordered chronologically
        """
        all_events = []
        
        for doc in self.document_metadata:
            doc_dates = doc['dates']
            
            for date_info in doc_dates:
                # Find the sentence containing this date
                date_text = date_info['original']
                
                for sentence in doc['sentences']:
                    if date_text in sentence:
                        all_events.append({
                            'date': date_info['datetime'],
                            'normalized_date': date_info['normalized'],
                            'has_year': date_info['has_year'],
                            'event_text': sentence,
                            'document_name': doc['name']
                        })
        
        # Sort events by date
        all_events.sort(key=lambda x: x['date'])
        
        return all_events
