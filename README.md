# Full-Stack AI-Powered Kanban App: Beginner Tutorial

Welcome! This tutorial will walk you step-by-step through how this **Full-Stack AI-Powered Project Management Kanban Application** was built, packaged, and tested.

Whether you are new to web development or looking to understand modern software architecture, this guide breaks down every concept, technology choice, code pattern, and execution flow in plain language.

---

## 1. Summary of Technologies Used

Our web application combines a modern front-end user interface, a fast Python back-end server, a persistent database, OpenRouter AI integration, and Docker containerization.

| Technology | Role | Why We Used It |
| :--- | :--- | :--- |
| **Next.js 16 (React 19)** | Front-End UI | Allows us to write clean, reusable visual components in TypeScript. We configured Next.js to export static HTML/CSS/JS assets (`output: 'export'`). |
| **TailwindCSS v4** | UI Styling | A modern, utility-first CSS framework for custom styling with curated color palettes without external UI overhead. |
| **`@dnd-kit`** | Drag & Drop | Lightweight React library for smooth drag-and-drop interactions across Kanban columns. |
| **Python 3.11 & FastAPI** | Back-End Server | A high-performance Python web framework that serves the static website at `/` and handles REST API endpoints at `/api/*`. |
| **`uv`** | Python Package Manager | An extremely fast Python package manager used inside Docker for instant dependency resolution. |
| **SQLite & SQLAlchemy** | Database | SQLite stores user, column, and card data locally in a single file (`pm.db`). SQLAlchemy provides async Object-Relational Mapping (ORM) in Python. |
| **OpenRouter (`gpt-oss-120b`)** | AI Assistant | Connects to the `openai/gpt-oss-120b` LLM model to interpret user chat prompts and return **Structured Outputs** (JSON actions) to create, move, or edit board cards automatically. |
| **Docker** | Containerization | Packages the Node.js build process and Python runtime into a single, isolated container that runs anywhere with a single script. |

---

## 2. High-Level Architectural Walkthrough

### System Architecture Flow

```
[ Browser (User) ]
       |
       |  1. Requests http://localhost:8000/
       v
[ FastAPI Web Server (Python) ]
       |
       +---> 2. Serves Next.js Static HTML/CSS/JS Assets
       |
       +---> 3. Handles REST API Calls (/api/auth, /api/board, /api/cards)
       |            |
       |            +---> Interacts with [ SQLite Database (pm.db) ]
       |
       +---> 4. Handles AI Chat (/api/ai/chat)
                    |
                    +---> Passes JSON state to [ OpenRouter AI Model ]
                    +---> Executes Structured Actions on [ SQLite Database ]
```

### End-to-End User Experience Journey

1. **Accessing the App**: When you open `http://localhost:8000`, FastAPI serves the Next.js static application.
2. **Authentication**: If unauthenticated, an elegant **Sign In** screen appears. Entering credentials (`user` / `password`) returns an authentication token stored in `localStorage`.
3. **Board Loading**: The Kanban board automatically fetches your columns and cards from `/api/board` (persisted in SQLite).
4. **Interactive Editing**: 
   - Dragging a card to a new column immediately updates the screen and sends a request to `/api/cards/move` to update SQLite.
   - Creating or deleting cards sends requests to `/api/cards`.
5. **AI Chat Assistant**: Clicking the **AI Assistant** widget opens a sidebar. Typing *"Add a card called Launch Feature to Backlog"* sends the message + board state to OpenRouter. The AI returns a structured JSON action, FastAPI updates SQLite, and the UI auto-refreshes in real time!

---

## 3. Detailed Code Review with Code Samples

### A. Front-End API Client (`frontend/src/lib/api.ts`)

The API client acts as the bridge between React components and our Python FastAPI backend. It reads the auth token from `localStorage` and attaches it to every request header.

