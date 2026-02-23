# UX & Frontend Guidelines – Process Spec

## Purpose

Define UI/UX rules for frontend changes to keep the AI Marketing Agent consistent, robust, and accessible.

## Scope

Applies to any frontend work: components, pages, styles, and interactions.

## React Hooks

- All hooks are defined at the top of the component function.
- No hooks in conditionals, loops, or nested functions.
- Avoid early returns before hooks.

## Internationalization

- Use the custom `@/i18n` `getTranslations()` helper, not `next-intl`.
- Load translations asynchronously and store them in component state.
- Always include a loading guard such as:
  - `if (loading || !t.pages) return <LoadingState />;`
- Return i18n keys from the backend (`user_message`) and resolve them on the frontend.

## Error Handling

- Never use `alert()` for errors.
- Use the `AIErrorDisplay` component with enriched error objects that include:
  - `error_type`, `message`, `user_message`, `provider`, `correlation_id`, etc.
- Ensure Axios interceptors or API clients attach correlation IDs to requests.

## Design System

- Use shadcn/ui as the primary component library.
- Follow Apple‑inspired design:
  - Clean layouts, clear hierarchy, generous spacing.
- Ensure responsive layouts work on desktop and mobile.
- Meet at least WCAG AA accessibility guidelines:
  - Color contrast,
  - Keyboard navigation,
  - ARIA attributes where needed.

## Layout & Structure

- Pages live in `frontend/src/app/[locale]/`.
- Shared components live in `frontend/src/components/`.
- Avoid duplicating layout logic across pages; extract shared shells/components instead.

## UX Acceptance Criteria

A frontend change is acceptable when:

- Hooks ordering is valid and React DevTools shows no hook order warnings.
- i18n uses the project pattern, with proper loading guards.
- Errors are displayed via `AIErrorDisplay` with correlation IDs.
- The UI looks consistent with existing screens and is usable on small screens.