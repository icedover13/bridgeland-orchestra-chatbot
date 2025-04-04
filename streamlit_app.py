import streamlit as st
import os
import pandas as pd
from datetime import datetime
import sys
import base64

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.text_processor import TextProcessor
from src.web_scraper import WebScraper
from src.data_integrator import DataIntegrator

class ChatbotApp:
    """
    Streamlit application for the chatbot that answers questions based on text files
    and the Bridgeland Orchestra website.
    """
    
    def __init__(self):
        """Initialize the chatbot application."""
        # Initialize the data integrator
        self.data_integrator = DataIntegrator()
        
        # Set up directories
        self.web_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "web")
        self.uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "uploads")
        
        # Create directories if they don't exist
        os.makedirs(self.web_data_dir, exist_ok=True)
        os.makedirs(self.uploads_dir, exist_ok=True)
        
        # Initialize session state
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = []
        
        if 'web_data_loaded' not in st.session_state:
            st.session_state.web_data_loaded = False
    
    def run(self):
        """Run the Streamlit application."""
        st.set_page_config(
            page_title="Bridgeland Orchestra Chatbot",
            page_icon="🎻",
            layout="wide"
        )
        
        st.title("Bridgeland Orchestra Chatbot")
        st.markdown("""
        This chatbot can answer questions based on uploaded text files and information from the 
        [Bridgeland Orchestra website](https://www.bridgelandorchestra.com).
        """)
        
        # Create sidebar for file uploads and data management
        with st.sidebar:
            st.header("Data Sources")
            
            # File upload section
            st.subheader("Upload Text Files")
            uploaded_files = st.file_uploader(
                "Upload text files (e.g., newsletters)",
                type=["txt"],
                accept_multiple_files=True
            )
            
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    # Check if file is already in session state
                    if uploaded_file.name not in [f['name'] for f in st.session_state.uploaded_files]:
                        # Save the file
                        file_path = os.path.join(self.uploads_dir, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Add to session state
                        st.session_state.uploaded_files.append({
                            'name': uploaded_file.name,
                            'path': file_path,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        
                        # Load into data integrator
                        self.data_integrator.add_text_file(file_path, uploaded_file.name)
                        
                        st.success(f"File uploaded: {uploaded_file.name}")
            
            # Web data section
            st.subheader("Web Data")
            if st.button("Load Bridgeland Orchestra Website Data"):
                with st.spinner("Scraping website data... This may take a minute."):
                    # Create a web scraper and crawl the website
                    scraper = WebScraper(base_url="https://www.bridgelandorchestra.com")
                    pages = scraper.crawl(max_pages=20, delay=1)
                    
                    # Save the scraped data to files
                    saved_files = scraper.save_to_files(self.web_data_dir)
                    
                    # Load the saved files into the data integrator
                    files_added = self.data_integrator.add_web_data(self.web_data_dir, "https://www.bridgelandorchestra.com")
                    
                    st.session_state.web_data_loaded = True
                    st.success(f"Loaded {files_added} pages from the Bridgeland Orchestra website")
            
            # Display loaded files
            st.subheader("Loaded Data Sources")
            
            # Display uploaded files
            if st.session_state.uploaded_files:
                st.write("Uploaded Files:")
                for file in st.session_state.uploaded_files:
                    st.write(f"- {file['name']} (uploaded {file['timestamp']})")
            
            # Display web data status
            if st.session_state.web_data_loaded:
                st.write("✅ Bridgeland Orchestra website data loaded")
            else:
                st.write("❌ Bridgeland Orchestra website data not loaded")
            
            # Clear data button
            if st.button("Clear All Data"):
                # Reset the data integrator
                self.data_integrator = DataIntegrator()
                
                # Clear session state
                st.session_state.uploaded_files = []
                st.session_state.web_data_loaded = False
                
                # Clear chat history
                st.session_state.chat_history = []
                
                st.success("All data cleared")
        
        # Main chat interface
        st.header("Chat")
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask a question about the Bridgeland Orchestra..."):
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = self.generate_response(prompt)
                    st.markdown(response)
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    def generate_response(self, query):
        """
        Generate a response to the user's query based on the loaded data.
        
        Args:
            query (str): User's query
            
        Returns:
            str: Response to the query
        """
        # Use the data integrator to generate a response
        response_data = self.data_integrator.get_response(query, include_additional_info=True)
        
        # Return the answer text
        return response_data['answer']

def main():
    app = ChatbotApp()
    app.run()

if __name__ == "__main__":
    main()
