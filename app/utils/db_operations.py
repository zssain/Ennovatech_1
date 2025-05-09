from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
import logging
from app.utils.error_handlers import handle_database_operation, DatabaseError

logger = logging.getLogger(__name__)

@handle_database_operation
async def execute_query(db: Session, query: str, params: Optional[Dict] = None) -> List[Dict]:
    try:
        result = db.execute(text(query), params or {})
        return [dict(row) for row in result]
    except Exception as e:
        logger.error(f"Query execution failed: {str(e)}")
        raise DatabaseError(str(e))

@handle_database_operation
async def execute_update(db: Session, query: str, params: Optional[Dict] = None) -> int:
    try:
        result = db.execute(text(query), params or {})
        db.commit()
        return result.rowcount
    except Exception as e:
        db.rollback()
        logger.error(f"Update execution failed: {str(e)}")
        raise DatabaseError(str(e))

@handle_database_operation
async def execute_insert(db: Session, query: str, params: Optional[Dict] = None) -> int:
    try:
        result = db.execute(text(query), params or {})
        db.commit()
        return result.lastrowid
    except Exception as e:
        db.rollback()
        logger.error(f"Insert execution failed: {str(e)}")
        raise DatabaseError(str(e))

@handle_database_operation
async def execute_delete(db: Session, query: str, params: Optional[Dict] = None) -> int:
    try:
        result = db.execute(text(query), params or {})
        db.commit()
        return result.rowcount
    except Exception as e:
        db.rollback()
        logger.error(f"Delete execution failed: {str(e)}")
        raise DatabaseError(str(e))

@handle_database_operation
async def execute_transaction(db: Session, operations: List[Dict[str, Any]]) -> bool:
    try:
        for operation in operations:
            query = operation.get('query')
            params = operation.get('params', {})
            operation_type = operation.get('type', 'query')
            
            if operation_type == 'query':
                await execute_query(db, query, params)
            elif operation_type == 'update':
                await execute_update(db, query, params)
            elif operation_type == 'insert':
                await execute_insert(db, query, params)
            elif operation_type == 'delete':
                await execute_delete(db, query, params)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Transaction failed: {str(e)}")
        raise DatabaseError(str(e))

@handle_database_operation
async def check_table_exists(db: Session, table_name: str) -> bool:
    try:
        query = """
        SELECT COUNT(*) 
        FROM USER_TABLES 
        WHERE TABLE_NAME = :table_name
        """
        result = await execute_query(db, query, {'table_name': table_name.upper()})
        return result[0]['COUNT(*)'] > 0
    except Exception as e:
        logger.error(f"Table existence check failed: {str(e)}")
        raise DatabaseError(str(e))

@handle_database_operation
async def get_table_columns(db: Session, table_name: str) -> List[Dict]:
    try:
        query = """
        SELECT column_name, data_type, data_length, nullable
        FROM USER_TAB_COLUMNS
        WHERE table_name = :table_name
        ORDER BY column_id
        """
        return await execute_query(db, query, {'table_name': table_name.upper()})
    except Exception as e:
        logger.error(f"Column retrieval failed: {str(e)}")
        raise DatabaseError(str(e)) 