# n8n API Authentication Troubleshooting Prompts by Auth Type

> n8n developers struggling with OAuth2, API key, and webhook authentication failures get 20 precise diagnostic prompts to identify misconfiguration, token expiry, and scope issues across third-party integrations.

---

## Prompts (20 total)

### 1. OAuth2 Token Expiry Diagnostic Checklist

**Use case:** Diagnosing sudden 401 errors in previously working OAuth2 flows

```
I am building an n8n workflow that integrates with [SERVICE NAME, e.g., Google Sheets, Salesforce, HubSpot] using OAuth2 authentication. My workflow was working previously but now returns a 401 Unauthorized error. Walk me through a step-by-step diagnostic checklist to determine if the issue is caused by token expiry, missing refresh token logic, or revoked access. For each step, explain what to check inside n8n's credential settings, what the expected value should look like, and what action to take if that step reveals the problem. Also explain how n8n handles OAuth2 token refresh automatically versus when manual intervention is required.
```

### 2. OAuth2 Scope Mismatch Root Cause Analysis

**Use case:** Resolving 403 errors caused by insufficient OAuth2 permission scopes

```
My n8n workflow is authenticated with [SERVICE NAME] via OAuth2 but certain API calls fail with a 403 Forbidden or 'insufficient permissions' error even though my credentials appear valid. I suspect a scope mismatch. Explain in detail how OAuth2 scopes work, how to identify which scopes were granted during the initial authorization versus which scopes the specific API endpoint requires, where to find the required scopes in [SERVICE NAME]'s developer documentation, and how to re-authorize the credential in n8n with the correct scopes without breaking existing workflow nodes. Include common scope-related mistakes developers make in n8n.
```

### 3. API Key Placement Troubleshooting Guide

**Use case:** Fixing API key authentication when placement method is unclear or wrong

```
I am connecting n8n to [SERVICE NAME] using an API key, but my HTTP Request node keeps returning authentication errors despite using what appears to be a valid key. The API documentation mentions the key can be passed as a header, query parameter, or in the request body. Help me diagnose which placement method is required by [SERVICE NAME], how to correctly configure each method inside n8n's HTTP Request node, common mistakes developers make when formatting the Authorization header (e.g., missing 'Bearer' prefix, incorrect capitalization of header names), and how to use n8n's built-in request inspector or external tools like Postman to verify the key is being sent correctly before debugging further inside n8n.
```

### 4. Webhook Signature Validation Failure Fix

**Use case:** Debugging HMAC webhook signature failures from third-party services

```
My n8n workflow receives webhooks from [SERVICE NAME, e.g., Stripe, GitHub, Shopify] but the webhook trigger node is rejecting incoming requests or my validation logic is failing. I believe the issue is related to HMAC signature verification. Explain step by step how webhook signature validation works, what [SERVICE NAME] sends in the request headers to prove authenticity, how to correctly implement signature verification inside an n8n Function node using the raw request body (not the parsed JSON), common reasons why signature validation fails even with the correct secret key (such as body parsing issues, encoding mismatches, or header name case sensitivity), and how to safely test webhook validation in n8n's development environment.
```

### 5. OAuth2 Redirect URI Configuration Errors

**Use case:** Fixing redirect URI mismatch errors during initial OAuth2 setup

```
I am setting up a new OAuth2 credential in n8n for [SERVICE NAME] and the authorization flow fails with a 'redirect_uri_mismatch' or 'invalid_redirect_uri' error. Explain what the OAuth2 redirect URI is, why it must exactly match between the n8n credential configuration and the OAuth2 application settings in [SERVICE NAME]'s developer portal, what the correct redirect URI format looks like for both self-hosted n8n instances and n8n Cloud, how trailing slashes, HTTP vs HTTPS, and port numbers can cause mismatches, and the exact steps to locate and update the redirect URI in both n8n and [SERVICE NAME]'s developer console to resolve this error.
```

### 6. Expired API Key Detection and Rotation Plan

**Use case:** Managing API key expiry detection and safe rotation in production workflows

