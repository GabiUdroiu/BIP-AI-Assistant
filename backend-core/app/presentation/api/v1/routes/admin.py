"""
Admin routes.
Database management and inspection endpoints.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_admin_service
from app.services.admin_service import AdminService
from app.presentation.api.v1.schemas import ApiResponse, TablesResponse, TableInfo

router = APIRouter(tags=["admin"], prefix="/admin")


class InsertRequest(BaseModel):
    """Request body for inserting a row."""
    data: dict[str, Any]


class UpdateRequest(BaseModel):
    """Request body for updating a row."""
    data: dict[str, Any]


class ColumnInfo(BaseModel):
    """Information about a column."""
    name: str
    type: str
    nullable: bool
    primary_key: bool


def _require_table(admin_service: AdminService, table_name: str) -> None:
    """Verify that a table exists."""
    if table_name not in admin_service.list_tables():
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")


@router.get("/tables", response_model=ApiResponse[list[str]])
def list_tables(admin_service: AdminService = Depends(get_admin_service)):
    """List all database tables."""
    try:
        tables = admin_service.list_tables()
        return ApiResponse(data=tables)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/tables/{table_name}/columns", response_model=ApiResponse[list[ColumnInfo]])
def get_columns(table_name: str, admin_service: AdminService = Depends(get_admin_service)):
    """Get column information for a table."""
    _require_table(admin_service, table_name)
    try:
        columns = admin_service.get_columns(table_name)
        return ApiResponse(data=columns)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/tables/{table_name}/rows")
def list_rows(table_name: str, limit: int = 50, admin_service: AdminService = Depends(get_admin_service)):
    """Get rows from a table."""
    _require_table(admin_service, table_name)
    try:
        rows = admin_service.list_rows(table_name, limit)
        return ApiResponse(data={"table": table_name, "rows": rows, "count": len(rows)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/tables/{table_name}/rows")
def insert_row(table_name: str, request: InsertRequest, admin_service: AdminService = Depends(get_admin_service)):
    """Insert a row into a table."""
    _require_table(admin_service, table_name)
    try:
        result = admin_service.insert_row(table_name, request.data)
        return ApiResponse(data={"inserted": result})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.patch("/tables/{table_name}/rows/{pk_column}/{pk_value}")
def update_row(
    table_name: str,
    pk_column: str,
    pk_value: str,
    request: UpdateRequest,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Update a row in a table."""
    _require_table(admin_service, table_name)
    try:
        result = admin_service.update_row(table_name, pk_column, pk_value, request.data)
        return ApiResponse(data={"updated": result})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/tables/{table_name}/rows/{pk_column}/{pk_value}")
def delete_row(
    table_name: str,
    pk_column: str,
    pk_value: str,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Delete a row from a table."""
    _require_table(admin_service, table_name)
    try:
        admin_service.delete_row(table_name, pk_column, pk_value)
        return ApiResponse(data={"deleted": True})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
