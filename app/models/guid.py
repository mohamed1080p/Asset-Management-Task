from sqlalchemy.types import TypeDecorator
from sqlalchemy import String
import uuid

class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses String impl, but binds and returns UUID objects.
    """
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            try:
                return uuid.UUID(value)
            except ValueError:
                return value
        return value
