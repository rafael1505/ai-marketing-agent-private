# Prompt Enrichment Conflict Analysis & UX Solution

**Date**: November 6, 2025  
**Issue**: "Include People" toggle conflicts with industry templates and other prompt enrichment options  
**Status**: Design Phase - Solution Proposed

---

## 🔍 Problem Analysis

### Current Enrichment Workflow

The system enriches AI prompts in **3 sequential stages**:

```
User Prompt (Phase 2)
    ↓
1. Material Context Enrichment
   - Title, Description (Campaign Brief)
   - Target Audience
   - Campaign Objective
   - Keywords
    ↓
2. Industry Template Enrichment (Optional)
   - Visual Keywords
   - Style Guide
   - Tone
   - Color Palette
   - Compliance rules
   - Avoid Elements
    ↓
3. Seasonal Context Enrichment (Automatic)
   - Season-specific themes
   - Holiday keywords
   - Seasonal colors
    ↓
4. Include People Toggle (NEW - Phase 9)
   - Modifies prompt on backend
   - Adds negative prompts
```

### Identified Conflicts

#### Conflict 1: Industry Templates → People Instructions
**Problematic Industries**:

1. **Nonprofit & Social Impact**:
   - Style Guide: **"Use real people**, authentic stories, positive change, community action, hopeful imagery"
   - ❌ Direct contradiction with "Include People = OFF"

2. **Fitness & Wellness**:
   - Style Guide: **"Use active people**, diverse body types, positive energy, natural settings, achievement moments"
   - ❌ Direct contradiction with "Include People = OFF"

3. **Education & Training**:
   - Style Guide: "Use **diverse learners**, achievement symbols, collaborative settings"
   - ❌ Direct contradiction with "Include People = OFF"

4. **Hospitality & Travel**:
   - Style Guide: "Use destination imagery, **happy travelers**, luxurious amenities"
   - ❌ Partial contradiction

5. **Retail & E-commerce**:
   - Style Guide: "Use product-focused imagery, **lifestyle contexts**, shopping scenarios"
   - ❌ Lifestyle contexts often imply people

6. **Real Estate & Property**:
   - Style Guide: "Use beautiful properties, welcoming interiors, **family-friendly imagery**"
   - ❌ Family-friendly often implies people

#### Conflict 2: Material Context → People References
**Potential Issues**:
- **Campaign Brief** (Phase 1 - "Description" field): User might write "Show happy customers using our product"
- **Target Audience**: "Young professionals aged 25-35" implies human-centric imagery
- **Keywords**: Could include "lifestyle", "community", "family", "customers"

#### Conflict 3: Seasonal Context → Holiday Imagery
**Problematic Holidays**:
- **Thanksgiving**: Themes include "family", "togetherness"
- **Mother's Day / Father's Day**: Inherently people-focused
- **Valentine's Day**: "couples", "romantic"
- **Back to School**: Implies students/children

---

## 🎯 User Scenarios & Navigation Workflows

### Scenario 1: Happy Path (No Conflicts)
```
Phase 1 (Idea): User creates product launch campaign
├─ Title: "New Smartwatch Launch"
├─ Campaign Brief: "Showcase sleek design and features"
├─ Target Audience: "Tech enthusiasts"
├─ Campaign Objective: "Generate pre-orders"
├─ Keywords: ["innovation", "design", "technology"]
└─ Industry: Technology

Phase 2 (Refinement): User generates images
├─ Industry Template: Technology (no people references)
├─ Seasonal Context: Winter (no people-centric holidays)
├─ Include People: OFF ✅
└─ Result: Product-only images, no conflicts
```

### Scenario 2: Conflicting Path (Current Issue)
```
Phase 1 (Idea): User creates charity campaign
├─ Title: "Help Feed Local Families"
├─ Campaign Brief: "Show the impact of donations on real people"
├─ Target Audience: "Compassionate donors"
├─ Campaign Objective: "Increase donations"
├─ Keywords: ["community", "impact", "families"]
└─ Industry: Nonprofit & Social Impact

Phase 2 (Refinement): User generates images
├─ Industry Template: "Use REAL PEOPLE, authentic stories..." ⚠️
├─ Material Context: "Show impact on REAL PEOPLE" ⚠️
├─ Keywords: "families" ⚠️
├─ Include People: OFF ❌ CONFLICT!
└─ Result: AI receives contradictory instructions
```

