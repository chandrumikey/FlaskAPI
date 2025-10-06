import json
import time
from typing import Any, Dict, Optional, AsyncGenerator
from datetime import datetime

class Response:
    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: str = "text/plain"
    ):
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}
        self.media_type = media_type
        self.timestamp = datetime.utcnow()
    
    async def __call__(self, scope, receive, send):
        """ASGI response implementation"""
        body = self._encode_content()
        
        headers = [
            (b"content-type", self.media_type.encode()),
            (b"content-length", str(len(body)).encode()),
        ]
        
        # Add custom headers
        for key, value in self.headers.items():
            headers.append((key.lower().encode(), value.encode()))
        
        # Add performance headers
        headers.append((b"x-response-time", str(int(time.time() * 1000)).encode()))
        
        await send({
            "type": "http.response.start",
            "status": self.status_code,
            "headers": headers,
        })
        
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    def _encode_content(self) -> bytes:
        """Encode content to bytes"""
        if isinstance(self.content, bytes):
            return self.content
        elif isinstance(self.content, str):
            return self.content.encode('utf-8')
        else:
            return str(self.content).encode('utf-8')

class JSONResponse(Response):
    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        **json_kwargs
    ):
        super().__init__(content, status_code, headers, "application/json")
        self.json_kwargs = json_kwargs
    
    def _encode_content(self) -> bytes:
        return json.dumps(self.content, **self.json_kwargs).encode('utf-8')

class HTMLResponse(Response):
    def __init__(
        self,
        content: str,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(content, status_code, headers, "text/html; charset=utf-8")

class TextResponse(Response):
    def __init__(
        self,
        content: str,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(content, status_code, headers, "text/plain; charset=utf-8")

class StreamResponse(Response):
    def __init__(
        self,
        generator: AsyncGenerator,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: str = "text/plain"
    ):
        super().__init__(None, status_code, headers, media_type)
        self.generator = generator
    
    async def __call__(self, scope, receive, send):
        """Streaming response implementation"""
        headers = [
            (b"content-type", self.media_type.encode()),
            (b"transfer-encoding", b"chunked"),
        ]
        
        for key, value in self.headers.items():
            headers.append((key.lower().encode(), value.encode()))
        
        await send({
            "type": "http.response.start",
            "status": self.status_code,
            "headers": headers,
        })
        
        async for chunk in self.generator:
            if isinstance(chunk, str):
                chunk = chunk.encode('utf-8')
            await send({
                "type": "http.response.body",
                "body": chunk,
                "more_body": True,
            })
        
        await send({
            "type": "http.response.body",
            "body": b"",
            "more_body": False,
        })