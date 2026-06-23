Create a single-file HTML presentation using Tailwind CSS and native JavaScript. This is for a 1.5-minute university project pitch about an AI Freshman Chatbot named "Nova" for Xiamen University Malaysia (XMUM).

### [Design & Interaction Constraints]
1. **Single File**: All HTML, CSS, and JS must be in one file. NO external images. You MUST generate rich inline SVG icons and CSS shapes to make the slides visually engaging.
2. **Navigation**: Smooth horizontal sliding transitions. Include left/right keyboard arrow support, UI navigation arrows, and a slide counter.
3. **Visual Style**: Rich, modern tech-corporate aesthetic. DO NOT make it overly empty. Fill the whitespace strategically using:
   - Subtle background patterns (CSS grids, dots, or faint glowing gradient blobs).
   - Glassmorphism effects or styled cards with soft shadows (`shadow-lg`, `rounded-xl`).
   - Decorative accents (colored borders, dividers, subtle watermark text in the background).
4. **Color Palette**: 
   - Backgrounds: Off-White (`#f8fafc`) with subtle Slate/Navy accents.
   - Primary Brand: Deep Navy (`#1f2a52`)
   - Highlight/Accent: Classic Gold (`#d6a93f`)
   - Success/Data: Emerald Green (`#2f9e5e`)

---

### [Slide Content & Rich Layout Requirements]

**Slide 1: Cover (The Hook)**
- **Background**: Faint, giant watermark text saying "NOVA" across the background.
- **Center Card**: A beautiful glass-like or bordered central card.
- **Top Badge**: "PROJECT SHOWCASE" inside a Gold pill-shaped badge.
- **Title**: "XMUM Freshman FAQ Chatbot" with a gradient text effect (Navy to Light Navy).
- **Subtitle**: "Code Name: NOVA" with a stylized inline SVG robot/AI icon.
- **Footer**: A pulsing "Press Right Arrow to Start" text.

**Slide 2: Brand & UI Design**
- **Layout**: 2-column. Title on the left, visual content on the right.
- **Left**: Title "Visual Identity" with a decorative gold underline.
- **Right (Rich Grid)**: 3 visually distinct cards:
  - Card 1 (Navy & Gold): Include actual colored circles/squares showing the palette.
  - Card 2 (Blueprint Watermark): Include a small CSS/SVG abstract wireframe illustration.
  - Card 3 (Pixel-Perfect): Include an inline SVG ruler or layout icon.

**Slide 3: Explainable AI (XAI)**
- **Background**: Subtle tech-grid pattern.
- **Left**: Title "Breaking the Blackbox". Below it, a vertical list of feature chips (pill shapes with icons): [7 Categories], [Real-time Metadata], [Info Rail Arch].
- **Right (Data Viz)**: A large, rich dashboard-style card.
  - Huge Text: "95%" in Emerald Green.
  - Visual: A CSS-based animated progress bar or circular ring filled to 95%.
  - Label: "Confidence Score Display".

**Slide 4: Engineering & Architecture**
- **Layout**: A "server/node" connection layout or a 3-step horizontal flow map.
- **Title**: "Zero-Dependency Architecture".
- **Nodes (Cards connected by CSS lines/arrows)**:
  1. Native HTML5 + Tailwind
  2. NO React/Webpack
  3. CORS-Free Local Execution
- **Highlight Area**: A glowing dark card featuring the stat "0ms Load Time" with a lightning bolt SVG icon.

**Slide 5: Micro-Interactions**
- **Layout**: A 3-column grid of rich, interactive-looking cards. Give them distinct borders and hover states (`hover:-translate-y-1`).
- **Title**: "UX Details".
- **Card 1**: "Dynamic Bouncing" (Show a mini mockup of 3 typing dots using CSS animations).
- **Card 2**: "Regex Auto-Linkify" (Show a fake URL stylized as a clickable blue link).
- **Card 3**: "Fluid Scroll" (Include a scroll-wheel or arrow SVG icon).

**Slide 6: Conclusion / CTA**
- **Layout**: Central focus, highly engaging.
- **Background**: Soft radial gradient (Navy to transparent).
- **Center element**: A large simulated "Chat Bubble" pointing to the title.
- **Title**: "Let's chat with Nova."
- **Action**: A large, glowing Gold button (non-functional but visually striking) saying "Start Live Demo".

---
Ensure the code is clean, responsive, heavily utilizes Tailwind utilities for rich visuals (cards, gradients, rings, shadows), and runs immediately upon opening.