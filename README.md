# ManageMyKitchen MVP (Runnable Skeleton)

This repo now contains a runnable MVP skeleton for a family kitchen co-pilot.

## What is implemented

- FastAPI backend with health check and OpenAPI docs.
- Username/password login for 2 seeded users.
- Plain-English preference ingestion endpoint (rule-based interpretation).
- Inventory event ingestion (add/use/set) and current inventory view.
- 7-day meal plan generation endpoint (MVP stub output).
- Minimal frontend to exercise all APIs from browser.

## Seeded users

- `you` / `changeme123`
- `wife` / `changeme123`

> Change credentials before real use.

## Run locally (Docker)

```bash
docker compose up --build
```

Then open:

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## API Endpoints in this MVP

- `POST /auth/login`
- `POST /preferences/interpret`
- `POST /inventory/events`
- `GET /inventory/current`
- `POST /plans/generate-week`
- `GET /health`

## Notes

- This is a starter implementation to make the app runnable quickly.
- OCR ingestion and WhatsApp automation are still pending next iterations.
- Planner currently returns deterministic sample dishes; recipe-engine + nutrition scoring are next.

## Next recommended steps

1. Add OCR pipeline for grocery screenshots.
2. Add WhatsApp provider + scheduler for daily cook instructions.
3. Add structured recipe catalog with ingredient-level quantities.
4. Add nutrition scoring and balancing logic.
5. Add auth token validation middleware + role checks.
