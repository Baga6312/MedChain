---
name: Clinical Integrity
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#42484b'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#72787c'
  outline-variant: '#c1c7cc'
  surface-tint: '#426373'
  primary: '#001e2a'
  on-primary: '#ffffff'
  primary-container: '#0f3443'
  on-primary-container: '#7b9daf'
  inverse-primary: '#a9cbde'
  secondary: '#006781'
  on-secondary: '#ffffff'
  secondary-container: '#8fdfff'
  on-secondary-container: '#00647d'
  tertiary: '#001f26'
  on-tertiary: '#ffffff'
  tertiary-container: '#003640'
  on-tertiary-container: '#00a7c3'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#c5e8fb'
  primary-fixed-dim: '#a9cbde'
  on-primary-fixed: '#001f2a'
  on-primary-fixed-variant: '#294b5b'
  secondary-fixed: '#b9eaff'
  secondary-fixed-dim: '#81d1f0'
  on-secondary-fixed: '#001f29'
  on-secondary-fixed-variant: '#004d62'
  tertiary-fixed: '#acedff'
  tertiary-fixed-dim: '#4cd7f6'
  on-tertiary-fixed: '#001f26'
  on-tertiary-fixed-variant: '#004e5c'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: 0em
  body-lg:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0.005em
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.03em
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-tablet: 1.5rem
  margin-desktop: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1.25rem
  space-xl: 2rem
---

## Brand & Style

The design system establishes a high-assurance, clinical-grade interface engineered for cryptographic medical records management and sensitive health data exchanges. Designed to serve three distinct operational perspectives—Patients, Practitioners, and Infrastructure Administrators—the visual tone replaces consumer-facing flourishes with absolute legibility, institutional poise, and operational precision.

The aesthetic philosophy draws strictly from **Modern Clinical Functionalism**:
- Zero superfluous marketing decor, ambiguous iconography, or performative whitespace.
- A foundational architecture built upon structural clarity, data-dense layouts, clear permission hierarchies, and unambiguous cryptographic/audit indicators.
- Emotional resonance centered on absolute trust, diagnostic calm, security, and institutional reliability without feeling punitive or archaic.

## Colors

The palette leverages a deep clinical spectrum optimized for high-contrast scanning (achieving rigorous WCAG AAA compliance on all primary data reading surfaces).

### Primary & Brand Accents
- **Primary Deep Petrol (`#0f3443`)**: Foundation for primary navigation bars, dominant structural framing, high-emphasis headers, and critical modal confirmations.
- **Secondary Slate Petrol (`#0e7490`)**: Interactive triggers, active navigation items, table focus states, and primary tab indicators.
- **Tertiary Cyan/Teal (`#06b6d4`)**: System indicators, active cryptographic signatures, live synchronizing badges, and selected row highlights.

### Neutral Foundation & Surfaces
- **Canvas Base (`#f8fafc`)**: Crisp, light medical-grade backdrop that minimizes retinal fatigue.
- **Surface Elevation (`#ffffff`)**: Pure white primary containers, table bodies, and inspect panels.
- **Subtle Surface Container (`#f1f5f9`)**: Form field backdrops, read-only audit tracks, and nested metadata blocks.
- **Border Crisp Line (`#cbd5e1`)**: Razor-sharp 1px boundary lines for tabular frames, panel headers, and segmented controls.
- **Text Primary (`#0f172a`)**: Deep ink slate ensuring AAA-level optical clarity.
- **Text Secondary (`#475569`)**: Supporting metadata, table column descriptors, and timestamps.

### Clinical & Security Status System
- **Authorized / Success (`#059669`)**: Verified consent, validated cryptographic transaction, normal lab ranges.
- **Attention / Pending (`#d97706`)**: Access pending approval, temporary delegation, expiring credential.
- **Critical / Security Revocation (`#e11d48`)**: Unverified access attempt, revoked ledger block, critical pathology alert, denial states.

## Typography

Typography prioritizes fast numerical comprehension, clinical data scanning, and high legibility across diverse display hardware:
- **Headlines (`Plus Jakarta Sans`)**: Clean, authoritative, geometric yet humanized to provide structured reassurance in critical dashboards and role portals.
- **Body & Data Displays (`Inter`)**: Engineered for tabular density, uniform optical rhythm, and rapid data extraction. Numerics must render using tabular lining figures (`font-feature-settings: "tnum" 1`) across all metric views and audit grids.
- **Cryptographic & Identifiers (`JetBrains Mono`)**: Strict monospace hierarchy deployed for public keys, patient anonymized hashes, transaction IDs, and consent audit hashes.

## Layout & Spacing

The layout model implements a structured, utility-dense 12-column layout designed to accommodate complex records, patient timelines, and split-screen medical charts without horizontal scrolling.

