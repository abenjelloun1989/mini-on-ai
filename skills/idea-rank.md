# Skill: idea-rank

## Purpose
Score unscored ideas in the backlog and select the best one to produce next.

## Inputs
- `data/idea-backlog.json` (unscored ideas where score === null)

## Outputs
Updates `data/idea-backlog.json`:
- Each unscored idea gets a `score` (0–100) and `rationale`
- The highest-scored idea gets `selected: true`

## Scoring Criteria
- **Demand** (0–40): Is there clear audience demand for this?
- **Uniqueness** (0–30): Is this differentiated from what's freely available?
- **Generability** (0–30): Can Claude generate high-quality content for this quickly?

## When to Run
- After trend-scan
- Manually when you want to pick the next idea

## Claude Prompt Template
```
Score each of these prompt pack ideas for a digital product catalog.

Ideas: {ideas}

Score each on:
- demand (0-40): audience size and urgency of need
- uniqueness (0-30): differentiation from free alternatives
- generability (0-30): how well AI can produce high-quality content

Return JSON array with added fields: score (total 0-100), rationale (one sentence)
Sort by score descending.
```

## Success Criteria
- All unscored ideas receive a score
- One idea marked `selected: true` (highest score)
- Rationale explains why it scored well
