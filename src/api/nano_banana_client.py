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


class NanoBananaProvider(AIImageProvider):
    """Nano Banana provider implementation"""

    def __init__(self, api_key: str, config: Dict[str, Any]):
        """Initialize Nano Banana provider"""
        super().__init__(api_key, config)
        self.endpoint = config.get("endpoint", "https://api.nano-banana.com/v1")

    async def generate_image_async(self, request: GenerationRequest) -> GenerationResult:
        """Generate image asynchronously via Nano Banana"""
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
                    timeout=90
                )

                # Handle different response formats
                if "task_id" in response_data:
                    # Async generation - poll for completion
                    task_id = response_data["task_id"]
                    image_url = await self._poll_for_completion_async(session, task_id)
                elif "image_url" in response_data:
                    # Sync generation - immediate result
                    image_url = response_data["image_url"]
                    task_id = response_data.get("id", "sync")
                else:
                    raise ValueError("Unexpected response format from Nano Banana")

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
            logger.error(f"Nano Banana generation failed: {error_msg}")

            return self.create_result(
                request,
                ProcessingStatus.FAILED,
                error_message=error_msg,
                processing_time=time.time() - start_time
            )

    def generate_image(self, request: GenerationRequest) -> GenerationResult:
        """Generate image synchronously via Nano Banana"""
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
                timeout=90
            )

            response_data = response.json()

            # Handle different response formats
            if "task_id" in response_data:
                # Async generation - poll for completion
                task_id = response_data["task_id"]
                image_url = self._poll_for_completion(task_id)
            elif "image_url" in response_data:
                # Sync generation - immediate result
                image_url = response_data["image_url"]
                task_id = response_data.get("id", "sync")
            else:
                raise ValueError("Unexpected response format from Nano Banana")

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
            logger.error(f"Nano Banana generation failed: {error_msg}")

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
        """Prepare API payload for Nano Banana"""
        # Prepare reference images
        reference_images = self.prepare_reference_images(request.reference_images)

        # Build base payload
        payload = {
            "prompt": request.prompt,
            "width": self._get_width(request.size, request.resolution),
            "height": self._get_height(request.size, request.resolution),
            "guidance_scale": request.guidance_scale,
            "num_inference_steps": request.num_inference_steps,
            "seed": -1,  # Random seed
            "scheduler": "DPMSolverMultistepScheduler",
            "safety_checker": True
        }

        # Add reference images if available
        if reference_images:
            payload["init_images"] = reference_images
            payload["strength"] = 0.8  # How much to transform the reference

            # Adjust prompt based on reference images
            if request.product.model_url and request.product.get_product_images():
                # Model + products provided
                payload["prompt"] = self._enhance_prompt_with_model_and_products(request.prompt)
                payload["controlnet_conditioning_scale"] = 0.7
            elif request.product.get_product_images():
                # Only products, need to generate model
                payload["prompt"] = self._enhance_prompt_for_model_generation(request.prompt)
                payload["controlnet_conditioning_scale"] = 0.5
            else:
                # Generic reference images
                payload["controlnet_conditioning_scale"] = 0.6

        # Add style parameters for better product photography
        if self._is_product_prompt(request.prompt):
            payload["negative_prompt"] = self._get_product_negative_prompt()
            payload["clip_skip"] = 2

        # Add quality enhancers
        payload["enable_attention_slicing"] = True
        payload["enable_cpu_offload"] = False

        return payload

    def _get_width(self, size: str, resolution: str) -> int:
        """Get width based on size and resolution"""
        base_sizes = {
            "landscape_4_3": (4, 3),
            "landscape_16_9": (16, 9),
            "portrait_3_4": (3, 4),
            "portrait_9_16": (9, 16),
            "square": (1, 1)
        }

        resolution_multipliers = {
            "HD": 80,
            "FHD": 120,
            "2K": 160,
            "4K": 240  # Note: Nano Banana may have lower max resolution
        }

        aspect_ratio = base_sizes.get(size, (4, 3))
        multiplier = resolution_multipliers.get(resolution, 120)

        return aspect_ratio[0] * multiplier

    def _get_height(self, size: str, resolution: str) -> int:
        """Get height based on size and resolution"""
        base_sizes = {
            "landscape_4_3": (4, 3),
            "landscape_16_9": (16, 9),
            "portrait_3_4": (3, 4),
            "portrait_9_16": (9, 16),
            "square": (1, 1)
        }

        resolution_multipliers = {
            "HD": 80,
            "FHD": 120,
            "2K": 160,
            "4K": 240
        }

        aspect_ratio = base_sizes.get(size, (4, 3))
        multiplier = resolution_multipliers.get(resolution, 120)

        return aspect_ratio[1] * multiplier

    def _enhance_prompt_with_model_and_products(self, prompt: str) -> str:
        """Enhance prompt when both model and products are provided"""
        enhancements = [
            "professional photography",
            "high quality",
            "studio lighting",
            "commercial product shot",
            "detailed textures"
        ]

        enhanced = f"{prompt}, {', '.join(enhancements)}"
        return enhanced

    def _enhance_prompt_for_model_generation(self, prompt: str) -> str:
        """Enhance prompt when model needs to be generated"""
        model_enhancements = [
            "professional model",
            "attractive person",
            "natural pose",
            "confident expression",
            "studio lighting",
            "commercial photography",
            "high fashion"
        ]

        enhanced = f"professional model wearing {prompt}, {', '.join(model_enhancements)}"
        return enhanced

    def _is_product_prompt(self, prompt: str) -> bool:
        """Check if prompt is product-related"""
        product_keywords = [
            "dress", "shirt", "shoes", "bag", "watch", "jewelry",
            "clothing", "apparel", "fashion", "accessory", "product",
            "wearing", "model", "professional"
        ]

        prompt_lower = prompt.lower()
        return any(keyword in prompt_lower for keyword in product_keywords)

    def _get_product_negative_prompt(self) -> str:
        """Get negative prompt for better product photography"""
        return (
            "blurry, low quality, distorted, deformed, "
            "bad anatomy, extra limbs, missing limbs, "
            "poor lighting, overexposed, underexposed, "
            "amateur photography, low resolution, pixelated, "
            "text, watermark, signature, logo"
        )

    def _poll_for_completion(self, task_id: str, max_wait: int = 180) -> str:
        """Poll for task completion (synchronous)"""
        start_time = time.time()

        while time.time() - start_time < max_wait:
            status_data = self.get_generation_status(task_id)

            status = status_data.get("status", "").lower()

            if status in ["completed", "success", "done"]:
                # Try different possible response formats
                image_url = (
                    status_data.get("image_url") or
                    status_data.get("result", {}).get("image_url") or
                    status_data.get("output", {}).get("image_url") or
                    status_data.get("images", [{}])[0].get("url")
                )

                if image_url:
                    return image_url
                raise ValueError("Completed but no image URL found")

            elif status in ["failed", "error"]:
                error = status_data.get("error") or status_data.get("message", "Unknown error")
                raise ValueError(f"Generation failed: {error}")

            elif status in ["processing", "running", "pending"]:
                # Still processing, continue polling
                pass

            # Wait before next poll
            time.sleep(3)

        raise TimeoutError(f"Generation timeout after {max_wait} seconds")

    async def _poll_for_completion_async(
        self,
        session: aiohttp.ClientSession,
        task_id: str,
        max_wait: int = 180
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

                status = status_data.get("status", "").lower()

                if status in ["completed", "success", "done"]:
                    # Try different possible response formats
                    image_url = (
                        status_data.get("image_url") or
                        status_data.get("result", {}).get("image_url") or
                        status_data.get("output", {}).get("image_url") or
                        status_data.get("images", [{}])[0].get("url")
                    )

                    if image_url:
                        return image_url
                    raise ValueError("Completed but no image URL found")

                elif status in ["failed", "error"]:
                    error = status_data.get("error") or status_data.get("message", "Unknown error")
                    raise ValueError(f"Generation failed: {error}")

            except Exception as e:
                logger.warning(f"Poll attempt failed: {str(e)}")

            # Wait before next poll
            await asyncio.sleep(3)

        raise TimeoutError(f"Generation timeout after {max_wait} seconds")