# Process Specification: UX & Frontend Guidelines

**Spec ID**: `002-migrate-ux-guidelines`
**Branch**: `002-migrate-dev-practices`
**Created**: 2026-02-23
**Status**: Active
**Supersedes**: `spec/process/ux-guidelines.speckit.md` (legacy informal doc)
**Applies to**: All frontend work — components, pages, styles, interactions, and any
change that touches the user interface.

---

## Purpose

Define the authoritative, enforceable UX and frontend standards for the AI Marketing
Agent. Any contributor — human or AI agent — MUST satisfy every rule in this spec
before a frontend change is considered mergeable.

---

## 1. Core UX Rules (Non-Negotiable)

### UX-001 — Visual Identity (Apple-Inspired)

The AI Marketing Agent follows a consistent Apple-inspired visual language. All new
and modified UI MUST conform to these design tokens and principles:

**Typography**
- Font family: system-ui / `-apple-system` stack as the default; no decorative or
  display fonts unless explicitly specified in a feature spec.
- Font sizes follow a strict scale: `text-sm` (14px), `text-base` (16px),
  `text-lg` (18px), `text-xl` (20px), `text-2xl` (24px) — use Tailwind utility
  classes only, never inline `style` font sizes.
- Font weights: `font-normal` for body, `font-medium` for labels and secondary
  headings, `font-semibold` for primary headings. Bold (`font-bold`) reserved for
  emphasis only.
- Line height: `leading-relaxed` (1.625) for body text; `leading-tight` for headings.

**Spacing & Layout**
- Generous whitespace is mandatory. Default padding for cards and panels: `p-6`
  (24px). Page-level horizontal padding: `px-4 sm:px-6 lg:px-8`.
- Section spacing: `space-y-6` between related groups; `space-y-10` between
  unrelated sections.
- Never use arbitrary Tailwind values (e.g. `p-[13px]`) unless a design constraint
  requires it and the value is documented in the component's JSDoc.

**Color Palette**
- Background: `bg-white` / `dark:bg-gray-950` (surface), `bg-gray-50` /
  `dark:bg-gray-900` (page canvas).
- Text: `text-gray-900` (primary), `text-gray-600` (secondary), `text-gray-400`
  (placeholder/disabled).
- Accent (primary action): `bg-blue-600` / `hover:bg-blue-700`; text on accent:
  `text-white`.
- Destructive: `bg-red-600` / `text-red-600` for errors and delete actions.
- Border: `border-gray-200` / `dark:border-gray-800`.

**Shadows & Depth**
- Cards and elevated panels: `shadow-sm` only. Never use `shadow-lg` or `shadow-xl`
  on standard content cards — reserve those for modals and popovers.
- Modals/dialogs: `shadow-xl` with a semi-transparent backdrop (`bg-black/50`).
- No `drop-shadow` CSS filter — use Tailwind `shadow-*` only.

**Radius**
- Default: `rounded-lg` (8px) for cards, panels, and buttons.
- Small controls (badges, tags): `rounded-md` (6px).
- Pills / full-round: `rounded-full` only for avatar thumbnails and icon-only buttons.

### UX-002 — Component Consistency (shadcn/ui)

- UX-002a: All interactive UI elements (buttons, inputs, selects, dialogs, toasts,
  dropdowns, checkboxes, radio groups, tabs) MUST use `shadcn/ui` components.
  Never implement custom equivalents from scratch.
- UX-002b: Custom CSS (`.css` files or `style={{}}` props) is forbidden unless
  ALL of the following are true:
  1. The desired style cannot be achieved with Tailwind utility classes.
  2. The deviation is documented in the component's JSDoc with the reason.
  3. The deviation is reviewed in the PR.
- UX-002c: Do not introduce additional component libraries (e.g. MUI, Chakra,
  Radix directly) without a constitution-level decision and a spec update.
- UX-002d: `shadcn/ui` component variants MUST NOT be overridden by wrapping with
  `!important` CSS. Use the `className` prop with Tailwind utilities to extend;
  never fight the variant system.

### UX-003 — Feedback Loops (Async Actions & Errors)

Every interaction that involves an asynchronous operation or a potential failure
MUST provide explicit feedback.

**Loading states**
- UX-003a: Any component that fetches data on mount MUST show a `Skeleton` (from
  `shadcn/ui`) while data is loading. Never show an empty or partially rendered UI.
- UX-003b: Any button or form that triggers an async action MUST show a `Spinner`
  (inline, within the button) while the action is in-flight and MUST be disabled
  to prevent double-submission.
- UX-003c: Page-level data loading uses `<LoadingState />` as the full-page
  placeholder (see also the i18n guard in UX-004).

**Error states**
- UX-003d: Every async error MUST be surfaced via `<AIErrorDisplay>`. Never use
  `alert()`, `console.error()` only, or raw `<p>` tags to show errors to users.
- UX-003e: The `error_details` object passed to `<AIErrorDisplay>` MUST include
  `correlation_id`. If the backend did not return one, generate a client-side UUID
  and attach it before displaying.
- UX-003f: After a recoverable error, the user MUST be given an actionable path
  forward (retry button, navigation link, or support message). Dead-end error
  screens are not acceptable.

