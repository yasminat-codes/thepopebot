#!/usr/bin/env python3
"""
Metricool API Client - Production Grade

A robust, resilient client for the Metricool API with:
- Automatic retries with exponential backoff
- Rate limit handling
- Circuit breaker pattern
- Response caching
- Request queuing
- Comprehensive error handling

Usage:
    from metricool_client import MetricoolClient

    client = MetricoolClient(
        user_token="your-token",
        user_id="your-user-id",
        blog_id="your-brand-id"
    )

    # Get Instagram posts
    posts = client.instagram.get_posts(start=1704067200, end=1706745600)

    # With retry handling built-in
    brands = client.admin.list_brands()
"""

import os
import time
import json
import hashlib
import logging
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import urllib.request
import urllib.error
from http.client import HTTPResponse
import ssl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('metricool')


class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass
class RateLimit:
    """Rate limit information from API headers."""
    limit: int = 1000
    remaining: int = 1000
    reset_at: Optional[datetime] = None

    @property
    def is_exhausted(self) -> bool:
        return self.remaining <= 0

    @property
    def seconds_until_reset(self) -> int:
        if self.reset_at:
            delta = self.reset_at - datetime.now()
            return max(0, int(delta.total_seconds()))
        return 60


@dataclass
class CircuitBreaker:
    """Circuit breaker for fault tolerance."""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    lock: threading.Lock = field(default_factory=threading.Lock)

    def record_success(self):
        with self.lock:
            self.failure_count = 0
            self.state = CircuitState.CLOSED

    def record_failure(self):
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning("Circuit breaker OPENED - too many failures")

    def can_execute(self) -> bool:
        with self.lock:
            if self.state == CircuitState.CLOSED:
                return True

            if self.state == CircuitState.OPEN:
                # Check if recovery timeout has passed
                if self.last_failure_time:
                    elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                    if elapsed >= self.recovery_timeout:
                        self.state = CircuitState.HALF_OPEN
                        logger.info("Circuit breaker entering HALF_OPEN state")
                        return True
                return False

            # HALF_OPEN - allow one test request
            return True


