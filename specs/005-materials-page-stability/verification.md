# Verification: Materials Page Stability (005)

**Date**: 2026-02-25  
**Tasks completed**: T001–T011 implemented; T012/T013 manual verification.

## Implementation summary

- **T004**: Retry button now calls `fetchMaterials(true)` and clears `error` (no full page reload).
- **T005**: 30s loading guard added in materials page; timer cleared in `finally`.
- **T006**: Materials GET request uses `timeout: 30000` in `frontend/src/services/materials.ts`.
- **T007**: Navbar already awaits `getUnreadNotificationCount()` inside try/catch; safe default 0 on failure.
- **T008**: Auth context uses try/catch for localStorage; no auth API on init that could throw.
- **T009**: Materials page `loadTranslations` catch sets fallback `t` and `translationsLoaded`; guards for `t.nav`, `t.materials`, `t.common` present.
- **T010/T011**: Materials error logging uses string + correlation_id only; page catch handles `getMaterials` rejection.

## Manual verification checklist (T012)

Run with backend failing or slow and confirm:

| ID   | Criterion                          | Pass/Fail | Notes |
|------|------------------------------------|-----------|--------|
| V1.1 | Retry re-requests without reload   | _manual_  | Click Retry; no full reload. |
| V1.2 | After retry success, list shown    | _manual_  | When API succeeds after retry. |
| V2.1 | Loading ends within 30s (slow req) | _manual_  | Slow/hanging request → error + retry within 30s. |
| V2.2 | Normal req: no spurious timeout    | _manual_  | Fast response → no timeout error. |
| V3.1 | Materials API fail → no crash      | _manual_  | 500/timeout → error state + retry. |
| V3.2 | Notifications fail → no crash      | _manual_  | Force 500 on notifications → materials page still loads. |
| V3.3 | Translations fail → no crash       | _manual_  | Fallback text shown. |
| V3.4 | Auth fail → no crash               | _manual_  | Per existing auth behavior. |
| V4.1 | Console: message + correlation_id  | _manual_  | No raw error object in log. |
| V4.2 | No unhandled rejection on load     | _manual_  | DevTools Console clean. |

Fill Pass/Fail and Notes when running manual tests.

---

## Verification protocol (technical)

### 1. UI state check — Retry clears error before new request

**Location**: `frontend/src/app/[locale]/materials/page.tsx`

**Result**: **PASS**  
The Retry button handler is `onClick={() => { setError(""); fetchMaterials(true); }}`. The `error` state is cleared before `fetchMaterials(true)` runs, so the UI leaves the error state and shows loading, then content or error again. No full page reload.

### 2. Timer leak check — 30s timeout cleared in finally and on unmount

**Location**: `frontend/src/app/[locale]/materials/page.tsx`

**Result**: **PASS (after fix)**  
- The 30s `setTimeout` is stored in `loadingGuardRef` and cleared in the `finally` block of `fetchMaterials` so it never runs after the request completes.
- `fetchCompletedRef.current = true` is set in `finally` so if the timer callback runs in a race it bails out with `if (fetchCompletedRef.current) return`.
- A cleanup effect was added: `useEffect(() => () => { if (loadingGuardRef.current) { clearTimeout(loadingGuardRef.current); loadingGuardRef.current = null; } }, []);` so the timer is cleared on unmount and does not update state after the user leaves the page.

### 3. Notification sandbox — fallback and no propagation

**Location**: `frontend/src/components/layouts/navbar.tsx`

**Result**: **PASS (after fix)**  
- `getUnreadNotificationCount()` is awaited inside a try/catch. On rejection, the catch now explicitly calls `setNotificationsCount(0)` and logs with `console.warn` (no raw error). Errors do not propagate to the layout; the materials page is unaffected.

### 4. Console hygiene — no raw Error or stack in materials flow

**Locations**: `frontend/src/app/[locale]/materials/page.tsx`, `frontend/src/services/materials.ts`

**Result**: **PASS (after fixes)**  
- **Materials page**: `fetchMaterials` catch logs only `msg` and `correlation_id`. Translations catch logs a fixed string. Delete-material catch logs `msg` and `correlation_id` (same pattern as fetch). No raw `Error` object or stack trace in these paths.
- **Materials service**: `getMaterials` catch already logged only msg + cid. `getMaterial` and `deleteMaterial` catch blocks now log `user_message` and `correlation_id` (from `normalizedErrorDetails` or request config) instead of the raw error. Other `console.error`/`console.warn` in materials.ts (e.g. localStorage, development mode) are non-API paths and were left as-is.

---

## Manual simulation: 31s delay for loading guard (V2.1)

To visually verify that the loading guard shows “Request took too long” after 30s, temporarily add a 31-second delay before the materials API call so the guard fires before the request resolves.

**File**: `frontend/src/services/materials.ts`  
**Function**: `getMaterials` (around the line where `api.get(url, { timeout: 30000 })` is called).

**Insert this snippet immediately before the `api.get` call** (and remove it after testing):

```typescript
    // TEMPORARY: Simulate 31s delay to verify loading guard (V2.1). Remove after verification.
    await new Promise((resolve) => setTimeout(resolve, 31000));
```

**Full context** (what to change):

```typescript
    console.log('[Materials Service] Fetching materials from API:', url);
    // TEMPORARY: Simulate 31s delay to verify loading guard (V2.1). Remove after verification.
    await new Promise((resolve) => setTimeout(resolve, 31000));
    const response = await api.get(url, { timeout: 30000 });
```

**Steps**:
1. Add the delay as above.
2. Open `/en/materials` (or `/pt/materials`).
3. Wait ~30 seconds. The page should show “Request took too long. Please try again.” and a Retry button (no full reload).
4. Click Retry; the second request will again wait 31s, so the guard will fire again (or remove the delay and retry to see success).
5. Remove the temporary delay and the comment after verification.
