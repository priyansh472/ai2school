import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.future import select

# Add app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.models.core import School, User
from app.core.security import get_password_hash

engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def seed():
    async with AsyncSessionLocal() as session:
        # Check if school exists
        result = await session.execute(select(School).filter(School.code == "DPS_RKP"))
        school = result.scalars().first()
        
        if not school:
            school = School(
                name="Delhi Public School, R.K. Puram",
                code="DPS_RKP",
                board="CBSE",
                config={"i18n": {"default_lang": "en", "available_langs": ["en", "hi"]}}
            )
            session.add(school)
            await session.commit()
            await session.refresh(school)
            print(f"Created School: {school.name} with ID: {school.id}")
        else:
            print(f"School already exists: {school.name}")

        # Check if admin user exists
        result = await session.execute(select(User).filter(User.email == "admin@ai2school.com"))
        admin = result.scalars().first()
        
        if not admin:
            admin = User(
                school_id=school.id,
                email="admin@ai2school.com",
                hashed_password=get_password_hash("password"),
                role="superadmin"
            )
            session.add(admin)
            await session.commit()
            print(f"Created Admin User: {admin.email}")
        else:
            print(f"Admin User already exists: {admin.email}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed())
