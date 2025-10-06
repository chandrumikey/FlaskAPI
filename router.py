import re
import inspect
from typing import Dict, List, Tuple, Callable, Optional, Any
from dataclasses import dataclass

@dataclass
class RouteConfig:
    cache_ttl: int = 0
    rate_limit: int = 0
    background_tasks: List[str] = None
    validate: bool = True

class Route:
    def __init__(self, path: str, methods: List[str], handler: Callable, config: RouteConfig = None):
        self.path = path
        self.methods = methods
        self.handler = handler
        self.config = config or RouteConfig()
        self.pattern, self.param_types = self._compile_pattern(path)
    
    def _compile_pattern(self, path: str) -> Tuple[re.Pattern, Dict[str, type]]:
        """Compile route pattern with type support"""
        # Extract type hints from path parameters
        type_pattern = re.compile(r'\{(\w+):(\w+)\}')
        basic_pattern = re.compile(r'\{(\w+)\}')
        
        param_types = {}
        path_regex = path
        
        # Handle typed parameters: {id:int}, {name:str}, {price:float}
        for match in type_pattern.finditer(path):
            param_name, param_type = match.groups()
            type_map = {'int': r'\d+', 'str': r'[^/]+', 'float': r'\d+\.?\d*', 'uuid': r'[0-9a-f-]+'}
            param_types[param_name] = param_type
            path_regex = path_regex.replace(
                f'{{{param_name}:{param_type}}}', 
                f'(?P<{param_name}>{type_map.get(param_type, r"[^/]+")})'
            )
        
        # Handle untyped parameters
        for match in basic_pattern.finditer(path_regex):
            param_name = match.group(1)
            path_regex = path_regex.replace(f'{{{param_name}}}', f'(?P<{param_name}>[^/]+)')
        
        return re.compile(f"^{path_regex}$"), param_types
    
    def match(self, path: str, method: str) -> Optional[Dict[str, Any]]:
        """Match route and convert parameters to proper types"""
        if method not in self.methods:
            return None
        
        match = self.pattern.match(path)
        if not match:
            return None
        
        params = match.groupdict()
        # Convert parameter types
        for param_name, value in params.items():
            if param_name in self.param_types:
                param_type = self.param_types[param_name]
                try:
                    if param_type == 'int':
                        params[param_name] = int(value)
                    elif param_type == 'float':
                        params[param_name] = float(value)
                    elif param_type == 'bool':
                        params[param_name] = value.lower() in ('true', '1', 'yes')
                except (ValueError, TypeError):
                    # If conversion fails, keep as string
                    pass
        
        return params

class Router:
    def __init__(self):
        self.routes: List[Route] = []
        self._route_cache: Dict[Tuple[str, str], Tuple[Callable, Dict, RouteConfig]] = {}
    
    def add_route(self, path: str, methods: List[str], handler: Callable, **kwargs):
        """Add route with configuration"""
        config = RouteConfig(**kwargs)
        route = Route(path, methods, handler, config)
        self.routes.append(route)
        # Clear cache when adding new routes
        self._route_cache.clear()
    
    def find_route(self, path: str, method: str) -> Optional[Tuple[Callable, Dict, RouteConfig]]:
        """Find route with caching for performance"""
        cache_key = (path, method)
        
        if cache_key in self._route_cache:
            return self._route_cache[cache_key]
        
        for route in self.routes:
            params = route.match(path, method)
            if params is not None:
                result = (route.handler, params, route.config)
                self._route_cache[cache_key] = result
                return result
        
        return None