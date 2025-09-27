from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


class User(BaseModel):
    __tablename__ = "users"

    packs: Mapped[list["StickerPack"]] = relationship(back_populates="owner")


class StickerPack(BaseModel):
    __tablename__ = "sticker_packs"

    name: Mapped[str] = mapped_column(String(100))
    short_name: Mapped[str] = mapped_column(String(150), unique=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship(back_populates="packs")
