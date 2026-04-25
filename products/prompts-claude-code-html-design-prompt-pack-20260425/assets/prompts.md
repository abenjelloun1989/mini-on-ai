# Claude Code HTML Design Prompt Pack

> Stop starting from scratch — get pixel-perfect HTML in one prompt.
> 25 copy-paste prompts for Claude Code, Cursor, and any AI coding agent.

---

## Hero & Landing Page Layouts

### 1. Full-Bleed SaaS Hero Section

**What it builds:** Produces a single-file HTML hero with headline, subheadline, CTA button, and a browser mockup screenshot area.

```
Build a full-bleed SaaS hero section in a single HTML file using Tailwind CDN. Include: a left-aligned headline '[HEADLINE TEXT]', a subheadline '[SUBHEADLINE TEXT]', a primary CTA button labeled '[CTA LABEL]' in [BRAND COLOR hex], a secondary ghost button labeled '[SECONDARY CTA]', and a right-side browser chrome mockup placeholder (gray rounded rectangle, 600x400px). Background is off-white (#F9FAFB). Use Inter font from Google Fonts. Make it fully responsive with a stacked mobile layout. No JavaScript required.
```

💡 **Remix tip:** Swap the browser mockup for a <video autoplay muted loop> tag and point src to a product demo clip to create an autoplaying video hero.

---

### 2. 3-Tier Pricing Table

**What it builds:** Produces a responsive 3-column pricing table with a highlighted recommended plan, feature checklist rows, and CTA buttons.

```
Build a responsive 3-tier pricing table in a single HTML file using Tailwind CDN. Plans: '[PLAN 1 NAME]' at [PRICE 1]/mo, '[PLAN 2 NAME]' at [PRICE 2]/mo (mark as 'Most Popular' with a [ACCENT COLOR hex] badge), '[PLAN 3 NAME]' at [PRICE 3]/mo. Each card has 5 feature rows — use a green checkmark SVG for included and a gray X for excluded features. Features list: [FEATURE 1], [FEATURE 2], [FEATURE 3], [FEATURE 4], [FEATURE 5]. CTA buttons say '[CTA TEXT]'. The popular plan card has a colored border and subtle box-shadow. Fully responsive: stack to single column on mobile.
```

💡 **Remix tip:** Add a toggle switch at the top that switches between monthly and annual pricing using vanilla JS to multiply prices by 10 and update the DOM.

---

### 3. Social Proof Testimonial Row

**What it builds:** Produces a horizontal testimonial row with avatar, name, role, company, star rating, and quote for three customers.

```
Build a testimonial section in a single HTML file using Tailwind CDN. Show 3 testimonial cards in a horizontal row (stack on mobile). Each card contains: a circular avatar placeholder (64px, bg-gray-200 with initials '[INITIALS]'), a 5-star rating in gold (#FBBF24), a quote '[TESTIMONIAL QUOTE]', the reviewer's name '[REVIEWER NAME]', role '[REVIEWER ROLE]', and company '[COMPANY NAME]'. Cards have white backgrounds, rounded-xl corners, and a subtle shadow. Section has a light gray (#F3F4F6) background with a centered heading '[SECTION HEADLINE]' above. Use Inter font from Google Fonts.
```

💡 **Remix tip:** Replace static avatar placeholders with real <img> tags and add a marquee-style CSS animation to make cards scroll horizontally on a loop for a live-feed effect.

---

### 4. Feature Grid with Icon Cards

**What it builds:** Produces a 3x2 feature grid where each card has an SVG icon, bold title, and description paragraph.

```
Build a 6-feature grid section in a single HTML file using Tailwind CDN. Layout: 3 columns on desktop, 2 on tablet, 1 on mobile. Each feature card contains: a 40px SVG icon (use inline heroicons-style outline SVG) in [ICON COLOR hex], a bold feature title '[FEATURE TITLE]', and a 2-sentence description '[FEATURE DESCRIPTION]'. The 6 features are: [FEATURE 1 TITLE + DESCRIPTION], [FEATURE 2 TITLE + DESCRIPTION], [FEATURE 3 TITLE + DESCRIPTION], [FEATURE 4 TITLE + DESCRIPTION], [FEATURE 5 TITLE + DESCRIPTION], [FEATURE 6 TITLE + DESCRIPTION]. Section heading is '[SECTION HEADLINE]'. White background. Subtle hover: card lifts with box-shadow on hover using CSS transition.
```

