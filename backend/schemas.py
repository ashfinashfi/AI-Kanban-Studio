from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    token: str
    username: str

class UserResponse(BaseModel):
    username: str

class CardSchema(BaseModel):
    id: str
    title: str
    details: str

class ColumnSchema(BaseModel):
    id: str
    title: str
    cardIds: List[str]

class BoardResponse(BaseModel):
    columns: List[ColumnSchema]
    cards: dict[str, CardSchema]

class RenameColumnRequest(BaseModel):
    title: str

class CreateCardRequest(BaseModel):
    column_id: str
    title: str
    details: Optional[str] = ""

class UpdateCardRequest(BaseModel):
    title: Optional[str] = None
    details: Optional[str] = None

class MoveCardRequest(BaseModel):
    active_id: str
    over_id: str

class ActionItem(BaseModel):
    type: Literal["create_card", "edit_card", "move_card", "delete_card", "rename_column"]
    column_id: Optional[str] = None
    column_title: Optional[str] = None
    card_id: Optional[str] = None
    title: Optional[str] = None
    details: Optional[str] = None
    target_column_id: Optional[str] = None
    position: Optional[int] = None

class AiChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = Field(default_factory=list)

class AiChatResponse(BaseModel):
    reply: str
    actions: List[ActionItem] = Field(default_factory=list)
    board: BoardResponse
