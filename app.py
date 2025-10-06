import asyncio
import time
import inspect
from typing import Dict, List, Callable, Any, Optional, Union
from dataclasses import dataclass
from .router import Router
from .request import Request
from .response import Response, JSONResponse
from .middleware import Middleware
from .exceptions import HTTPException
from .caching import MemoryCache
from .background import BackgroundTaskManager

@dataclass
class FlashConfig:
    debug: bool = False
    title: str = "FlashAPI"
    version: str = "1.0.0"
    description: str = "Ultra-fast API"
    enable_compression: bool = True
    enable_caching: bool = True
    cache_ttl: int = 300

class FlashAPI:
    def __init__(self, config: Optional[FlashConfig] = None):
        self.config = config or FlashConfig()
        self.router = Router()
        self.middleware: List[Middleware] = []
        self.exception_handlers: Dict[Any, Callable] = {}
        self.startup_tasks: List[Callable] = []
        self.shutdown_tasks: List[Callable] = []
        self.cache = MemoryCache() if self.config.enable_caching else None
        self.background_tasks = BackgroundTaskManager()
        
        # Performance tracking
        self.request_times: List[float] = []
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default exception handlers"""
        self.add_exception_handler(HTTPException, self._handle_http_exception)
        self.add_exception_handler(500, self._handle_500_exception)
        self.add_exception_handler(404, self._handle_404_exception)
    
    def add_route(self, path: str, methods: List[str], handler: Callable, **kwargs):
        """Add route with performance optimizations"""
        self.router.add_route(path, methods, handler, **kwargs)
    
    def add_middleware(self, middleware_class: type, **kwargs):
        """Add middleware with dependency injection"""
        middleware = middleware_class(**kwargs)
        self.middleware.append(middleware)
    
    def add_exception_handler(self, exc_class: Any, handler: Callable):
        """Add exception handler"""
        self.exception_handlers[exc_class] = handler
    
    def on_startup(self, func: Callable):
        """Register startup task"""
        self.startup_tasks.append(func)
        return func
    
    def on_shutdown(self, func: Callable):
        """Register shutdown task"""
        self.shutdown_tasks.append(func)
        return func
    
    async def __call__(self, scope: Dict, receive: Callable, send: Callable):
        """ASGI interface with performance monitoring"""
        if scope["type"] == "http":
            start_time = time.perf_counter()
            await self._handle_http_request(scope, receive, send)
            response_time = time.perf_counter() - start_time
            self.request_times.append(response_time)
            
            # Keep only last 1000 timings for stats
            if len(self.request_times) > 1000:
                self.request_times.pop(0)
    
    async def _handle_http_request(self, scope: Dict, receive: Callable, send: Callable):
        """Handle HTTP request with middleware pipeline"""
        request = Request(scope, receive)
        response = None
        
        try:
            # Pre-process middleware
            for middleware in self.middleware:
                if hasattr(middleware, 'before_request'):
                    request = await middleware.before_request(request) or request
            
            # Route matching
            route_match = self.router.find_route(request.path, request.method)
            if not route_match:
                raise HTTPException(404, f"Route {request.path} not found")
            
            handler, path_params, route_config = route_match
            request.path_params = path_params
            
            # Execute handler
            handler_args = await self._prepare_handler_args(request, handler, path_params)
            
            if asyncio.iscoroutinefunction(handler):
                result = await handler(**handler_args)
            else:
                # Run sync handlers in thread pool
                result = await asyncio.get_event_loop().run_in_executor(
                    None, handler, **handler_args
                )
            
            # Convert to response
            response = self._create_response(result)
            
        except Exception as exc:
            response = await self._handle_exception(exc)
        
        # Post-process middleware
        for middleware in reversed(self.middleware):
            if hasattr(middleware, 'after_request'):
                response = await middleware.after_request(request, response) or response
        
        await response(scope, receive, send)
    
    async def _prepare_handler_args(self, request: Request, handler: Callable, path_params: Dict):
        """Prepare handler arguments with dependency injection"""
        sig = inspect.signature(handler)
        handler_args = {}
        
        for param_name, param in sig.parameters.items():
            if param_name in path_params:
                handler_args[param_name] = path_params[param_name]
            elif param_name == 'request':
                handler_args[param_name] = request
            elif param.annotation != inspect.Parameter.empty:
                # Auto-inject based on type hints
                if param.annotation == Request:
                    handler_args[param_name] = request
        
        return handler_args
    
    def _create_response(self, result: Any) -> Response:
        """Convert handler result to appropriate response"""
        if isinstance(result, Response):
            return result
        elif isinstance(result, (dict, list)):
            return JSONResponse(result)
        elif isinstance(result, str):
            return TextResponse(result)
        else:
            return JSONResponse({"result": result})
    
    async def _handle_exception(self, exc: Exception) -> Response:
        """Handle exceptions with registered handlers"""
        for exc_class, handler in self.exception_handlers.items():
            if isinstance(exc, exc_class) or exc_class == type(exc):
                if asyncio.iscoroutinefunction(handler):
                    return await handler(exc)
                else:
                    return handler(exc)
        
        # Default error response
        return JSONResponse(
            {"error": "Internal Server Error", "message": str(exc)},
            status_code=500
        )
    
    async def _handle_http_exception(self, exc: HTTPException) -> Response:
        return JSONResponse(
            {"error": exc.detail, "status_code": exc.status_code},
            status_code=exc.status_code
        )
    
    async def _handle_404_exception(self, exc: Exception) -> Response:
        return JSONResponse(
            {"error": "Not Found", "message": str(exc)},
            status_code=404
        )
    
    async def _handle_500_exception(self, exc: Exception) -> Response:
        return JSONResponse(
            {"error": "Internal Server Error"},
            status_code=500
        )
    
    def get_stats(self) -> Dict:
        """Get performance statistics"""
        if not self.request_times:
            return {}
        
        return {
            "total_requests": len(self.request_times),
            "avg_response_time": sum(self.request_times) / len(self.request_times),
            "min_response_time": min(self.request_times),
            "max_response_time": max(self.request_times),
            "p95_response_time": sorted(self.request_times)[int(len(self.request_times) * 0.95)]
        }
    
    def run(self, host: str = "127.0.0.1", port: int = 8000, **kwargs):
        """Run development server"""
        try:
            import uvicorn
            uvicorn.run(self, host=host, port=port, **kwargs)
        except ImportError:
            raise RuntimeError("Uvicorn required: pip install uvicorn")