💡 **Remix tip:** Change the grid to 4 columns and reduce card padding to create a dense comparison-style benefits grid for a product comparison page.

---

### 5. Email Capture CTA Banner

**What it builds:** Produces a full-width CTA banner with headline, supporting text, and an inline email input with submit button.

```
Build a full-width email capture CTA section in a single HTML file using Tailwind CDN. Dark background [BACKGROUND COLOR hex]. Centered layout with: a bold headline '[CTA HEADLINE]' in white, a supporting line '[SUPPORTING TEXT]' in gray-300, and an inline form with an email input (placeholder '[EMAIL PLACEHOLDER]') and a submit button labeled '[BUTTON TEXT]' in [BUTTON COLOR hex]. Form is side-by-side on desktop, stacked on mobile. Add a small trust line below the form: '[TRUST LINE e.g. No spam. Unsubscribe anytime.]' in gray-400, font-size small. On button click, use vanilla JS to replace the form with a success message '[SUCCESS MESSAGE]'. Single file, no external JS.
```

💡 **Remix tip:** Wrap the whole section in a sticky bottom bar (position: fixed; bottom: 0) to create a persistent email capture bar that appears after the user scrolls 400px.

---

## Data Visualization Slides

### 6. Animated Bar Chart Slide

**What it builds:** Produces a presentation-style slide with a pure CSS animated vertical bar chart showing up to 6 data points.

```
Build a single-file HTML presentation slide (1280x720px fixed canvas, centered in viewport) containing a pure CSS animated vertical bar chart. Chart has [NUMBER] bars representing: [LABEL 1]: [VALUE 1], [LABEL 2]: [VALUE 2], [LABEL 3]: [VALUE 3], [LABEL 4]: [VALUE 4], [LABEL 5]: [VALUE 5], [LABEL 6]: [VALUE 6]. Max value is [MAX VALUE]. Bars animate upward from height 0 on page load using CSS keyframes (ease-out, 800ms, staggered 100ms delay per bar). Bar color is [BAR COLOR hex]. Labels below bars, values above. Slide has a white background, slide title '[SLIDE TITLE]' top-left in dark gray, and a thin [ACCENT COLOR hex] left border. Use Inter font from Google Fonts. No Chart.js, no Canvas, pure CSS only.
```

💡 **Remix tip:** Change to a horizontal bar chart by rotating the flex direction and adjusting width instead of height animations — better for long category labels.

---

### 7. KPI Dashboard Stat Callout Slide

**What it builds:** Produces a dark-mode KPI slide with 4 large metric callout cards, trend indicators, and sparkline placeholders.

```
Build a single-file HTML KPI dashboard slide (1280x720px fixed canvas, centered in viewport) with a dark background (#0F172A). Display 4 KPI cards in a 2x2 grid. Each card has: a metric label '[METRIC LABEL]' in gray-400, a large number '[METRIC VALUE]' in white (font-size 48px, font-weight 700), a trend indicator showing '[TREND DIRECTION up/down]' '[TREND PERCENT]%' in green (#10B981) or red (#EF4444) with an arrow SVG, and a mini sparkline placeholder (a simple SVG polyline using values [SPARKLINE VALUES comma-separated]). Cards have bg-slate-800 backgrounds and rounded-xl corners. Slide title '[DASHBOARD TITLE]' top-left. Subtitle '[DATE RANGE]' in gray-500. Use Inter font from Google Fonts.
```

💡 **Remix tip:** Add a fifth full-width card at the bottom as a progress-bar card showing a goal completion percentage using a CSS width animation.

---

### 8. Side-by-Side Comparison Table Slide

**What it builds:** Produces a feature comparison table slide with two product columns and color-coded yes/no/partial indicators.

```
Build a single-file HTML comparison table slide (1280x720px fixed canvas, centered in viewport). Table compares '[PRODUCT A NAME]' vs '[PRODUCT B NAME]' across [NUMBER] criteria. Criteria: [CRITERION 1], [CRITERION 2], [CRITERION 3], [CRITERION 4], [CRITERION 5], [CRITERION 6], [CRITERION 7], [CRITERION 8]. For each criterion, Product A has [A RESULTS comma-separated: yes/no/partial] and Product B has [B RESULTS comma-separated: yes/no/partial]. Use: green filled circle for yes, red X for no, yellow dash for partial. Highlight the '[WINNER PRODUCT]' column header with a [ACCENT COLOR hex] background. Alternating row shading. Slide title '[SLIDE TITLE]' at top. White background. Use Inter font from Google Fonts.
```

