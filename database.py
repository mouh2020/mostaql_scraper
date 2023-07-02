from typing import Optional

from sqlmodel import Field, SQLModel, create_engine

class Offer(SQLModel, table=True):
    id              : Optional[int]     = Field(default=None, primary_key=True)
    offer_id        : int
    category        : Optional[str]     = Field(default=None)
    title           : Optional[str]     = Field(default=None)
    price           : Optional[str]     = Field(default=None)
    project_owner   : Optional[str]     = Field(default=None)

sqlite_file_name = "mostaql_offers.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
