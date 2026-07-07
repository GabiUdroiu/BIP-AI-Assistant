from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_admin_service
from app.models.api_response import ApiResponse
from app.services.admin_service import AdminService

router = APIRouter(tags=["admin"], prefix="/admin")


class InsertRequest(BaseModel):
    data: dict[str, Any]


class ColumnInfo(BaseModel):
    name: str
    type: str
    nullable: bool
    primary_key: bool


def _require_table(admin_service: AdminService, table_name: str) -> None:
    if table_name not in admin_service.list_tables():
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")


@router.get("/tables", response_model=ApiResponse[list[str]])
def list_tables(admin_service: AdminService = Depends(get_admin_service)):
    return ApiResponse.ok(admin_service.list_tables())


@router.get("/tables/{table_name}/columns", response_model=ApiResponse[list[ColumnInfo]])
def get_columns(table_name: str, admin_service: AdminService = Depends(get_admin_service)):
    _require_table(admin_service, table_name)
    return ApiResponse.ok(admin_service.get_columns(table_name))


@router.get("/tables/{table_name}/rows")
def list_rows(table_name: str, limit: int = 50, admin_service: AdminService = Depends(get_admin_service)):
    _require_table(admin_service, table_name)
    return ApiResponse.ok(admin_service.list_rows(table_name, limit))


@router.post("/tables/{table_name}/rows")
def insert_row(table_name: str, request: InsertRequest, admin_service: AdminService = Depends(get_admin_service)):
    _require_table(admin_service, table_name)
    try:
        return ApiResponse.ok(admin_service.insert_row(table_name, request.data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/tables/{table_name}/rows/{pk_column}/{pk_value}")
def delete_row(
    table_name: str,
    pk_column: str,
    pk_value: str,
    admin_service: AdminService = Depends(get_admin_service),
):
    _require_table(admin_service, table_name)
    admin_service.delete_row(table_name, pk_column, pk_value)
    return ApiResponse.ok({"deleted": True})