💡 **Remix tip:** Add a third column for a competitor product to turn this into a 3-way competitive battlecard — useful for sales enablement slides.

---

### 9. Donut Chart Infographic Slide

**What it builds:** Produces a slide with a pure SVG donut chart, legend, and supporting stat callouts beside it.

```
Build a single-file HTML infographic slide (1280x720px fixed canvas, centered in viewport) with a pure SVG donut chart on the left side. The donut chart shows [NUMBER] segments: [SEGMENT 1 LABEL]: [SEGMENT 1 PERCENT]% in [COLOR 1 hex], [SEGMENT 2 LABEL]: [SEGMENT 2 PERCENT]% in [COLOR 2 hex], [SEGMENT 3 LABEL]: [SEGMENT 3 PERCENT]% in [COLOR 3 hex], [SEGMENT 4 LABEL]: [SEGMENT 4 PERCENT]% in [COLOR 4 hex]. Center of donut shows '[CENTER LABEL]' and '[CENTER VALUE]'. Right side has a vertical legend with colored squares and labels, plus 2 stat callout boxes showing '[CALLOUT 1 LABEL]': '[CALLOUT 1 VALUE]' and '[CALLOUT 2 LABEL]': '[CALLOUT 2 VALUE]'. Slide title '[SLIDE TITLE]' at top. White background. Use inline SVG only, no JS charting libraries.
```

💡 **Remix tip:** Animate each donut segment drawing in sequence using SVG stroke-dasharray and stroke-dashoffset CSS animations for a reveal effect.

---

### 10. Timeline Milestone Infographic

**What it builds:** Produces a horizontal timeline slide with milestone nodes, dates, and description labels along a colored track line.

```
Build a single-file HTML horizontal timeline infographic slide (1280x720px fixed canvas, centered in viewport). Show [NUMBER] milestones along a horizontal line. Milestones: [MILESTONE 1 DATE] — '[MILESTONE 1 TITLE]': '[MILESTONE 1 DESCRIPTION]', [MILESTONE 2 DATE] — '[MILESTONE 2 TITLE]': '[MILESTONE 2 DESCRIPTION]', [MILESTONE 3 DATE] — '[MILESTONE 3 TITLE]': '[MILESTONE 3 DESCRIPTION]', [MILESTONE 4 DATE] — '[MILESTONE 4 TITLE]': '[MILESTONE 4 DESCRIPTION]', [MILESTONE 5 DATE] — '[MILESTONE 5 TITLE]': '[MILESTONE 5 DESCRIPTION]'. The track line is [LINE COLOR hex]. Odd milestones have labels above the line, even ones below. Each node is a filled circle [NODE COLOR hex] with a white border. Animate nodes popping in left-to-right using CSS keyframes on page load. Slide title '[SLIDE TITLE]' at top-left. Use Inter font from Google Fonts.
```

💡 **Remix tip:** Switch to a vertical layout with the line running down the left edge to create a scrollable product changelog or roadmap page.

---

## Interactive Prototypes

### 11. Tabbed Content Panel

**What it builds:** Produces a tabbed interface with 4 tabs, active state styling, and fully swappable content panels using vanilla JS.

```
Build a tabbed content panel in a single HTML file using Tailwind CDN and vanilla JavaScript. Create 4 tabs: '[TAB 1 LABEL]', '[TAB 2 LABEL]', '[TAB 3 LABEL]', '[TAB 4 LABEL]'. Active tab has a bottom border in [ACCENT COLOR hex] and [ACCENT COLOR hex] text. Each panel contains: a heading '[PANEL HEADING]', a paragraph '[PANEL BODY TEXT]', and an optional '[PANEL CTA LABEL]' button. Clicking a tab instantly shows its panel and hides others (no animation needed). Default active tab is Tab 1. Style with white background, gray tab bar, clean sans-serif font (Inter from Google Fonts). Fully responsive: tabs wrap on mobile. No external JS libraries.
```

💡 **Remix tip:** Add URL hash routing (window.location.hash) so each tab is deep-linkable and the correct tab auto-opens on page load based on the URL.

---

### 12. Confirmation Modal Dialog

**What it builds:** Produces a page with a trigger button that opens a centered modal with overlay, confirm/cancel actions, and focus trap.

