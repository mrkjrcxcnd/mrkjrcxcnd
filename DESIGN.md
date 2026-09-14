---
name: MJ Exconde GitHub Profile
description: Screenshot-led dark terminal artwork with preserved ASCII identity.
colors:
  background: "#0d1117"
  border: "#262d35"
  foreground: "#c9d1d9"
  muted: "#8b949e"
  terminal-green: "#009100"
  ascii-green: "#008e00"
  heading-blue: "#58a6ff"
  metric-green: "#008f51"
typography:
  body: {fontFamily: 'Menlo, Consolas, "DejaVu Sans Mono", monospace', fontSize: "12px", fontWeight: 400}
rounded: {terminal: "14px", calendar: "3px", strip: "10px", pill: "15px"}
---

## Overview
The supplied screenshot fixes this GitHub README's dark terminal composition: portrait and neofetch biography, contribution calendar, large ASCII wordmark, metrics, then scrolling technology pills. Preserve the exact 75 × 150 portrait characters and five wordmark rows in `profile/config.json`.

## Colors
Neutral background, border, foreground, and muted tokens frame green identity and metrics; blue separates biography subsections. The count-based calendar ramp is `#161b22`, `#0e4429`, `#006d32`, `#26a641`, `#39d353`, `#69f0a0`. Pills use `#0c241e`, `#005c3b` borders, and `#d5e9e4` text on a `#10161c` strip.

## Typography
Use the local monospace fallback stack above; no downloaded fonts. Labels and prose range from 10–15 SVG units, with 34-unit desktop / 25-unit mobile metric values. Preserve ASCII whitespace and renderer-controlled text lengths; portrait text is 3.42 units, wordmark text 14 desktop / 8 mobile.

## Layout
Desktop artwork is 958 × 1236: a 344 × 374 portrait at (58, 48), a 458 × 374 biography at (448, 48), and an 844 × 286 calendar below. Mobile is 480 × 1614 with 24-unit side margins, stacked panels, a calendar split after 27 weeks, and metrics in two rows of three. README `<picture>` selects `assets/profile-mobile.svg` at ≤600 CSS pixels; `assets/profile.svg` is the full-width fallback.

## Elevation & Depth
Flat surfaces use thin borders and dividers without shadows. Terminal headers are 28 units tall, with red, amber, and green window dots.

## Shapes
Use the corner radii above for terminals, calendar cells, the clipped technology strip, and pills. The metrics enclosure stays rectangular; portrait and biography interiors use compact, aligned terminal rows.

## Components
The technology strip repeats text pills in a 95-second linear loop and stops under `prefers-reduced-motion: reduce`. SVG title/description and README alt text describe the artwork; real text links and expandable biography supply accessible profile details. The calendar and metrics reflect `profile/github-data.json`; daily/manual GitHub Actions refreshes use the bot identity.

## Do's and Don'ts
Do edit identity, stack, portrait, and wordmark in `profile/config.json`; edit geometry in the Python standard-library renderer `scripts/generate_profile.py`, then regenerate both SVGs. Follow `profile/README.md` for offline rendering and API refresh. Don't redraw the preserved ASCII, invent contribution activity, or introduce remote widget images, fonts, or a website framework.