### Scenario 3: User Changes Mind (Navigation Issue)
```
Phase 1 → Phase 2 → User sets "Include People: OFF"
    ↓
Generates 3 images (product-only)
    ↓
User goes BACK to Phase 1
    ↓
Changes Industry from "Technology" to "Fitness & Wellness"
    ↓
Goes forward to Phase 2
    ↓
"Include People: OFF" still set BUT Industry now says "Use active people"
❌ Silent conflict - user doesn't realize!
```

---

## 💡 Proposed UX Solution: Smart Toggle with Contextual Warnings

### Solution Architecture

#### 1. **Context-Aware Toggle State**
Replace simple ON/OFF with **intelligent state management**:

```typescript
type PeoplePreference = 
  | "auto"          // Let industry/context decide (DEFAULT)
  | "include"       // Force include people
  | "exclude"       // Force exclude people
  | "minimal";      // Prefer product-focus but allow people if contextually appropriate
```

#### 2. **Conflict Detection System**
Create a **real-time conflict detector** that analyzes:

```typescript
interface ConflictAnalysis {
  hasConflict: boolean;
  severity: "low" | "medium" | "high";
  conflictingSources: Array<{
    source: "industry" | "material_context" | "seasonal" | "keywords";
    reason: string;
    suggestion: string;
  }>;
}

function detectPeopleConflicts(
  peoplePreference: PeoplePreference,
  industry: string | null,
  material: Material,
  seasonalContext: SeasonalContext
): ConflictAnalysis
```

#### 3. **Smart UI Component**
Replace current toggle with **enhanced control**:

```tsx
<Card className="border-l-4 border-l-amber-500">
  <CardHeader>
    <CardTitle>👥 People Preference</CardTitle>
    <CardDescription>
      Control whether people appear in your images
    </CardDescription>
  </CardHeader>
  
  <CardContent className="space-y-4">
    {/* Radio Group: Auto / Include / Exclude / Minimal */}
    <RadioGroup value={peoplePreference} onChange={...}>
      <RadioOption value="auto">
        <Label>🤖 Auto (Recommended)</Label>
        <Description>Let the system decide based on your industry and campaign context</Description>
      </RadioOption>
      
      <RadioOption value="include">
        <Label>✅ Always Include People</Label>
        <Description>Generate lifestyle and human-centric images</Description>
      </RadioOption>
      
      <RadioOption value="exclude">
        <Label>🚫 Never Include People</Label>
        <Description>Product-only, object-focused, or abstract imagery</Description>
        {conflictAnalysis.hasConflict && (
          <Alert variant="warning">
            <AlertTitle>⚠️ Potential Conflict Detected</AlertTitle>
            <AlertDescription>
              Your {industry} industry template recommends including people.
              <Button onClick={showConflictDetails}>View Details</Button>
            </AlertDescription>
          </Alert>
        )}
      </RadioOption>
      
      <RadioOption value="minimal">
        <Label>📦 Product-Focused (Minimal People)</Label>
        <Description>Prioritize products/objects, but allow people if contextually relevant</Description>
      </RadioOption>
    </RadioGroup>
    
    {/* Real-time Conflict Warnings */}
    {conflictAnalysis.conflictingSources.length > 0 && (
      <Alert variant="info">
        <AlertTitle>💡 Context Analysis</AlertTitle>
        <ul>
          {conflictAnalysis.conflictingSources.map(source => (
            <li key={source.source}>
              <strong>{source.source}</strong>: {source.reason}
              <br />
              <em>Suggestion: {source.suggestion}</em>
            </li>
          ))}
        </ul>
      </Alert>
    )}
  </CardContent>
</Card>
```

#### 4. **Backend Prompt Modification Strategy**
Update backend to handle **4 preference modes**:

```python
def modify_prompt_for_people_preference(
    prompt: str,
    preference: str,
    has_industry_people_refs: bool,
    has_material_people_refs: bool
) -> tuple[str, Optional[str]]:
    """
    Returns: (modified_prompt, negative_prompt)
    """
    
    if preference == "auto":
        # Don't modify - let enrichments guide naturally
        return (prompt, None)
    
    elif preference == "include":
        # Reinforce people presence
        if not has_industry_people_refs and not has_material_people_refs:
            prompt += "\n\nIMPORTANT: Include diverse, authentic people in natural settings. Show real human moments and connections."
        return (prompt, None)
    
    elif preference == "exclude":
        # Strong people exclusion
        prompt += "\n\nCRITICAL REQUIREMENT: Absolutely NO people, NO humans, NO faces, NO body parts. Focus exclusively on products, objects, abstract elements, or scenery. This is a product-only visual."
        negative_prompt = "people, humans, persons, faces, portraits, crowds, human figures, body parts, hands, feet, silhouettes, human shadows"
        
        # Clean industry template conflicts
        prompt = remove_people_references_from_prompt(prompt)
        
        return (prompt, negative_prompt)
    
    elif preference == "minimal":
        # Gentle guidance toward product focus
        prompt += "\n\nGUIDELINE: Prioritize product showcase. If people appear, they should be minimal, in background, or partial (hands holding product). Main focus must be on the product/object."
        negative_prompt = "crowds, group photos, portrait mode, face close-ups, human-centric composition"
        return (prompt, negative_prompt)
```

