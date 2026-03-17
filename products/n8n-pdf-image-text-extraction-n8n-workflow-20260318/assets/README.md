# PDF Image & Text Extraction n8n Workflow

A ready-to-use n8n workflow that extracts images and text from PDFs, transcodes images, merges text elements with regex-based arrays, and exports results to CSV.

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

1. Step 1: Import this JSON into n8n via Settings > Import Workflow, then open the imported workflow.
2. Step 2: Sign up at https://pdf.co and obtain your API key. Replace 'YOUR_PDFCO_API_KEY' in both 'Extract PDF Content' and 'Extract Images from PDF' nodes with your actual PDF.co API key.
3. Step 3: Sign up at https://cloudinary.com and create a free account. Replace 'YOUR_CLOUD_NAME' in the 'Transcode Images' node URL with your Cloudinary cloud name, and replace 'YOUR_UPLOAD_PRESET' with an unsigned upload preset created in your Cloudinary dashboard.
4. Step 4: Set up Google Sheets OAuth2 credentials in n8n (Settings > Credentials > New > Google Sheets OAuth2 API). Replace 'YOUR_GOOGLE_CREDENTIAL_ID' in the 'Export to Google Sheets' node and update 'YOUR_GOOGLE_SHEET_ID' with the actual Google Spreadsheet ID from the sheet URL.
5. Step 5: Create a Google Sheet named 'PDF Extractions' with the following header columns: paragraph_index, text_content, word_count, extracted_emails, extracted_urls, extracted_phones, extracted_dates, extracted_currencies, image_count, image_urls, processing_timestamp.
6. Step 6: Configure Slack credentials in n8n (Settings > Credentials > New > Slack API). Replace 'YOUR_SLACK_CREDENTIAL_ID' in the 'Send Slack Notification' node and update the channel name '#pdf-extractions' to match your desired Slack channel.
7. Step 7: Set up SMTP credentials in n8n (Settings > Credentials > New > SMTP). Replace 'YOUR_SMTP_CREDENTIAL_ID', 'your-email@example.com', and 'admin@example.com' in the 'Send Error Email' node with real email addresses and credentials.
8. Step 8: Test the webhook by sending a POST request to your n8n webhook URL (e.g., https://your-n8n-instance.com/webhook/pdf-extract) with a JSON body containing { "pdf_url": "https://example.com/sample.pdf" }.
9. Step 9: Activate the workflow by toggling the 'Active' switch in the top-right corner of the n8n workflow editor once all credentials are configured and tested.
10. Step 10: Monitor execution logs in n8n under Executions to verify that PDF text and image extraction, regex parsing, Google Sheets export, and Slack notifications are all working correctly.

## Requirements

- n8n (self-hosted or n8n.cloud)
- Relevant credentials configured in n8n (see setup steps above)

## Files

- `workflow.json` — Importable n8n workflow
- `README.md` — This file
