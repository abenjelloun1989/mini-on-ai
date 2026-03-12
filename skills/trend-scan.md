# Skill: trend-scan

## Purpose
Generate a list of prompt pack ideas based on current trends, pain points, and underserved use-cases.

## Inputs
- `category`: always "prompt-packs" in V1
- `seed` (optional): keyword to focus the search (e.g. "marketing", "coding", "sales")
- `count`: number of ideas to generate (default: 10)

## Outputs
Appends to `data/idea-backlog.json`:
```json
{
  "id": "idea-{timestamp}",
  "title": "Short title of the prompt pack",
  "description": "One sentence describing who it's for and what it does",
  "category": "prompt-packs",
  "tags": ["marketing", "copywriting"],
  "score": null,
  "selected": false,
  "generated_at": "2026-03-12T00:00:00Z",
  "source": "trend-scan"
}
```

## When to Run
- At the start of each factory cycle
- Manually when backlog has fewer than 5 unscored ideas

## Claude Prompt Template
```
Generate {count} specific, practical prompt pack ideas for digital creators.
Each idea should be:
- Focused on a real workflow or pain point
- Immediately usable by the target audience
- Describable in one clear sentence
- Differentiated from generic AI prompts

{seed ? `Focus area: ${seed}` : ''}

Return as JSON array matching this schema:
[{ "title": string, "description": string, "tags": string[] }]
```

## Success Criteria
- At least 5 ideas added to backlog
- Each idea has a clear title and one-sentence description
- Ideas are specific (not "prompts for writers" but "30 prompts for writing cold email sequences")