```
My n8n workflow that calls [SERVICE NAME]'s API has started failing with authentication errors and I suspect the API key may have expired or been rotated on the service provider's side. Help me create a systematic approach to: (1) confirm whether API key expiry is the actual cause versus other authentication issues, (2) locate where to generate a new API key inside [SERVICE NAME]'s dashboard, (3) safely update the credential in n8n without causing downtime in active workflows, (4) understand whether n8n caches credentials and if a workflow restart is needed after updating, and (5) implement a proactive monitoring strategy within n8n to detect future API key expiry before it causes workflow failures.
```

### 7. OAuth2 Client ID and Secret Misconfiguration

**Use case:** Resolving invalid client errors during OAuth2 credential setup in n8n

```
I am configuring an OAuth2 credential in n8n for [SERVICE NAME] and receive an 'invalid_client' or 'client authentication failed' error when attempting to authorize. Walk me through every possible cause of this error related to the Client ID and Client Secret configuration, including: how to verify you are using the correct OAuth2 application credentials from [SERVICE NAME]'s developer portal, whether the service requires confidential vs public client settings, common copy-paste errors (extra spaces, missing characters), whether the client secret needs URL encoding, how to distinguish between OAuth2 authorization code flow vs client credentials flow and which n8n credential type maps to each, and how to test the client credentials independently using a curl command before configuring them in n8n.
```

### 8. n8n HTTP Request Node Auth Header Debug

**Use case:** Inspecting and debugging exact headers sent by n8n HTTP Request node

```
I have an n8n HTTP Request node configured to call [SERVICE NAME]'s API and I am getting authentication failures, but I am unsure whether the issue is in how n8n is constructing the Authorization header. Provide a detailed debugging guide that covers: how to enable and read n8n's execution log to see the exact headers being sent, how to use the HTTP Request node's 'Send Headers' section correctly versus using the built-in Authentication field, the correct syntax for common authentication header formats (Basic Auth base64 encoding, Bearer tokens, API key headers like 'X-API-Key'), how to use a service like webhook.site or requestbin.com as a temporary endpoint to inspect what n8n is actually sending, and how to compare that against what [SERVICE NAME]'s API documentation specifies.
```

### 9. Service Account vs Personal OAuth2 Token Issues

**Use case:** Migrating from personal OAuth2 tokens to service accounts for reliability

```
My n8n workflow uses OAuth2 to connect to [SERVICE NAME, e.g., Google Workspace, Microsoft 365] and works fine during testing but fails in production. I believe the issue is related to using a personal OAuth2 token instead of a service account or application-level authentication. Explain the difference between personal OAuth2 tokens and service account credentials, why personal tokens cause problems in automated workflows (user account changes, password resets, token revocation), how to set up a dedicated service account or application credential in [SERVICE NAME] specifically for n8n automation, the step-by-step process to migrate an n8n credential from personal OAuth2 to service account authentication, and any permission or domain-wide delegation settings required for service accounts in [SERVICE NAME].
```

### 10. Webhook URL Not Receiving Events Diagnosis

**Use case:** Diagnosing n8n webhook triggers that receive no events from external services

```
I have configured an n8n webhook trigger node and registered the webhook URL with [SERVICE NAME], but my workflow is not being triggered when events occur. Help me diagnose this issue systematically by covering: how to verify the n8n webhook URL is correctly formed and publicly accessible (including issues with localhost vs production URLs), how to check if [SERVICE NAME] is successfully delivering events by reviewing its webhook delivery logs or dashboard, common network issues such as firewall rules, SSL certificate errors, and reverse proxy misconfigurations that prevent webhook delivery to self-hosted n8n, how to test the webhook URL manually using curl or Postman, what HTTP response codes n8n must return for [SERVICE NAME] to consider delivery successful, and how to handle webhook payload format differences between test and production events.
```

### 11. Rate Limiting vs Authentication Error Distinction

**Use case:** Distinguishing between authentication failures and API rate limit responses

```
My n8n workflow calling [SERVICE NAME]'s API is returning errors that could be either authentication failures or rate limiting, and I cannot determine which is the root cause. The HTTP status codes I am seeing are [INSERT STATUS CODES, e.g., 429, 401, 403]. Explain how to definitively distinguish between authentication errors and rate limit errors by analyzing response status codes, response body messages, and response headers. Describe what rate limit headers look like (e.g., X-RateLimit-Remaining, Retry-After) and how to read them in n8n. Explain whether [SERVICE NAME] uses API keys with usage quotas that can be exhausted (which would look like auth failures), how to implement retry logic with exponential backoff in n8n specifically for rate limit errors, and how to set up error handling branches in n8n to handle auth errors and rate limit errors differently.
```

