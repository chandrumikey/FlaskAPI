from typing import Callable, List
from functools import wraps

def route(path: str, methods: List[str], **kwargs):
    """Base route decorator with configuration"""
    def decorator(handler: Callable):
        @wraps(handler)
        def wrapper(app):
            app.add_route(path, methods, handler, **kwargs)
            return handler
        return wrapper
    return decorator

def get(path: str, **kwargs):
    """GET route with caching support"""
    return route(path, ["GET"], **kwargs)

def post(path: str, **kwargs):
    """POST route with validation"""
    return route(path, ["POST"], **kwargs)

def put(path: str, **kwargs):
    """PUT route"""
    return route(path, ["PUT"], **kwargs)

def delete(path: str, **kwargs):
    """DELETE route"""
    return route(path, ["DELETE"], **kwargs)

def patch(path: str, **kwargs):
    """PATCH route"""
    return route(path, ["PATCH"], **kwargs)

def head(path: str, **kwargs):
    """HEAD route"""
    return route(path, ["HEAD"], **kwargs)

def options(path: str, **kwargs):
    """OPTIONS route"""
    return route(path, ["OPTIONS"], **kwargs)