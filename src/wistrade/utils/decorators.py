"""
Decorators for error handling and retries
"""

import asyncio
import functools
import logging
import time
from typing import Callable, Optional, Type

logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    on_failure: Optional[Callable] = None,
):
    """
    Retry decorator for synchronous functions
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each attempt
        exceptions: Tuple of exception types to retry on
        on_failure: Callback function on final failure
    
    Example:
        @retry(max_attempts=3, delay=1.0, exceptions=(ConnectionError,))
        def fetch_data():
            # May raise ConnectionError
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}: {e}"
                        )
                        
                        if on_failure:
                            on_failure(e, *args, **kwargs)
                        
                        raise
            
            # This should never be reached, but satisfies type checker
            raise last_exception
        
        return wrapper
    
    return decorator


def async_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    on_failure: Optional[Callable] = None,
):
    """
    Async retry decorator
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each attempt
        exceptions: Tuple of exception types to retry on
        on_failure: Async callback function on final failure
    
    Example:
        @async_retry(max_attempts=3, delay=1.0)
        async def fetch_data():
            # Async operation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}: {e}"
                        )
                        
                        if on_failure:
                            await on_failure(e, *args, **kwargs)
                        
                        raise
            
            # This should never be reached, but satisfies type checker
            raise last_exception
        
        return wrapper
    
    return decorator


def log_execution_time(func: Callable) -> Callable:
    """
    Decorator to log function execution time
    
    Example:
        @log_execution_time
        def slow_function():
            time.sleep(2)
            # Logs: "slow_function executed in 2.00s"
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        logger.debug(
            f"{func.__name__} executed in {execution_time:.2f}s"
        )
        
        return result
    
    return wrapper


def async_log_execution_time(func: Callable) -> Callable:
    """Async version of log_execution_time"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        logger.debug(
            f"{func.__name__} executed in {execution_time:.2f}s"
        )
        
        return result
    
    return wrapper