#### 5. **Conflict Resolution Modal**
When high-severity conflicts detected, show **interactive resolution**:

```tsx
<Dialog open={showConflictResolution}>
  <DialogHeader>
    <DialogTitle>⚠️ Conflicting Instructions Detected</DialogTitle>
  </DialogHeader>
  
  <DialogContent>
    <p>Your settings may produce conflicting instructions for the AI:</p>
    
    <div className="space-y-3">
      <ConflictCard severity="high">
        <ConflictSource>Industry Template: {industry}</ConflictSource>
        <ConflictInstruction>"Use real people, authentic stories..."</ConflictInstruction>
        <ConflictIcon>👥</ConflictIcon>
      </ConflictCard>
      
      <div className="text-center text-2xl">⚔️ VS</div>
      
      <ConflictCard severity="high">
        <ConflictSource>Your People Preference</ConflictSource>
        <ConflictInstruction>"Never Include People"</ConflictInstruction>
        <ConflictIcon>🚫</ConflictIcon>
      </ConflictCard>
    </div>
    
    <div className="space-y-2 mt-4">
      <p className="font-semibold">How would you like to resolve this?</p>
      
      <Button onClick={() => resolveTo("change_preference")}>
        Change People Preference to "Auto"
      </Button>
      
      <Button onClick={() => resolveTo("change_industry")}>
        Choose Different Industry Template
      </Button>
      
      <Button variant="destructive" onClick={() => resolveTo("force_exclude")}>
        Force "Exclude People" (Override Industry Template)
      </Button>
      
      <Button variant="outline" onClick={() => resolveTo("ignore")}>
        Proceed Anyway (Not Recommended)
      </Button>
    </div>
  </DialogContent>
</Dialog>
```

---

## 🔧 Implementation Plan

### Phase 1: Backend Conflict Detection (Priority: HIGH)
**Files to modify**:
- `/app/ai_providers/provider_manager.py` - Add conflict detection
- `/app/services/prompt_enrichment.py` - NEW: Centralized enrichment with conflict resolution

**Tasks**:
1. Create `PromptEnrichmentService` class
2. Implement `detect_people_conflicts()`
3. Add `clean_conflicting_instructions()` function
4. Update all 3 providers to use centralized service

### Phase 2: Frontend Smart Toggle (Priority: HIGH)
**Files to modify**:
- `/frontend/src/components/forms/enhanced-refinement-form.tsx` - Replace toggle with radio group
- `/frontend/src/components/ui/people-preference-selector.tsx` - NEW: Smart component
- `/frontend/src/types/index.ts` - Add `PeoplePreference` type

**Tasks**:
1. Create radio group component with 4 options (auto/include/exclude/minimal)
2. Implement real-time conflict detection
3. Add contextual warnings based on industry/material/seasonal analysis
4. Update form state management

### Phase 3: Conflict Resolution UI (Priority: MEDIUM)
**Files to create**:
- `/frontend/src/components/materials/conflict-resolution-dialog.tsx`
- `/frontend/src/lib/conflict-analyzer.ts`

**Tasks**:
1. Build conflict analysis engine
2. Create resolution dialog
3. Implement one-click resolution actions
4. Add conflict severity indicators

### Phase 4: User Education (Priority: LOW)
**Tasks**:
1. Add inline help text explaining each mode
2. Create example images showing "Auto vs Include vs Exclude vs Minimal"
3. Add tooltip with industry-specific recommendations
4. Update user documentation

---

## 📊 Industry-Specific Recommendations

### Automatic Recommendations by Industry:

