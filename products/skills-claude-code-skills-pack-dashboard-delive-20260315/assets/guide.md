# Claude Code Skills Pack: Dashboard Delivery — 5 Skills for Translating Data Into Executive Insights

> For analytics engineers and data product managers, this pack handles KPI narrative generation, chart annotation writing, dashboard layout recommendations, metric interpretation summaries, and executive briefing drafts so they can turn raw dashboard outputs into clear business communication without manual write-ups.

---

## What's in This Pack

Transforms raw dashboard outputs and metric data into polished executive-ready business communication for analytics engineers and data product managers.

This pack includes **5 ready-to-use Claude Code skills**:

**1. `/narrate-kpis`** — `01-kpi-narrative-generator.md`
   Converts raw KPI values, targets, and period-over-period changes into a coherent written narrative explaining business performance.

**2. `/annotate-chart`** — `02-chart-annotation-writer.md`
   Generates concise, context-aware annotations for chart anomalies, inflection points, and trend shifts to guide viewer interpretation.

**3. `/layout-dashboard`** — `03-dashboard-layout-advisor.md`
   Recommends optimal dashboard layout structure, visual hierarchy, and widget placement based on audience role and decision-making priorities.

**4. `/interpret-metric`** — `04-metric-interpretation-summarizer.md`
   Produces plain-language summaries that explain what a metric measures, why it moved, and what business action it implies.

**5. `/draft-briefing`** — `05-executive-briefing-drafter.md`
   Assembles a structured executive briefing document from multiple dashboard metrics, synthesizing key findings, risks, and recommended next steps.

---

## How to Install

1. **Create a `skills/` directory** in your project root (if it doesn't exist):
   ```bash
   mkdir -p skills
   ```

2. **Copy all skill files** from the `skills/` folder in this pack:
   ```bash
   cp skills/*.md /your-project/skills/
   ```

3. **Run Claude Code** in your project directory — all skills are immediately available:
   ```bash
   claude
   ```

---

## Quick Reference

| Skill | Trigger | File |
|-------|---------|------|
| Converts raw KPI values, targets, and period-over-period changes into a coherent written narrative explaining business performance. | `/narrate-kpis` | `01-kpi-narrative-generator.md` |
| Generates concise, context-aware annotations for chart anomalies, inflection points, and trend shifts to guide viewer interpretation. | `/annotate-chart` | `02-chart-annotation-writer.md` |
| Recommends optimal dashboard layout structure, visual hierarchy, and widget placement based on audience role and decision-making priorities. | `/layout-dashboard` | `03-dashboard-layout-advisor.md` |
| Produces plain-language summaries that explain what a metric measures, why it moved, and what business action it implies. | `/interpret-metric` | `04-metric-interpretation-summarizer.md` |
| Assembles a structured executive briefing document from multiple dashboard metrics, synthesizing key findings, risks, and recommended next steps. | `/draft-briefing` | `05-executive-briefing-drafter.md` |

---

## Tips

- Each skill works independently — use only the ones you need
- Skills can be combined in the same session (e.g. scaffold a component, then review it)
- Customize any `.md` file to match your project's conventions
- Add the `skills/` folder to git to share the pack across your team