### 12. n8n Credential Sharing and Environment Issues

**Use case:** Resolving credential failures when moving workflows between n8n environments

```
I have set up OAuth2 or API key credentials in n8n for [SERVICE NAME] and they work in one environment (e.g., development) but fail in another (e.g., production or a different n8n instance). Help me understand how n8n stores and manages credentials, why credentials do not automatically transfer between n8n instances or environments, how to safely export and import credentials between n8n instances while maintaining security, whether environment variables can be used to manage API keys in n8n and how to configure this, common issues that arise when credentials are shared between multiple n8n users or workflows, and how to audit which workflows are using which credentials to prevent unexpected failures when credentials are updated or rotated.
```

### 13. JWT Authentication Configuration in n8n

**Use case:** Setting up and debugging JWT bearer token authentication in n8n workflows

```
I need to authenticate n8n's HTTP Request node with [SERVICE NAME] which uses JWT (JSON Web Token) bearer authentication. I am either receiving invalid token errors or I am unsure how to correctly generate and include the JWT in my requests. Explain step by step: how JWT authentication works and what components (header, payload, signature) need to be configured correctly, how to generate a JWT inside an n8n Function or Code node using the correct signing algorithm (RS256, HS256) required by [SERVICE NAME], where to include the JWT in the HTTP request (Authorization header format), how to handle JWT expiry by generating a fresh token before each API call versus caching the token during its validity period, and common JWT mistakes such as incorrect clock skew, wrong audience claim, and missing required payload fields that [SERVICE NAME] validates.
```

### 14. OAuth2 Refresh Token Missing or Invalid

**Use case:** Fixing OAuth2 workflows that fail after access token expiry due to refresh issues

```
My n8n OAuth2 credential for [SERVICE NAME] stops working after a period of time, specifically when the access token expires. I believe n8n is not successfully using the refresh token to obtain a new access token. Diagnose this problem comprehensively by explaining: how to verify whether a refresh token was actually granted during the initial OAuth2 authorization (some services require specific scopes like 'offline_access' to issue refresh tokens), why [SERVICE NAME] might invalidate refresh tokens (user password change, security event, token reuse policy, long inactivity), how to check n8n's credential settings to confirm a refresh token is stored, the steps to manually re-authorize the credential in n8n to obtain a fresh refresh token, and any [SERVICE NAME]-specific configuration required to enable long-lived refresh tokens in their developer console.
```

### 15. Basic Authentication Encoding and Format Errors

**Use case:** Fixing Basic Auth 401 errors caused by encoding or formatting mistakes

```
I am connecting n8n to [SERVICE NAME] which uses HTTP Basic Authentication, and I am receiving 401 Unauthorized errors despite entering what I believe are correct credentials. Provide a thorough troubleshooting guide covering: the exact format of Basic Authentication (Base64 encoding of 'username:password'), common mistakes such as URL-encoding issues with special characters in passwords, how n8n's built-in Basic Auth credential type encodes and sends credentials versus manually setting the Authorization header in an HTTP Request node, how to verify the Base64-encoded value is correct using command-line tools or online decoders, whether [SERVICE NAME] uses username/password or API token as the username with a blank or fixed password (a common variation), and how to test Basic Auth credentials independently using curl before troubleshooting within n8n.
```

### 16. Webhook Secret Key Mismatch Debugging

**Use case:** Debugging webhook secret key validation failures in n8n Function nodes

```
I have configured a webhook in [SERVICE NAME] with a secret key and am trying to validate incoming webhook payloads in my n8n workflow, but validation keeps failing even though I believe I have entered the correct secret. Walk me through every possible reason the secret validation could fail, including: where to find or reset the webhook secret in [SERVICE NAME]'s dashboard, how secret keys are used differently across services (some use them as HMAC keys, some include them directly in the payload, some send them as a header value), how to correctly access the raw unparsed request body in n8n for HMAC validation (and why using the parsed JSON body always causes validation failure), how to implement the validation code correctly in an n8n Function node for [SERVICE NAME]'s specific signing algorithm, and how to temporarily disable validation to confirm the rest of the workflow functions correctly while debugging.
```

