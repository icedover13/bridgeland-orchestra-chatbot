# Bridgeland Orchestra Chatbot

A chatbot that can answer questions based on text files and the Bridgeland Orchestra website content.

## Features

- Upload multiple text files as sources for the chatbot
- Automatically scrape and integrate content from the [Bridgeland Orchestra website](https://www.bridgelandorchestra.com)
- Process text with varying formats, especially handling dates in chronological order
- Normalize dates that may be missing month information or have odd spacing
- Provide comprehensive responses with additional relevant information
- Fallback response when specific information isn't available

## Deployment Instructions

### Option 1: Deploy to Streamlit Community Cloud (Recommended)

Streamlit Community Cloud is a free hosting service that won't run out of credits.

1. Create a GitHub repository and push this code to it
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. Go to [Streamlit Community Cloud](https://streamlit.io/cloud)

3. Sign in with your GitHub account

4. Click "New app"

5. Select your repository, branch, and set the main file path to `streamlit_app.py`

6. Click "Deploy"

7. Your app will be deployed and available at a public URL

### Option 2: Run Locally

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the Streamlit app:
   ```bash
   streamlit run streamlit_app.py
   ```

3. Open your browser and go to http://localhost:8501

## Usage Instructions

1. **Upload Text Files**: Use the sidebar to upload text files (e.g., newsletters) that will serve as knowledge sources for the chatbot.

2. **Load Website Data**: Click the "Load Bridgeland Orchestra Website Data" button to scrape and integrate content from the orchestra's website.

3. **Ask Questions**: Type your questions in the chat input at the bottom of the page.

4. **View Responses**: The chatbot will provide detailed answers based on the uploaded text files and website content.

## Project Structure

- `streamlit_app.py`: Main application file for Streamlit
- `src/text_processor.py`: Module for processing text with varying formats and normalizing dates
- `src/web_scraper.py`: Module for scraping content from the Bridgeland Orchestra website
- `src/data_integrator.py`: Module for integrating data from multiple sources
- `data/uploads/`: Directory for storing uploaded text files
- `data/web/`: Directory for storing scraped website content
- `requirements.txt`: List of Python dependencies

## Notes

- The chatbot is designed to provide additional relevant information beyond what was specifically asked
- When the chatbot doesn't have enough information, it will respond with: "I have some information on this topic, but please ask the directors for further details."
- All data is processed locally within the application; no external AI services are used
