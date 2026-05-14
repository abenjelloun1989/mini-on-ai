# Google Calendar Service Account Setup Guide

## Who This Is For

This guide is for n8n users who need server-to-server Google Calendar access without OAuth2 user consent flows — typically for automation pipelines, shared team calendars, or headless server deployments. You'll walk away with a working service account credential wired into n8n's HTTP Request node to replace the native Google Calendar connector.

---

## 1. Create the Service Account in Google Cloud Console

Navigate to **IAM & Admin → Service Accounts** in your Google Cloud project and create a new account. Give it a descriptive name like `n8n-calendar-bot` so it's identifiable in audit logs.

**Tips:**
- Assign the role **Service Account Token Creator** at creation time — you'll need it for JWT signing later.
- Generate and download a **JSON key file** immediately after creation. This is your only chance; if you lose it, you'll need to create a new key.
- Store the JSON file in a secrets manager (e.g., HashiCorp Vault, AWS Secrets Manager) rather than on disk. In n8n, paste the key contents directly into a credential field or environment variable.

---

## 2. Enable the Google Calendar API

Even with a valid service account, calls will fail with a `403 accessNotConfigured` error if the API isn't enabled for your project.

**Tips:**
- Go to **APIs & Services → Library**, search for "Google Calendar API," and click **Enable**. This takes effect within seconds, not minutes.
- If you manage multiple GCP projects, confirm you're enabling the API in the **same project** where the service account lives — a common source of phantom auth errors.
- Enable **Admin SDK API** as well if you plan to list or manage calendars across a Google Workspace domain.

---

## 3. Share the Calendar with the Service Account

Service accounts are not users — they have no inherent access to any calendar. You must explicitly share the target calendar with the service account's email address (formatted like `n8n-calendar-bot@your-project-id.iam.gserviceaccount.com`).

**Tips:**
- In Google Calendar, open **Settings → [Calendar Name] → Share with specific people**, paste the service account email, and set permission to **Make changes to events** for read/write or **See all event details** for read-only.
- For organization-wide calendar access (e.g., reading all employees' free/busy data), use **Domain-Wide Delegation** instead of manual sharing — covered in the next section.
- Test access immediately by making a simple `GET` request to `https://www.googleapis.com/calendar/v3/calendars/{calendarId}/events` before building your n8n workflow.

---

## 4. Configure Domain-Wide Delegation (Workspace Users Only)

If you're a Google Workspace admin and need the service account to act on behalf of real users, enable Domain-Wide Delegation.

**Tips:**
- In the Google Cloud Console, open the service account, click **Edit**, and check **Enable Google Workspace Domain-Wide Delegation**. Note the generated **Client ID**.
- In Google Workspace Admin Console, go to **Security → API Controls → Domain-wide Delegation → Add new** and paste the Client ID. Add the scope `https://www.googleapis.com/auth/calendar` (or `calendar.readonly` if that's sufficient).
- When generating tokens, include the `sub` claim set to the user email you're impersonating, e.g., `"sub": "jane@yourcompany.com"`. Without `sub`, the token authenticates as the service account itself, not the delegated user.

---

## 5. Generate a JWT and Exchange It for an Access Token in n8n

n8n's native Google Calendar node doesn't support service accounts, so use the **HTTP Request node** with a custom JWT flow.

**Tips:**
- Use a **Function node** before your HTTP Request to build and sign the JWT. Libraries like `jsonwebtoken` aren't available natively in n8n's sandboxed Code node, so construct the JWT manually: Base64URL-encode the header (`{"alg":"RS256","typ":"JWT"}`), the claims payload, then sign with the private key from your JSON file using the **Crypto node** or a self-hosted n8n instance with custom npm packages.
- The token endpoint is `https://oauth2.googleapis.com/token`. POST with `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer` and your signed assertion. You'll receive a Bearer token valid for **3600 seconds**.
- Cache the access token in n8n's static data (`$getWorkflowStaticData('global')`) and only refresh when within 60 seconds of expiry — this avoids hammering the token endpoint on every execution.

---

## 6. Make Authenticated Calendar API Calls

With a valid Bearer token, all standard Google Calendar REST endpoints are available.

**Tips:**
- Set the `Authorization: Bearer {access_token}` header in your HTTP Request node. For creating events, `POST` to `/calendar/v3/calendars/{calendarId}/events` with a JSON body — `calendarId` is usually the user's email or the calendar's unique ID found in Calendar Settings.
- Use `timeMin` and `timeMax` query parameters in ISO 8601 format when listing events to avoid pulling thousands of records: `timeMin=2024-01-01T00:00:00Z`.
- Handle `401 Unauthorized` responses explicitly in your workflow — set up an error branch that re-generates the token and retries the request once.

---

## Quick-Reference Summary

- **Service account email** must be explicitly shared on any calendar it needs to access.
- **JSON key file** contains your private key — treat it like a password; store it in a secrets manager.
- **Domain-Wide Delegation** is required to impersonate Workspace users; add the `sub` claim with the target email.
- **Access tokens expire in 3600 seconds** — cache them and refresh proactively.
- **Use HTTP Request node** (not the native Google Calendar node) for service account auth in n8n.
- Always **enable the Google Calendar API** in the exact GCP project where your service account lives.