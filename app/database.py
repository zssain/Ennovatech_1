from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import cx_Oracle
from fastapi import HTTPException
import logging
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database_health():
    try:
        with engine.connect() as connection:
            # Test basic connection
            connection.execute(text("SELECT 1 FROM DUAL"))
            
            # Test table existence
            tables = [
                "USERS", "DEPARTMENTS", "EMPLOYEES", "TASKS",
                "EMPLOYEE_SKILLS", "SKILLS", "EMPLOYEE_COURSES",
                "LEARNING_RESOURCES", "CAREER_LEVELS", "ATTENDANCE_RECORDS",
                "LEAVE_REQUESTS", "PERFORMANCE_METRICS", "NOTIFICATIONS",
                "SESSION_STORE"
            ]
            
            for table in tables:
                try:
                    connection.execute(text(f"SELECT 1 FROM {table} WHERE ROWNUM = 1"))
                    logger.info(f"Table {table} exists and is accessible")
                except Exception as e:
                    logger.error(f"Error accessing table {table}: {str(e)}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Database table {table} is not accessible"
                    )
            
            logger.info("Database health check passed successfully")
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Database health check failed"
        )

try:
    # Oracle connection settings from environment variables
    dsn = cx_Oracle.makedsn(
        settings.DB_HOST,
        settings.DB_PORT,
        service_name=settings.DB_SERVICE
    )
    DATABASE_URL = f"oracle+cx_oracle://{settings.DB_USER}:{settings.DB_PASSWORD}@{dsn}"

    # Create engine with connection pooling
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        echo=True
    )

    # Test the connection and run health check
    check_database_health()

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    def get_db():
        db = SessionLocal()
        try:
            yield db
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Database operation failed"
            )
        finally:
            db.close()

except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    raise HTTPException(
        status_code=500,
        detail="Failed to initialize database connection. Please check your Oracle installation and configuration."
    )
