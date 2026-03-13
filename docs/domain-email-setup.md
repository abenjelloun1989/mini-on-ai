# Domain + Email Setup Guide

Last updated: 2026-03-13

## Domain: mini-on-ai.com

### Step 1 — Buy the domain

Go to **Namecheap** (namecheap.com) — best price + free WhoisGuard privacy:

1. Search `mini-on-ai.com` → add to cart
2. **Uncheck** all upsells (hosting, SSL, etc.)
3. Enable **WhoisGuard** (free, protects your personal info)
4. Complete purchase (~$12/year)

### Step 2 — Point domain to GitHub Pages

In Namecheap → Domain List → mini-on-ai.com → **Manage** → **Advanced DNS**

Delete any existing A records or CNAME for `@`, then add:

| Type  | Host | Value                    | TTL  |
|-------|------|--------------------------|------|
| A     | @    | 185.199.108.153          | Auto |
| A     | @    | 185.199.109.153          | Auto |
| A     | @    | 185.199.110.153          | Auto |
| A     | @    | 185.199.111.153          | Auto |
| CNAME | www  | abenjelloun1989.github.io | Auto |

### Step 3 — Configure GitHub Pages

1. Go to https://github.com/abenjelloun1989/mini-on-ai/settings/pages
2. Under **Custom domain** → type `mini-on-ai.com` → Save
3. Wait ~5 minutes for DNS propagation
4. Check **Enforce HTTPS** (appears once DNS is confirmed)

> ✅ The repo already has `site/CNAME` containing `mini-on-ai.com` — GitHub Pages will pick this up automatically.

### DNS propagation time

Full propagation: up to 48 hours, usually 15–30 minutes.
Check at: https://dnschecker.org/#A/mini-on-ai.com

---

## Email: hello@mini-on-ai.com

### Option A — Zoho Mail (Recommended, free)

Zoho gives you 5 free mailboxes with your own domain.

1. Go to **zoho.com/mail** → **Add your domain** → enter `mini-on-ai.com`
2. Verify domain ownership (Zoho gives you a TXT record to add in Namecheap)
3. Add MX records in Namecheap **Advanced DNS**:

| Type | Host | Value                        | Priority | TTL  |
|------|------|------------------------------|----------|------|
| MX   | @    | mx.zoho.com                  | 10       | Auto |
| MX   | @    | mx2.zoho.com                 | 20       | Auto |
| MX   | @    | mx3.zoho.com                 | 50       | Auto |
| TXT  | @    | (paste verification code from Zoho) | — | Auto |

4. Create mailbox: `hello` → set a password
5. Done — access at **mail.zoho.com**

### Option B — Cloudflare Email Routing (free, forward-only)

If you only want to **receive** email at hello@mini-on-ai.com and read it in Gmail:

1. Move DNS to Cloudflare (free) → enable Email Routing
2. hello@mini-on-ai.com → forwards to your Gmail
3. Can reply "from" hello@mini-on-ai.com via Gmail SMTP (extra setup)

**Recommendation: Use Zoho** — you get a real inbox, works with any email app,
and it's free forever for your use case.

---

## Order of operations

```
Day 1:
  1. Buy mini-on-ai.com on Namecheap (5 min)
  2. Add A records + CNAME for GitHub Pages (5 min)
  3. Set custom domain in GitHub Pages (2 min)
  4. Start Zoho Mail setup + add MX records (10 min)

Day 1–2:
  - Wait for DNS to propagate
  - Check https://mini-on-ai.com works

Day 2:
  5. Finish Zoho mailbox creation
  6. Test: send an email to hello@mini-on-ai.com

Done.
```

## Estimated cost

| Item              | Cost       |
|-------------------|------------|
| mini-on-ai.com    | ~$12/year  |
| Zoho Mail (free)  | $0/year    |
| GitHub Pages      | $0/year    |
| **Total**         | **~$1/month** |
