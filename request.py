import json
from typing import Dict, Any, Optional, List
from urllib.parse import parse_qs

class Request:
    def __init__(self, scope: Dict, receive: Callable):
        self.scope = scope
        self.receive = receive
        self._body: Optional[bytes] = None
        self._json: Optional[Dict] = None
        self._form: Optional[Dict] = None
        self.path_params: Dict[str, Any] = {}
    
    @property
    def method(self) -> str:
        return self.scope["method"]
    
    @property
    def path(self) -> str:
        return self.scope["path"]
    
    @property
    def headers(self) -> Dict[str, str]:
        return {
            key.decode().lower(): value.decode() 
            for key, value in self.scope["headers"]
        }
    
    @property
    def query_params(self) -> Dict[str, List[str]]:
        query_string = self.scope.get("query_string", b"").decode()
        return parse_qs(query_string)
    
    @property
    def client(self) -> str:
        client = self.scope.get("client", ["unknown"])[0]
        return client
    
    async def body(self) -> bytes:
        """Get request body with efficient streaming"""
        if self._body is None:
            self._body = b""
            more_body = True
            while more_body:
                message = await self.receive()
                self._body += message.get("body", b"")
                more_body = message.get("more_body", False)
        return self._body
    
    async def json(self) -> Optional[Dict[str, Any]]:
        """Parse JSON body with error handling"""
        if self._json is None:
            body = await self.body()
            if body:
                try:
                    self._json = json.loads(body)
                except json.JSONDecodeError:
                    self._json = {}
        return self._json
    
    async def form(self) -> Dict[str, str]:
        """Parse form data"""
        if self._form is None:
            content_type = self.get_header('content-type', '')
            if 'application/x-www-form-urlencoded' in content_type:
                body = await self.body()
                self._form = parse_qs(body.decode())
            else:
                self._form = {}
        return self._form
    
    def get_header(self, name: str, default: Any = None) -> Optional[str]:
        """Get specific header with case-insensitive lookup"""
        return self.headers.get(name.lower(), default)
    
    def get_query_param(self, name: str, default: Any = None) -> Any:
        """Get single query parameter"""
        params = self.query_params.get(name, [])
        return params[0] if params else default
    
    def get_path_param(self, name: str, default: Any = None) -> Any:
        """Get path parameter"""
        return self.path_params.get(name, default)