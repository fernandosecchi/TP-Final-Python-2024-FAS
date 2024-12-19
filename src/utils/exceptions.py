class TickerBaseException(Exception):
    """Base exception class for ticker-related errors"""
    pass

class DatabaseError(TickerBaseException):
    """Raised when there's an error with database operations"""
    pass

class DatabaseConnectionError(DatabaseError):
    """Raised when unable to connect to the database"""
    pass

class DatabaseAccessError(DatabaseError):
    """Raised when there's an error accessing the database file"""
    pass

class InvalidDataError(TickerBaseException):
    """Raised when data is invalid or corrupted"""
    pass

class APIError(TickerBaseException):
    """Raised when there's an error with API operations"""
    pass

class APIRateLimitError(APIError):
    """Raised when API rate limit is exceeded"""
    pass

class APIConnectionError(APIError):
    """Raised when unable to connect to the API"""
    pass

class DataValidationError(TickerBaseException):
    """Raised when data validation fails"""
    pass
