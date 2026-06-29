# =========================================================================
# AI Medical Scribe Platform - Common / Shared Pydantic Schemas
# =========================================================================
# Generic building blocks shared across multiple resources.
# Using Python generics (TypeVar + Generic) so one schema definition
# serves all paginated list responses: patients, doctors, appointments, etc.
# =========================================================================

import math
from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field

# T is bound to any Pydantic BaseModel subclass
T = TypeVar("T", bound=BaseModel)


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response envelope returned by all list endpoints.

    Attributes:
        items:  The slice of results for the requested page.
        total:  Total number of records matching the current filter/search.
        page:   The current page number (1-indexed).
        size:   The number of items requested per page.
        pages:  The total number of pages available.
    """

    items: List[T]
    total: int = Field(..., description="Total number of matching records", ge=0)
    page: int = Field(..., description="Current page number (1-indexed)", ge=1)
    size: int = Field(..., description="Items per page", ge=1)
    pages: int = Field(..., description="Total number of pages", ge=0)

    @classmethod
    def create(cls, items: List[T], total: int, page: int, size: int) -> "PaginatedResponse[T]":
        """
        Factory helper that computes `pages` automatically.

        Args:
            items: The slice of records for this page.
            total: Total count across all pages.
            page:  Current page number.
            size:  Page size.

        Returns:
            A fully-constructed PaginatedResponse instance.
        """
        pages = math.ceil(total / size) if size > 0 else 0
        return cls(items=items, total=total, page=page, size=size, pages=pages)
