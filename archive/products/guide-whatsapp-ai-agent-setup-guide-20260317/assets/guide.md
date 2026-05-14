# WhatsApp AI Agent Setup Guide

## Overview
This guide is for developers and technical founders who want to deploy a WhatsApp-connected AI agent that responds on their behalf using their personal communication style. By the end, you'll have a working pipeline that ingests your chat history, fine-tunes response behavior, and handles automated replies through the WhatsApp Business API.

---

## 1. Export and Prepare Your Conversation Data

Your chat history is the training foundation. Quality here directly determines how convincing the agent sounds.

- Export WhatsApp chats via **Settings → Chats → Export Chat** (without media). A typical active contact yields 500–2,000 messages — aim for at least 300 messages from your side per relationship type (professional, personal, client).
- Parse exported `.txt` files to isolate only your messages. Strip timestamps and contact names, leaving clean utterance pairs: `[Received]: "Can we meet Friday?" → [Sent]: "Friday works, 3pm?"`.
- Categorize conversations by context: **scheduling**, **project updates**, **casual check-ins**, **decline/redirect**. This lets you weight the agent's behavior per scenario later.

---

## 2. Connect to WhatsApp Business API

You need a verified Business API account — not the standard app — to send and receive programmatic messages.

- Use **Meta's Cloud API** (free tier supports ~1,000 conversations/month) or a middleware provider like **360dialog** or **Twilio** if you need faster onboarding. Cloud API requires Facebook Business Manager verification, which takes 2–5 business days.
- Set up a webhook endpoint (e.g., a FastAPI or Express server) that receives POST events. Your payload will include `messages[0].text.body` for the inbound message and the sender's `wa_id` for routing replies.
- Test with Meta's **Graph API Explorer** first: send a template message to your own number before wiring in the AI layer. Confirm round-trip latency — target under 3 seconds for a natural feel.

---

## 3. Build the Style-Matching Prompt Layer

Raw GPT-4 or Claude responses sound generic. Your prompt engineering is what makes the agent sound like *you*.

- Create a **persona block** at the top of your system prompt: include your average message length (e.g., "Responses are typically 1–2 sentences"), punctuation habits (no Oxford commas, uses em dashes), and common phrases you actually use ("Let me loop back on this," "Makes sense to me").
- Include 8–12 few-shot examples drawn directly from your exported history. Format them as `User: [incoming] / Assistant: [your actual reply]`. This dramatically outperforms general instruction prompting for style mimicry.
- Add a **constraint block**: define what the agent should never do — apologize excessively, use filler phrases like "Certainly!", or make commitments about dates and money without flagging for your review.

---

## 4. Implement a Context Memory System

WhatsApp threads are ongoing relationships. The agent needs memory beyond a single conversation window.

- Store per-contact conversation summaries in a lightweight database (SQLite works fine at small scale; switch to Postgres when you exceed 500 active contacts). On each new message, retrieve the last summary + the last 5 message pairs to inject into the prompt as context.
- Use a **rolling summary pattern**: after every 10 exchanges, ask the LLM to compress the thread into a 3-sentence summary and overwrite the stored version. This keeps token usage predictable — typically 400–600 tokens of context per conversation.
- Tag contacts with relationship metadata: `{"type": "client", "project": "rebrand", "status": "active"}`. Inject this into the system prompt so the agent adjusts formality and topic awareness automatically.

---

## 5. Set Up Human-in-the-Loop Escalation

Fully autonomous responses will eventually misfire. Build the escape hatch before you need it.

- Define trigger rules that pause the agent and notify you directly: questions containing keywords like "contract," "invoice," "urgent," or "legal"; messages from contacts tagged as `tier: high-value`; or any message the model returns with a confidence score below your threshold.
- Route escalations to a **Slack or Telegram notification** with the original message and the agent's draft reply. You approve, edit, or override — then the approved response sends. Use n8n or Make (formerly Integromat) to wire this without custom code.
- Set a **response delay** of 60–180 seconds on all automated replies. Instant responses feel bot-like and remove urgency signaling that humans naturally use.

---

## 6. Monitor, Iterate, and Tune

Your first deployment will be rough. Build feedback loops from day one.

- Log every inbound/outbound pair with a timestamp and contact ID. After one week, manually review 20–30 responses and score them: **on-brand / acceptable / misfire**. Misfires reveal gaps in your few-shot examples or missing constraint rules.
- Track your **escalation rate** — if it exceeds 15%, your trigger rules are too conservative; below 3%, they're probably too loose and you're missing edge cases.
- Re-export and refresh your persona examples every 60–90 days. Communication style drifts over time, and stale training data is the most common reason agents start sounding "off."

---

## Quick-Reference Summary

- **Data first**: Export and clean 300+ of your own messages per context type before touching any API
- **Cloud API** is the fastest path to WhatsApp integration; verify your Business Manager account early
- **Persona prompts + few-shot examples** beat generic instructions for style accuracy
- **Rolling summaries** keep memory costs predictable — store summaries, not full transcripts
- **Always build escalation** before going live; high-value contacts should never be fully autonomous
- **60–180 second send delay** is a simple, high-impact tweak for natural-feeling responses
- Review 20–30 logged responses weekly; target escalation rate of 5–10% as a healthy baseline