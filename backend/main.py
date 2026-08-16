import uuid
from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.config import STATIC_DIR
from backend.database import init_db, get_db
from backend.models import UserModel, BoardModel, ColumnModel, CardModel
from backend.schemas import (
    LoginRequest, LoginResponse, UserResponse,
    BoardResponse, ColumnSchema, CardSchema,
    RenameColumnRequest, CreateCardRequest, UpdateCardRequest, MoveCardRequest,
    AiChatRequest, AiChatResponse, ActionItem
)
from backend.ai_service import call_openrouter_test, call_ai_chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Project Management MVP API", lifespan=lifespan)

VALID_TOKEN = "pm-demo-auth-token-12345"

def verify_token(request: Request) -> str:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        if token == VALID_TOKEN:
            return "user"
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing authentication token")

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "Project Management MVP Backend"}

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    if req.username == "user" and req.password == "password":
        return LoginResponse(success=True, token=VALID_TOKEN, username="user")
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/api/auth/logout")
async def logout():
    return {"success": True}

@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(username: str = Depends(verify_token)):
    return UserResponse(username=username)

async def fetch_user_board(db: AsyncSession, username: str = "user") -> BoardResponse:
    res = await db.execute(select(UserModel).where(UserModel.username == username))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    res = await db.execute(select(BoardModel).where(BoardModel.user_id == user.id))
    board = res.scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    res = await db.execute(select(ColumnModel).where(ColumnModel.board_id == board.id).order_by(ColumnModel.position))
    columns = res.scalars().all()

    cards_by_id = {}
    col_schemas = []

    for col in columns:
        res = await db.execute(select(CardModel).where(CardModel.column_id == col.id).order_by(CardModel.position))
        col_cards = res.scalars().all()
        card_ids = []
        for card in col_cards:
            card_ids.append(card.id)
            cards_by_id[card.id] = CardSchema(id=card.id, title=card.title, details=card.details)
        
        col_schemas.append(ColumnSchema(id=col.id, title=col.title, cardIds=card_ids))

    return BoardResponse(columns=col_schemas, cards=cards_by_id)

@app.get("/api/board", response_model=BoardResponse)
async def get_board(db: AsyncSession = Depends(get_db), username: str = Depends(verify_token)):
    return await fetch_user_board(db, username)

@app.post("/api/columns/{column_id}/rename", response_model=BoardResponse)
async def rename_column(column_id: str, req: RenameColumnRequest, db: AsyncSession = Depends(get_db), username: str = Depends(verify_token)):
    res = await db.execute(select(ColumnModel).where(ColumnModel.id == column_id))
    column = res.scalar_one_or_none()
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    column.title = req.title
    await db.commit()
    return await fetch_user_board(db, username)

@app.post("/api/cards", response_model=BoardResponse)
async def create_card(req: CreateCardRequest, db: AsyncSession = Depends(get_db), username: str = Depends(verify_token)):
    res = await db.execute(select(ColumnModel).where(ColumnModel.id == req.column_id))
    column = res.scalar_one_or_none()
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")

    res = await db.execute(select(CardModel).where(CardModel.column_id == req.column_id))
    existing_cards = res.scalars().all()
    next_pos = len(existing_cards)

    new_card_id = f"card-{uuid.uuid4().hex[:6]}"
    card = CardModel(
        id=new_card_id,
        column_id=req.column_id,
        title=req.title,
        details=req.details or "No details yet.",
        position=next_pos
    )
    db.add(card)
    await db.commit()
    return await fetch_user_board(db, username)

@app.put("/api/cards/{card_id}", response_model=BoardResponse)
async def update_card(card_id: str, req: UpdateCardRequest, db: AsyncSession = Depends(get_db), username: str = Depends(verify_token)):
    res = await db.execute(select(CardModel).where(CardModel.id == card_id))
    card = res.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    if req.title is not None:
        card.title = req.title
    if req.details is not None:
        card.details = req.details
    await db.commit()
    return await fetch_user_board(db, username)

@app.delete("/api/cards/{card_id}", response_model=BoardResponse)
async def delete_card(card_id: str, db: AsyncSession = Depends(get_db), username: str = Depends(verify_token)):
    res = await db.execute(select(CardModel).where(CardModel.id == card_id))
    card = res.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    await db.delete(card)
    await db.commit()
    return await fetch_user_board(db, username)

