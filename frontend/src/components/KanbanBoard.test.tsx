import { render, screen, within, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { KanbanBoard } from "@/components/KanbanBoard";

beforeEach(() => {
  localStorage.setItem("pm_auth_token", "pm-demo-auth-token-12345");
  global.fetch = vi.fn().mockImplementation((url: string) => {
    if (url.includes("/api/board")) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            columns: [
              { id: "col-backlog", title: "Backlog", cardIds: ["card-1"] },
              { id: "col-discovery", title: "Discovery", cardIds: [] },
              { id: "col-progress", title: "In Progress", cardIds: [] },
              { id: "col-review", title: "Review", cardIds: [] },
              { id: "col-done", title: "Done", cardIds: [] },
            ],
            cards: {
              "card-1": { id: "card-1", title: "Card 1", details: "Details 1" },
            },
          }),
      });
    }
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    });
  });
});

afterEach(() => {
  localStorage.clear();
  vi.resetAllMocks();
});

describe("KanbanBoard", () => {
  it("renders five columns after loading", async () => {
    render(<KanbanBoard />);
    await waitFor(() => {
      expect(screen.getAllByTestId(/column-/i)).toHaveLength(5);
    });
  });

  it("shows login form if unauthenticated", async () => {
    localStorage.removeItem("pm_auth_token");
    render(<KanbanBoard />);
    await waitFor(() => {
      expect(screen.getByText(/Kanban Studio Sign In/i)).toBeInTheDocument();
    });
  });
});
