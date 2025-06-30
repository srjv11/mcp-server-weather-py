"""
Example: State Machine approach for HTTP requests
This shows how we COULD refactor make_request using a state machine pattern
"""

import asyncio
from dataclasses import dataclass
from enum import Enum

import httpx


class RequestState(Enum):
    """States for the HTTP request state machine"""

    INITIAL = "initial"
    CHECK_CACHE = "check_cache"
    RATE_LIMIT_CHECK = "rate_limit_check"
    MAKE_REQUEST = "make_request"
    HANDLE_RESPONSE = "handle_response"
    CACHE_RESPONSE = "cache_response"
    RETRY_DELAY = "retry_delay"
    SUCCESS = "success"
    ERROR = "error"


class RequestEvent(Enum):
    """Events that trigger state transitions"""

    START = "start"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    RATE_LIMIT_OK = "rate_limit_ok"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    REQUEST_SUCCESS = "request_success"
    REQUEST_TIMEOUT = "request_timeout"
    REQUEST_SERVER_ERROR = "request_server_error"
    REQUEST_CLIENT_ERROR = "request_client_error"
    REQUEST_UNEXPECTED_ERROR = "request_unexpected_error"
    RETRY_NEEDED = "retry_needed"
    MAX_RETRIES_REACHED = "max_retries_reached"
    RETRY_DELAY_COMPLETE = "retry_delay_complete"


@dataclass
class RequestContext:
    """Context object that holds state data"""

    url: str
    cache_key: str | None = None
    attempt: int = 0
    max_retries: int = 3
    response_data: dict | None = None
    last_exception: Exception | None = None
    cached_data: dict | None = None


