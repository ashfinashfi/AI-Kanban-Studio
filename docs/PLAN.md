# Project Management MVP Master Execution Plan

## Part 1: Plan
- [x] Create AGENTS.md file inside frontend directory describing existing code structure.
- [x] Enrich docs/PLAN.md with detailed checklists, tests, and success criteria for all 10 parts.
- [x] Ensure user approves implementation plan before proceeding.
- **Tests**: Verify `docs/PLAN.md` and `frontend/AGENTS.md` exist and contain comprehensive documentation.
- **Success Criteria**: Clear roadmap aligned with project requirements.

## Part 2: Scaffolding
- [x] Create `backend/pyproject.toml` with FastAPI, Uvicorn, SQLModel/SQLAlchemy, HTTPX, and Pytest dependencies managed by `uv`.
- [x] Build baseline FastAPI application in `backend/main.py` serving static assets at `/` and health check at `/api/health`.
- [x] Create Dockerfile with multi-stage build (Next.js build -> Python uv runtime).
- [x] Create `scripts/start.sh`, `scripts/stop.sh`, `scripts/start.bat`, `scripts/stop.bat`, `scripts/start.ps1`, `scripts/stop.ps1`.
- **Tests**: Run Docker build or uvicorn dev server and call `/api/health`.
- **Success Criteria**: HTTP 200 response from `/api/health` and start/stop scripts operational across platforms.

## Part 3: Add in Frontend
- [x] Update `frontend/next.config.ts` to set `output: 'export'`.
- [x] Build Next.js static output using `npm run build` in `frontend/`.
- [x] Mount Next.js `/out` static build in FastAPI backend at root `/`.
- **Tests**: Fetch `/` from FastAPI server and confirm initial HTML contains Kanban title and default columns.
- **Success Criteria**: Frontend Kanban board accessible at `http://localhost:8000/`.

## Part 4: Add in Fake User Sign-in Experience
- [x] Backend auth routes (`POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`).
- [x] Validate hardcoded credentials: username `user`, password `password`.
- [x] Frontend Login interface and Auth Guard component.
- [x] Logout functionality in board header.
- **Tests**: Test invalid credentials (returns 401), valid credentials (returns 200 + token), and unauthenticated access to board (displays login form).
- **Success Criteria**: User must sign in with `user`/`password` before viewing board.

## Part 5: Database Modeling
- [x] Propose SQLite schema in `docs/DATABASE_SCHEMA.md` and `docs/schema.json`.
- [x] Define tables: `users`, `boards`, `columns`, `cards`.
- [x] Configure async SQLite connection in FastAPI using SQLAlchemy/SQLModel.
- **Tests**: Validate schema SQL statements and test auto-creation of database file (`pm.db`) on startup.
- **Success Criteria**: SQLite database schema handles multiple users, 1 board per user, fixed columns, and cards.

## Part 6: Backend APIs
- [x] Implement REST endpoints:
  - `GET /api/board`: Fetch user's board state.
  - `POST /api/columns/{column_id}/rename`: Rename column.
  - `POST /api/cards`: Create new card.
  - `PUT /api/cards/{card_id}`: Edit card title/details.
  - `DELETE /api/cards/{card_id}`: Delete card.
  - `POST /api/cards/move`: Reorder/move card between columns.
- [x] Write backend unit test suite in `backend/tests/test_api.py`.
- **Tests**: Execute `pytest` in backend directory verifying full CRUD functionality.
- **Success Criteria**: 100% passing pytest backend tests for all board endpoints.

## Part 7: Frontend + Backend Integration
- [x] Replace static in-memory state in `KanbanBoard.tsx` with API client calls.
- [x] Implement persistent state sync across browser reloads.
- **Tests**: Perform card creation, move, edit, and column renaming; reload page and verify state persists.
- **Success Criteria**: Board state completely persisted in SQLite database.

## Part 8: AI Connectivity
- [x] Implement OpenRouter API client in `backend/ai_service.py` using `openai/gpt-oss-120b` and `OPENROUTER_API_KEY`.
- [x] Add `GET /api/ai/test` endpoint performing simple "2+2" prompt query.
- **Tests**: Call `/api/ai/test` and assert response contains expected answer ("4").
- **Success Criteria**: OpenRouter LLM call succeeds and returns valid response.

## Part 9: AI Structured Output Kanban Agent
- [x] Define Pydantic response models for AI structured actions (`create_card`, `edit_card`, `move_card`, `delete_card`, `rename_column`).
- [x] Implement `POST /api/ai/chat` endpoint taking chat history, current board JSON, and user prompt.
- [x] Apply returned actions to database and return structured AI response message.
- **Tests**: Unit test backend AI structured output parsing and board state mutations using pytest mocks and live checks.
- **Success Criteria**: Natural language prompts like "Move task 1 to Done" result in database updates.

## Part 10: AI Chat Sidebar UI & Full System Testing
- [x] Build expandable `AiSidebar.tsx` component matching color palette (#ecad0a, #209dd7, #753991, #032147, #888888) with zero emojis.
- [x] Connect sidebar to `/api/ai/chat` API and trigger automatic Kanban board refresh upon AI action execution.
- [x] Run full test suite: frontend Vitest, Playwright E2E, and backend Pytest.
- **Tests**: Complete end-to-end user journey test (Sign in -> Board view -> AI chat card update -> Persistence verification).
- **Success Criteria**: All unit, integration, and E2E tests pass cleanly.
