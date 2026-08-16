import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.config import DATABASE_URL
from backend.models import Base, UserModel, BoardModel, ColumnModel, CardModel

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        res = await session.execute(select(UserModel).where(UserModel.username == "user"))
        user = res.scalar_one_or_none()
        if not user:
            user_id = str(uuid.uuid4())
            user = UserModel(id=user_id, username="user", password_hash="password")
            session.add(user)

            board_id = str(uuid.uuid4())
            board = BoardModel(id=board_id, user_id=user_id, title="Kanban Studio")
            session.add(board)

            default_columns = [
                ("col-backlog", "Backlog", 0, [
                    ("card-1", "Align roadmap themes", "Draft quarterly themes with impact statements and metrics."),
                    ("card-2", "Gather customer signals", "Review support tags, sales notes, and churn feedback.")
                ]),
                ("col-discovery", "Discovery", 1, [
                    ("card-3", "Prototype analytics view", "Sketch initial dashboard layout and key drill-downs.")
                ]),
                ("col-progress", "In Progress", 2, [
                    ("card-4", "Refine status language", "Standardize column labels and tone across the board."),
                    ("card-5", "Design card layout", "Add hierarchy and spacing for scanning dense lists.")
                ]),
                ("col-review", "Review", 3, [
                    ("card-6", "QA micro-interactions", "Verify hover, focus, and loading states.")
                ]),
                ("col-done", "Done", 4, [
                    ("card-7", "Ship marketing page", "Final copy approved and asset pack delivered."),
                    ("card-8", "Close onboarding sprint", "Document release notes and share internally.")
                ])
            ]

            for col_id, col_title, col_pos, cards in default_columns:
                column = ColumnModel(id=col_id, board_id=board_id, title=col_title, position=col_pos)
                session.add(column)
                for pos, (card_id, card_title, card_details) in enumerate(cards):
                    card = CardModel(id=card_id, column_id=col_id, title=card_title, details=card_details, position=pos)
                    session.add(card)

            await session.commit()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