```typescript
// frontend/src/lib/api.ts
const TOKEN_KEY = "pm_auth_token";

export const getStoredToken = (): string | null => {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
};

const getHeaders = () => {
  const token = getStoredToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
};

// Fetch current board data from FastAPI
export async function fetchBoardApi(): Promise<BoardData | null> {
  const res = await fetch("/api/board", { headers: getHeaders() });
  if (!res.ok) return null;
  return await res.json();
}
```

---

### B. Front-End Authentication Screen (`frontend/src/components/LoginForm.tsx`)

This component provides a clean sign-in form adhering strictly to the primary color palette (`#032147`, `#209dd7`, `#753991`).

```tsx
// frontend/src/components/LoginForm.tsx
export const LoginForm = ({ onLoginSuccess }: LoginFormProps) => {
  const [username, setUsername] = useState("user");
  const [password, setPassword] = useState("password");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const success = await loginApi(username, password);
    if (success) {
      onLoginSuccess();
    } else {
      setError("Invalid username or password.");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--surface)]">
      <form onSubmit={handleSubmit} className="w-full max-w-md rounded-3xl bg-white p-8 border">
        <h1 className="text-3xl font-bold text-[var(--navy-dark)]">Kanban Studio Sign In</h1>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="mt-2 w-full rounded-xl border px-4 py-3 text-sm"
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-2 w-full rounded-xl border px-4 py-3 text-sm"
        />
        <button type="submit" className="mt-4 w-full rounded-xl bg-[var(--secondary-purple)] py-3 text-white">
          Sign In
        </button>
      </form>
    </div>
  );
};
```

---

### C. AI Chat Sidebar Widget (`frontend/src/components/AiSidebar.tsx`)

The sidebar allows natural language interaction with the board. When the AI returns updated board state, `onBoardUpdate(res.board)` refreshes the UI instantly.

```tsx
// frontend/src/components/AiSidebar.tsx
export const AiSidebar = ({ onBoardUpdate }: AiSidebarProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    const userText = input.trim();
    setInput("");

    const newMessages = [...messages, { role: "user", content: userText }];
    setMessages(newMessages);

    const res = await aiChatApi(userText, newMessages);
    if (res) {
      setMessages((prev) => [...prev, { role: "assistant", content: res.reply }]);
      if (res.board) {
        onBoardUpdate(res.board); // Auto-refreshes Kanban board state!
      }
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Expandable chat interface */}
    </div>
  );
};
```

---

### D. Back-End Server & Database (`backend/main.py` & `backend/database.py`)

FastAPI handles authentication checks, SQLite board operations, and mounts Next.js static assets at `/`.

```python
# backend/main.py
@app.get("/api/board", response_model=BoardResponse)
async def get_board(db: AsyncSession = Depends(get_db), username: str = Depends(verify_token)):
    return await fetch_user_board(db, username)

@app.post("/api/cards/move", response_model=BoardResponse)
async def move_card_endpoint(req: MoveCardRequest, db: AsyncSession = Depends(get_db), username: str = Depends(verify_token)):
    res = await db.execute(select(CardModel).where(CardModel.id == req.active_id))
    active_card = res.scalar_one_or_none()
    
    res = await db.execute(select(ColumnModel).where(ColumnModel.id == req.over_id))
    target_column = res.scalar_one_or_none()
    if target_column:
        active_card.column_id = target_column.id

    await db.commit()
    return await fetch_user_board(db, username)
```

---

### E. AI Service & Structured Output Parsing (`backend/ai_service.py`)

We prompt OpenRouter model `openai/gpt-oss-120b` to respond strictly in JSON formatted actions. If the API key is unconfigured or rate-limited, our rule-based parser guarantees fallback operations cleanly.

```python
# backend/ai_service.py
async def call_ai_chat(message: str, history: List[Dict[str, str]], board_data: BoardResponse) -> Dict[str, Any]:
    board_json = json.dumps(board_data.model_dump(), indent=2)
    messages = [
        {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nCurrent Board State:\n{board_json}"},
        {"role": "user", "content": message}
    ]

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(OPENROUTER_URL, headers=headers, json=payload)
            if res.status_code == 200:
                return json.loads(res.json()["choices"][0]["message"]["content"])
            else:
                return parse_fallback_intent(message, board_data)
    except Exception:
        return parse_fallback_intent(message, board_data)
```

