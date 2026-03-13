# Lead Source Attribution Audit Checklist for Growth Marketers

> Growth marketers use this step-by-step audit to identify broken UTM tracking, misattributed conversions, and gaps in their lead source reporting inside HubSpot or GA4.

---

## Preparation

- [ ] **Define the audit scope and date range before touching any data**
  *Without a fixed time window and defined channels, you risk comparing inconsistent data sets. Choose a 30, 60, or 90-day range and document it upfront.*

- [ ] **Inventory every active traffic source and campaign currently running**
  *You need a complete list of paid, organic, email, social, and partner channels to cross-reference against what is actually appearing in your attribution reports.*

- [ ] **Export your UTM parameter naming convention documentation and flag any gaps**
  *Inconsistent naming (e.g., 'Facebook' vs 'facebook' vs 'FB') causes traffic to fragment into multiple source buckets, distorting your lead counts per channel.*

- [ ] **Confirm that GA4 data streams are actively firing on all landing pages and conversion pages**
  *A missing or broken data stream silently drops tracking on entire page groups, causing leads to appear unattributed or fall into direct traffic.*

- [ ] **Verify that the HubSpot tracking code is installed on every page that hosts a form or CTA**
  *If HubSpot's tracking script is absent from even one high-traffic landing page, contact records will be created without original source data, permanently breaking attribution for those leads.*

## Execution

- [ ] **Pull a HubSpot contacts report filtered by 'Original Source = Direct Traffic' and sort by volume**
  *An unusually high percentage of direct traffic is a red flag that UTM parameters are being stripped, links are untagged, or redirects are dropping query strings.*

- [ ] **Click every active paid ad URL and confirm UTM parameters survive the redirect chain to the final landing page**
  *301 redirects, link shorteners, or misconfigured landing page platforms frequently strip UTM parameters, causing paid traffic to register as direct or organic.*

- [ ] **Test each active form submission using a dedicated test email and verify the contact record populates with the correct original source in HubSpot**
  *This confirms the end-to-end tracking chain is working, not just the URL tagging. It catches issues where the HubSpot cookie is not being read at the moment of form submission.*

- [ ] **Cross-reference GA4 session counts by source/medium against HubSpot contact creation counts by original source for the same date range**
  *Large discrepancies between GA4 sessions and HubSpot contacts from the same source indicate a broken handoff, such as forms not connected to HubSpot or cookie consent blocking tracking.*

- [ ] **Audit the HubSpot 'Other Campaigns' and 'Offline Sources' buckets to identify misrouted contacts**
  *These catch-all buckets often contain leads with malformed UTMs or unrecognized source values. Reviewing them reveals systemic tagging errors across specific campaigns or channels.*

- [ ] **Check GA4 for sessions tagged with (not set) as the campaign or source value and trace back to the originating URLs**
  *'Not set' in GA4 means the parameter was expected but not received, commonly caused by auto-tagged Google Ads links conflicting with manual UTMs or broken campaign configurations.*

- [ ] **Audit your Google Ads and Meta Ads accounts to confirm auto-tagging settings align with your GA4 and HubSpot integration setup**
  *Google Ads auto-tagging (gclid) and manual UTMs can conflict if both are applied simultaneously, causing duplicate or misattributed sessions in GA4.*

- [ ] **Review all email campaign links in HubSpot to ensure utm_medium=email and utm_source values are consistently applied**
  *Email links without proper UTMs will attribute leads to direct traffic, making email appear to underperform while inflating direct channel numbers.*

- [ ] **Inspect the HubSpot attribution report for any conversion events mapped to the wrong deal or contact lifecycle stage**
  *Misaligned conversion events cause the model to credit the wrong touchpoint, skewing first-touch or multi-touch attribution data used for budget decisions.*

- [ ] **Validate that offline lead sources such as events, calls, and referrals are being manually logged in HubSpot with a standardized source property**
  *Offline leads without a logged source default to unknown or direct, understating the ROI of offline channels and overstating digital channel efficiency.*

## Review

- [ ] **Compare the total lead volume from your CRM against leads captured in GA4 conversion events to calculate your attribution coverage rate**
  *This percentage tells you how much of your pipeline has traceable attribution. A rate below 80% signals significant blind spots that are distorting your channel performance data.*

- [ ] **Document every broken or inconsistent UTM pattern found and create a standardized UTM taxonomy to enforce going forward**
  *Without a documented and enforced standard, the same errors will recur with each new campaign. A shared taxonomy spreadsheet or UTM builder tool prevents future fragmentation.*

- [ ] **Reassign or update misattributed contact source properties in HubSpot where the correct source can be confidently determined**
  *Cleaning historical records where attribution is provably wrong improves the accuracy of lifecycle reports and reduces distortion in closed-won analysis.*

- [ ] **Create a recurring monthly attribution health dashboard in GA4 or HubSpot that flags direct traffic spikes and untagged sessions automatically**
  *A proactive monitoring dashboard catches new tracking breaks within days rather than quarters, preventing months of corrupted data from compounding before anyone notices.*

- [ ] **Brief your demand generation, content, and paid media teams on the audit findings and distribute the updated UTM naming convention with mandatory adoption**
  *Attribution breaks most often originate from human error across distributed teams. Shared accountability and clear documentation reduce repeat errors and maintain data integrity over time.*
