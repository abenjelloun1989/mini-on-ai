# Skill: telegram-report

## Purpose
Send a concise pipeline run summary to a Telegram chat.

## Inputs
- Latest entry from `data/pipeline-log.json`

## Outputs
- Telegram message sent to configured chat

## Message Format

### Success
```
✅ New product published

📦 {title}
{description}

🔗 {site_url}/products/{id}.html
🕐 Completed in {duration}s
```

### Failure
```
❌ Pipeline failed at stage: {stage}

Error: {error_message}
Product: {title or "none"}
🕐 {timestamp}
```

## When to Run
- Always at the end of the pipeline (success or failure)
- Never skipped, even if upstream stages failed

## Environment Variables Required
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

## Success Criteria
- Message received in Telegram within 5 seconds
- Message contains product name on success
- Message contains stage name and error on failure
