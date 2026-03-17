# Instagram Messaging API Setup Guide

This guide is for developers integrating Instagram's Messaging API into n8n workflows who are hitting error #3 or permission-related failures. You'll learn how to correctly configure app capabilities, scope permissions, and authenticate so your workflows actually run without silent failures or blocked requests.

---

## 1. Understanding Error #3 in Context

Error #3 (`OAuthException`) typically means your app lacks the capability or permission to perform the requested action — not that your token is invalid. The error message "Unsupported request" often masks the real cause: missing `instagram_manage_messages` permission or the Instagram messaging capability not being enabled at the app level.

**Key distinctions:**
- Error #3 ≠ expired token. A valid token can still throw error #3 if scopes were granted before the capability was enabled.
- If your token predates your capability setup, it won't inherit new permissions — you must re-authenticate.
- Check `developers.facebook.com/tools/explorer` to confirm which scopes are actually attached to your current token, not which ones you *think* you requested.

---

## 2. Enabling Instagram Messaging Capability in Meta App Dashboard

Before any token or scope configuration matters, the capability must be active at the app level. This is a separate toggle from permissions and is missed more often than you'd expect.

**Steps to verify and enable:**
- Navigate to **App Dashboard → Add a Product → Messenger**, then separately check **Instagram → Settings → Instagram Messaging**. Both may need to be active depending on your integration type.
- In the Instagram product section, confirm "Allow Instagram users and Page-backed Instagram accounts to message your app" is toggled **on** — this is disabled by default on new apps.
- For apps still in Development mode, messaging is restricted to app roles (admins, developers, testers). Add your test account explicitly under **Roles → Test Users** or you'll get error #3 even with correct permissions.

---

## 3. Requesting the Right Permission Scopes

The `instagram_manage_messages` permission is required and must be explicitly requested during OAuth. Requesting `pages_messaging` alone is insufficient for Instagram Direct — a common misconfiguration.

**Scope configuration checklist:**
- Required minimum scopes: `instagram_manage_messages`, `instagram_basic`, `pages_show_list`, `pages_read_engagement`. Missing any one of these breaks the chain.
- In n8n's Instagram node or HTTP Request node, set the OAuth2 credential scope field to: `instagram_basic,instagram_manage_messages,pages_show_list,pages_read_engagement` — comma-separated, no spaces.
- After adding `instagram_manage_messages` in the App Dashboard under **App Review → Permissions and Features**, the status must show **Approved** or **In Development** before tokens can carry it. "Not Requested" status means no token will ever include it.

---

## 4. Generating a Valid Long-Lived Page Access Token

Short-lived user tokens (1-hour expiry) are the most common cause of intermittent failures in n8n scheduled workflows. Use long-lived Page Access Tokens instead.

**Token generation workflow:**
1. Exchange your short-lived user token for a long-lived one (60-day): `GET /oauth/access_token?grant_type=fb_exchange_token&client_id={app_id}&client_secret={app_secret}&fb_exchange_token={short_token}`
2. Use that long-lived user token to fetch your Page Access Token: `GET /me/accounts?access_token={long_lived_user_token}` — the `access_token` field in the response is your permanent Page Access Token (no expiry if the app remains active).
3. In n8n, store this Page Access Token in a credential of type **Header Auth** with the key `Authorization` and value `Bearer {token}` — avoid storing it in query parameters for production workflows.

---

## 5. Wiring It Correctly in n8n

Even with valid tokens and permissions, n8n HTTP Request node configuration issues can surface as API errors.

**Practical configuration tips:**
- When calling `POST /{page_id}/messages`, set Content-Type to `application/json` explicitly in the Headers section. n8n doesn't always infer this and the API will reject malformed requests with misleading error codes.
- The recipient field requires `{"id": "IGSID"}` format where the IGSID (Instagram-Scoped User ID) comes from the webhook event — not the username or regular UID. Hardcoding a regular user ID here returns error #3.
- Enable **"Return Full Response"** in the HTTP Request node during debugging. n8n's default error display truncates the response body, hiding the specific `error_subcode` (e.g., subcode `2018109` = messaging capability not enabled) that tells you exactly what's wrong.

---

## 6. Testing Before Going to Production

**Validate your setup systematically:**
- Use Graph API Explorer with your Page Access Token to manually call `POST /{page_id}/messages` with a test IGSID before touching n8n — this isolates whether the issue is in the API config or the workflow.
- Set up a webhook in n8n using the **Webhook node** to receive `messaging` events from Instagram. Confirm you're receiving `messaging` objects (not just `message_reads`) before building send logic.
- Keep a test conversation active — Instagram's API won't let you message a user outside of a 24-hour window from their last interaction unless you use approved Message Tags.

---

## Quick-Reference Summary

- **Error #3 = capability or scope issue**, not an expired token — re-authenticate after enabling new capabilities
- Enable **Instagram Messaging toggle** in App Dashboard under Instagram product settings before anything else
- Required scopes: `instagram_basic`, `instagram_manage_messages`, `pages_show_list`, `pages_read_engagement`
- Use **long-lived Page Access Tokens** (permanent) not user tokens (1-hour) for scheduled n8n workflows
- Recipients need **IGSID format** from webhook events — regular user IDs will fail silently with error #3
- Always test via **Graph API Explorer first**, then replicate in n8n to isolate the failure layer