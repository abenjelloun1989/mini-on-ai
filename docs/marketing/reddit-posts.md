# Reddit Posts — Ready to Publish

> Post after account is 3-4 days old with ~10 comment karma.
> Never post both on the same day — space them 2-3 days apart.
> Reply to every comment within the first hour for algorithm boost.

---

## Post 1 — r/ClaudeAI
**Status:** Ready (product set to pay-what-you-want on Gumroad)
**Product:** Claude Code Skills Pack: Codebase Onboarding Docs
**Gumroad URL:** https://minionai.gumroad.com/l/vpqbfs

**Title:**
I made 5 Claude Code skills for codebase onboarding — sharing one inline, free pack in comments

---

**Body:**

Onboarding a new engineer always takes longer than it should. The architecture docs are stale, nobody knows who to ask about the auth middleware, and the "just read the code" answer doesn't scale.

I spent some time writing Claude Code skills specifically for onboarding documentation — skills that actually read your codebase and produce grounded docs instead of generic templates.

Here's one of them inline (drop this in your `~/.claude/skills/` folder):

```
---
name: architecture-overview
trigger: /gen-architecture
description: >
  Analyzes the codebase structure and generates a high-level architecture
  overview document covering system components, data flow, service boundaries,
  and technology stack decisions. Designed for engineering leads onboarding
  new hires who need a mental map of the system before diving into code.
when_to_use: >
  Use this skill when a new engineer joins the team and needs to understand
  how the system fits together, when preparing for a design review, or when
  existing architecture documentation is stale or missing entirely.
---
```

Run `/gen-architecture` and Claude reads your actual repo — dependency manifests, Dockerfiles, route files, service configs — and writes a full architecture overview doc. No hallucinated tech stack, every claim grounded in a real file.

The full pack has 5 skills covering architecture overview, module dependency map, environment setup guide, design decisions explainer, and contributor guide.

Pay-what-you-want if you want the full set: https://minionai.gumroad.com/l/vpqbfs

Happy to answer questions or take requests for other skill types.

---

## Post 2 — r/ChatGPT
**Status:** Ready (product set to pay-what-you-want on Gumroad)
**Product:** ATS-Optimized Resume Bullet Rewriter
**Gumroad URL:** https://minionai.gumroad.com/l/hromk

**Title:**
I made 25 prompts that rewrite resume bullets to pass ATS filters — free

---

**Body:**

ATS systems just match keywords. If the job posting says "cross-functional stakeholder alignment" and your resume says "worked with teams", you get filtered before a human ever reads it.

The fix is using the job description as the rewrite brief. Paste your bullets and the JD, and you get back versions that mirror the exact language they're scanning for. I wrote 25 prompts covering different cases: keyword gap analysis, metric injection, career changers, executive summaries, cover letters.

Works with ChatGPT or Claude. Free here: https://mini-on-ai.com/products/prompts-ats-optimized-resume-bullet-rewriter-by--20260312.html

I've been making other free tools like this, you can find them at https://mini-on-ai.com if you're curious. Happy to take feedback.

---

## Post 3 — r/n8n
**Status:** Ready
**Product:** Multi-Agent API Integration Blueprint (10 n8n workflow templates)
**Site:** https://mini-on-ai.com

**Title:**
I got tired of rewriting the same API auth boilerplate for every n8n multi-agent project — made 10 templates, free

---

**Body:**

Every multi-agent project I build in n8n starts the same way: 30–60 minutes of plumbing before any actual logic — API key passing, OAuth token refresh, error propagation between agents, retry handling. None of it is hard, it's just always the same work.

I packaged the connection patterns I reuse most into 10 ready-to-import n8n workflow templates: auth handling for the common APIs (OpenAI, Anthropic, Perplexity, Serper, etc.), agent-to-agent data passing, error routing, and credential isolation so sub-agents don't inherit permissions they shouldn't have.

Nothing exotic — just the boilerplate so you can skip straight to the part that's actually specific to your project.

Free to grab at https://mini-on-ai.com

---

## Post 4 — r/productivity
**Status:** Ready
**Product:** Meeting Notes to Action Items Fast
**Site:** https://mini-on-ai.com

**Title:**
I made a set of prompts that turn raw meeting notes into clean action items in under a minute — free

---

**Body:**

The pattern in most teams: someone takes notes during the meeting, they sit in a doc for a week, nobody follows up. The notes exist but extracting "who owns what by when" takes more effort than it should, so it doesn't happen.

I wrote a small set of prompts for this. Paste your raw notes — even the messy, stream-of-consciousness kind — and it pulls out every action item, assigns an owner if one was named, adds a due date if one was mentioned, and flags anything that was left unresolved. Output is a clean list you can drop straight into Notion, Linear, or just reply-all.

Works with ChatGPT, Claude, or any LLM. Free at https://mini-on-ai.com

---

## Post 5 — r/freelance
**Status:** Ready
**Product:** AI Usage & Service Pricing Strategy Guide
**Site:** https://mini-on-ai.com

**Title:**
How do you charge clients for AI costs in your projects? I wrote up the pricing models that actually work for automation freelancers

---

**Body:**

This comes up constantly in automation freelancing: you build an n8n workflow that hits the OpenAI API a few hundred times per day for a client. Do you absorb the token cost? Pass it through at cost? Mark it up? Wrap it into a monthly retainer?

There's no obvious right answer and getting it wrong either eats your margin or kills the deal. I spent time mapping out the models that actually work — flat development fee + usage passthrough, service tiers with AI included, cost-plus with a buffer, and managed service pricing where you own the infrastructure. Each one has a different risk profile depending on how predictable the client's usage is.

Wrote it up as a short guide. Free at https://mini-on-ai.com

---

## Notes
- Reply to every comment within the first hour for algorithm boost
- For r/ChatGPT post: if someone drops a bullet in comments, run it through prompt 3 and reply with the rewrite — that engagement drives the post up
- For r/ClaudeAI post: if someone asks about other skill types, offer to build one and mention the pack
- For r/n8n post: if someone asks which APIs are covered, name 3-4 specifically (OpenAI, Anthropic, Serper, Perplexity)
- For r/productivity post: if someone asks for an example, offer to run their notes through it in the comments
- For r/freelance post: open with a question to invite discussion — the post title itself is question-framed, lean into that
