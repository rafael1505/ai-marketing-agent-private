---
applyTo: "frontend/**"
---

# AI Marketing Agent – UX Guidelines (Apple-Inspired Gradual Transition)

**Version**: 1.0.0  
**Last Updated**: January 28, 2025  
**Applies To**: Frontend UI/UX work

## 🎯 Context
The current UX of the AI Marketing Agent project was initially created by AI without strict design rules.  
We are now progressively evolving it toward a **refined, Apple-inspired experience**: simple, elegant, and user-centered.

These guidelines should apply **only to new features and UI components** for now, while **existing pages are gradually updated** as part of normal development work.

## 📚 Related Guidelines
When working on UI/UX, also reference:
- **Component Organization**: See `.github/instructions/ai-marketing-agent.development-best-practices.instructions.md`
- **Architecture Standards**: See `.github/instructions/ai-marketing-agent.architecture-and-development-guidelines.instructions.md`
- **Error Display**: Always use `AIErrorDisplay` component (see `.github/copilot-instructions.md`)
- **Instruction Hierarchy**: Check `.github/copilot-instructions.md` for precedence rules

---

## 🧭 Design Philosophy

- **Less but better:** Each element must serve a clear purpose.  
- **Clarity first:** Simplicity, space, and intuitive structure above all.  
- **Elegant motion:** Use subtle transitions — avoid exaggerated animations.  
- **Unified language:** All components should feel part of the same ecosystem.  
- **Accessibility:** Every design decision must consider accessibility (WCAG AA).

---

## 🎨 Layout & Structure

- Use **ample spacing** between sections (`p-6`, `space-y-6`, etc.).  
- Prefer **centered or balanced grid layouts**.  
- Apply **soft rounded corners** (`rounded-2xl`) and **light shadows** (`shadow-sm`).  
- Avoid clutter; use whitespace to emphasize hierarchy.  
- Use Tailwind utilities to maintain design consistency.

**Preferred patterns:**
- Page containers → `max-w-5xl mx-auto p-6`
- Cards → `rounded-2xl bg-white shadow-sm border border-gray-100`
- Sections → `divide-y divide-gray-100`

---

## ✍️ Typography

- **Base font:** System default (Apple-like) — use Tailwind’s `font-sans`.  
- **Hierarchy:**
  - `h1`: `text-3xl font-semibold tracking-tight`
  - `h2`: `text-2xl font-semibold`
  - `h3`: `text-xl font-medium`
  - Paragraph: `text-base text-gray-700 leading-relaxed`
  - Small text: `text-sm text-gray-500`
- Avoid uppercase for labels unless essential.
- Prioritize **clarity, rhythm, and harmony** over contrast.

---

## 🌈 Color Palette

| Role | Description | Example |
|------|--------------|----------|
| Primary | Calm and modern blue | `#007AFF` or `blue-500` |
| Background | Clean and bright | `bg-gray-50` / `bg-white` |
| Borders | Subtle | `border-gray-200` |
| Text | Neutral and readable | `text-gray-700` / `text-gray-900` |
| Accent | Limited, meaningful highlights | one accent color per page |

> Always maintain **high contrast** for readability and accessibility.

---

## 🧩 Components

- Use **shadcn/ui** components as base whenever possible.  
- Each component should have **consistent spacing, rounded corners, and shadow**.  
- Use **lucide-react** icons (minimal line icons).  
- Include smooth transitions (`transition-all ease-in-out duration-200`).

**Examples:**
- Buttons: `bg-blue-500 hover:bg-blue-600 text-white rounded-xl px-4 py-2 transition-all`
- Inputs: `border border-gray-300 rounded-xl px-3 py-2 focus:ring-2 focus:ring-blue-500`
- Cards: `bg-white rounded-2xl shadow-sm hover:shadow-md transition-all`

---

## 🧠 Interaction & Feedback

- Use **toasts** for feedback (success, info, warning, error).  
- Always show progress indicators for async actions.  
- Motion must be **gentle** — no abrupt or distracting transitions.  
- Avoid modal overuse; prefer inline or toast feedback when possible.  
- Use **consistent microinteractions** across all actions (hover, click, focus).

---

## 📱 Responsiveness & Accessibility

- **Mobile-first** design approach.  
- Always test on different viewports (`sm`, `md`, `lg`, `xl`).  
- Minimum touch target: 44x44px.  
- Include `aria-labels` and proper keyboard navigation.  
- Check contrast ratios before committing new UI colors.

---

## 🧩 Integration with the Stack

- **Frontend framework:** Next.js (TypeScript)  
- **Styling:** TailwindCSS + shadcn/ui  
- **Icons:** lucide-react  
- **Internationalization:** i18n (English + Portuguese)  
- **Linting:** ESLint + Prettier with consistent formatting  

Follow these conventions when building new pages or refactoring existing components.

---

## 🚀 Gradual Adoption Strategy

1. **New Features:**  
   Implement fully using the Apple-inspired guidelines.  
2. **Existing Features:**  
   Apply small UX refinements (spacing, color, typography) without breaking layout.  
3. **Refactor Opportunities:**  
   When modifying or fixing components, migrate them toward the new UX standard.  

---

## 💬 Tone & Copywriting

- Calm, confident, and concise.  
- Use natural, human language (avoid jargon).  
- Maintain consistency between English and Portuguese i18n texts.  
- Example tone: “Everything just works.”

---

## 🧩 Example AI Prompts

> “Create a new dashboard page using our Apple-inspired UX guidelines.”  
> “Refactor the login page to match the new UX standards without changing functionality.”  
> “Design a clean and minimal settings form using shadcn/ui components.”  

---

## ✅ Summary

This instruction ensures that every new UI element:
- Aligns with Apple’s elegant, human-centered design language  
- Maintains technical consistency with the AI Marketing Agent stack  
- Contributes to a gradual, controlled UX transformation

---

