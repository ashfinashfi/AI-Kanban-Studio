export type Card = {
  id: string;
  title: string;
  details: string;
};

export type Column = {
  id: string;
  title: string;
  cardIds: string[];
};

export type BoardData = {
  columns: Column[];
  cards: Record<string, Card>;
};

export type ActionItem = {
  type: "create_card" | "edit_card" | "move_card" | "delete_card" | "rename_column";
  column_id?: string;
  column_title?: string;
  card_id?: string;
  title?: string;
  details?: string;
  target_column_id?: string;
};

export type AiChatResponse = {
  reply: string;
  actions: ActionItem[];
  board: BoardData;
};

const TOKEN_KEY = "pm_auth_token";

export const getStoredToken = (): string | null => {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
};

export const setStoredToken = (token: string): void => {
  if (typeof window !== "undefined") {
    localStorage.setItem(TOKEN_KEY, token);
  }
};

export const removeStoredToken = (): void => {
  if (typeof window !== "undefined") {
    localStorage.removeItem(TOKEN_KEY);
  }
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

export async function loginApi(username: string, password: string): Promise<boolean> {
  const res = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) return false;
  const data = await res.json();
  if (data.token) {
    setStoredToken(data.token);
    return true;
  }
  return false;
}

export async function logoutApi(): Promise<void> {
  removeStoredToken();
  try {
    await fetch("/api/auth/logout", { method: "POST" });
  } catch {
    // Ignore error
  }
}

export async function fetchBoardApi(): Promise<BoardData | null> {
  const res = await fetch("/api/board", { headers: getHeaders() });
  if (!res.ok) return null;
  return await res.json();
}

export async function renameColumnApi(columnId: string, title: string): Promise<BoardData | null> {
  const res = await fetch(`/api/columns/${columnId}/rename`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ title }),
  });
  if (!res.ok) return null;
  return await res.json();
}

export async function createCardApi(columnId: string, title: string, details: string): Promise<BoardData | null> {
  const res = await fetch("/api/cards", {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ column_id: columnId, title, details }),
  });
  if (!res.ok) return null;
  return await res.json();
}

export async function updateCardApi(cardId: string, title: string, details: string): Promise<BoardData | null> {
  const res = await fetch(`/api/cards/${cardId}`, {
    method: "PUT",
    headers: getHeaders(),
    body: JSON.stringify({ title, details }),
  });
  if (!res.ok) return null;
  return await res.json();
}

export async function deleteCardApi(cardId: string): Promise<BoardData | null> {
  const res = await fetch(`/api/cards/${cardId}`, {
    method: "DELETE",
    headers: getHeaders(),
  });
  if (!res.ok) return null;
  return await res.json();
}

export async function moveCardApi(activeId: string, overId: string): Promise<BoardData | null> {
  const res = await fetch("/api/cards/move", {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ active_id: activeId, over_id: overId }),
  });
  if (!res.ok) return null;
  return await res.json();
}

export async function aiChatApi(message: string, history: Array<{ role: string; content: string }>): Promise<AiChatResponse | null> {
  const res = await fetch("/api/ai/chat", {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ message, history }),
  });
  if (!res.ok) return null;
  return await res.json();
}
