# ManageMyKitchen (MVP Blueprint)

An MVP blueprint for a **family kitchen co-pilot** that:

- Accepts natural-language updates for meal preferences and inventory.
- Builds a 7-day breakfast/lunch meal plan.
- Generates exact daily cooking instructions with quantities.
- Keeps household users and cook in loop via WhatsApp.
- Bootstraps inventory from grocery-order screenshots/images.
- Prioritizes a balanced diet and low/no recurring cost.

> This repository currently contains the architecture and delivery plan so you can start building quickly with a local-first, low-cost stack.

## Goals

1. **Personalized planning**: You and your wife can update preferences in plain English.
2. **Inventory awareness**: Inventory is continuously updated (name, qty, purchase date, expiry date).
3. **Operational automation**: Cook receives daily WhatsApp instructions.
4. **Health guardrails**: Plans aim for balanced nutrition and portions.
5. **Minimal operating cost**: Prefer self-hosted/open-source models and free tiers.

## Suggested MVP Stack (Zero/Minimal Cost)

- **Backend API**: FastAPI (Python)
- **Database**: PostgreSQL (or SQLite for local prototype)
- **Scheduler/automation**: Cron + Celery/RQ (or APScheduler)
- **NLP/LLM**: Ollama (local), model options: Llama 3.1/3.2, Mistral, Phi
- **OCR for grocery images**: Tesseract + PaddleOCR
- **Nutrition data**: OpenFoodFacts + USDA FoodData Central (free)
- **WhatsApp**:
  - Start with **WhatsApp Cloud API sandbox/free tier behavior varies** OR
  - Build first with Telegram/Signal for prototyping, swap adapter later.
- **Auth**: Username/password (single household tenancy)

## Core Product Capabilities

### 1) Preferences in Plain English
Examples:
- "For breakfast this week keep it high-protein, no eggs on Monday and Friday."
- "Lunch should be mostly vegetarian, but include chicken twice."

System converts to structured constraints:
- cuisine likes/dislikes
- dietary exclusions
- meal frequency rules
- effort/time budget
- macro priorities

### 2) Inventory from Images + Text Updates
- User uploads grocery-order screenshots.
- OCR extracts items + timestamps.
- Normalization maps names to canonical pantry entities.
- Quantities are inferred when missing using household profile defaults.
- Expiry is estimated from item category + storage type.

Plain-English updates:
- "We used 500g tomatoes and 6 eggs today"
- "Bought 2 liters milk yesterday"

### 3) 7-Day Meal Planning
Planner combines:
- current constraints from preferences
- inferred + explicit inventory
- nutrition targets for both users

Outputs:
- breakfast/lunch dishes per day
- recipe steps
- exact ingredient quantities
- inventory consumption impact

### 4) Daily Cook Instructions via WhatsApp
Every morning (configurable):
- What to cook
- How much to cook
- Step-by-step recipe
- Prep notes/substitutions

Loop-in behavior:
- Cook message sent in group or 1:1
- You + your wife receive same summary/confirmation

## Repo Contents

- `docs/SYSTEM_DESIGN.md` – architecture, modules, and data model.
- `docs/MVP_ROADMAP.md` – phased execution plan and milestones.

## Recommended Build Sequence

1. Build data model + auth + CRUD for preferences/inventory.
2. Add plain-English command parser (rule-based first, LLM second).
3. Add weekly planner with deterministic fallback templates.
4. Add OCR ingestion for grocery screenshots.
5. Add WhatsApp messaging adapter and scheduler.
6. Add nutrition scoring and balancing logic.

## Non-Goals (MVP)

- Multi-household SaaS tenancy.
- Payments/billing.
- Real-time IoT kitchen integrations.

## Security & Privacy Baseline

- Hash passwords using Argon2/bcrypt.
- Encrypt sensitive fields at rest where possible.
- Restrict WhatsApp webhook endpoints with signatures.
- Keep audit trail for inventory and plan changes.

---

If useful, next step can be implementing a runnable `backend/` FastAPI skeleton with DB schema and first four endpoints.
