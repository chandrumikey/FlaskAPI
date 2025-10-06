import re
from typing import Any, Dict, get_type_hints
from functools import wraps
from .exceptions import ValidationError

class Validator:
    @staticmethod
    def validate_email(value: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, value))
    
    @staticmethod
    def validate_phone(value: str) -> bool:
        pattern = r'^\+?1?\d{9,15}$'
        return bool(re.match(pattern, value))
    
    @staticmethod
    def validate_length(value: str, min_len: int = 0, max_len: int = None) -> bool:
        if max_len:
            return min_len <= len(value) <= max_len
        return len(value) >= min_len

def validate(**validators):
    """Decorator for request validation"""
    def decorator(handler):
        @wraps(handler)
        async def wrapper(request, *args, **kwargs):
            data = await request.json() or {}
            errors = {}
            
            for field, rules in validators.items():
                value = data.get(field)
                
                for rule in rules if isinstance(rules, list) else [rules]:
                    if rule == 'required' and (value is None or value == ''):
                        errors[field] = f"{field} is required"
                    elif rule == 'email' and value and not Validator.validate_email(value):
                        errors[field] = f"{field} must be a valid email"
                    elif rule == 'phone' and value and not Validator.validate_phone(value):
                        errors[field] = f"{field} must be a valid phone number"
                    elif isinstance(rule, dict):
                        if 'min_length' in rule and value and len(value) < rule['min_length']:
                            errors[field] = f"{field} must be at least {rule['min_length']} characters"
                        if 'max_length' in rule and value and len(value) > rule['max_length']:
                            errors[field] = f"{field} must be at most {rule['max_length']} characters"
            
            if errors:
                raise ValidationError({"errors": errors})
            
            return await handler(request, *args, **kwargs)
        return wrapper
    return decorator