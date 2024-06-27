from sqlalchemy import text

from app.db.models import Base


async def truncate_tables(session):
    query = text(f"""TRUNCATE {",".join(Base.metadata.tables)} RESTART IDENTITY CASCADE""")
    await session.execute(query)
    await session.commit()