```
Build a modal dialog prototype in a single HTML file using Tailwind CDN and vanilla JavaScript. The page has a '[TRIGGER BUTTON LABEL]' button centered on screen. Clicking it opens a modal with: a dark semi-transparent overlay (bg-black/50), a centered white dialog card (max-width 480px, rounded-2xl, shadow-2xl), a modal title '[MODAL TITLE]', a body paragraph '[MODAL BODY TEXT]', a primary action button '[CONFIRM LABEL]' in [ACCENT COLOR hex], and a secondary 'Cancel' button. Clicking Cancel or the overlay closes the modal. Clicking Confirm shows an inline success state: replace buttons with a checkmark and '[SUCCESS MESSAGE]'. Modal opens/closes with a CSS scale + opacity transition (200ms). Trap focus inside modal when open. No external JS.
```

💡 **Remix tip:** Turn the modal body into a <form> with input fields to create a quick-add or invite-user modal — add form validation before the confirm action fires.

---

### 13. FAQ Accordion Component

**What it builds:** Produces a smooth-expanding FAQ accordion with 6 items, chevron rotation, and single-open behavior.

```
Build a FAQ accordion component in a single HTML file using Tailwind CDN and vanilla JavaScript. Include [NUMBER] accordion items. Questions: '[Q1]', '[Q2]', '[Q3]', '[Q4]', '[Q5]', '[Q6]'. Answers: '[A1]', '[A2]', '[A3]', '[A4]', '[A5]', '[A6]'. Behavior: only one item open at a time (opening a new item closes the previous). Each row has the question text left-aligned and a chevron-down SVG right-aligned. Open state: chevron rotates 180deg, answer panel expands smoothly using CSS max-height transition (300ms ease). Open item has a [ACCENT COLOR hex] left border. Section heading '[SECTION TITLE]' above. White background. Inter font from Google Fonts. No external JS.
```

💡 **Remix tip:** Allow multiple items to be open simultaneously by removing the close-others logic — better for feature comparison FAQs where users compare multiple answers.

---

### 14. Multi-Step Onboarding Form

**What it builds:** Produces a 3-step form flow with a progress bar, field validation, back/next navigation, and a completion screen.

```
Build a multi-step onboarding form in a single HTML file using Tailwind CDN and vanilla JavaScript. 3 steps total. Step 1 — '[STEP 1 TITLE]': fields for [FIELD 1 LABEL] (text, required), [FIELD 2 LABEL] (email, required). Step 2 — '[STEP 2 TITLE]': fields for [FIELD 3 LABEL] (select with options [OPTION 1], [OPTION 2], [OPTION 3]), [FIELD 4 LABEL] (textarea, optional). Step 3 — '[STEP 3 TITLE]': fields for [FIELD 5 LABEL] (checkbox group: [CHECKBOX 1], [CHECKBOX 2], [CHECKBOX 3]). Top progress bar shows current step as [ACCENT COLOR hex] fill. Next button validates required fields before advancing (shows red border + error message on failure). Back button returns to previous step. Final step has a '[FINISH BUTTON LABEL]' button that shows a full-panel success screen: '[SUCCESS TITLE]' and '[SUCCESS MESSAGE]'. No external JS.
```

💡 **Remix tip:** Replace the final step checkboxes with a plan selection card grid to turn this into a product onboarding + plan selection flow.

---

### 15. Mega Dropdown Navigation Menu

**What it builds:** Produces a top navigation bar with a mega dropdown panel containing categorized links, icons, and a featured CTA card.

```
Build a top navigation bar with a mega dropdown in a single HTML file using Tailwind CDN and vanilla JavaScript. Nav brand: '[BRAND NAME]'. Nav links: '[NAV LINK 1]', '[PRODUCTS]' (has dropdown), '[NAV LINK 3]', '[NAV LINK 4]'. Clicking or hovering 'Products' opens a full-width dropdown panel below the nav (white background, shadow-xl). The panel has 3 columns: Column 1 titled '[COL 1 TITLE]' with 3 links each having an inline SVG icon, label '[LINK LABEL]', and sublabel '[LINK SUBLABEL]'. Column 2 titled '[COL 2 TITLE]' with 3 similar links. Column 3 is a featured card with [ACCENT COLOR hex] background, title '[CARD TITLE]', description '[CARD DESC]', and a white button '[CARD CTA]'. Clicking outside the dropdown closes it. CSS transition: dropdown fades in + slides down 8px (150ms). Inter font from Google Fonts.
```

