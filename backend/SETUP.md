# Career Coach AI Backend Setup

## Issue

The app is showing "⚠️ Something went wrong. Please try again." because the backend is missing required API keys.

## Required API Keys

You need to create a `.env` file in the `backend` folder with the following API keys:

### 1. OpenAI API Key

- **Purpose**: Powers the AI career insights
- **Get it from**: https://platform.openai.com/api-keys
- **Cost**: Pay-per-use (very affordable for testing)

### 2. News API Key

- **Purpose**: Fetches recent news about careers
- **Get it from**: https://newsapi.org/register
- **Cost**: Free tier available

### 3. Serper API Key

- **Purpose**: Searches for job outlook data
- **Get it from**: https://serper.dev/
- **Cost**: Free tier available

### 4. Reddit API Credentials

- **Purpose**: Gets community insights from Reddit
- **Get it from**: https://www.reddit.com/prefs/apps
- **Cost**: Free

## Setup Steps

1. **Create the .env file**:

   ```bash
   cd backend
   copy config_template.txt .env
   ```

2. **Edit the .env file** and replace the placeholder values with your actual API keys:

   ```
   OPENAI_API_KEY=sk-your-actual-openai-key-here
   NEWS_API_KEY=your-actual-news-api-key-here
   SERPER_API_KEY=your-actual-serper-api-key-here
   REDDIT_CLIENT_ID=your-actual-reddit-client-id-here
   REDDIT_CLIENT_SECRET=your-actual-reddit-client-secret-here
   REDDIT_USER_AGENT=your-app-name/1.0
   ```

3. **Start the backend**:

   ```bash
   cd backend
   python main.py
   ```

4. **Start the frontend** (in a new terminal):
   ```bash
   cd frontend
   npm start
   ```

## Testing

Once both servers are running:

- Backend should be at: http://localhost:8000
- Frontend should be at: http://localhost:3000
- Test the health check: http://localhost:8000/

## Troubleshooting

- If you get API key errors, make sure all keys are valid and have sufficient credits
- If the backend won't start, check that all dependencies are installed: `pip install -r requirements.txt`
- If the frontend can't connect, make sure the backend is running on port 8000
