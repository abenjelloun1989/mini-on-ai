# mini-on-ai

An AI-powered digital product factory running on a Mac mini. It automatically generates, packages, and publishes free prompt packs and digital resources — no manual work required.

**Live site:** [mini-on-ai](https://abenjelloun1989.github.io/mini-on-ai)

## How it works

1. Scans for trending topics and generates product ideas
2. Ranks ideas and picks the best one
3. Uses Claude AI to generate a full prompt pack
4. Packages it as a downloadable zip
5. Publishes to the site and notifies via Telegram

## Stack

- Python 3 + Anthropic Claude API
- Static HTML site deployed to GitHub Pages
- Telegram bot for monitoring and control
- Runs on a Mac mini as a scheduled daily job