💡 **Remix tip:** Add keyboard accessibility (arrow keys navigate links, Escape closes the panel) to make this production-ready for accessibility audits.

---

## Presentation Decks

### 16. Magazine-Style Swipe Deck

**What it builds:** Produces a horizontal swipe presentation deck with 5 slides, arrow navigation, dot indicators, and keyboard support.

```
Build a horizontal swipe presentation deck in a single HTML file using Tailwind CDN and vanilla JavaScript. 5 slides, each 1280x720px (fixed canvas centered in viewport). Slide 1: Cover — full [COVER BG COLOR hex] background, large title '[DECK TITLE]', subtitle '[DECK SUBTITLE]', author '[AUTHOR NAME]'. Slide 2: '[SLIDE 2 TITLE]' — white background, 2-column layout with a stat on the left and body text '[SLIDE 2 BODY]' on the right. Slide 3: '[SLIDE 3 TITLE]' — 3-column icon+text feature layout. Slide 4: '[SLIDE 4 TITLE]' — centered blockquote '[QUOTE TEXT]' with attribution '[QUOTE AUTHOR]'. Slide 5: Thank You — dark background, '[CLOSING HEADLINE]', '[CONTACT INFO]'. Left/right arrow buttons navigate slides. Dot indicators at bottom. Left/right keyboard arrows also navigate. Slide transition: CSS translateX slide animation (300ms ease). No external JS.
```

💡 **Remix tip:** Add a fullscreen button that calls document.documentElement.requestFullscreen() for a true presentation mode experience.

---

### 17. Bold Cover Slide

**What it builds:** Produces a single bold cover slide with a gradient background, large display headline, eyebrow label, and presenter info.

```
Build a single cover slide in a single HTML file (1280x720px fixed canvas, centered in viewport). Background: a diagonal CSS gradient from [GRADIENT START hex] to [GRADIENT END hex]. Layout centered vertically and horizontally. Elements top to bottom: a small eyebrow label '[EYEBROW TEXT]' in a pill badge (white text, semi-transparent white border), a large display headline '[MAIN HEADLINE]' (font-size 72px, font-weight 800, white, tight letter-spacing), a subtitle '[SUBTITLE TEXT]' (font-size 24px, white, opacity 80%), a horizontal divider line (white, 80px wide, 2px, centered, margin 32px), presenter name '[PRESENTER NAME]' and role '[PRESENTER ROLE]' in white opacity-70. Bottom-right corner: company logo placeholder (white rounded rectangle 120x40px with '[LOGO TEXT]'). Use Inter font from Google Fonts. Absolutely no JavaScript needed.
```

💡 **Remix tip:** Add a subtle animated grain texture overlay using an SVG feTurbulence filter for a premium editorial magazine feel.

---

### 18. Section Divider Transition Slide

**What it builds:** Produces a bold section divider slide with a large section number, section title, and brief description on a colored background.

```
Build a section divider slide in a single HTML file (1280x720px fixed canvas, centered in viewport). Background color [SECTION BG COLOR hex]. Left half: a massive section number '[SECTION NUMBER]' (font-size 220px, font-weight 900, color white opacity-10, absolutely positioned). Center-left content: a small label '[SECTION LABEL]' (uppercase, letter-spacing wide, [ACCENT COLOR hex] text), a large section title '[SECTION TITLE]' (font-size 56px, font-weight 800, white), a description paragraph '[SECTION DESCRIPTION]' (white, opacity 75%, max-width 480px). Right half: a decorative abstract shape — a large circle (600px, border: 2px solid white opacity-20, positioned right-center overlapping edge). Bottom: a progress indicator showing '[CURRENT SECTION] of [TOTAL SECTIONS]' in white opacity-50. Use Inter font from Google Fonts. No JavaScript.
```

💡 **Remix tip:** Use a different background color for each section divider slide to create a color-coded chapter system throughout your deck.

---

### 19. Pull Quote Highlight Slide

**What it builds:** Produces an editorial-style quote slide with a large quotation mark, styled quote text, attribution, and accent details.

