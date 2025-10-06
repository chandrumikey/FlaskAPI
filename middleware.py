import gzip
import time
from typing import Optional
from .request import Request
from .response import Response

class Middleware:
    async def before_request(self, request: Request) -> Optional[Request]:
        return request
    
    async def after_request(self, request: Request, response: Response) -> Optional[Response]:
        return response

class CORSMiddleware(Middleware):
    def __init__(self, allow_origins: list = None, allow_methods: list = None, allow_headers: list = None):
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "PATCH"]
        self.allow_headers = allow_headers or ["Content-Type", "Authorization"]
    
    async def after_request(self, request: Request, response: Response) -> Response:
        origin = request.get_header("origin")
        
        if origin and (origin in self.allow_origins or "*" in self.allow_origins):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
            response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response

class CompressionMiddleware(Middleware):
    def __init__(self, min_size: int = 500):
        self.min_size = min_size
    
    async def after_request(self, request: Request, response: Response) -> Response:
        accept_encoding = request.get_header('accept-encoding', '')
        
        if 'gzip' in accept_encoding and self._should_compress(response):
            response = await self._compress_response(response)
        
        return response
    
    def _should_compress(self, response: Response) -> bool:
        content_type = response.headers.get('content-type', '')
        compressible_types = ['text/', 'application/json', 'application/javascript']
        return any(ct in content_type for ct in compressible_types)
    
    async def _compress_response(self, response: Response) -> Response:
        content = response._encode_content()
        if len(content) < self.min_size:
            return response
        
        compressed = gzip.compress(content)
        response.content = compressed
        response.headers['content-encoding'] = 'gzip'
        response.headers['content-length'] = str(len(compressed))
        return response

class TimingMiddleware(Middleware):
    async def before_request(self, request: Request) -> Request:
        request.start_time = time.perf_counter()
        return request
    
    async def after_request(self, request: Request, response: Response) -> Response:
        if hasattr(request, 'start_time'):
            duration = (time.perf_counter() - request.start_time) * 1000
            response.headers['x-response-time'] = f"{duration:.2f}ms"
        return response