---

### F. Multi-Stage Docker Build (`Dockerfile`)

Multi-stage builds allow us to use Node.js to compile Next.js static assets in Stage 1, and then copy only the compiled static files into a slim Python container in Stage 2.

```dockerfile
# Stage 1: Build Next.js Static Site
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python FastAPI Backend with uv
FROM python:3.11-slim
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PYTHONPATH=/app

COPY backend/pyproject.toml ./backend/
RUN uv pip install --system -r backend/pyproject.toml

COPY backend/ ./backend/
COPY --from=frontend-builder /app/frontend/out ./backend/static

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 4. How to Run, Stop, and Manage the Application

### Environment Configuration
Before running the application, make sure `backend/.env` contains your OpenRouter API Key:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Starting the Application

The startup scripts build the Docker image and launch the container on port 8000:

- **Windows PowerShell**:
  ```powershell
  .\scripts\start.ps1
  ```
- **Windows Command Prompt (cmd.exe)**:
  ```cmd
  scripts\start.bat
  ```
- **Mac / Linux Terminal**:
  ```bash
  chmod +x scripts/start.sh
  ./scripts/start.sh
  ```

Once started, open your browser and navigate to:
**`http://localhost:8000`**

- **Sign In Username**: `user`
- **Sign In Password**: `password`

---

### Stopping the Application

To cleanly stop and remove the container:

- **Windows PowerShell**:
  ```powershell
  .\scripts\stop.ps1
  ```
- **Windows Command Prompt (cmd.exe)**:
  ```cmd
  scripts\stop.bat
  ```
- **Mac / Linux Terminal**:
  ```bash
  ./scripts/stop.sh
  ```
- **Direct Docker CLI Command**:
  ```bash
  docker stop pm-kanban-app
  ```

---

### Running Automated Test Suites

To execute unit and integration tests:

- **Back-End Pytest Suite**:
  ```bash
  cd backend
  uv run pytest
  ```
- **Front-End Vitest Unit Suite**:
  ```bash
  cd frontend
  npm run test:unit
  ```
- **Front-End Playwright E2E Suite**:
  ```bash
  cd frontend
  npm run test:e2e
  ```

---

## 5. Five Code Improvement Suggestions (Self-Review)

While our MVP satisfies all functional, architectural, and business requirements, here are five high-impact enhancements for future production iterations:

### 1. Secure Password Hashing
- **Current State**: Uses plain text string comparison (`username == "user"` and `password == "password"`).
- **Improvement**: Implement `passlib` / `bcrypt` or `argon2` hashing in `backend/database.py` to securely store and verify hashed passwords in the SQLite `users` table.

### 2. HTTP-Only Cookie JWT Authentication
- **Current State**: Stores a static bearer token in `localStorage`.
- **Improvement**: Replace `localStorage` with JSON Web Tokens (JWT) stored in HTTP-Only, Secure, SameSite cookies to protect against Cross-Site Scripting (XSS) attacks.

### 3. Intra-Column Card Order Index Persistence
- **Current State**: Moving a card across columns updates its `column_id`. Reordering cards within the *same* column relies on front-end sortable list indexing.
- **Improvement**: Update `POST /api/cards/move` to accept an ordered list of `cardIds` for the target column and persist exact integer `position` values in the `cards` table.

### 4. Real-Time WebSockets / SSE for Multi-User Collaboration
- **Current State**: State updates are fetched via REST polling or local component state changes.
- **Improvement**: Integrate FastAPI WebSockets (`/ws/board`) or Server-Sent Events (SSE) so that when one user (or the AI) updates the board, all connected browsers see the board update instantly without reloading.

### 5. Multi-Board & Workspace Management
- **Current State**: Restricted to 1 Kanban board per signed-in user for MVP simplicity.
- **Improvement**: Add a board selector navigation bar allowing users to create, rename, archive, and switch between multiple project boards per user workspace.