```
Build a pull quote slide in a single HTML file (1280x720px fixed canvas, centered in viewport). Background: white. Layout is centered with max-width 800px. Elements: a giant decorative opening quotation mark (font-size 200px, [ACCENT COLOR hex], opacity 15%, absolutely positioned top-left of content area), the quote text '[FULL QUOTE TEXT]' (font-size 36px, font-weight 600, dark gray #1F2937, line-height 1.4), a horizontal rule (60px wide, 3px, [ACCENT COLOR hex], left-aligned, margin 24px 0), attribution block with '[SPEAKER NAME]' (font-weight 700, dark) and '[SPEAKER TITLE + COMPANY]' (gray-500). Bottom-left corner: a small '[CONTEXT LABEL e.g. Customer Story]' tag. Optional right-side accent: a vertical [ACCENT COLOR hex] bar (4px wide, full height). Use Playfair Display for the quote and Inter for attribution, both from Google Fonts. No JavaScript.
```

💡 **Remix tip:** Set the background to a dark color and invert text to white for a high-contrast quote slide that photographs well on stage.

---

### 20. Visual Roadmap Timeline Slide

**What it builds:** Produces a quarterly roadmap slide with a horizontal 4-quarter track, color-coded swim lanes, and milestone cards.

```
Build a product roadmap timeline slide in a single HTML file (1280x720px fixed canvas, centered in viewport). Show a 4-quarter horizontal timeline: Q1 [YEAR], Q2 [YEAR], Q3 [YEAR], Q4 [YEAR]. Three swim lanes labeled '[LANE 1 NAME]', '[LANE 2 NAME]', '[LANE 3 NAME]'. Each lane has milestone cards placed in the appropriate quarter column. Milestones: Lane 1 — Q1: '[M1]', Q3: '[M2]'. Lane 2 — Q2: '[M3]', Q4: '[M4]'. Lane 3 — Q1: '[M5]', Q2: '[M6]', Q4: '[M7]'. Cards are colored by lane: Lane 1 [COLOR 1 hex], Lane 2 [COLOR 2 hex], Lane 3 [COLOR 3 hex]. Quarter columns have alternating light gray backgrounds. Slide title '[ROADMAP TITLE]' and '[DATE RANGE]' at top. Current quarter (Q[CURRENT]) has a subtle [ACCENT COLOR hex] top border highlight. Use Inter font from Google Fonts. No JavaScript.
```

💡 **Remix tip:** Add a 'Now' vertical indicator line over the current date using absolute positioning to make the roadmap feel live and real-time.

---

## Animation & Polish

### 21. CSS Keyframe Page Load Animation

**What it builds:** Produces a landing page hero where each element (eyebrow, headline, subtext, CTA) animates in sequentially on load.

```
Build a single-file HTML landing page hero section using Tailwind CDN where every element animates in on page load using pure CSS keyframes. Animation sequence: 1) eyebrow badge '[EYEBROW TEXT]' fades up from 20px below, 0→1 opacity, 0ms delay. 2) Headline '[HEADLINE TEXT]' fades up, 80ms delay. 3) Subheadline '[SUBHEADLINE TEXT]' fades up, 160ms delay. 4) Primary CTA '[CTA TEXT]' fades up, 240ms delay. 5) Secondary link '[SECONDARY LINK TEXT]' fades up, 320ms delay. 6) Hero image placeholder (gray rounded-2xl, 600x400px) fades in + scales from 0.96 to 1, 400ms delay. All animations use ease-out cubic-bezier(0.16, 1, 0.3, 1), duration 600ms. No JavaScript. Tailwind for layout only — all animations in a <style> block. Use Inter from Google Fonts.
```

💡 **Remix tip:** Add animation-fill-mode: backwards to each element so they stay invisible until their delay fires, preventing a flash of unstyled content.

---

### 22. Animated Canvas Particle Background

**What it builds:** Produces a hero section with a full-screen HTML5 Canvas particle network animation behind the headline and CTA.

```
Build a single-file HTML hero section with a full-screen Canvas particle network animation as the background. Canvas fills the entire viewport. Animate [NUMBER e.g. 80] particles: each is a small circle (radius 2px, color '[PARTICLE COLOR hex]', opacity 0.6) moving in random directions at low speed. Draw lines between any two particles within [CONNECTION DISTANCE e.g. 120]px of each other (line color '[LINE COLOR hex]', opacity proportional to distance). Particles wrap around viewport edges. Over the canvas (position: relative, z-index: 10): centered hero content with headline '[HEADLINE TEXT]' (white, font-size 56px, font-weight 800), subheadline '[SUBHEADLINE TEXT]' (white opacity-80), and a CTA button '[CTA TEXT]' with solid [BUTTON COLOR hex] background. Background behind canvas is dark ([BG COLOR hex]). Use requestAnimationFrame loop. Single file, vanilla JS only.
```

