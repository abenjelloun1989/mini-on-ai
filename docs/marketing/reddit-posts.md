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
I made 25 prompts that fix weak resume bullets to pass ATS filters — sharing 4 inline, full pack free

---

**Body:**

Job hunting tip that actually moved the needle for me: stop rewriting your bullets from memory and start using the job description as the rewrite brief.

ATS systems are essentially keyword matchers. If the job posting says "cross-functional stakeholder alignment" and your resume says "worked with teams", you get filtered before a human ever sees it.

Here are 4 prompts I use. Paste them directly into ChatGPT or Claude:

**1. Core bullet rewriter from job description**
```
I need you to rewrite my resume bullets to be ATS-optimized for a specific job posting. Here is the job description:

[PASTE FULL JOB DESCRIPTION HERE]

Here are my current resume bullets:
[PASTE YOUR CURRENT BULLETS HERE]

Please rewrite each bullet by: (1) incorporating exact keywords and phrases from the job description, (2) adding measurable metrics where I can insert them (use placeholders like [X%] or [$ amount] where I need to fill in numbers), (3) starting each bullet with a strong action verb that matches the job description's language, (4) keeping each bullet under 2 lines, and (5) prioritizing the top skills and requirements mentioned in the job posting.
```

**2. Keyword gap analyzer**
```
Before I rewrite my resume, I need to identify the keyword gaps between my current resume and this job description.

Job Description: [PASTE JOB DESCRIPTION]
My Current Resume: [PASTE RESUME TEXT]

Extract the top 20 keywords from the JD, identify which are missing from my resume, flag which are likely ATS eliminators, and suggest where to insert each one naturally. Format as a table: Keyword | Found in Resume | Priority | Suggested Placement.
```

**3. Single weak bullet transformer**
```
Transform this single weak resume bullet into 3 ATS-optimized versions tailored to the job description below.

Job Description: [PASTE JD]
Weak Bullet: [PASTE YOUR BULLET]

For each version: use a different strong action verb, incorporate JD keywords, include a metric placeholder, and vary the structure. After the 3 versions, explain in one sentence what makes each stronger.
```

**4. Metric injection specialist**
```
My resume bullets lack measurable results. For each bullet below: (1) rewrite it with a metric placeholder in the most logical position, (2) ask me one specific question to help me find the real number.

Job Description: [PASTE JD]
My Bullets: [PASTE BULLETS]

Format: Original → Rewritten Bullet → Question to Find Your Metric.
```

I packaged 25 of these (covering career changers, executive summaries, skills sections, cover letter matching, etc.) into a pay-what-you-want pack if anyone wants the full set: https://minionai.gumroad.com/l/hromk

Drop a weak bullet in the comments and I'll run it through prompt #3 for you.

---

## Notes
- Reply to every comment within the first hour for algorithm boost
- For r/ChatGPT post: if someone drops a bullet in comments, run it through prompt 3 and reply with the rewrite — that engagement drives the post up
- For r/ClaudeAI post: if someone asks about other skill types, offer to build one and mention the pack
