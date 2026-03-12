# Skill: product-generate

## Purpose
Generate the complete content of a prompt pack product based on a selected idea.

## Inputs
- Selected idea from `data/idea-backlog.json` (where `selected: true`)
- Product ID: `prompts-{kebab-title}-{YYYYMMDD}`

## Outputs
Creates `products/{id}/`:
```
assets/
  prompts.md      — 20–30 prompts, human-readable, one section per prompt
  prompts.json    — structured array of prompt objects
  README.md       — product title, target audience, use instructions
meta.json         — product metadata
```

## Product Schema: `meta.json`
```json
{
  "id": "prompts-marketing-hooks-20260312",
  "title": "Marketing Hook Prompts",
  "description": "30 prompts for writing attention-grabbing marketing hooks",
  "category": "prompt-packs",
  "tags": ["marketing", "copywriting"],
  "prompt_count": 30,
  "created_at": "2026-03-12T00:00:00Z",
  "status": "generated",
  "package_path": null,
  "site_path": null
}
```

## Prompt Object Schema (in `prompts.json`)
```json
{
  "id": 1,
  "title": "Hook for SaaS trial signup",
  "prompt": "Write a compelling hook for a SaaS product that...",
  "use_case": "Email subject line, landing page headline",
  "example_output": "Optional: what great output looks like"
}
```

## Claude Prompt Template
```
Create a professional prompt pack titled "{title}".

Target audience: {description}

Generate exactly 25 high-quality prompts. Each prompt should:
- Be immediately usable with any AI assistant
- Include clear context about the desired output
- Be specific enough to produce consistent, high-quality results
- Cover different angles and use cases within the theme

Format as JSON array with fields: id, title, prompt, use_case
```

## Success Criteria
- `prompts.json` contains 20–30 well-formed prompts
- `prompts.md` is clean and readable
- `README.md` clearly explains the product
- `meta.json` is valid JSON with all required fields