### 17. OAuth2 State Parameter CSRF Validation Failure

**Use case:** Resolving OAuth2 state parameter CSRF validation errors during authorization

```
When attempting to complete the OAuth2 authorization flow for [SERVICE NAME] in n8n, I receive an error related to the 'state' parameter, such as 'state mismatch', 'invalid state', or 'CSRF validation failed'. Explain what the OAuth2 state parameter is and why it exists as a security measure, why this error typically occurs during the n8n OAuth2 credential authorization process, how browser session issues (multiple tabs, private browsing, session expiry) can cause state parameter mismatches, whether this issue is specific to self-hosted n8n configurations and how proxy or load balancer settings can interfere with the state parameter flow, the exact steps to retry the authorization cleanly without state conflicts, and whether any n8n configuration settings (such as the N8N_EDITOR_BASE_URL environment variable) affect OAuth2 state validation.
```

### 18. API Key Permissions and IP Allowlisting Issues

**Use case:** Diagnosing API key failures caused by permission settings or IP restrictions

```
My n8n workflow is using an API key to connect to [SERVICE NAME] but receives authentication or access denied errors even though the API key appears valid. I suspect the issue may be related to API key permission settings or IP address restrictions. Guide me through: how to review the API key's assigned permissions or roles within [SERVICE NAME]'s dashboard and which permissions are required for the specific API endpoints my workflow calls, how IP allowlisting works and how to find the outbound IP addresses used by n8n Cloud or my self-hosted n8n instance, the steps to add n8n's IP addresses to the allowlist in [SERVICE NAME]'s security settings, common mistakes such as creating the API key under the wrong account, team, or project within [SERVICE NAME], and how to test whether IP restrictions are the cause of the failure by temporarily disabling the restriction and observing whether authentication succeeds.
```

### 19. Multi-Step OAuth2 Flow Interruption Analysis

**Use case:** Configuring non-standard or custom OAuth2 flows not supported by default n8n templates

```
I am setting up an OAuth2 credential in n8n for [SERVICE NAME] which requires a multi-step or custom OAuth2 flow (for example, requiring a tenant ID, custom authorization URL, or additional parameters). The standard n8n OAuth2 credential template does not seem to accommodate this service's requirements, and the authorization keeps failing. Help me understand: how to identify the exact OAuth2 endpoints ([SERVICE NAME]'s authorization URL, token URL, and any custom parameters) from its developer documentation, how to configure n8n's generic OAuth2 credential type with custom authorization and token URLs, how to add required additional parameters (such as tenant_id, resource, or audience) that [SERVICE NAME] requires during the token request, whether n8n supports non-standard OAuth2 flows such as device code flow or PKCE and what alternatives exist if not, and how to use n8n's HTTP Request node as a fallback to manually implement the token exchange when the built-in credential type is insufficient.
```

### 20. Authentication Error Logging and Monitoring Setup

**Use case:** Building proactive authentication failure monitoring across all n8n integrations

```
I manage multiple n8n workflows that integrate with various third-party services including [LIST SERVICES, e.g., Salesforce, Slack, Google APIs] using different authentication methods (OAuth2, API keys, webhooks). Authentication failures are occurring intermittently and I want to implement a proactive monitoring and alerting system. Design a comprehensive strategy that includes: how to configure n8n's error workflow feature to catch authentication failures (401, 403 errors) across all workflows and route them to a central handler, how to extract meaningful diagnostic information from authentication error responses (status code, error message, which credential and workflow failed) and format them into actionable alerts, how to send these alerts to a notification channel such as [NOTIFICATION CHANNEL, e.g., Slack, email, PagerDuty] with enough context to diagnose the issue quickly, how to implement a credential health-check workflow that periodically tests each integration's authentication status before failures impact production workflows, and how to build a simple dashboard or log aggregation approach using n8n itself to track authentication failure patterns over time.
```
