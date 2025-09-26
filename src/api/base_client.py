from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import time
import asyncio
import aiohttp
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog
from core.models import (
    GenerationRequest,
    GenerationResult,
    ImageProvider,
    ProcessingStatus
)


logger = structlog.get_logger()


class AIImageProvider(ABC):
    """Abstract base class for AI image generation providers"""

    def __init__(self, api_key: str, config: Dict[str, Any]):
        """Initialize provider with API key and configuration"""
        self.api_key = api_key
        self.config = config
        self.name = config.get("name", "Unknown Provider")
        self.endpoint = config.get("endpoint", "")
        self.supports_multi_reference = config.get("supports_multi_reference", False)
        self.max_resolution = config.get("max_resolution", "2K")
        self.cost_per_image = config.get("cost_per_image", 0.025)
        self.rate_limit = config.get("rate_limit", 60)
        self.max_reference_images = config.get("max_reference_images", 3)

        # Rate limiting
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_window = 60  # seconds

    @abstractmethod
    async def generate_image_async(
        self,
        request: GenerationRequest
    ) -> GenerationResult:
        """Generate image asynchronously"""
        pass

    @abstractmethod
    def generate_image(
        self,
        request: GenerationRequest
    ) -> GenerationResult:
        """Generate image synchronously"""
        pass

    @abstractmethod
    def get_generation_status(self, task_id: str) -> Dict[str, Any]:
        """Check status of image generation task"""
        pass

    @abstractmethod
    def download_image(self, image_url: str) -> bytes:
        """Download generated image"""
        pass

    def validate_request(self, request: GenerationRequest) -> Tuple[bool, Optional[str]]:
        """Validate generation request"""
        # Check API key
        if not self.api_key:
            return False, "API key not configured"

        # Check number of reference images
        if len(request.reference_images) > self.max_reference_images:
            return False, f"Too many reference images. Maximum allowed: {self.max_reference_images}"

        # Check if multi-reference is supported
        if len(request.reference_images) > 1 and not self.supports_multi_reference:
            return False, "Provider does not support multiple reference images"

        # Check resolution support
        if request.resolution == "4K" and self.max_resolution == "2K":
            return False, "Provider does not support 4K resolution"

        return True, None

    def estimate_cost(self, request: GenerationRequest) -> float:
        """Estimate cost for generation request"""
        base_cost = self.cost_per_image

        # Adjust for resolution
        if request.resolution == "4K":
            base_cost *= 1.5

        # Adjust for number of reference images
        if len(request.reference_images) > 2:
            base_cost *= 1.2

        return base_cost

    def check_rate_limit(self) -> bool:
        """Check if rate limit allows new request"""
        current_time = time.time()

        # Reset counter if window has passed
        if current_time - self.last_request_time > self.rate_limit_window:
            self.request_count = 0
            self.last_request_time = current_time

        # Check if under rate limit
        if self.request_count < self.rate_limit:
            self.request_count += 1
            return True

        return False

    async def wait_for_rate_limit(self):
        """Wait if rate limited"""
        while not self.check_rate_limit():
            wait_time = self.rate_limit_window - (time.time() - self.last_request_time)
            logger.info(f"Rate limited. Waiting {wait_time:.1f} seconds...")
            await asyncio.sleep(min(wait_time, 5))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _make_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        json_data: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> requests.Response:
        """Make HTTP request with retry logic"""
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=json_data, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    async def _make_async_request(
        self,
        session: aiohttp.ClientSession,
        method: str,
        url: str,
        headers: Dict[str, str],
        json_data: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Make async HTTP request"""
        try:
            async with session.request(
                method,
                url,
                headers=headers,
                json=json_data,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                response.raise_for_status()
                return await response.json()

        except aiohttp.ClientError as e:
            logger.error(f"Async request failed: {str(e)}")
            raise

    def format_error_message(self, error: Exception) -> str:
        """Format error message for logging and display"""
        error_type = type(error).__name__
        error_msg = str(error)

        if isinstance(error, requests.exceptions.HTTPError):
            if error.response:
                try:
                    error_detail = error.response.json()
                    return f"{error_type}: {error_detail.get('message', error_msg)}"
                except:
                    return f"{error_type}: {error.response.text[:200]}"

        return f"{error_type}: {error_msg}"

    def prepare_reference_images(self, images: List[str]) -> List[str]:
        """Prepare and validate reference image URLs"""
        validated_images = []

        for image_url in images:
            if image_url and image_url.strip():
                # Ensure URL is properly formatted
                url = image_url.strip()
                if url.startswith(("http://", "https://")):
                    validated_images.append(url)
                else:
                    logger.warning(f"Invalid image URL format: {url}")

        return validated_images[:self.max_reference_images]

    def create_result(
        self,
        request: GenerationRequest,
        status: ProcessingStatus,
        task_id: Optional[str] = None,
        image_url: Optional[str] = None,
        error_message: Optional[str] = None,
        processing_time: Optional[float] = None
    ) -> GenerationResult:
        """Create GenerationResult object"""
        return GenerationResult(
            product_name=request.product.product_name,
            brand_name=request.product.brand_name,
            task_id=task_id,
            image_url=image_url,
            provider_used=request.provider,
            status=status,
            error_message=error_message,
            processing_time=processing_time,
            api_cost=self.estimate_cost(request) if status == ProcessingStatus.SUCCESS else None
        )