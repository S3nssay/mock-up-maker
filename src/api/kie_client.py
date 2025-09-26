import time
import asyncio
import aiohttp
import requests
from typing import Dict, Any, Optional
import structlog
from api.base_client import AIImageProvider
from core.models import (
    GenerationRequest,
    GenerationResult,
    ProcessingStatus
)


logger = structlog.get_logger()


class KieSeedreamProvider(AIImageProvider):
    """Seedream provider implementation via Kie.ai"""

    def __init__(self, api_key: str, config: Dict[str, Any]):
        """Initialize Kie.ai Seedream provider"""
        super().__init__(api_key, config)
        self.endpoint = config.get("endpoint", "https://api.kie.ai/v1/seedream")

    async def generate_image_async(self, request: GenerationRequest) -> GenerationResult:
        """Generate image asynchronously via Kie.ai"""
        start_time = time.time()

        # Validate request
        is_valid, error_msg = self.validate_request(request)
        if not is_valid:
            return self.create_result(
                request,
                ProcessingStatus.FAILED,
                error_message=error_msg
            )

        try:
            # Wait for rate limit if needed
            await self.wait_for_rate_limit()

            # Prepare request payload
            payload = self._prepare_payload(request)

            # Make async request
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                response_data = await self._make_async_request(
                    session,
                    "POST",
                    f"{self.endpoint}/generate",
                    headers,
                    payload,
                    timeout=60
                )

                # Get task ID
                task_id = response_data.get("task_id")
                if not task_id:
                    raise ValueError("No task_id in response")

                # Poll for completion
                image_url = await self._poll_for_completion_async(session, task_id)

                processing_time = time.time() - start_time

                return self.create_result(
                    request,
                    ProcessingStatus.SUCCESS,
                    task_id=task_id,
                    image_url=image_url,
                    processing_time=processing_time
                )

        except Exception as e:
            error_msg = self.format_error_message(e)
            logger.error(f"Kie.ai generation failed: {error_msg}")

            return self.create_result(
                request,
                ProcessingStatus.FAILED,
                error_message=error_msg,
                processing_time=time.time() - start_time
            )

    def generate_image(self, request: GenerationRequest) -> GenerationResult:
        """Generate image synchronously via Kie.ai"""
        start_time = time.time()

        # Validate request
        is_valid, error_msg = self.validate_request(request)
        if not is_valid:
            return self.create_result(
                request,
                ProcessingStatus.FAILED,
                error_message=error_msg
            )

        try:
            # Check rate limit
            if not self.check_rate_limit():
                time.sleep(2)  # Simple wait for sync version

            # Prepare request payload
            payload = self._prepare_payload(request)

            # Make request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            response = self._make_request(
                "POST",
                f"{self.endpoint}/generate",
                headers,
                payload,
                timeout=60
            )

            response_data = response.json()

            # Get task ID
            task_id = response_data.get("task_id")
            if not task_id:
                raise ValueError("No task_id in response")

            # Poll for completion
            image_url = self._poll_for_completion(task_id)

            processing_time = time.time() - start_time

            return self.create_result(
                request,
                ProcessingStatus.SUCCESS,
                task_id=task_id,
                image_url=image_url,
                processing_time=processing_time
            )

        except Exception as e:
            error_msg = self.format_error_message(e)
            logger.error(f"Kie.ai generation failed: {error_msg}")

            return self.create_result(
                request,
                ProcessingStatus.FAILED,
                error_message=error_msg,
                processing_time=time.time() - start_time
            )

    def get_generation_status(self, task_id: str) -> Dict[str, Any]:
        """Check status of generation task"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            response = self._make_request(
                "GET",
                f"{self.endpoint}/status/{task_id}",
                headers,
                timeout=30
            )

            return response.json()

        except Exception as e:
            logger.error(f"Failed to get status for task {task_id}: {str(e)}")
            return {"status": "error", "error": str(e)}

    def download_image(self, image_url: str) -> bytes:
        """Download generated image"""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            return response.content

        except Exception as e:
            logger.error(f"Failed to download image from {image_url}: {str(e)}")
            raise

    def _prepare_payload(self, request: GenerationRequest) -> Dict[str, Any]:
        """Prepare API payload for Kie.ai Seedream"""
        # Prepare reference images
        reference_images = self.prepare_reference_images(request.reference_images)

        # Build payload
        payload = {
            "prompt": request.prompt,
            "model": "seedream-4.0",
            "guidance_scale": request.guidance_scale,
            "num_inference_steps": request.num_inference_steps,
            "aspect_ratio": self._get_aspect_ratio(request.size),
            "resolution": self._get_resolution_value(request.resolution)
        }

        # Add reference images if available
        if reference_images:
            payload["reference_images"] = reference_images

            # Determine reference mode based on product type
            if request.product.model_url:
                # Model image provided - use it as primary reference
                payload["reference_mode"] = "person_with_products"
                payload["person_image"] = request.product.model_url
                payload["product_images"] = request.product.get_product_images()
            else:
                # No model - generate person with products
                payload["reference_mode"] = "products_only"
                payload["product_images"] = reference_images
                payload["generate_person"] = True

        # Add optional parameters
        if request.product.needs_model_generation():
            payload["enhance_prompt"] = True
            payload["add_model_description"] = True

        return payload

    def _get_aspect_ratio(self, size: str) -> str:
        """Convert size to aspect ratio for API"""
        size_mapping = {
            "landscape_4_3": "4:3",
            "landscape_16_9": "16:9",
            "portrait_3_4": "3:4",
            "portrait_9_16": "9:16",
            "square": "1:1"
        }
        return size_mapping.get(size, "4:3")

    def _get_resolution_value(self, resolution: str) -> str:
        """Convert resolution to API value"""
        resolution_mapping = {
            "HD": "1280x720",
            "FHD": "1920x1080",
            "2K": "2560x1440",
            "4K": "3840x2160"
        }
        return resolution_mapping.get(resolution, "1920x1080")

    def _poll_for_completion(self, task_id: str, max_wait: int = 120) -> str:
        """Poll for task completion (synchronous)"""
        start_time = time.time()

        while time.time() - start_time < max_wait:
            status_data = self.get_generation_status(task_id)

            if status_data.get("status") == "completed":
                image_url = status_data.get("result", {}).get("image_url")
                if image_url:
                    return image_url
                raise ValueError("Completed but no image URL")

            elif status_data.get("status") == "failed":
                error = status_data.get("error", "Unknown error")
                raise ValueError(f"Generation failed: {error}")

            # Wait before next poll
            time.sleep(2)

        raise TimeoutError(f"Generation timeout after {max_wait} seconds")

    async def _poll_for_completion_async(
        self,
        session: aiohttp.ClientSession,
        task_id: str,
        max_wait: int = 120
    ) -> str:
        """Poll for task completion (asynchronous)"""
        start_time = time.time()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        while time.time() - start_time < max_wait:
            try:
                status_data = await self._make_async_request(
                    session,
                    "GET",
                    f"{self.endpoint}/status/{task_id}",
                    headers,
                    timeout=30
                )

                if status_data.get("status") == "completed":
                    image_url = status_data.get("result", {}).get("image_url")
                    if image_url:
                        return image_url
                    raise ValueError("Completed but no image URL")

                elif status_data.get("status") == "failed":
                    error = status_data.get("error", "Unknown error")
                    raise ValueError(f"Generation failed: {error}")

            except Exception as e:
                logger.warning(f"Poll attempt failed: {str(e)}")

            # Wait before next poll
            await asyncio.sleep(2)

        raise TimeoutError(f"Generation timeout after {max_wait} seconds")