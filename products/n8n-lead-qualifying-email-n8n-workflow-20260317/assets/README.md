# Lead Qualifying & Email n8n Workflow

A ready-to-use n8n workflow template that automates lead qualification and sends personalized follow-up emails, helping sales teams save time on manual lead scoring and outreach.

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

1. Step 1: Import this JSON into n8n by going to Workflows > Import from JSON and pasting this file.
2. Step 2: Configure Google Sheets credentials — go to Credentials > New > Google Sheets OAuth2 API and authenticate with your Google account.
3. Step 3: Replace 'YOUR_GOOGLE_SHEET_ID' in both Google Sheets nodes (node5 and node8) with your actual Google Spreadsheet ID (found in the sheet URL).
4. Step 4: Create two sheets in your Google Spreadsheet named 'Leads' and 'Cold Leads' with matching column headers: First Name, Last Name, Email, Company, Job Title, Company Size, Budget, Lead Score, Lead Tier, Source, Qualified At.
5. Step 5: Configure SMTP credentials — go to Credentials > New > SMTP and enter your email provider's SMTP host, port, username, and password (e.g., Gmail, SendGrid, Mailgun).
6. Step 6: Replace 'sales@yourcompany.com' in both email nodes (node6 and node9) with your actual sender email address.
7. Step 7: Configure Slack credentials — go to Credentials > New > Slack API and provide your Slack Bot Token with 'chat:write' scope enabled.
8. Step 8: Replace '#sales-leads' in the Slack node (node7) with your actual Slack channel name where lead notifications should be sent.
9. Step 9: Update the Calendly booking link in the qualified email (node6) from 'https://calendly.com/yourcompany/discovery' to your actual meeting scheduler URL.
10. Step 10: Update all resource links in the nurture email (node9) — replace '/ebook', '/webinar', and '/case-studies' URLs with your actual content URLs.
11. Step 11: Review and adjust the lead scoring thresholds in the 'Score Lead' Code node (node3) — modify company size, budget ranges, and job title keywords to match your ideal customer profile.
12. Step 12: Activate the webhook by enabling the workflow (toggle Active on). Copy the webhook URL from the 'Lead Webhook' node and paste it into your CRM, landing page form, or lead capture tool as the POST endpoint.
13. Step 13: Test the workflow by sending a test POST request to the webhook URL with a JSON body containing: firstName, lastName, email, company, jobTitle, companySize, budget, interest, and source fields.
14. Step 14: (Optional) Set up error handling by configuring an error workflow under Settings to be notified if any node fails during execution.

## Requirements

- n8n (self-hosted or n8n.cloud)
- Relevant credentials configured in n8n (see setup steps above)

## Files

- `workflow.json` — Importable n8n workflow
- `README.md` — This file