### Breakpoints & Layout Adaptations
- **Mobile (< 768px)**: 4-column flow. Navigational sidebars collapse to an explicit accessible drawer; high-density tables reformat into stacked key-value diagnostic blocks. Standard outer canvas margin is `margin` (16px).
- **Tablet (768px - 1024px)**: 8-column flow with collapsed icon navigation. Toolbars display high-frequency filters natively while shifting secondary tools into segmented menus. Outer canvas margin expands to `margin-tablet` (24px).
- **Desktop (1024px+)**: 12-column fluid-grid architecture bounded inside high-resolution widescreen monitors. Permanent contextual sidebars, simultaneous dual-pane inspection views (e.g., patient identity ledger beside encrypted DICOM/EHR records), and sticky filter toolbars. Outer canvas margin is `margin-desktop` (32px).

### Internal Rhythm
Margins within cards and modals follow strict, compressed increments (`space-sm` to `space-lg`) to preserve context without excessive vertical travel.

## Elevation & Depth

The design system eschews dynamic decorative drop-shadows and blurred glass treatments in favor of **Crisp Low-Contrast Outlines & Tonal Stratification**. Health practitioners and auditors require deterministic boundaries that display reliably across calibrated hospital displays and mobile tablets.

### Stratification Model
- **Level 0 (Canvas Base)**: `#f8fafc` background.
- **Level 1 (Data Cards, Record Panes)**: Crisp pure white (`#ffffff`) background bounded by a continuous 1px `#cbd5e1` or `#e2e8f0` structural rule. No drop shadows.
- **Level 2 (Dropdown Menus, Toolbars, Floating Filters)**: `#ffffff` surface, bounded by 1px `#94a3b8` outline, accented with an ambient clinical shadow: `0 4px 6px -1px rgba(15, 23, 42, 0.08), 0 2px 4px -2px rgba(15, 23, 42, 0.04)`.
- **Level 3 (Modal Dialogues, Consent Grant Overlays)**: Pure `#ffffff` surface, sharp border (`1px solid #64748b`), surrounded by a structured semi-opaque clinical scrim (`rgba(15, 52, 67, 0.65)`).

## Shapes

The design system employs **Soft (`1`)** geometry:
- Default radius: `0.25rem` (4px) for controls, inputs, table cell selections, and micro-tags.
- Medium/Card radius: `0.5rem` (8px) for containers, modals, and panel wrappers.
- System tags/chips: Slightly pill-shaped or capped at `0.25rem` to convey structured categorization rather than playful tags.

This controlled roundedness conveys modern engineering discipline while softening rigid rectangular data interfaces just enough to avoid sterile industrial brutality.

## Components

### Buttons
- **Primary**: Solid Deep Petrol (`#0f3443`), text `#ffffff`. Hover: `#164e63`. Focused: 2px offset ring in `#06b6d4`. 
- **Secondary**: Outlined 1px `#0e7490`, transparent fill, text `#0e7490`. Hover: `#f0fdfa`.
- **Destructive/Revocation**: Solid `#e11d48`, white text. Used for revoking doctor access permissions, deleting audit records, or declining patient requests.
- **Geometry**: Compact 36px standard height for tables and dashboards; 40px for modal actions. Corner radius `4px`.

### Data Tables & Status Badges
- **Table Density**: Header row 36px tall (`#f1f5f9` fill, text `#475569`, 11px uppercase bold). Body row 44px with a 1px border-bottom `#e2e8f0`. Zebra striping is omitted in favor of explicit row hover states (`#f8fafc`).
- **Status Badges**: Subtly tinted container with a high-contrast dot indicator and bold label:
  - *Active/Valid*: Green tint (`#ecfdf5`), border `#a7f3d0`, text `#065f46`.
  - *Pending Consent*: Amber tint (`#fffbeb`), border `#fde68a`, text `#92400e`.
  - *Revoked/Forbidden*: Red tint (`#fff1f2`), border `#fecdd3`, text `#9f1239`.

### Consent & Permission Modal
- Dedicated dialog centered on screen containing explicit role indicators (Patient / Practitioner / Org), cryptographic hash verification, and clear duration tags (e.g., "Access expires in 72h"). Must require explicit confirmation toggles before primary action unlocks.

### Input Fields & Search Bars
- Background `#ffffff`, border 1px `#cbd5e1`, text `#0f172a`, height 36px.
- Focus state: Border `#0e7490` with an outer ring `0 0 0 1px #0e7490`. Clear error states show red outlines with immediate contextual inline descriptions below the field.

### System & 403 Access Denied States
- Clean, empty-slate panels bounded in `#e2e8f0`. Centered security badge, cryptographic error reference code in `JetBrains Mono`, clear explanation of permission deficiencies, and a secondary action to request consent or return to the authenticated dashboard.