# Frontend Architecture and Components

## Overview

The frontend is built with Next.js 16 (App Router), React 19, TypeScript, and TailwindCSS v4. It features a responsive, single-board Kanban interface using `@dnd-kit/core` and `@dnd-kit/sortable` for drag-and-drop mechanics.

## Component Structure

- **`src/app/page.tsx`**: Main page rendering `KanbanBoard`.
- **`src/components/KanbanBoard.tsx`**: Manages top-level board state, drag-and-drop context (`DndContext`), column rendering, and modal dialogs.
- **`src/components/KanbanColumn.tsx`**: Represents a single column (Backlog, Discovery, In Progress, Review, Done). Renders cards using sortable context and column renaming UI.
- **`src/components/KanbanCard.tsx`**: Renders individual task card with title, details preview, edit, and delete functionality.
- **`src/components/KanbanCardPreview.tsx`**: Drag overlay preview element when dragging a card across columns.
- **`src/components/NewCardForm.tsx`**: Modal form for creating a new card within a specific column.

## Data Layer (`src/lib/kanban.ts`)

- **`Card`**: `{ id: string, title: string, details: string }`
- **`Column`**: `{ id: string, title: string, cardIds: string[] }`
- **`BoardData`**: `{ columns: Column[], cards: Record<string, Card> }`
- **`moveCard`**: Pure helper function handling intra-column reordering and inter-column card moves.
- **`initialData`**: Default board configuration containing 5 fixed columns and initial cards.

## Testing Setup

- **Unit Testing**: Vitest with `@testing-library/react` and `@testing-library/jest-dom`. Command: `npm run test:unit`.
- **End-to-End Testing**: Playwright. Command: `npm run test:e2e`.
- **Linting**: ESLint with `eslint-config-next`. Command: `npm run lint`.
