"""
Models for the in-memory cache.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class Node:
    """
    A single node in the doubly linked list.
    """
    key: str
    value: Any
    prev: Optional[Node] = field(default=None, repr=False)
    next: Optional[Node] = field(default=None, repr=False)