class HTTPRequestStateMachine:
    """State machine for handling HTTP requests with retries and caching"""

    def __init__(self):
        self.state = RequestState.INITIAL
        self.context = None

        # Define state transitions
        self.transitions = {
            (RequestState.INITIAL, RequestEvent.START): RequestState.CHECK_CACHE,
            (RequestState.CHECK_CACHE, RequestEvent.CACHE_HIT): RequestState.SUCCESS,
            (
                RequestState.CHECK_CACHE,
                RequestEvent.CACHE_MISS,
            ): RequestState.RATE_LIMIT_CHECK,
            (
                RequestState.RATE_LIMIT_CHECK,
                RequestEvent.RATE_LIMIT_OK,
            ): RequestState.MAKE_REQUEST,
            (
                RequestState.RATE_LIMIT_CHECK,
                RequestEvent.RATE_LIMIT_EXCEEDED,
            ): RequestState.ERROR,
            (
                RequestState.MAKE_REQUEST,
                RequestEvent.REQUEST_SUCCESS,
            ): RequestState.HANDLE_RESPONSE,
            (
                RequestState.MAKE_REQUEST,
                RequestEvent.REQUEST_TIMEOUT,
            ): RequestState.RETRY_DELAY,
            (
                RequestState.MAKE_REQUEST,
                RequestEvent.REQUEST_SERVER_ERROR,
            ): RequestState.RETRY_DELAY,
            (
                RequestState.MAKE_REQUEST,
                RequestEvent.REQUEST_CLIENT_ERROR,
            ): RequestState.ERROR,
            (
                RequestState.HANDLE_RESPONSE,
                RequestEvent.REQUEST_SUCCESS,
            ): RequestState.CACHE_RESPONSE,
            (
                RequestState.CACHE_RESPONSE,
                RequestEvent.REQUEST_SUCCESS,
            ): RequestState.SUCCESS,
            (
                RequestState.RETRY_DELAY,
                RequestEvent.RETRY_DELAY_COMPLETE,
            ): RequestState.MAKE_REQUEST,
            (
                RequestState.RETRY_DELAY,
                RequestEvent.MAX_RETRIES_REACHED,
            ): RequestState.ERROR,
        }

    async def transition(self, event: RequestEvent) -> bool:
        """Execute a state transition"""
        current_state = self.state
        new_state = self.transitions.get((current_state, event))

        if new_state is None:
            print(f"Invalid transition: {current_state} + {event}")
            return False

        print(f"Transition: {current_state} --{event}--> {new_state}")
        self.state = new_state

        # Execute state-specific logic
        await self._execute_state_logic()
        return True

    async def _execute_state_logic(self):
        """Execute logic for the current state"""
        if self.state == RequestState.CHECK_CACHE:
            await self._check_cache()
        elif self.state == RequestState.RATE_LIMIT_CHECK:
            await self._check_rate_limit()
        elif self.state == RequestState.MAKE_REQUEST:
            await self._make_request()
        elif self.state == RequestState.HANDLE_RESPONSE:
            await self._handle_response()
        elif self.state == RequestState.CACHE_RESPONSE:
            await self._cache_response()
        elif self.state == RequestState.RETRY_DELAY:
            await self._retry_delay()
        elif self.state == RequestState.SUCCESS:
            print("✅ Request successful!")
        elif self.state == RequestState.ERROR:
            print("❌ Request failed!")

    async def _check_cache(self):
        """Check if cached data exists"""
        if self.context.cache_key and self.context.cached_data:
            await self.transition(RequestEvent.CACHE_HIT)
        else:
            await self.transition(RequestEvent.CACHE_MISS)

    async def _check_rate_limit(self):
        """Check rate limiting"""
        # Simplified rate limit check
        await self.transition(RequestEvent.RATE_LIMIT_OK)

    async def _make_request(self):
        """Make the actual HTTP request"""
        try:
            # Simplified HTTP request
            async with httpx.AsyncClient() as client:
                response = await client.get(self.context.url)

                if response.status_code == 200:
                    self.context.response_data = response.json()
                    await self.transition(RequestEvent.REQUEST_SUCCESS)
                elif response.status_code >= 500:
                    await self.transition(RequestEvent.REQUEST_SERVER_ERROR)
                else:
                    await self.transition(RequestEvent.REQUEST_CLIENT_ERROR)

        except httpx.TimeoutException:
            await self.transition(RequestEvent.REQUEST_TIMEOUT)
        except Exception as e:
            self.context.last_exception = e
            await self.transition(RequestEvent.REQUEST_UNEXPECTED_ERROR)

    async def _handle_response(self):
        """Handle successful response"""
        await self.transition(RequestEvent.REQUEST_SUCCESS)

    async def _cache_response(self):
        """Cache the response"""
        if self.context.cache_key:
            # Cache the response data
            pass
        await self.transition(RequestEvent.REQUEST_SUCCESS)

    async def _retry_delay(self):
        """Handle retry delay logic"""
        self.context.attempt += 1

        if self.context.attempt >= self.context.max_retries:
            await self.transition(RequestEvent.MAX_RETRIES_REACHED)
        else:
            # Exponential backoff
            delay = 1.0 * (2**self.context.attempt)
            print(f"Retrying in {delay} seconds...")
            await asyncio.sleep(delay)
            await self.transition(RequestEvent.RETRY_DELAY_COMPLETE)

    async def execute_request(self, url: str, cache_key: str = None) -> dict:
        """Main entry point for executing a request"""
        self.context = RequestContext(url=url, cache_key=cache_key)
        self.state = RequestState.INITIAL

        await self.transition(RequestEvent.START)

        # Continue until we reach a terminal state
        while self.state not in [RequestState.SUCCESS, RequestState.ERROR]:
            await asyncio.sleep(0.1)  # Prevent tight loop

        if self.state == RequestState.SUCCESS:
            return self.context.response_data
        else:
            raise Exception(f"Request failed: {self.context.last_exception}")


# Example usage:
async def example_usage():
    """Example of how to use the state machine"""
    state_machine = HTTPRequestStateMachine()

    try:
        result = await state_machine.execute_request(
            url="https://api.weather.gov/alerts/active", cache_key="alerts_active"
        )
        print(f"Success: {result}")
    except Exception as e:
        print(f"Failed: {e}")


if __name__ == "__main__":
    asyncio.run(example_usage())
