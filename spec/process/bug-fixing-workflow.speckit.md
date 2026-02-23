# Bug Fixing Workflow – Process Spec

## Purpose

Standardize how bugs are diagnosed, fixed, tested, and documented in the AI Marketing Agent.

## Scope

Applies to any change whose primary goal is to fix a defect.

## Pre‑Fix Checklist

Before writing code:

- Reproduce the bug reliably.
- Capture logs and correlation IDs where available.
- Check for similar patterns or past fixes in the codebase and docs.
- Identify the **root cause**, not just the symptom.

## Workflow

1. **Reproduce**
   - Reproduce in development or a safe environment.
   - For frontend issues, check browser console and network tab.
   - For backend issues, check API logs, correlation IDs, and stack traces.

2. **Analyze**
   - Trace code from the failing behavior back to:
     - Frontend component and service,
     - API endpoint,
     - Service layer,
     - DB access.
   - Confirm where the invariant from the constitution or specs is being broken.

3. **Design the Fix**
   - Ensure the fix respects:
     - Architecture rules (services vs routes vs db),
     - Database‑driven AI providers (no hardcoded lists),
     - Error handling conventions (correlation IDs, enriched errors),
     - UX and i18n patterns.

4. **Implement**
   - Change only the necessary modules.
   - Keep business logic in services, not in route handlers.
   - For frontend:
     - Preserve hook ordering rules.
     - Use `AIErrorDisplay` for errors.
     - Use `getTranslations()` and loading guards when touching i18n.

5. **Test**
   - Add or update automated tests in `tests/unit`, `tests/integration`, or `tests/frontend`.
   - Ensure tests fail before the fix and pass after.
   - Manually test the user flow when appropriate.

6. **Document & Commit**
   - Update relevant docs if behavior or APIs changed.
   - Reference the bug and the affected spec(s) in the commit message.
   - Use a `fix:` commit prefix.

## Acceptance Criteria

A bug fix is complete when:

- Root cause is understood and documented (at least in the commit or PR description).
- Automated tests cover the scenario.
- UX, error handling, and architecture rules from the constitution are still satisfied.