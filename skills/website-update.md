# Skill: website-update

## Purpose
Add a new product to the showcase website and update the product catalog.

## Inputs
- `products/{id}/meta.json`
- `data/product-catalog.json`

## Outputs
- `site/products/{id}.html` — individual product page
- Updated `site/index.html` — product card added to grid
- Updated `data/product-catalog.json` — product entry added
- Updated `products/{id}/meta.json` with `site_path` and `status: "published"`

## Website Rules (CRITICAL)
The website NEVER mentions:
- AI, Claude, or automation
- How the product was made
- The factory system

The website ONLY shows:
- Product name
- Short description (1–2 sentences)
- Tags
- Download button / link
- Product count on homepage

## Product Card HTML Structure
```html
<article class="product-card">
  <div class="product-tags">
    <span class="tag">Prompt Pack</span>
    <span class="tag">Marketing</span>
  </div>
  <h2 class="product-title"><a href="/products/{id}.html">{title}</a></h2>
  <p class="product-desc">{description}</p>
  <a href="/products/{id}/package.zip" class="btn-download">Download Free</a>
</article>
```

## When to Run
- After product-package succeeds

## Success Criteria
- Product page exists at `site/products/{id}.html`
- Homepage shows the new product card
- Download link points to existing zip file
- Catalog entry added
