# Lead Source Attribution Audit Checklist for Growth Marketers

> Growth marketers use this step-by-step audit to identify broken UTM tracking, misattributed conversions, and gaps in their lead source reporting inside HubSpot or GA4.

---

## Preparation

- [ ] **Define the audit scope and time range before touching any data**
  *Establishing a clear date range (e.g., last 90 days) and which channels are in scope prevents scope creep and ensures you're comparing apples to apples across all reports.*

- [ ] **Document your expected lead sources and their corresponding UTM parameter conventions**
  *Without a source-of-truth for what UTM values should look like (e.g., utm_source=linkedin, utm_medium=paid-social), you cannot identify inconsistencies or typos in the wild.*

- [ ] **Export your current UTM taxonomy spreadsheet or build one if it doesn't exist**
  *A UTM taxonomy document is the baseline for every audit step. If one doesn't exist, creating it now exposes structural gaps before you analyze any data.*

- [ ] **Confirm that HubSpot tracking code or GA4 tag is firing correctly on all landing pages and thank-you pages**
  *Missing or misfiring tracking scripts mean conversions are never recorded, making attribution incomplete at the most fundamental level. Use Google Tag Assistant or HubSpot's tracking status tool to verify.*

- [ ] **Verify that GA4 data streams are connected to the correct property and that events are flowing in real time**
  *A misconfigured data stream silently drops data. Check the GA4 DebugView and the Realtime report to confirm events like form_submit and page_view are being captured.*

## Execution

- [ ] **Pull the 'Original Source' and 'Latest Source' breakdown report in HubSpot for all contacts created in your audit period**
  *Comparing original versus latest source reveals if campaigns are getting credit for assisted conversions or if the first-touch source is being overwritten incorrectly.*

- [ ] **Filter HubSpot contacts by 'Original Source = Direct Traffic' and investigate what percentage of total leads this represents**
  *An unusually high direct traffic percentage (above 20-30%) is a red flag that UTM parameters are being stripped, links are untagged, or dark social traffic is being miscategorized.*

- [ ] **Run a GA4 Exploration report using the UTM source/medium dimensions and filter for rows where source contains 'not set' or medium equals 'none'**
  *'Not set' and '(none)' values indicate sessions where tracking parameters were absent or failed to pass through, representing a direct measurement gap in your attribution model.*

- [ ] **Audit all active paid campaign URLs in Google Ads, LinkedIn Campaign Manager, and Meta Ads Manager to confirm every destination URL contains a complete UTM string**
  *Paid campaigns without UTM parameters will be attributed to direct or organic traffic in both HubSpot and GA4, inflating those channels and hiding true paid media performance.*

- [ ] **Check for UTM parameter case inconsistencies by searching your HubSpot contacts for duplicate source variations such as 'LinkedIn', 'linkedin', and 'LinkedIn-paid'**
  *GA4 and HubSpot are case-sensitive for UTM values. Mixed casing fragments your data into multiple source buckets, making it impossible to accurately measure a single channel's total contribution.*

- [ ] **Test five to ten recent form submission thank-you page URLs to confirm UTM parameters persist through the conversion flow**
  *UTM parameters can be dropped by redirects, single-page application routing, or misconfigured HubSpot forms. If parameters don't reach the thank-you page, the conversion is attributed incorrectly.*

- [ ] **Cross-reference lead volume reported in HubSpot against conversion events recorded in GA4 for the same time period and channels**
  *Significant discrepancies between HubSpot and GA4 conversion counts reveal integration gaps, double-counting issues, or events that are firing in one platform but not the other.*

- [ ] **Inspect your HubSpot-to-GA4 integration settings to confirm that HubSpot form submissions are being passed as GA4 conversion events**
  *Without explicit event bridging, GA4 only records the page visit but not the form completion as a conversion, causing your GA4 attribution paths to be incomplete.*

- [ ] **Review offline conversion imports if your team uses offline lead scoring or CRM syncs and verify that source data is being uploaded with each batch**
  *Offline conversions imported without source information default to unattributed, which distorts your channel-level ROI calculations and makes pipeline attribution unreliable.*

- [ ] **Identify any third-party tools such as Calendly, Typeform, or Drift that collect leads and confirm they are passing UTM parameters back to HubSpot via hidden fields**
  *Third-party tools are a common attribution black hole. If UTM values are not captured in hidden form fields and mapped to HubSpot contact properties, those leads will always appear as direct traffic.*

## Review

- [ ] **Compare channel-level lead counts in your attribution report to actual spend data from your ad platforms and flag any channels showing leads with zero associated spend**
  *Leads appearing under a paid channel with no corresponding spend often indicate misattribution from untagged organic posts or brand mentions being incorrectly labeled as paid.*

- [ ] **Categorize all identified issues by severity (data loss, misattribution, or cosmetic) and assign an owner and deadline to each fix**
  *Not all attribution issues have equal business impact. Prioritizing by severity ensures the fixes that most distort pipeline and revenue reporting are resolved first.*

- [ ] **Document all findings in a shared audit report including screenshots, affected contact counts, and estimated attribution impact**
  *A written audit report creates accountability, provides a before-and-after baseline for measuring improvement, and communicates the business case for resourcing the fixes to stakeholders.*

- [ ] **Update your UTM taxonomy document with any new conventions discovered during the audit and share it with all teams who create campaign links**
  *Attribution errors are mostly a process problem, not a technical one. Keeping the taxonomy document current and distributed prevents the same inconsistencies from reappearing next quarter.*

- [ ] **Schedule a recurring monthly UTM audit using this checklist and set a HubSpot or GA4 alert for when direct traffic exceeds your defined threshold**
  *Attribution decay is continuous as new campaigns, tools, and team members are added. A monthly audit cadence and automated alerts catch new issues before they compound into quarters of bad data.*
