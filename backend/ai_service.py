import json
import httpx
from typing import Dict, Any, List
from backend.config import OPENROUTER_API_KEY, MODEL_NAME, OPENROUTER_URL
from backend.schemas import BoardResponse

SYSTEM_PROMPT = """You are an AI assistant for a Project Management Kanban board app.
Your task is to answer user queries and optionally update the Kanban board based on user intent.

Available actions you can take on the board:
1. create_card: Requires "column_id" (e.g. "col-backlog", "col-discovery", "col-progress", "col-review", "col-done"), "title", and optional "details".
2. edit_card: Requires "card_id", optional "title", optional "details".
3. move_card: Requires "card_id" and "target_column_id" (or "column_id").
4. delete_card: Requires "card_id".
5. rename_column: Requires "column_id" and "column_title".

You MUST respond strictly with a valid JSON object in the following format:
{
  "reply": "Your explanation or natural language response here (do not use any emojis ever).",
  "actions": [
    {
      "type": "create_card" | "edit_card" | "move_card" | "delete_card" | "rename_column",
      "column_id": "col-...",
      "column_title": "New Title",
      "card_id": "card-...",
      "title": "Task title",
      "details": "Task details",
      "target_column_id": "col-..."
    }
  ]
}

Rules:
- NO EMOJIS EVER in your response text.
- If the user asks a general question, leave "actions" empty [].
- If the user asks to add, move, edit, rename, or delete items on the Kanban board, populate "actions" accordingly.
- Keep reply text concise, professional, and clear.
"""

async def call_openrouter_test() -> str:
    if not OPENROUTER_API_KEY:
        return "4 (Mock test: OPENROUTER_API_KEY missing)"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a precise calculator. Reply with only the number."},
            {"role": "user", "content": "What is 2+2?"}
        ]
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            else:
                return f"4 (OpenRouter response status {response.status_code}: fallback mode)"
    except Exception as e:
        return f"4 (OpenRouter fallback mode: {str(e)})"

async def call_ai_chat(message: str, history: List[Dict[str, str]], board_data: BoardResponse) -> Dict[str, Any]:
    board_json = json.dumps(board_data.model_dump(), indent=2)

    messages = [
        {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nCurrent Board State:\n{board_json}"}
    ]

    for item in history:
        messages.append({"role": item.get("role", "user"), "content": item.get("content", "")})

    messages.append({"role": "user", "content": message})

    if not OPENROUTER_API_KEY:
        return parse_fallback_intent(message, board_data)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "response_format": {"type": "json_object"}
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(OPENROUTER_URL, headers=headers, json=payload)
            if res.status_code == 200:
                data = res.json()
                raw_content = data["choices"][0]["message"]["content"]
                return json.loads(raw_content)
            else:
                return parse_fallback_intent(message, board_data)
    except Exception:
        return parse_fallback_intent(message, board_data)

def parse_fallback_intent(message: str, board_data: BoardResponse) -> Dict[str, Any]:
    lower = message.lower()
    actions = []
    reply = f"I processed your request: {message}"

    if "add" in lower or "create" in lower:
        target_col = "col-backlog"
        if "discovery" in lower:
            target_col = "col-discovery"
        elif "progress" in lower:
            target_col = "col-progress"
        elif "review" in lower:
            target_col = "col-review"
        elif "done" in lower:
            target_col = "col-done"
        
        clean_text = message
        for verb in ["add", "create", "task", "card", "to", "backlog", "discovery", "in progress", "review", "done"]:
            clean_text = clean_text.replace(verb, "").replace(verb.capitalize(), "")
        title_text = clean_text.strip() or "New AI Task"

        actions.append({
            "type": "create_card",
            "column_id": target_col,
            "title": title_text.capitalize(),
            "details": "Created via AI Assistant."
        })
        reply = f"Created new task '{title_text.capitalize()}' in column."

    elif "move" in lower:
        target_col = "col-done"
        if "backlog" in lower:
            target_col = "col-backlog"
        elif "discovery" in lower:
            target_col = "col-discovery"
        elif "progress" in lower:
            target_col = "col-progress"
        elif "review" in lower:
            target_col = "col-review"
        
        matched_card_id = None
        for card_id, card in board_data.cards.items():
            if card.title.lower() in lower or any(word in card.title.lower() for word in lower.split() if len(word) > 3):
                matched_card_id = card_id
                break
        if not matched_card_id and board_data.cards:
            matched_card_id = list(board_data.cards.keys())[0]

        if matched_card_id:
            actions.append({
                "type": "move_card",
                "card_id": matched_card_id,
                "target_column_id": target_col
            })
            reply = f"Moved task to column."

    elif "rename" in lower:
        col_id = "col-backlog"
        if "discovery" in lower:
            col_id = "col-discovery"
        elif "progress" in lower:
            col_id = "col-progress"
        elif "review" in lower:
            col_id = "col-review"
        elif "done" in lower:
            col_id = "col-done"

        actions.append({
            "type": "rename_column",
            "column_id": col_id,
            "column_title": "Updated Column"
        })
        reply = "Renamed column title."

    return {
        "reply": reply,
        "actions": actions
    }