@app.post("/api/cards/move", response_model=BoardResponse)
async def move_card_endpoint(req: MoveCardRequest, db: AsyncSession = Depends(get_db), username: str = Depends(verify_token)):
    res = await db.execute(select(CardModel).where(CardModel.id == req.active_id))
    active_card = res.scalar_one_or_none()
    if not active_card:
        raise HTTPException(status_code=404, detail="Active card not found")

    res = await db.execute(select(ColumnModel).where(ColumnModel.id == req.over_id))
    target_column = res.scalar_one_or_none()

    if target_column:
        active_card.column_id = target_column.id
    else:
        res = await db.execute(select(CardModel).where(CardModel.id == req.over_id))
        over_card = res.scalar_one_or_none()
        if over_card:
            active_card.column_id = over_card.column_id

    await db.commit()
    return await fetch_user_board(db, username)

@app.get("/api/ai/test")
async def ai_test_endpoint():
    result = await call_openrouter_test()
    return {"result": result}

@app.post("/api/ai/chat", response_model=AiChatResponse)
async def ai_chat_endpoint(req: AiChatRequest, db: AsyncSession = Depends(get_db), username: str = Depends(verify_token)):
    board = await fetch_user_board(db, username)
    ai_res = await call_ai_chat(req.message, req.history or [], board)

    reply = ai_res.get("reply", "Action completed.")
    actions_raw = ai_res.get("actions", [])

    for act in actions_raw:
        act_type = act.get("type")
        if act_type == "create_card":
            col_id = act.get("column_id") or "col-backlog"
            title = act.get("title") or "New AI Task"
            details = act.get("details") or "Created by AI Assistant."
            res = await db.execute(select(ColumnModel).where(ColumnModel.id == col_id))
            col = res.scalar_one_or_none()
            if col:
                res = await db.execute(select(CardModel).where(CardModel.column_id == col_id))
                next_pos = len(res.scalars().all())
                new_card = CardModel(
                    id=f"card-{uuid.uuid4().hex[:6]}",
                    column_id=col_id,
                    title=title,
                    details=details,
                    position=next_pos
                )
                db.add(new_card)

        elif act_type == "move_card":
            card_id = act.get("card_id")
            target_col_id = act.get("target_column_id") or act.get("column_id")
            if card_id and target_col_id:
                res = await db.execute(select(CardModel).where(CardModel.id == card_id))
                card = res.scalar_one_or_none()
                if card:
                    card.column_id = target_col_id

        elif act_type == "edit_card":
            card_id = act.get("card_id")
            if card_id:
                res = await db.execute(select(CardModel).where(CardModel.id == card_id))
                card = res.scalar_one_or_none()
                if card:
                    if act.get("title"):
                        card.title = act.get("title")
                    if act.get("details"):
                        card.details = act.get("details")

        elif act_type == "delete_card":
            card_id = act.get("card_id")
            if card_id:
                res = await db.execute(select(CardModel).where(CardModel.id == card_id))
                card = res.scalar_one_or_none()
                if card:
                    await db.delete(card)

        elif act_type == "rename_column":
            col_id = act.get("column_id")
            col_title = act.get("column_title") or act.get("title")
            if col_id and col_title:
                res = await db.execute(select(ColumnModel).where(ColumnModel.id == col_id))
                col = res.scalar_one_or_none()
                if col:
                    col.title = col_title

    await db.commit()
    updated_board = await fetch_user_board(db, username)

    typed_actions = [ActionItem(**a) for a in actions_raw if isinstance(a, dict)]
    return AiChatResponse(reply=reply, actions=typed_actions, board=updated_board)

if STATIC_DIR.exists():
    app.mount("/_next", StaticFiles(directory=STATIC_DIR / "_next"), name="next-static")

@app.get("/{full_path:path}")
async def serve_static_spa(full_path: str):
    file_path = STATIC_DIR / full_path
    if full_path and file_path.is_file():
        return FileResponse(file_path)
    index_path = STATIC_DIR / "index.html"
    if index_path.is_file():
        return FileResponse(index_path)
    return JSONResponse({"status": "Frontend building..."}, status_code=200)
