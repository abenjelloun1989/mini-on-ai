# N8n Customer Dashboard ROI Template

A ready-to-deploy n8n workflow template that automatically calculates and visualizes time saved, cost savings, and ROI metrics for customers, eliminating the manual dashboard creation struggle.

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

1. Step 1: Configure N8n API Access - In the 'Fetch Workflow Executions' node, replace 'YOUR_N8N_INSTANCE' with your actual n8n instance URL (e.g., https://myinstance.app.n8n.cloud) and replace 'YOUR_N8N_API_KEY' with an API key generated from your n8n instance Settings > API.
2. Step 2: Set Up Google Sheets Credential - Go to n8n Credentials > New > Google Sheets OAuth2 API. Complete the OAuth flow, then replace 'YOUR_GOOGLE_SHEETS_CREDENTIAL_ID' in the 'Update Google Sheet' node with your credential ID.
3. Step 3: Create Google Sheet - Create a new Google Sheet with a tab named 'ROI Dashboard'. Add headers: Report Week, Report Date, Total Executions, Time Saved (Hours), Weekly Cost Savings ($), Monthly Cost Savings ($), Annual Cost Savings ($), Annual N8n Cost ($), Net Annual Savings ($), ROI (%). Replace 'YOUR_GOOGLE_SHEET_ID' in the node parameters and email HTML with the ID from your Google Sheet URL.
4. Step 4: Configure Slack Integration - Go to n8n Credentials > New > Slack API. Add your Slack Bot Token (starts with xoxb-). Replace 'YOUR_SLACK_CREDENTIAL_ID' in the 'Send Slack Notification' node. Update '#automation-roi' to your preferred Slack channel name.
5. Step 5: Configure SMTP Email Credentials - Go to n8n Credentials > New > SMTP. Enter your email provider's SMTP host, port, username, and password. Replace 'YOUR_SMTP_CREDENTIAL_ID' in the 'Send Email Report' node.
6. Step 6: Update Email Addresses - In the 'Send Email Report' node, replace 'your-email@example.com' with the sender address and 'client@example.com' with the recipient(s) who should receive the weekly ROI report.
7. Step 7: Customize ROI Parameters - In the 'Calculate ROI Metrics' Code node, update HOURLY_RATE (default $50/hr), AVG_MANUAL_MINUTES_PER_TASK (default 30 min), and MONTHLY_N8N_COST (default $20/mo) to match your actual values for accurate ROI calculations.
8. Step 8: Adjust Schedule - In the 'Schedule Trigger' node, modify the schedule to suit your reporting cadence. Default is every Monday at 8:00 AM. You can change to daily, bi-weekly, or monthly as needed.
9. Step 9: Test the Workflow - Before activating, click 'Execute Workflow' manually to verify all nodes run successfully. Check that data appears in your Google Sheet and notifications are sent to Slack and email.
10. Step 10: Activate the Workflow - Once all credentials are configured and testing is successful, toggle the workflow to Active using the switch in the top-right corner of the workflow editor. The ROI dashboard will now auto-update on your defined schedule.

## Requirements

- n8n (self-hosted or n8n.cloud)
- Relevant credentials configured in n8n (see setup steps above)

## Files

- `workflow.json` — Importable n8n workflow
- `README.md` — This file