| Industry | Default Mode | Rationale |
|----------|--------------|-----------|
| Healthcare | **Minimal** | Show care context but focus on services/equipment |
| Technology | **Auto** | Flexible - products or lifestyle depending on context |
| Finance | **Minimal** | Professional settings with subtle human context |
| Retail | **Include** | Lifestyle and shopping experiences crucial |
| Education | **Include** | Learners and teachers are central to message |
| Real Estate | **Minimal** | Properties first, but lifestyle context valuable |
| Hospitality | **Include** | Guest experiences drive bookings |
| Professional Services | **Minimal** | Professional context without making it about individuals |
| Food & Beverage | **Minimal** | Food as hero, but dining context can help |
| Manufacturing | **Exclude** | Equipment and products, not operators |
| Nonprofit | **Include** | Impact on real people is the core message |
| Automotive | **Minimal** | Vehicle showcase with lifestyle context |
| Fitness & Wellness | **Include** | Transformation and active lifestyles central |

---

## 🎓 UX Best Practices Applied

### 1. **Progressive Disclosure**
- Default to "Auto" mode (hide complexity)
- Show advanced options only when user clicks "Customize People Preference"
- Display warnings only when actual conflicts exist

### 2. **Contextual Guidance**
- Industry templates drive initial recommendation
- Real-time feedback as user changes settings
- Clear explanations of why conflicts exist

### 3. **Forgiving Design**
- Allow users to override but warn about consequences
- Provide one-click resolution for common conflicts
- Remember user preferences per industry

### 4. **Transparent AI Behavior**
- Show exactly what instructions will be sent to AI
- Preview enriched prompt before generation
- Explain how each enrichment affects the output

### 5. **Workflow Resilience**
- Detect conflicts when navigating back/forward
- Prompt user to review settings if industry changes
- Preserve user intent across navigation

---

## 🚀 Migration Path (Current to Proposed)

### Immediate Quick Fix (Stop the Bleeding)
**Time**: 1 hour  
**Impact**: Prevents worst conflicts

1. Move "Include People" toggle INSIDE "Advanced Options" accordion
2. Add warning text: "⚠️ Note: This setting may conflict with your selected industry template"
3. When toggle is OFF + Industry has people references → Show alert

### Short-Term Solution (Conflict Detection)
**Time**: 4 hours  
**Impact**: Warns users of conflicts

1. Implement basic conflict detection
2. Show warning banner when conflicts detected
3. Add "Review Settings" button that highlights conflicting options

### Long-Term Solution (Smart Toggle)
**Time**: 2 days  
**Impact**: Professional, elegant solution

1. Full implementation of 4-mode system
2. Real-time conflict analysis
3. Interactive resolution dialogs
4. Industry-specific defaults

---

## 📝 Translation Keys Needed

```json
{
  "creation": {
    "refinement": {
      "people_preference": {
        "title": "People Preference",
        "description": "Control whether people appear in your images",
        "mode_auto": "Auto (Recommended)",
        "mode_auto_desc": "Let the system decide based on your campaign context",
        "mode_include": "Always Include People",
        "mode_include_desc": "Generate lifestyle and human-centric images",
        "mode_exclude": "Never Include People",
        "mode_exclude_desc": "Product-only, object-focused, or abstract imagery",
        "mode_minimal": "Product-Focused (Minimal People)",
        "mode_minimal_desc": "Prioritize products, but allow people if contextually relevant",
        "conflict_warning": "Potential Conflict Detected",
        "conflict_industry": "Your {industry} industry template recommends {recommendation}",
        "conflict_material": "Your campaign brief mentions people or human elements",
        "conflict_seasonal": "This holiday ({holiday}) typically features people-centric imagery",
        "resolve_conflict": "How would you like to resolve this?",
        "change_to_auto": "Change to Auto mode",
        "change_industry": "Choose different industry",
        "force_preference": "Keep my preference (override template)",
        "proceed_anyway": "Proceed anyway"
      }
    }
  }
}
```

---

## ✅ Success Metrics

### Before Solution:
- ❌ Silent conflicts produce inconsistent images
- ❌ User confusion when images don't match expectations
- ❌ Wasted AI generation credits on conflicting prompts

### After Solution:
- ✅ 0 silent conflicts (all detected and resolved)
- ✅ User satisfaction with image output increases
- ✅ Clear understanding of how settings affect output
- ✅ Reduced need for regeneration due to unexpected results

---

## 🎯 Recommendation

**Immediate Action**: Implement **Short-Term Solution** (4 hours)  
**Next Sprint**: Implement **Long-Term Solution** (2 days)

This approach:
1. **Stops the bleeding** - Prevents current conflicts
2. **Educates users** - Clear feedback on settings interaction
3. **Maintains flexibility** - Users can override when needed
4. **Future-proof** - Extensible architecture for more enrichments

The key insight: **Don't just add a toggle—design an intelligent system that understands context and guides users toward successful outcomes.**
