import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    boards = relationship("BoardModel", back_populates="user", cascade="all, delete-orphan")

class BoardModel(Base):
    __tablename__ = "boards"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("UserModel", back_populates="boards")
    columns = relationship("ColumnModel", back_populates="board", cascade="all, delete-orphan", order_by="ColumnModel.position")

class ColumnModel(Base):
    __tablename__ = "columns"

    id = Column(String(36), primary_key=True)
    board_id = Column(String(36), ForeignKey("boards.id"), nullable=False, index=True)
    title = Column(String(128), nullable=False)
    position = Column(Integer, nullable=False, default=0)

    board = relationship("BoardModel", back_populates="columns")
    cards = relationship("CardModel", back_populates="column", cascade="all, delete-orphan", order_by="CardModel.position")

class CardModel(Base):
    __tablename__ = "cards"

    id = Column(String(36), primary_key=True)
    column_id = Column(String(36), ForeignKey("columns.id"), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    details = Column(Text, nullable=False, default="")
    position = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    column = relationship("ColumnModel", back_populates="cards")
