"""FlashAPI - Ultra-fast, modern web framework for Python"""

__version__ = "0.1.0"

from .app import FlashAPI
from .request import Request
from .response import JSONResponse, HTMLResponse, TextResponse, StreamResponse
from .middleware import Middleware, CORSMiddleware, CompressionMiddleware
from .decorators import get, post, put, delete, patch, head, options
from .validation import validate, Validator
from .caching import cache, MemoryCache, RedisCache
from .background import background_task
from .exceptions import HTTPException, ValidationError

__all__ = [
    "FlashAPI",
    "Request",
    "JSONResponse", "HTMLResponse", "TextResponse", "StreamResponse",
    "Middleware", "CORSMiddleware", "CompressionMiddleware",
    "get", "post", "put", "delete", "patch", "head", "options",
    "validate", "Validator",
    "cache", "MemoryCache", "RedisCache",
    "background_task",
    "HTTPException", "ValidationError"
]