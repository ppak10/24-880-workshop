from typing import Union, Dict, Any, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar("T")


class ToolError(BaseModel):
    """Standard error response for MCP tools."""

    success: bool = False
    error: str
    error_code: str
    details: Dict[str, Any] = {}


class ToolSuccess(BaseModel, Generic[T]):
    """Standard success response for MCP tools."""

    success: bool = True
    data: T


ToolResponse = Union[ToolSuccess[T], ToolError]
