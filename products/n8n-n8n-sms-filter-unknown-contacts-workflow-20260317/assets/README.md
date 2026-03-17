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
2. Step 2: Set up Google OAuth2 credentials in n8n (Credentials > New > Google OAuth2 API) with scopes for Google Contacts (https://www.googleapis.com/auth/contacts.readonly) and authenticate with your Google account.
3. Step 3: Set up Google Sheets OAuth2 credentials in n8n (Credentials > New > Google Sheets OAuth2 API) using the same or a separate Google account with Sheets access.
4. Step 4: Create a Twilio account at https://www.twilio.com, get your Account SID and Auth Token, and configure HTTP Basic Auth credentials in n8n with Username = YOUR_TWILIO_ACCOUNT_SID and Password = YOUR_TWILIO_AUTH_TOKEN.
5. Step 5: In the 'Send SMS Notification' node, replace YOUR_TWILIO_ACCOUNT_SID in the URL with your actual Twilio Account SID.
6. Step 6: In the 'Send SMS Notification' node, replace YOUR_NOTIFICATION_PHONE_NUMBER with the phone number you want to receive unknown caller SMS alerts (in E.164 format, e.g. +11234567890).
7. Step 7: In the 'Send SMS Notification' node, replace YOUR_TWILIO_PHONE_NUMBER with your Twilio purchased phone number (in E.164 format).
8. Step 8: Create a Google Sheet with two tabs named 'Unknown Callers' and 'Known Callers'. Add headers: Timestamp, Phone Number, Contact Name (Known tab only), Call SID, Status, SMS Sent. Copy the Sheet ID from the URL (the long string between /d/ and /edit) and replace YOUR_GOOGLE_SHEET_ID in both Google Sheets nodes.
9. Step 9: Set up a Telegram Bot by messaging @BotFather on Telegram, create a new bot, and copy the API token. Add Telegram API credentials in n8n. Then get your personal or group Chat ID (use @userinfobot or the Telegram API) and replace YOUR_TELEGRAM_CHAT_ID in the 'Send Telegram Alert' node.
10. Step 10: Configure your call provider (e.g., Twilio, Vonage, or phone system) to send a POST webhook to the n8n webhook URL when a call is received. The webhook URL will be shown in the 'Incoming Call Webhook' node after activation. Ensure the payload includes a 'From' or 'caller_number' field with the caller's phone number.
11. Step 11: Test the workflow by clicking 'Test Webhook' in n8n and sending a sample POST request with a phone number payload: {"body": {"From": "+11234567890", "CallSid": "TEST123"}}.
12. Step 12: Verify that numbers in your Google Contacts are correctly identified as known, and unknown numbers trigger an SMS and Telegram notification.
13. Step 13: Once testing is complete, activate the workflow by toggling the 'Active' switch in n8n to enable live call filtering.

## Requirements

- n8n (self-hosted or n8n.cloud)
- Relevant credentials configured in n8n (see setup steps above)

## Files

- `workflow.json` — Importable n8n workflow
- `README.md` — This file