### UX-004 — i18n First (No Hardcoded UI Text)

- UX-004a: No UI-visible string (labels, button text, placeholders, error messages,
  empty-state copy, ARIA labels) may be hardcoded in JSX. Every string MUST come
  from the translation object `t`.
- UX-004b: Use `getTranslations()` from `@/i18n` exclusively. Never import from
  `next-intl` directly.
- UX-004c: Every component that uses translations MUST include the loading guard
  before any JSX that references `t`:

  ```tsx
  if (loading || !t.pages) return <LoadingState />;
  ```

- UX-004d: Translation keys MUST follow the namespace convention
  `pages.<pageName>.<element>` (e.g. `t.pages.dashboard.title`). Never use flat
  or ambiguous keys.
- UX-004e: Backend error responses return a `user_message` i18n key. The frontend
  MUST resolve this key via `getTranslations()` before displaying it. Never display
  raw backend error strings to the user.
- UX-004f: Both `en` and `pt` locale files under `frontend/src/i18n/locales/` MUST
  be updated in the same PR as any new UI text. Untranslated strings in either
  locale are a merge blocker.

### UX-005 — Responsiveness (Mobile-First)

- UX-005a: All layouts MUST be designed mobile-first. Start from the smallest
  viewport and add responsive breakpoint overrides (`sm:`, `md:`, `lg:`) as needed.
- UX-005b: No fixed pixel widths on containers or panels. Use `w-full`, `max-w-*`,
  or grid/flex layouts that reflow naturally.
- UX-005c: Touch targets (buttons, links, interactive icons) MUST be at least 44×44
  px (`min-h-[44px] min-w-[44px]`) on mobile viewports.
- UX-005d: Tables with many columns MUST use horizontal scroll (`overflow-x-auto`)
  on small screens, not truncation or overflow clipping.
- UX-005e: Test every new or modified page at three breakpoints before opening a PR:
  - Mobile: 375px wide (iPhone SE baseline)
  - Tablet: 768px wide
  - Desktop: 1280px wide

---

## 2. React Architecture Rules

These rules govern how components are structured; violations break React's contract
and cause runtime hook-order errors.

- UX-ARCH-001: All hooks (`useState`, `useEffect`, `useCallback`, `useMemo`, custom
  hooks) MUST be declared at the top of the component function, before any
  conditional logic or early returns.
- UX-ARCH-002: No hooks inside conditionals, loops, nested functions, or after early
  returns. Any hook that depends on a condition MUST internalize that condition
  inside the hook itself.
- UX-ARCH-003: Use React functional components only. Class components are forbidden.
- UX-ARCH-004: Shared UI logic (e.g. data fetching patterns, error boundary wiring)
  MUST be extracted into custom hooks in `frontend/src/hooks/`. Components should
  contain only rendering logic.
- UX-ARCH-005: Pages live in `frontend/src/app/[locale]/`. Shared components live in
  `frontend/src/components/`. Never duplicate layout logic across pages — extract a
  shared shell component instead.

---

## 3. Accessibility Baseline

- UX-A11Y-001: Meet WCAG 2.1 AA contrast ratios for all text on backgrounds.
  (Minimum 4.5:1 for normal text, 3:1 for large text.)
- UX-A11Y-002: All interactive elements MUST be keyboard-navigable and have visible
  focus rings. Never remove `outline` without providing an equivalent focus
  indicator.
- UX-A11Y-003: All images and icon-only buttons MUST have descriptive `alt` or
  `aria-label` attributes.
- UX-A11Y-004: Dynamic content changes (toasts, dialogs, error messages) MUST
  announce themselves to screen readers via appropriate ARIA live regions or roles.
  `shadcn/ui` handles this for its own components; custom components must implement
  it manually.

---

## 4. Frontend Acceptance Criteria

A frontend change is **complete** when ALL of the following are true:

| ID     | Criterion                                                                         |
|--------|-----------------------------------------------------------------------------------|
| AC-001 | React DevTools shows no hook-order warnings (UX-ARCH-001/002).                    |
| AC-002 | All interactive elements use `shadcn/ui`; no unsanctioned custom CSS (UX-002).   |
| AC-003 | Every async action shows a Skeleton/Spinner loading state (UX-003a/003b).         |
| AC-004 | Every error surfaced via `<AIErrorDisplay>` with `correlation_id` (UX-003d/003e). |
| AC-005 | No hardcoded UI strings; both `en` and `pt` locale files updated (UX-004).        |
| AC-006 | Layout verified at 375px, 768px, and 1280px viewports (UX-005e).                 |
| AC-007 | WCAG AA contrast and keyboard navigation pass (UX-A11Y-001/002).                  |
| AC-008 | Visual output matches Apple-inspired design tokens (UX-001).                      |

---

## Changelog

| Date       | Change                                                                      |
|------------|-----------------------------------------------------------------------------|
| 2026-02-23 | Migrated from legacy informal doc; added UX-001 (Visual Identity tokens),   |
|            | UX-002 (shadcn/ui consistency), UX-003 (feedback loops), UX-004 (i18n       |
|            | first), UX-005 (mobile-first), React architecture rules, accessibility       |
|            | baseline, and 8-item acceptance criteria table.                              |
