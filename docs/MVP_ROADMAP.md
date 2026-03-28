# MVP Roadmap

## Phase 0 — Foundation (Week 1)

- Project setup: backend, db migrations, basic UI shell.
- Household-scoped auth for 2 users.
- Base entities: users, household, preferences, inventory, recipes.

**Exit criteria**
- Both users can log in and edit profile/preferences.

## Phase 1 — Preference + Inventory Core (Week 2)

- Plain-English preference updates (rule-based parser first).
- Inventory CRUD with events.
- Auto-expiry estimation based on item type/storage.

**Exit criteria**
- User can update inventory/preferences via text and view latest snapshot.

## Phase 2 — Grocery Screenshot Bootstrap (Week 3)

- Image upload endpoint.
- OCR pipeline (Tesseract/PaddleOCR).
- Item normalization and quantity extraction.
- Merge extracted data into inventory with confidence labels.

**Exit criteria**
- Uploading last grocery orders creates a usable initial inventory list.

## Phase 3 — 7-Day Planner (Week 4)

- Add recipe catalog and nutrition metadata.
- Implement weekly planner with constraints.
- Generate dish + ingredients + steps + servings for breakfast/lunch.

**Exit criteria**
- One-click weekly plan generation from latest preferences + inventory.

## Phase 4 — WhatsApp Automation (Week 5)

- Message adapter interface.
- WhatsApp provider implementation.
- Daily scheduled dispatch with delivery logs.

**Exit criteria**
- Cook receives daily instructions automatically; users get copies.

## Phase 5 — Quality + Safety (Week 6)

- Diet-balance scoring checks.
- Inventory drift controls and reconciliation prompts.
- Prompt hardening, schema validation, audit logs.

**Exit criteria**
- Stable daily workflow with explainable updates and low manual correction.

## Suggested Initial API Endpoints

- `POST /auth/login`
- `POST /preferences/interpret`
- `POST /inventory/events`
- `POST /inventory/bootstrap-image`
- `GET /inventory/current`
- `POST /plans/generate-week`
- `POST /dispatch/daily`

## Practical Launch Strategy

1. Start with web app + manual "Send to cook" button.
2. Turn on scheduled messages once plan quality is stable.
3. Add inbound WhatsApp commands only after outbound reliability.
4. Keep all LLM outputs behind validation rules before applying state changes.

