# Notion Workspace Debt Cleanup Checklist for Teams

> For team admins inheriting a chaotic Notion workspace, this structured checklist walks through database audits, permission hygiene, orphaned page removal, and naming convention enforcement in one sitting.

---

## Preparation

- [ ] **Request full admin access and a list of all current members before touching anything**
  *Making changes without full visibility can break workflows or lock out active users. Confirm you have owner-level permissions and a complete member roster before proceeding.*

- [ ] **Export a full workspace backup via Settings → Export content as a safety snapshot**
  *Irreversible deletions happen during cleanup. A full HTML or Markdown export gives you a restore reference point if something critical is accidentally removed.*

- [ ] **Create a private 'Cleanup Staging' page to document findings, decisions, and items flagged for deletion**
  *A running log prevents duplicate work, creates an audit trail for stakeholders, and helps you communicate what changed and why after the session ends.*

- [ ] **Interview or survey 2–3 active team members to identify the 5 most-used pages or databases**
  *You need a clear picture of what is actively relied upon before removing or restructuring anything. Protect high-traffic assets first.*

## Execution

- [ ] **Navigate to Settings → Members and remove deactivated, departed, or contractor accounts that no longer need access**
  *Ghost accounts inflate member counts, expose sensitive data, and can retain edit permissions on pages long after someone has left the organization.*

- [ ] **Audit every workspace-level Guest and review whether their page-level access is still appropriate**
  *Guests are often added for a one-off project and forgotten. Each guest with broad access is a potential data exposure risk.*

- [ ] **Review all pages set to 'Share to web' and disable public sharing on any that contain internal or sensitive information**
  *Public pages are indexed by search engines and accessible without authentication. Many teams forget these are on after a public launch or demo.*

- [ ] **Open the sidebar and identify all top-level pages that have not been edited in more than 90 days using the 'Last edited' metadata**
  *Stale top-level pages are the primary source of workspace clutter. The 90-day threshold surfaces genuinely dormant content without catching seasonally-used pages.*

- [ ] **Move all confirmed orphaned pages — pages with no parent, no backlinks, and no recent views — into a 'Pending Deletion' archive folder**
  *Deleting immediately is risky. A 2-week archive window lets team members flag anything incorrectly identified before permanent removal.*

- [ ] **Run a database audit: open each database, check for duplicate databases serving the same purpose, and merge or deprecate redundant ones**
  *Teams frequently create new databases instead of expanding existing ones. Duplicate databases fragment data, create sync issues, and confuse new members.*

- [ ] **Inspect every database schema and remove unused properties that have no data or have not been populated in over 60 days**
  *Unused properties add visual noise, slow down database loading, and confuse contributors about what fields are actually required.*

- [ ] **Check all Relation and Rollup properties across databases to confirm linked databases still exist and connections are intact**
  *When a linked database is deleted or renamed, Relation fields break silently and Rollups return empty or incorrect values, corrupting downstream reporting.*

- [ ] **Audit all active database views and delete saved views that are duplicates, have no filters, or belong to team members who have left**
  *Orphaned views accumulate quickly and make the view-switcher unusable. Each database should have a clear default view plus intentionally named filtered views.*

- [ ] **Define and document a naming convention (e.g., [TEAM] - [Type] - [Name]) and rename all top-level databases and pages to follow it**
  *Inconsistent naming is the root cause of most search failures in Notion. A standardized format makes pages scannable and searchable within seconds.*

- [ ] **Restructure the sidebar into a maximum of 5–7 top-level sections using clearly labeled teamspaces or parent pages**
  *A flat, sprawling sidebar forces users to scroll endlessly. Grouping by team or workflow function reduces cognitive load and speeds up navigation.*

- [ ] **Review all active Notion automations and integrations (Zapier, Make, API connections) and disable or update any pointing to deleted or renamed pages**
  *Broken automations fail silently or error loudly and can orphan data. This step prevents downstream tool failures after restructuring.*

## Review

- [ ] **Pin or favorite the 5 most-used databases and pages identified in your pre-work interviews to the sidebar for fast access**
  *Quick wins in discoverability immediately demonstrate value from the cleanup and increase adoption of the restructured workspace.*

- [ ] **Document the finalized structure, naming conventions, and permission rules in a 'Workspace Guide' page pinned at the top of the sidebar**
  *Without documented standards, the workspace will return to chaos within months. A pinned guide sets expectations for new members and current contributors.*

- [ ] **Share a summary of changes made, pages archived, and members removed with the team lead or stakeholders within 24 hours**
  *Transparency builds trust in the cleanup process, allows stakeholders to flag missed items, and gives leadership visibility into the scope of the debt that existed.*

- [ ] **Schedule a recurring quarterly 30-minute workspace hygiene review on the team calendar to prevent debt from accumulating again**
  *A one-time cleanup without a maintenance cadence is temporary. Quarterly reviews catch stale pages, permission drift, and schema sprawl before they become unmanageable.*
