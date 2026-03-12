# Skill: product-package

## Purpose
Bundle product assets into a clean downloadable package.

## Inputs
- `products/{id}/assets/` — generated product files

## Outputs
- `products/{id}/package.zip` — downloadable bundle
- Updated `products/{id}/meta.json` with `package_path` and `status: "packaged"`

## Package Contents
```
{product-title}/
  prompts.md
  prompts.json
  README.md
```

## When to Run
- After product-generate succeeds

## Success Criteria
- `package.zip` exists and is readable
- Zip contains all three asset files
- `meta.json` status updated to "packaged"
