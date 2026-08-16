"use client";

import { useState } from "react";
import { aiChatApi, type BoardData } from "@/lib/api";

type Message = {
  role: "user" | "assistant";
  content: string;
};

type AiSidebarProps = {
  onBoardUpdate: (newBoard: BoardData) => void;
};

export const AiSidebar = ({ onBoardUpdate }: AiSidebarProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello. I am your Project Management AI Assistant. How can I help with your Kanban board today?",
    },
  ]);
  const [loading, setLoading] = useState(false);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userText = input.trim();
    setInput("");

    const newMessages: Message[] = [...messages, { role: "user", content: userText }];
    setMessages(newMessages);
    setLoading(true);

    try {
      const historyPayload = newMessages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const res = await aiChatApi(userText, historyPayload);
      if (res) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: res.reply },
        ]);
        if (res.board) {
          onBoardUpdate(res.board);
        }
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: "Unable to process request at this time." },
        ]);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Error connecting to AI service." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="flex items-center gap-3 rounded-full border border-[var(--stroke)] bg-[var(--navy-dark)] px-6 py-3.5 text-sm font-semibold text-white shadow-xl hover:bg-opacity-95 transition"
        >
          <span className="h-2.5 w-2.5 rounded-full bg-[var(--accent-yellow)]" />
          AI Assistant
        </button>
      )}

      {isOpen && (
        <div className="flex h-[540px] w-[360px] flex-col rounded-3xl border border-[var(--stroke)] bg-white shadow-2xl overflow-hidden">
          <div className="flex items-center justify-between border-b border-[var(--stroke)] bg-[var(--navy-dark)] px-5 py-4 text-white">
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-[var(--accent-yellow)]" />
              <h2 className="text-sm font-bold uppercase tracking-wider">AI Assistant</h2>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-xs font-semibold text-[var(--gray-text)] hover:text-white"
            >
              Close
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3.5 bg-gray-50/50">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 text-xs leading-5 ${
                    msg.role === "user"
                      ? "bg-[var(--secondary-purple)] text-white rounded-br-none"
                      : "bg-white border border-[var(--stroke)] text-[var(--navy-dark)] rounded-bl-none shadow-sm"
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="max-w-[85%] rounded-2xl rounded-bl-none bg-white border border-[var(--stroke)] px-4 py-3 text-xs text-[var(--gray-text)] shadow-sm">
                  Thinking and updating board...
                </div>
              </div>
            )}
          </div>

          <form onSubmit={handleSend} className="border-t border-[var(--stroke)] p-3 bg-white">
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask AI to create, edit, or move cards..."
                disabled={loading}
                className="flex-1 rounded-xl border border-[var(--stroke)] px-3.5 py-2.5 text-xs text-[var(--navy-dark)] focus:border-[var(--primary-blue)] focus:outline-none disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="rounded-xl bg-[var(--primary-blue)] px-4 py-2.5 text-xs font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
              >
                Send
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