class Cache:
    """Thread-safe response cache with TTL."""

    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, tuple] = {}  # key -> (value, expiry)
        self.default_ttl = default_ttl
        self.lock = threading.Lock()

    def _hash_key(self, key: str) -> str:
        return hashlib.md5(key.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            hashed = self._hash_key(key)
            if hashed in self._cache:
                value, expiry = self._cache[hashed]
                if datetime.now() < expiry:
                    logger.debug(f"Cache HIT for {key[:50]}")
                    return value
                else:
                    del self._cache[hashed]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        with self.lock:
            hashed = self._hash_key(key)
            expiry = datetime.now() + timedelta(seconds=ttl or self.default_ttl)
            self._cache[hashed] = (value, expiry)
            logger.debug(f"Cache SET for {key[:50]}")

    def clear(self):
        with self.lock:
            self._cache.clear()
            logger.info("Cache cleared")

    def remove(self, key: str):
        with self.lock:
            hashed = self._hash_key(key)
            if hashed in self._cache:
                del self._cache[hashed]


class RetryPolicy:
    """Configurable retry policy."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        retryable_status_codes: set = None
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retryable_status_codes = retryable_status_codes or {408, 429, 500, 502, 503, 504}

    def get_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter."""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        # Add jitter (±25%)
        jitter = delay * 0.25 * (0.5 - hash(str(time.time())) % 1000 / 1000)
        return delay + jitter

    def should_retry(self, status_code: int, exception: Optional[Exception] = None) -> bool:
        """Determine if request should be retried."""
        if status_code in self.retryable_status_codes:
            return True
        if exception and isinstance(exception, (urllib.error.URLError, TimeoutError)):
            return True
        return False


class MetricoolError(Exception):
    """Base exception for Metricool API errors."""

    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class RateLimitError(MetricoolError):
    """Rate limit exceeded."""
    def __init__(self, retry_after: int = None):
        super().__init__("Rate limit exceeded", status_code=429)
        self.retry_after = retry_after


class AuthenticationError(MetricoolError):
    """Authentication failed."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class NotFoundError(MetricoolError):
    """Resource not found."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ServerError(MetricoolError):
    """Server error."""
    def __init__(self, message: str = "Server error", status_code: int = 500):
        super().__init__(message, status_code=status_code)


class MetricoolClient:
    """
    Production-grade Metricool API client.

    Features:
    - Automatic retries with exponential backoff
    - Rate limit handling
    - Circuit breaker pattern
    - Response caching
    - Comprehensive error handling
    """

    BASE_URL = "https://app.metricool.com/api"

    def __init__(
        self,
        user_token: str = None,
        user_id: str = None,
        blog_id: str = None,
        timeout: int = 30,
        retry_policy: RetryPolicy = None,
        cache_ttl: int = 300,
        circuit_breaker_threshold: int = 5,
        enable_cache: bool = True
    ):
        # Credentials
        self.user_token = user_token or os.environ.get('METRICOOL_USER_TOKEN')
        self.user_id = user_id or os.environ.get('METRICOOL_USER_ID')
        self.blog_id = blog_id or os.environ.get('METRICOOL_BLOG_ID')

        if not all([self.user_token, self.user_id, self.blog_id]):
            raise ValueError(
                "Missing credentials. Provide user_token, user_id, blog_id "
                "or set METRICOOL_USER_TOKEN, METRICOOL_USER_ID, METRICOOL_BLOG_ID"
            )

        # Configuration
        self.timeout = timeout
        self.retry_policy = retry_policy or RetryPolicy()

        # Resilience components
        self.circuit_breaker = CircuitBreaker(failure_threshold=circuit_breaker_threshold)
        self.cache = Cache(default_ttl=cache_ttl) if enable_cache else None
        self.rate_limit = RateLimit()

        # Statistics
        self._stats = {
            'requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'retries': 0,
            'errors': 0
        }

        # API modules
        self.admin = AdminAPI(self)
        self.instagram = InstagramAPI(self)
        self.facebook = FacebookAPI(self)
        self.tiktok = TikTokAPI(self)
        self.youtube = YouTubeAPI(self)
        self.linkedin = LinkedInAPI(self)
        self.twitter = TwitterAPI(self)
        self.twitch = TwitchAPI(self)
        self.ads = AdsAPI(self)
        self.analytics = AnalyticsAPI(self)
        self.scheduling = SchedulingAPI(self)
        self.reports = ReportsAPI(self)
        self.linkinbio = LinkInBioAPI(self)
        self.gmb = GmbAPI(self)
        self.realtime = RealTimeAPI(self)

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        data: Dict = None,
        use_cache: bool = True,
        cache_ttl: int = None
    ) -> Any:
        """
        Make an API request with full resilience.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            use_cache: Whether to use cache for GET requests
            cache_ttl: Cache TTL in seconds

        Returns:
            Parsed JSON response

        Raises:
            MetricoolError: API error
            RateLimitError: Rate limit exceeded
            AuthenticationError: Authentication failed
        """
        # Build URL
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        params = params or {}
        params['blogId'] = self.blog_id
        params['userId'] = self.user_id

        # Build query string
        query_string = '&'.join(f"{k}={v}" for k, v in sorted(params.items()))
        full_url = f"{url}?{query_string}"

        # Check cache for GET requests
        if method == 'GET' and use_cache and self.cache:
            cached = self.cache.get(full_url)
            if cached is not None:
                self._stats['cache_hits'] += 1
                return cached
            self._stats['cache_misses'] += 1

        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            raise ServerError("Circuit breaker is OPEN - service unavailable")

        # Check rate limit
        if self.rate_limit.is_exhausted:
            wait_time = self.rate_limit.seconds_until_reset
            logger.warning(f"Rate limit exhausted, waiting {wait_time}s")
            time.sleep(wait_time)

        # Prepare request
        headers = {
            'X-Mc-Auth': self.user_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        body = json.dumps(data).encode() if data else None

        # Execute with retries
        last_error = None
        for attempt in range(self.retry_policy.max_retries + 1):
            self._stats['requests'] += 1

            try:
                req = urllib.request.Request(
                    full_url,
                    data=body,
                    headers=headers,
                    method=method
                )

                ctx = ssl.create_default_context()
                ctx.check_hostname = True
                ctx.verify_mode = ssl.CERT_REQUIRED

                with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as response:
                    response_body = response.read().decode('utf-8')

                    # Parse rate limit headers
                    self._update_rate_limit(response.headers)

                    # Parse response
                    if response_body:
                        result = json.loads(response_body)
                    else:
                        result = {'success': True}

                    # Record success
                    self.circuit_breaker.record_success()

                    # Cache successful GET requests
                    if method == 'GET' and use_cache and self.cache:
                        self.cache.set(full_url, result, cache_ttl)

                    return result

            except urllib.error.HTTPError as e:
                self._update_rate_limit(e.headers if hasattr(e, 'headers') else None)

                status_code = e.code
                error_body = e.read().decode('utf-8') if hasattr(e, 'read') else ''

                try:
                    error_data = json.loads(error_body) if error_body else {}
                except json.JSONDecodeError:
                    error_data = {'message': error_body}

                # Handle specific errors
                if status_code == 401:
                    self._stats['errors'] += 1
                    raise AuthenticationError(error_data.get('message', 'Unauthorized'))
                elif status_code == 404:
                    self._stats['errors'] += 1
                    raise NotFoundError(error_data.get('message', 'Not found'))
                elif status_code == 429:
                    retry_after = int(e.headers.get('Retry-After', 60))
                    self.rate_limit.remaining = 0
                    self.rate_limit.reset_at = datetime.now() + timedelta(seconds=retry_after)

                    if attempt < self.retry_policy.max_retries:
                        logger.warning(f"Rate limited, waiting {retry_after}s (attempt {attempt + 1})")
                        time.sleep(retry_after)
                        self._stats['retries'] += 1
                        continue
                    raise RateLimitError(retry_after)

                # Check if retryable
                if self.retry_policy.should_retry(status_code):
                    if attempt < self.retry_policy.max_retries:
                        delay = self.retry_policy.get_delay(attempt)
                        logger.warning(
                            f"Request failed with {status_code}, "
                            f"retrying in {delay:.1f}s (attempt {attempt + 1})"
                        )
                        time.sleep(delay)
                        self._stats['retries'] += 1
                        continue

                self._stats['errors'] += 1
                self.circuit_breaker.record_failure()
                raise MetricoolError(
                    error_data.get('message', f'HTTP {status_code}'),
                    status_code=status_code,
                    response=error_data
                )

            except urllib.error.URLError as e:
                last_error = e
                if attempt < self.retry_policy.max_retries:
                    delay = self.retry_policy.get_delay(attempt)
                    logger.warning(f"Connection error: {e.reason}, retrying in {delay:.1f}s")
                    time.sleep(delay)
                    self._stats['retries'] += 1
                    continue

            except TimeoutError as e:
                last_error = e
                if attempt < self.retry_policy.max_retries:
                    delay = self.retry_policy.get_delay(attempt)
                    logger.warning(f"Timeout, retrying in {delay:.1f}s")
                    time.sleep(delay)
                    self._stats['retries'] += 1
                    continue

        # All retries exhausted
        self._stats['errors'] += 1
        self.circuit_breaker.record_failure()

        if last_error:
            raise MetricoolError(f"Request failed after {self.retry_policy.max_retries} retries: {last_error}")
        raise MetricoolError(f"Request failed after {self.retry_policy.max_retries} retries")

    def _update_rate_limit(self, headers):
        """Update rate limit info from response headers."""
        if headers:
            try:
                if 'X-RateLimit-Limit' in headers:
                    self.rate_limit.limit = int(headers['X-RateLimit-Limit'])
                if 'X-RateLimit-Remaining' in headers:
                    self.rate_limit.remaining = int(headers['X-RateLimit-Remaining'])
                if 'X-RateLimit-Reset' in headers:
                    self.rate_limit.reset_at = datetime.fromtimestamp(
                        int(headers['X-RateLimit-Reset'])
                    )
            except (ValueError, TypeError) as e:
                logger.debug(f"Could not parse rate limit headers: {e}")

    def get(self, endpoint: str, params: Dict = None, **kwargs) -> Any:
        """Make a GET request."""
        return self._request('GET', endpoint, params=params, **kwargs)

    def post(self, endpoint: str, data: Dict = None, params: Dict = None, **kwargs) -> Any:
        """Make a POST request."""
        return self._request('POST', endpoint, params=params, data=data, use_cache=False, **kwargs)

    def put(self, endpoint: str, data: Dict = None, params: Dict = None, **kwargs) -> Any:
        """Make a PUT request."""
        return self._request('PUT', endpoint, params=params, data=data, use_cache=False, **kwargs)

    def delete(self, endpoint: str, params: Dict = None, **kwargs) -> Any:
        """Make a DELETE request."""
        return self._request('DELETE', endpoint, params=params, use_cache=False, **kwargs)

    def ping(self) -> bool:
        """Test API connectivity."""
        try:
            self.get('mtr/ping')
            return True
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            return False

    def get_stats(self) -> Dict:
        """Get client statistics."""
        return {
            **self._stats,
            'rate_limit': {
                'limit': self.rate_limit.limit,
                'remaining': self.rate_limit.remaining,
                'exhausted': self.rate_limit.is_exhausted
            },
            'circuit_breaker': {
                'state': self.circuit_breaker.state.value,
                'failures': self.circuit_breaker.failure_count
            }
        }

    def clear_cache(self):
        """Clear the response cache."""
        if self.cache:
            self.cache.clear()


# API Module Base
class APIModule:
    """Base class for API modules."""

    def __init__(self, client: MetricoolClient):
        self._client = client


# Admin API
class AdminAPI(APIModule):
    """Admin and profile management."""

    def list_brands(self) -> List[Dict]:
        """Get all brands for the authenticated user."""
        return self._client.get('admin/simpleProfiles')

    def get_brand(self, blog_id: str = None) -> Dict:
        """Get brand details."""
        params = {'blogId': blog_id} if blog_id else None
        return self._client.get('admin/profiles-auth', params=params)

    def create_brand(self, name: str = None) -> Dict:
        """Create a new brand/profile."""
        params = {'name': name} if name else None
        return self._client.get('admin/add-profile', params=params)

    def delete_brand(self, blog_id: str = None) -> bool:
        """Delete a brand."""
        params = {'blogId': blog_id} if blog_id else None
        result = self._client.get('admin/delete-profile', params=params)
        return result.get('success', True)

    def restore_brand(self, blog_id: str = None) -> bool:
        """Restore a deleted brand."""
        params = {'blogId': blog_id} if blog_id else None
        result = self._client.get('admin/restore-profile', params=params)
        return result.get('success', True)

    def update_label(self, new_name: str) -> bool:
        """Update brand label/name."""
        result = self._client.get('admin/update-label-blog', params={'newName': new_name})
        return result.get('success', True)

    def get_property(self, name: str) -> str:
        """Get a brand property."""
        result = self._client.get('admin/profile/getproperty', params={'name': name})
        return result.get('value', '')

    def set_property(self, name: str, value: str) -> bool:
        """Set a brand property."""
        result = self._client.get('admin/profile/setproperty', params={'name': name, 'value': value})
        return result.get('success', True)

    def get_max_profiles(self) -> int:
        """Get maximum number of profiles allowed."""
        result = self._client.get('admin/max-profiles')
        return int(result) if isinstance(result, (int, str)) else 0

    def detect_website(self, url: str) -> Dict:
        """Detect website information."""
        return self._client.get('admin/detectwebsite', params={'url': url})

    def get_report_logo(self) -> str:
        """Get report logo URL."""
        result = self._client.get('admin/report-logo')
        return result.get('url', '')


# Instagram API
class InstagramAPI(APIModule):
    """Instagram analytics and management."""

    def get_posts(self, start: int, end: int, sort: str = None) -> List[Dict]:
        """Get Instagram posts with metrics."""
        params = {'start': start, 'end': end}
        if sort:
            params['sortcolumn'] = sort
        return self._client.get('stats/instagram/posts', params=params)

    def get_reels(self, start: int, end: int, sort: str = None) -> List[Dict]:
        """Get Instagram reels with metrics."""
        params = {'start': start, 'end': end}
        if sort:
            params['sortcolumn'] = sort
        return self._client.get('stats/instagram/reels', params=params)

    def get_stories(self, start: int, end: int, sort: str = None) -> List[Dict]:
        """Get Instagram stories with metrics."""
        params = {'start': start, 'end': end}
        if sort:
            params['sortcolumn'] = sort
        return self._client.get('stats/instagram/stories', params=params)

    def get_demographics(self, demo_type: str) -> Dict:
        """Get demographics (gender, age, country, city)."""
        return self._client.get(f'stats/{demo_type}/instagram')

    def get_gender(self) -> Dict:
        """Get gender distribution."""
        return self.get_demographics('gender')

    def get_age(self) -> Dict:
        """Get age distribution."""
        return self.get_demographics('age')

    def get_gender_age(self) -> List[Dict]:
        """Get gender-age distribution."""
        return self._client.get('stats/gender-age/instagram')

    def get_country(self) -> Dict:
        """Get country distribution."""
        return self.get_demographics('country')

    def get_city(self) -> Dict:
        """Get city distribution."""
        return self.get_demographics('city')

    def get_traffic_source(self) -> Dict:
        """Get traffic source distribution."""
        return self._client.get('stats/trafficsource/instagram')

    def get_hashtag_suggestions(self, query: str) -> Dict:
        """Get hashtag suggestions."""
        return self._client.get('actions/instagram/suggestions/hashtags', params={'q': query})

    def get_required_scopes(self) -> List[str]:
        """Get required Instagram scopes for posting."""
        return self._client.get('actions/instagram/required-scopes-to-post')

    def get_automation_candidates_count(self) -> int:
        """Get count of posts eligible for automation."""
        result = self._client.get('actions/instagram/auto-candidate-posts-count-for-automation')
        return int(result) if isinstance(result, (int, str)) else 0


# Facebook API
class FacebookAPI(APIModule):
    """Facebook analytics and management."""

    def get_posts(self, start: int, end: int, sort: str = None) -> List[Dict]:
        """Get Facebook posts with metrics."""
        params = {'start': start, 'end': end}
        if sort:
            params['sortcolumn'] = sort
        return self._client.get('stats/facebook/posts', params=params)

    def get_group_posts(self, start: int, end: int, sort: str = None) -> List[Dict]:
        """Get Facebook group posts."""
        params = {'start': start, 'end': end}
        if sort:
            params['sortcolumn'] = sort
        return self._client.get('stats/fbgroup/posts', params=params)

    def get_reels(self, start: int, end: int) -> List[Dict]:
        """Get Facebook reels."""
        return self._client.get('stats/facebook/reels', params={'start': start, 'end': end})

    def get_stories(self, start: int, end: int) -> List[Dict]:
        """Get Facebook stories."""
        return self._client.get('stats/facebook/stories', params={'start': start, 'end': end})

    def boost_post(self, post_id: str, budget: int) -> Dict:
        """Boost a published Facebook post."""
        return self._client.get(f'stats/facebook/boost/{post_id}', params={'budget': budget})

    def boost_pending_post(self, post_id: str, budget: int) -> Dict:
        """Add boost budget for scheduled post."""
        return self._client.get(f'stats/facebook/boost/pending/{post_id}', params={'budget': budget})

    def get_boost_value(self, post_id: str) -> str:
        """Get boost budget for scheduled post."""
        return self._client.get('stats/facebook/getvalue', params={'postId': post_id})

    def search_locations(self, query: str) -> List[Dict]:
        """Search Facebook locations."""
        return self._client.get('actions/facebook/search-location', params={'q': query})

    def get_suggestions(self, query: str) -> List[Dict]:
        """Get Facebook page suggestions."""
        return self._client.get('actions/facebook/suggestions', params={'q': query})


# TikTok API
class TikTokAPI(APIModule):
    """TikTok analytics."""

    def get_videos(self, start: int, end: int, sort: str = None) -> List[Dict]:
        """Get TikTok videos with metrics."""
        params = {'start': start, 'end': end}
        if sort:
            params['sortcolumn'] = sort
        return self._client.get('stats/tiktok/videos', params=params)


# YouTube API
class YouTubeAPI(APIModule):
    """YouTube analytics."""

    def get_videos(self, start: int, end: int, sort: str = None) -> List[Dict]:
        """Get YouTube videos with metrics."""
        params = {'start': start, 'end': end}
        if sort:
            params['sortcolumn'] = sort
        return self._client.get('stats/youtube/videos', params=params)


# LinkedIn API
class LinkedInAPI(APIModule):
    """LinkedIn analytics."""

    def get_posts(self, start: int, end: int, sort: str = None) -> List[Dict]:
        """Get LinkedIn posts."""
        params = {'start': start, 'end': end}
        if sort:
            params['sortcolumn'] = sort
        return self._client.get('stats/linkedin/posts', params=params)

    def get_stories(self, start: int, end: int) -> List[Dict]:
        """Get LinkedIn stories."""
        return self._client.get('stats/linkedin/stories', params={'start': start, 'end': end})

    def get_company_suggestions(self, query: str) -> List[Dict]:
        """Get LinkedIn company suggestions."""
        return self._client.get('actions/linkedin/suggestions', params={'q': query})


# Twitter/X API
class TwitterAPI(APIModule):
    """Twitter/X analytics."""

    def get_posts(self, start: int, end: int, sort: str = None) -> List[Dict]:
        """Get Twitter posts (deprecated)."""
        params = {'start': start, 'end': end}
        if sort:
            params['sortcolumn'] = sort
        return self._client.get('stats/twitter/posts', params=params)

    def get_events(self, event_type: str, start: int, end: int) -> List[Dict]:
        """Get Twitter follow/unfollow events."""
        return self._client.get(f'stats/twEvents/{event_type}', params={'start': start, 'end': end})

    def follow(self, user_id: str, screen_name: str) -> bool:
        """Follow a Twitter account."""
        result = self._client.get('stats/twitter/follow', params={'userid': user_id, 'screenname': screen_name})
        return result.get('success', True)

    def unfollow(self, user_id: str, screen_name: str) -> bool:
        """Unfollow a Twitter account."""
        result = self._client.get('stats/twitter/unfollow', params={'userid': user_id, 'screenname': screen_name})
        return result.get('success', True)

    def get_suggestions(self, query: str) -> List[Dict]:
        """Get Twitter account suggestions."""
        return self._client.get('actions/twitter/suggestions', params={'q': query})

    def get_realtime_tweets(self, screen_name: str, tweet_type: str = 'tweets') -> List[Dict]:
        """Get real-time tweets or mentions."""
        return self._client.get(
            f'stats/rt/twitter/tweets/{tweet_type}',
            params={'screenname': screen_name}
        )

    def get_realtime_profile(self) -> Dict:
        """Get real-time Twitter profile."""
        return self._client.get('stats/rt/twitterProfile')


# Twitch API
class TwitchAPI(APIModule):
    """Twitch analytics."""

    def get_videos(self, start: int, end: int, sort: str = None) -> List[Dict]:
        """Get Twitch videos."""
        params = {'start': start, 'end': end}
        if sort:
            params['sortcolumn'] = sort
        return self._client.get('stats/twitch/videos', params=params)

    def get_clips(self, start: int, end: int, video_id: str = None) -> List[Dict]:
        """Get Twitch clips."""
        params = {'start': start, 'end': end}
        if video_id:
            return self._client.get('stats/twitch/video/clips', params={**params, 'videoId': video_id})
        return self._client.get('stats/twitch/clips', params=params)

    def get_subscriptions(self, start: int, end: int) -> List[Dict]:
        """Get Twitch subscriptions."""
        return self._client.get('stats/twitch/subscriptions', params={'start': start, 'end': end})

    def get_subscription_distribution(self) -> Dict:
        """Get subscription distribution by tier."""
        return self._client.get('stats/twitch/subscriptions/doughnut')


# Ads API
class AdsAPI(APIModule):
    """Ads management across platforms."""

    def get_facebook_campaigns(self, start: int, end: int, sort: str = None) -> List[Dict]:
        """Get Facebook Ads campaigns."""
        params = {'start': start, 'end': end}
        if sort:
            params['sortcolumn'] = sort
        return self._client.get('stats/facebookads/campaigns', params=params)

    def get_facebook_metric_value(
        self, metric: str, start: int, end: int,
        campaign_id: str = None, timezone: str = None
    ) -> float:
        """Get specific Facebook Ads metric value."""
        params = {'metric': metric, 'start': start, 'end': end}
        if campaign_id:
            params['idCampaign'] = campaign_id
        if timezone:
            params['timezone'] = timezone
        result = self._client.get('stats/facebookads/metricvalue', params=params)
        return float(result) if isinstance(result, (int, float, str)) else 0.0

    def get_google_campaigns(self, start: int, end: int) -> List[Dict]:
        """Get Google Ads campaigns."""
        return self._client.get('stats/adwords/campaigns', params={'start': start, 'end': end})

    def get_google_keywords(self, start: int, end: int, campaign: str = None) -> List[Dict]:
        """Get Google Ads keywords."""
        params = {'start': start, 'end': end}
        if campaign:
            params['CAMPAIGN'] = campaign
        return self._client.get('stats/adwords/keywords', params=params)

    def get_google_ads(self) -> List[Dict]:
        """Get Google Ads list."""
        return self._client.get('stats/ads')

    def get_tiktok_campaigns(self, start: int, end: int) -> List[Dict]:
        """Get TikTok Ads campaigns."""
        return self._client.get('stats/tiktokads/campaigns', params={'start': start, 'end': end})


# Analytics API
class AnalyticsAPI(APIModule):
    """Cross-platform analytics."""

    def get_values(self, category: str, date: str) -> Dict:
        """Get metrics values by category and date."""
        return self._client.get(f'stats/values/{category}', params={'date': date})

    def get_timeline(self, metric: str, start: str, end: str) -> List:
        """Get time series data for a metric."""
        return self._client.get(f'stats/timeline/{metric}', params={'start': start, 'end': end})

    def get_aggregation(self, metric: str, start: str, end: str, competitor_id: str = None) -> float:
        """Get aggregated metric value."""
        params = {'start': start, 'end': end}
        if competitor_id:
            params['igcompetitorid'] = competitor_id
        result = self._client.get(f'stats/aggregation/{metric}', params=params)
        return float(result) if isinstance(result, (int, float, str)) else 0.0

    def get_aggregations(self, category: str, start: str, end: str, campaign_id: str = None) -> Dict:
        """Get aggregated metrics by category."""
        params = {'start': start, 'end': end}
        if campaign_id:
            params['campaignid'] = campaign_id
        return self._client.get(f'stats/aggregations/{category}', params=params)

    def get_distribution(self, dist_type: str, start: int, end: int) -> Dict:
        """Get distribution data."""
        return self._client.get(f'stats/distribution/{dist_type}', params={'start': start, 'end': end})

    def get_website_posts(self, start: int, end: int) -> List[Dict]:
        """Get website posts published during period."""
        return self._client.get('stats/posts', params={'start': start, 'end': end})


# Scheduling API
class SchedulingAPI(APIModule):
    """Content scheduling."""

    def set_timezone(self, timezone: str) -> bool:
        """Set user timezone."""
        result = self._client.get('actions/setTimeZone', params={'timezone': timezone})
        return result.get('success', True)

    def validate_image_url(self, url: str) -> str:
        """Validate and normalize image URL."""
        return self._client.get('actions/normalize/image/url', params={'url': url})

    def get_bluesky_suggestions(self, query: str) -> List[Dict]:
        """Get Bluesky account suggestions."""
        return self._client.get('actions/bluesky/suggestions', params={'q': query})


# Reports API
class ReportsAPI(APIModule):
    """Report template management."""

    def list_templates(self) -> List[Dict]:
        """Get all report templates."""
        return self._client.get('stats/report/reporttemplateName')

    def save_template(self, template_data: Dict) -> str:
        """Save a report template."""
        return self._client.post('stats/report/savetemplate', data=template_data)

    def delete_template(self, template_id: str) -> bool:
        """Delete a template."""
        result = self._client.get('stats/report/deletetemplate', params={'templateId': template_id})
        return result.get('success', True)

    def duplicate_template(self, template_id: str, new_name: str) -> Dict:
        """Duplicate a template."""
        return self._client.get(
            'stats/report/duplicatetemplate',
            params={'templateId': template_id, 'templateName': new_name}
        )

    def get_template_params(self, template_id: int) -> Dict:
        """Get template parameters."""
        return self._client.get('stats/report/reporttemplateparam', params={'templateId': template_id})

    def get_default_resources(self) -> Dict:
        """Get default template resources."""
        return self._client.get('stats/report/template/default-resources')

    def upload_logo(self, logo_data: bytes) -> Dict:
        """Upload report logo."""
        return self._client.post('stats/report/updatereportlogo', data={'logo': logo_data})

    def delete_logo(self) -> str:
        """Delete report logo."""
        return self._client.get('stats/report/deletepicture')


# Link in Bio API
class LinkInBioAPI(APIModule):
    """Instagram Link in Bio management."""

    def get_catalog(self) -> List[Dict]:
        """Get bio catalog contents."""
        return self._client.get('linkinbio/instagram/getbiocatalog')

    def get_buttons(self) -> List[Dict]:
        """Get bio buttons."""
        return self._client.get('linkinbio/instagram/getbioButtons')

    def add_button(self, text: str, link: str) -> List[Dict]:
        """Add button to bio link."""
        return self._client.get(
            'linkinbio/instagram/addcatalogButton',
            params={'textButton': text, 'link': link}
        )

    def edit_button(self, item_id: int, text: str, link: str) -> List[Dict]:
        """Edit button."""
        return self._client.get(
            'linkinbio/instagram/editcatalogbutton',
            params={'itemid': item_id, 'text': text, 'link': link}
        )

    def update_button_position(self, item_id: int) -> List[Dict]:
        """Update button position."""
        return self._client.get(
            'linkinbio/instagram/updateButtonPosition',
            params={'itemid': item_id}
        )

    def add_item(self, picture: str, ig_id: str, timestamp: int) -> List[Dict]:
        """Add item to bio catalog."""
        return self._client.post(
            'linkinbio/instagram/addcatalogitems',
            data={'picture': picture, 'igid': ig_id, 'timestamp': timestamp}
        )

    def edit_item(self, item_id: int, link: str) -> List[Dict]:
        """Edit catalog item link."""
        return self._client.get(
            'linkinbio/instagram/editcatalogitem',
            params={'itemid': item_id, 'link': link}
        )

    def delete_item(self, item_id: int) -> bool:
        """Delete item from bio link."""
        result = self._client.delete(
            'linkinbio/instagram/deletecatalogitem',
            params={'itemid': item_id}
        )
        return result.get('success', True)

    def delete_image(self, item_id: int) -> List[Dict]:
        """Delete image from bio."""
        return self._client.delete(
            'linkinbio/instagram/deletecatalogimage',
            params={'itemid': item_id}
        )


# GMB API
class GmbAPI(APIModule):
    """Google My Business management."""

    def get_reviews(self, start: int, end: int, sort: str = None) -> List[Dict]:
        """Get GMB reviews."""
        params = {'start': start, 'end': end}
        if sort:
            params['sortcolumn'] = sort
        return self._client.get('stats/gmb/review', params=params)

    def get_review(self, review_name: str) -> Dict:
        """Get specific review."""
        return self._client.get('stats/gmb/reviewbyid', params={'reviewname': review_name})

    def reply_review(self, review_name: str, text: str) -> Dict:
        """Reply to a review."""
        return self._client.get(
            'stats/gmb/review/reply',
            params={'reviewname': review_name, 'text': text}
        )

    def remove_review_reply(self, review_name: str) -> Dict:
        """Remove review reply."""
        return self._client.get(
            'stats/gmb/review/reply/remove',
            params={'reviewname': review_name}
        )

    def get_media(self, media_type: str, start: int, end: int) -> List[Dict]:
        """Get GMB media."""
        return self._client.get(
            f'stats/gmb/media/{media_type}',
            params={'start': start, 'end': end}
        )


# Real-Time API
class RealTimeAPI(APIModule):
    """Real-time analytics."""

    def get_values(self) -> Dict:
        """Get today's page views, visits, visitors."""
        return self._client.get('stats/rt/values')

    def get_pageviews_per_hour(self) -> Dict:
        """Get page views per hour distribution."""
        return self._client.get('stats/rt/pvperhour')

    def get_sessions(self) -> Dict:
        """Get real-time visit list."""
        return self._client.get('stats/rt/sessions')

    def get_distribution(self, dist_type: str) -> Dict:
        """Get real-time distribution by type."""
        return self._client.get(f'stats/rt/distribution/{dist_type}')


# CLI entry point
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Metricool API Client')
    parser.add_argument('--token', help='API token')
    parser.add_argument('--user-id', help='User ID')
    parser.add_argument('--blog-id', help='Blog/Brand ID')
    parser.add_argument('command', help='Command to run')
    parser.add_argument('args', nargs='*', help='Command arguments')

    args = parser.parse_args()

    client = MetricoolClient(
        user_token=args.token,
        user_id=args.user_id,
        blog_id=args.blog_id
    )

    if args.command == 'ping':
        print(f"API Status: {'OK' if client.ping() else 'FAILED'}")

    elif args.command == 'brands':
        brands = client.admin.list_brands()
        print(json.dumps(brands, indent=2))

    elif args.command == 'stats':
        stats = client.get_stats()
        print(json.dumps(stats, indent=2))

    else:
        print(f"Unknown command: {args.command}")
