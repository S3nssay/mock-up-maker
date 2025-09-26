import time
import functools
import asyncio
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime, timedelta


def retry_on_failure(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Decorator for retrying function calls on failure"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = delay * (backoff_factor ** attempt)
                        time.sleep(wait_time)

            raise last_exception

        return wrapper
    return decorator


def async_retry_on_failure(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Async version of retry decorator"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = delay * (backoff_factor ** attempt)
                        await asyncio.sleep(wait_time)

            raise last_exception

        return wrapper
    return decorator


def timing_decorator(func):
    """Decorator to measure function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        execution_time = end_time - start_time
        print(f"{func.__name__} took {execution_time:.4f} seconds")
        return result

    return wrapper


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        return f"{hours}h {remaining_minutes}m"


def format_file_size(bytes_size: int) -> str:
    """Format file size in bytes to human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency"""
    if currency == "USD":
        return f"${amount:.2f}"
    elif currency == "EUR":
        return f"€{amount:.2f}"
    elif currency == "GBP":
        return f"£{amount:.2f}"
    else:
        return f"{amount:.2f} {currency}"


def calculate_percentage(part: Union[int, float], total: Union[int, float]) -> float:
    """Calculate percentage safely"""
    if total == 0:
        return 0.0
    return (part / total) * 100


def batch_items(items: List[Any], batch_size: int) -> List[List[Any]]:
    """Split list into batches of specified size"""
    batches = []
    for i in range(0, len(items), batch_size):
        batches.append(items[i:i + batch_size])
    return batches


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def validate_url(url: str) -> bool:
    """Validate URL format"""
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def validate_hex_color(color: str) -> bool:
    """Validate hex color format"""
    import re
    hex_color_pattern = re.compile(r'^#(?:[0-9a-fA-F]{3}){1,2}$')
    return hex_color_pattern.match(color) is not None


def generate_timestamp(format_str: str = "%Y%m%d_%H%M%S") -> str:
    """Generate timestamp string"""
    return datetime.now().strftime(format_str)


def parse_timestamp(timestamp_str: str, format_str: str = "%Y%m%d_%H%M%S") -> datetime:
    """Parse timestamp string to datetime"""
    return datetime.strptime(timestamp_str, format_str)


def get_eta(processed: int, total: int, start_time: float) -> Optional[datetime]:
    """Calculate estimated time of arrival"""
    if processed == 0 or total == 0:
        return None

    elapsed_time = time.time() - start_time
    rate = processed / elapsed_time
    remaining_items = total - processed

    if rate > 0:
        remaining_seconds = remaining_items / rate
        return datetime.now() + timedelta(seconds=remaining_seconds)

    return None


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to maximum length with optional suffix"""
    if len(text) <= max_length:
        return text

    truncate_length = max_length - len(suffix)
    return text[:truncate_length] + suffix


def safe_cast(value: Any, target_type: type, default: Any = None) -> Any:
    """Safely cast value to target type with default fallback"""
    try:
        return target_type(value)
    except (ValueError, TypeError):
        return default


def extract_numbers(text: str) -> List[float]:
    """Extract all numbers from text string"""
    import re
    numbers = re.findall(r'-?\d+\.?\d*', text)
    return [float(num) for num in numbers]


def sanitize_for_json(obj: Any) -> Any:
    """Sanitize object for JSON serialization"""
    if hasattr(obj, 'dict'):
        return obj.dict()
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: sanitize_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, (datetime,)):
        return obj.isoformat()
    else:
        return obj


class RateLimiter:
    """Simple rate limiter for API calls"""

    def __init__(self, max_calls: int, time_window: float = 60.0):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []

    def can_proceed(self) -> bool:
        """Check if call can proceed under rate limit"""
        now = time.time()

        # Remove old calls outside time window
        self.calls = [call_time for call_time in self.calls
                     if now - call_time < self.time_window]

        return len(self.calls) < self.max_calls

    def record_call(self) -> None:
        """Record a call for rate limiting"""
        self.calls.append(time.time())

    def wait_time(self) -> float:
        """Get wait time until next call is allowed"""
        if self.can_proceed():
            return 0.0

        oldest_call = min(self.calls)
        return self.time_window - (time.time() - oldest_call)


class CircuitBreaker:
    """Circuit breaker pattern implementation"""

    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    def call(self, func: Callable, *args, **kwargs):
        """Call function with circuit breaker protection"""
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = "closed"

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"