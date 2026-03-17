# N8N SMS Filter Unknown Contacts Workflow

A ready-to-use n8n workflow template that filters incoming calls to identify unknown/unsaved contacts and sends SMS notifications only to numbers not in Google Contacts, eliminating manual exclusion lists.

## What's included

- Ready-to-import n8n workflow (`workflow.json`)
- 9 connected nodes
- Setup instructions for credentials and configuration

## How to import

1. Open your n8n instance
2. Go to **Workflows** → **Import from file**
3. Select `workflow.json`
4. Follow the setup steps below

## Setup

1. Step 1: Import this workflow JSON into your n8n instance via Settings > Import Workflow.
2. Step 2: Configure Google OAuth2 credentials — go to Credentials > New > Google OAuth2 API. Enable the 'People API' and 'Google Sheets API' in your Google Cloud Console project. Set the credential name to 'Google OAuth2 API'.
3. Step 3: Configure Google Sheets OAuth2 credentials — create a separate credential named 'Google Sheets OAuth2' or reuse the same Google OAuth2 credential scoped to Sheets. Ensure 'Google Sheets API' is enabled.
4. Step 4: Set up Twilio credentials — go to Credentials > New > HTTP Basic Auth. Set the username to your Twilio Account SID and password to your Twilio Auth Token. Name the credential 'Twilio Basic Auth'.
5. Step 5: In the 'Send SMS Notification' node, replace 'YOUR_TWILIO_ACCOUNT_SID' in the URL with your actual Twilio Account SID (format: ACxxxxxxxxxxxxxxxxx).
6. Step 6: In the 'Send SMS Notification' node, replace 'YOUR_PERSONAL_PHONE_NUMBER' with the phone number where you want to receive unknown caller SMS alerts (E.164 format, e.g., +15551234567).
7. Step 7: In the 'Send SMS Notification' node, replace 'YOUR_TWILIO_PHONE_NUMBER' with your Twilio purchased phone number in E.164 format (e.g., +15559876543).
8. Step 8: Create a Google Sheet with two tabs named 'Unknown Callers' and 'Known Callers'. Add headers: Caller Number, Timestamp, Call SID, SMS Sent, Contacts Checked. Copy the Google Sheet ID from the URL (the long string between /d/ and /edit) and replace 'YOUR_GOOGLE_SHEET_ID' in both Google Sheets nodes.
9. Step 9: Set up Telegram Bot credentials — create a new bot via @BotFather on Telegram to get a bot token. In n8n, go to Credentials > New > Telegram API and enter your bot token. Name it 'Telegram Bot API'.
10. Step 10: Replace 'YOUR_TELEGRAM_CHAT_ID' in the 'Notify via Telegram' node with your actual Telegram chat ID. You can find this by messaging @userinfobot on Telegram or using the getUpdates API endpoint.
11. Step 11: Configure your telephony provider (e.g., Twilio, Vonage, or a PBX system) to send a POST webhook to your n8n webhook URL when a call is received. The webhook URL will be: https://YOUR_N8N_HOST/webhook/incoming-call
12. Step 12: Ensure your telephony provider sends the caller number in the request body as 'From', 'caller_number', or 'phone' field. Adjust the 'Extract Caller Number' node expression if your provider uses a different field name.
13. Step 13: Test the workflow by clicking 'Test Workflow' in n8n and sending a test POST request to the webhook URL with a sample caller number. Verify Google Contacts lookup returns results and the IF condition branches correctly.
14. Step 14: Once tested successfully, toggle the workflow to 'Active' using the toggle switch at the top of the workflow editor to enable live processing of incoming calls.
15. Step 15: Monitor the Google Sheets log regularly to review unknown caller patterns. Consider adding a periodic cleanup or summary email workflow to aggregate weekly unknown caller reports.

## Requirements

- n8n (self-hosted or n8n.cloud)
- Relevant credentials configured in n8n (see setup steps above)

## Files

- `workflow.json` — Importable n8n workflow
- `README.md` — This file
