# Multi-Agent API Integration Blueprint

Pre-built n8n workflows that eliminate API plumbing work by providing ready-to-use connections, auth handling, and glue code for common multi-agent tool integrations.

## What's included

- Ready-to-import n8n workflow (`workflow.json`)
- 10 connected nodes
- Setup instructions for credentials and configuration

## How to import

1. Open your n8n instance
2. Go to **Workflows** → **Import from file**
3. Select `workflow.json`
4. Follow the setup steps below

## Setup

1. Step 1: Import this JSON into n8n via Settings > Import Workflow.
2. Step 2: Configure OpenAI credentials — replace 'YOUR_OPENAI_API_KEY' in the 'Call OpenAI Agent' node's Authorization header with your actual OpenAI API key.
3. Step 3: Configure Slack credentials — go to the 'Post to Slack Agent' node, create or select a Slack API credential with a valid Bot Token, and replace 'YOUR_WORKSPACE' with your Slack workspace name.
4. Step 4: Update the Slack channel in 'Post to Slack Agent' — replace '#agent-notifications' with your target Slack channel name.
5. Step 5: Configure Google Sheets credentials — go to the 'Log to Google Sheets' node, create an OAuth2 credential for Google Sheets, and replace 'YOUR_GOOGLE_SHEET_ID' with your actual Google Spreadsheet ID.
6. Step 6: Ensure the Google Sheet has a tab named 'AgentLogs' with columns: RequestID, AgentName, Task, APITarget, Timestamp, Status.
7. Step 7: Configure Telegram credentials — create a Telegram Bot via @BotFather, add the token as a Telegram API credential in n8n, and replace 'YOUR_TELEGRAM_CHAT_ID' with your target chat/group ID.
8. Step 8: For the Fallback HTTP Handler, replace 'YOUR_FALLBACK_API_KEY' with your external API's bearer token, and update the URL pattern 'https://api.example.com/agents/...' to match your actual API endpoint.
9. Step 9: Test the webhook by sending a POST request to your n8n webhook URL (e.g., https://your-n8n-instance.com/webhook/multi-agent-trigger) with a JSON body like: {"agent_name": "test-agent", "task": "Summarize today's news", "api_target": "openai", "payload": {}}.
10. Step 10: Activate the workflow by toggling the Active switch once all credentials are configured and tested successfully.

## Requirements

- n8n (self-hosted or n8n.cloud)
- Relevant credentials configured in n8n (see setup steps above)

## Files

- `workflow.json` — Importable n8n workflow
- `README.md` — This file
