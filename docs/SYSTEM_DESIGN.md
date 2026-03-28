# System Design (MVP)

## 1. High-Level Architecture

1. **Client layer**
   - Simple web UI for you and your wife.
   - Optional WhatsApp command intake.

2. **API layer**
   - Auth (username/password)
   - Preference management
   - Inventory management
   - Planning service
   - Messaging service

3. **Intelligence layer**
   - NLP command parser (plain-English to structured updates)
   - OCR pipeline for grocery screenshots
   - Meal planner + nutrition balancer
   - Expiry estimator

4. **Data layer**
   - Users
   - Household profile
   - Preferences history
   - Inventory ledger
   - Recipes + meal plans
   - Message logs

## 2. Core Domain Entities

- **User**: one of household decision-makers.
- **Household**: your kitchen context (members, cook contact, timezone).
- **PreferenceSnapshot**: current interpreted preference profile.
- **PreferenceEvent**: raw plain-English update + parsed delta.
- **InventoryItem**: canonical item, qty, unit, purchase/expiry dates.
- **InventoryEvent**: add/use/adjust operations (event-sourced style).
- **MealPlanWeek**: generated weekly plan.
- **MealPlanDay**: breakfast/lunch with servings and recipe references.
- **DispatchMessage**: WhatsApp instructions sent/failed/acknowledged.

## 3. Planner Logic (MVP)

### Inputs
- Current preference snapshot
- Current inventory state
- Household profile (age, height, weight, diet pattern)
- Recipe catalog

### Flow
1. Determine caloric/macro targets per person.
2. Convert targets to household meal targets.
3. Filter recipes by preferences + exclusions.
4. Score recipes by nutrition balance, prep effort, and inventory fit.
5. Select 7-day breakfast/lunch schedule with variety constraints.
6. Compute ingredient requirements and deduct expected inventory.
7. Generate daily instruction packs for cook.

## 4. Inventory Inference

### Initial bootstrap from grocery screenshots
1. OCR extraction of lines and dates.
2. Item normalization (e.g., "atta flour" -> "wheat flour").
3. Quantity parsing (kg/g/l/pcs).
4. Purchase-date inference from order timestamp.
5. Expiry-date estimation from shelf-life table.

### Continuous updates
- NLP command parser emits structured inventory events.
- Current inventory = fold(all events) with guardrails (no negative stock).

## 5. WhatsApp Integration Pattern

### Outbound (daily)
- Scheduler triggers at configured local time.
- Compose instruction message from day plan.
- Send to cook and cc household users.
- Record delivery status.

### Inbound (optional)
- Webhook receives updates like "done", "out of paneer".
- Parser maps to inventory/plan actions.
- Sends confirmations.

## 6. Cost Control Strategy

- Use local Ollama for parsing/planning prompts.
- Add rule-based fallback parser for common commands.
- Cache plan-generation results.
- Prefer open recipe/nutrition data.
- Keep infra on one low-cost VM or local mini-PC.

## 7. Risks & Mitigations

- **OCR noise**: use confidence thresholds + manual correction UI.
- **Recipe mismatch with inventory**: enforce substitution suggestions.
- **Messaging API limits**: abstract provider interface.
- **LLM hallucinations**: constrain output with JSON schema and validators.

