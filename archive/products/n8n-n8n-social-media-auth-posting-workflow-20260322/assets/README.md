# n8n Social Media Auth & Posting Workflow

A ready-to-use n8n workflow template that handles OAuth authentication for multiple social platforms and enables users to post AI-generated images/videos without requiring app developers to store user credentials.

## What's included

- Ready-to-import n8n workflow (`workflow.json`)
- 14 connected nodes
- Setup instructions for credentials and configuration

## How to import

1. Open your n8n instance
2. Go to **Workflows** → **Import from file**
3. Select `workflow.json`
4. Follow the setup steps below

## Setup

1. Step 1: Import this workflow JSON into your n8n instance via Settings > Import Workflow.
2. Step 2: Replace 'YOUR_N8N_DOMAIN' in all redirect_uri fields with your actual n8n public domain (e.g., https://n8n.yourdomain.com).
3. Step 3: Create a Twitter Developer App at https://developer.twitter.com and replace the HTTP Basic Auth credentials on the 'Exchange Twitter Token' node with your Twitter Client ID and Client Secret.
4. Step 4: Create a Facebook/Instagram App at https://developers.facebook.com, enable Instagram Basic Display API, and replace 'YOUR_INSTAGRAM_CLIENT_ID' and 'YOUR_INSTAGRAM_CLIENT_SECRET' with your app credentials.
5. Step 5: Create a LinkedIn App at https://www.linkedin.com/developers and replace 'YOUR_LINKEDIN_CLIENT_ID' and 'YOUR_LINKEDIN_CLIENT_SECRET' with your LinkedIn OAuth credentials.
6. Step 6: Replace 'YOUR_OPENAI_API_KEY' with your OpenAI API key from https://platform.openai.com/api-keys to enable AI caption generation.
7. Step 7: Create a Google Sheet with a tab named 'UserTokens' and columns: userId, platform, accessToken, refreshToken, expiresIn, tokenSavedAt. Then replace 'YOUR_GOOGLE_SHEET_ID' with the sheet's ID from its URL.
8. Step 8: Add Google Sheets credentials in n8n (OAuth2 or Service Account) and link them to both Google Sheets nodes.
9. Step 9: Create a Telegram Bot via @BotFather, get the Bot Token, add it as a Telegram credential in n8n, and replace 'YOUR_TELEGRAM_CHAT_ID' with your Telegram chat or channel ID.
10. Step 10: To initiate OAuth for a user, redirect them to the appropriate platform's authorization URL with state parameter formatted as 'platform:userId' (e.g., state=twitter:user123) and set the redirect_uri to https://YOUR_N8N_DOMAIN/webhook/social-oauth-callback.
11. Step 11: To post content, send a POST request to https://YOUR_N8N_DOMAIN/webhook/social-post-content with JSON body: { userId, platform, topic, imageUrl (optional), tone (optional) }.
12. Step 12: Activate the workflow by toggling the 'Active' switch in n8n after all credentials have been configured and tested.

## Requirements

- n8n (self-hosted or n8n.cloud)
- Relevant credentials configured in n8n (see setup steps above)

## Files

- `workflow.json` — Importable n8n workflow
- `README.md` — This file