💡 **Remix tip:** Make particles mouse-interactive: on mousemove, push particles away from the cursor position within a 100px radius for a repulsion effect.

---

### 23. Scroll-Triggered Reveal Animations

**What it builds:** Produces a multi-section landing page where feature cards and stat numbers animate in as they enter the viewport via IntersectionObserver.

```
Build a single-file HTML landing page using Tailwind CDN with scroll-triggered reveal animations using vanilla JS IntersectionObserver (no external libraries). Page sections: 1) Static hero with headline '[HERO HEADLINE]'. 2) A row of 3 stat callouts — '[STAT 1 VALUE]' '[STAT 1 LABEL]', '[STAT 2 VALUE]' '[STAT 2 LABEL]', '[STAT 3 VALUE]' '[STAT 3 LABEL]' — each counting up from 0 to its value when it enters viewport (vanilla JS counter animation, 1000ms duration). 3) A 3-column feature card grid where each card fades in and slides up (translateY 40px → 0, opacity 0 → 1) with staggered 100ms delays as the section enters viewport. 4) A CTA section '[CTA HEADLINE]' and '[CTA BUTTON TEXT]' that fades in. All animations defined in CSS, triggered by adding an 'is-visible' class via IntersectionObserver.
```

💡 **Remix tip:** Add a horizontal slide-in direction based on card position: left cards slide from the left, right cards from the right, center cards from below.

---

### 24. Hover Microinteractions for UI Elements

**What it builds:** A component library showcasing tactile hover microinteractions for buttons, cards, links, and icons using pure CSS and minimal JS.

```
Build a self-contained HTML page that demonstrates a suite of hover microinteractions for common UI elements. Include: (1) Buttons with a magnetic pull effect that slightly follows the cursor using JS mousemove, a ripple burst on click, and a subtle scale + shadow lift on hover. (2) Cards that tilt in 3D perspective toward the cursor (tilt.js-style, vanilla JS), reveal a hidden action bar sliding up from the bottom, and show a shimmer highlight that tracks mouse position via CSS custom properties. (3) Icon buttons that wobble (rotation keyframe) on hover, change stroke color with a drawing/unDrawing SVG stroke-dashoffset animation, and display a tooltip that pops in with a spring-like overshoot (cubic-bezier). (4) Text links with an underline that fills left-to-right on hover and reverses right-to-left on mouse-out using a pseudo-element scaleX transform. All interactions must feel instantaneous (≤100ms delay) and use hardware-accelerated properties (transform, opacity) only. Provide a dark neutral background (#111) so the effects read clearly. Add a small legend labeling each interaction type.
```

💡 **Remix tip:** Swap the magnetic pull radius (currently ~30px) to a larger value like 80px for a more dramatic cursor-chasing effect on hero CTA buttons.

---

### 25. Skeleton & Progress Loading States

**What it builds:** A fully animated loading-state system with skeleton screens, progress indicators, and smooth content-reveal transitions for a dashboard UI.

```
Create a single HTML file that simulates a realistic dashboard loading experience with three phases: (1) Skeleton screens — render placeholder versions of a stat card row, a data table (5 rows × 4 cols), and a sidebar nav using gray rounded rectangles animated with a left-to-right shimmer wave (CSS linear-gradient animation, staggered per element). (2) Progress indicators — include a thin top-of-page linear progress bar that eases from 0% to 100% over 2.5 seconds (non-linear, fast start / slow finish easing), a circular spinner for an avatar image slot using SVG stroke-dasharray animation, and a percentage counter inside the circle that ticks up in real time. (3) Content reveal — after the simulated load completes, replace each skeleton with real content using a staggered fade-up animation (translateY 12px → 0, opacity 0 → 1, 60ms stagger between cards). Add a 'Reload' button that resets all states so the full sequence replays. Use CSS custom properties for shimmer color and duration so they're easy to theme. The overall color palette should be light mode (#f5f5f5 background, white cards) with a blue (#3b6ef8) accent for the progress bar.
```

💡 **Remix tip:** Change the shimmer gradient colors from gray to a brand hue (e.g., soft purple) and increase the animation duration to 2s for a more luxurious feel on marketing pages.

---
