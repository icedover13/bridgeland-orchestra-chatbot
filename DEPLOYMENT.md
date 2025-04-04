# Bridgeland Orchestra Chatbot Deployment Guide

This guide will walk you through the process of deploying the Bridgeland Orchestra Chatbot as a permanent website using Streamlit Community Cloud.

## Prerequisites

- A GitHub account (free)
- A Streamlit Community Cloud account (free)

## Step 1: Create a GitHub Repository

1. Go to [GitHub](https://github.com) and sign in to your account
2. Click on the "+" icon in the top right corner and select "New repository"
3. Name your repository (e.g., "bridgeland-orchestra-chatbot")
4. Make sure the repository is set to "Public" (required for free Streamlit deployment)
5. Click "Create repository"
6. Follow the instructions on the next page to push an existing repository from the command line:

```bash
git remote add origin https://github.com/YOUR-USERNAME/bridgeland-orchestra-chatbot.git
git push -u origin main
```

## Step 2: Deploy to Streamlit Community Cloud

1. Go to [Streamlit Community Cloud](https://streamlit.io/cloud) and sign in with your GitHub account
2. Click "New app"
3. Select your repository, branch (main), and set the main file path to `streamlit_app.py`
4. Click "Deploy"
5. Wait for the deployment to complete (this may take a few minutes)

## Step 3: Access Your Deployed Chatbot

Once the deployment is complete, you'll receive a permanent URL for your chatbot (e.g., https://bridgeland-orchestra-chatbot.streamlit.app).

This URL will remain active as long as your GitHub repository exists, and the service is completely free with no credit limitations.

## Step 4: Updating Your Chatbot

To update your chatbot in the future:

1. Make changes to your local code
2. Commit and push the changes to GitHub:

```bash
git add .
git commit -m "Description of changes"
git push
```

3. Streamlit Community Cloud will automatically detect the changes and redeploy your application

## Troubleshooting

If you encounter any issues during deployment:

1. Check the deployment logs in Streamlit Community Cloud
2. Ensure all dependencies are listed in `requirements.txt`
3. Verify that the `streamlit_app.py` file is in the root directory of your repository

For more information, visit the [Streamlit Community Cloud documentation](https://docs.streamlit.io/streamlit-community-cloud).
