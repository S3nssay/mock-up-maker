import asyncio
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import structlog
from core.models import (
    ProductData,
    GenerationRequest,
    GenerationResult,
    ProcessingStatus,
    ImageProvider
)
from api.base_client import AIImageProvider


logger = structlog.get_logger()


@dataclass
class QueueItem:
    """Individual queue item for processing"""
    id: str
    product: ProductData
    request: GenerationRequest
    priority: int = 0
    retry_count: int = 0
    max_retries: int = 3
    created_at: float = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    result: Optional[GenerationResult] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


class QueueManager:
    """Advanced queue manager for batch processing with concurrency control"""

    def __init__(
        self,
        providers: Dict[ImageProvider, AIImageProvider],
        concurrent_limit: int = 3,
        checkpoint_file: Optional[str] = None
    ):
        """Initialize queue manager"""
        self.providers = providers
        self.concurrent_limit = concurrent_limit
        self.checkpoint_file = Path(checkpoint_file) if checkpoint_file else None

        # Queue management
        self.queue: List[QueueItem] = []
        self.processing: Dict[str, QueueItem] = {}
        self.completed: Dict[str, QueueItem] = {}
        self.failed: Dict[str, QueueItem] = {}

        # Statistics
        self.stats = {
            "total_items": 0,
            "processed": 0,
            "success": 0,
            "failed": 0,
            "retries": 0,
            "start_time": None,
            "end_time": None,
            "total_cost": 0.0
        }

        # Semaphore for concurrency control
        self.semaphore = asyncio.Semaphore(concurrent_limit)
        self.executor = ThreadPoolExecutor(max_workers=concurrent_limit)

        # Progress callback
        self.progress_callback: Optional[Callable] = None

    def add_products(
        self,
        products: List[ProductData],
        generation_config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add products to processing queue"""
        generation_config = generation_config or {}

        for i, product in enumerate(products):
            # Create generation request
            request = self._create_generation_request(product, generation_config)

            # Create queue item
            queue_item = QueueItem(
                id=f"product_{product.row_number or i}",
                product=product,
                request=request,
                priority=self._calculate_priority(product),
                max_retries=generation_config.get('max_retries', 3)
            )

            self.queue.append(queue_item)

        # Sort by priority (higher first)
        self.queue.sort(key=lambda x: (-x.priority, x.created_at))

        self.stats["total_items"] = len(self.queue)
        logger.info(f"Added {len(products)} products to queue")

    def set_progress_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Set callback for progress updates"""
        self.progress_callback = callback

    async def process_queue(self) -> Dict[str, List[GenerationResult]]:
        """Process entire queue with concurrency control"""
        self.stats["start_time"] = time.time()
        logger.info(f"Starting queue processing with {self.concurrent_limit} concurrent workers")

        # Load checkpoint if available
        self._load_checkpoint()

        # Create semaphore tasks
        tasks = []
        for _ in range(min(self.concurrent_limit, len(self.queue))):
            task = asyncio.create_task(self._worker())
            tasks.append(task)

        # Wait for all workers to complete
        await asyncio.gather(*tasks, return_exceptions=True)

        self.stats["end_time"] = time.time()
        self.stats["processing_time"] = self.stats["end_time"] - self.stats["start_time"]

        # Final progress update
        self._update_progress()

        # Clean up checkpoint
        if self.checkpoint_file and self.checkpoint_file.exists():
            self.checkpoint_file.unlink()

        logger.info(f"Queue processing completed in {self.stats['processing_time']:.2f}s")

        return self._get_results()

    async def _worker(self) -> None:
        """Worker coroutine that processes queue items"""
        while True:
            # Get next item
            item = self._get_next_item()
            if item is None:
                break

            async with self.semaphore:
                await self._process_item(item)

    def _get_next_item(self) -> Optional[QueueItem]:
        """Get next item from queue (thread-safe)"""
        if not self.queue:
            return None

        # Get highest priority item
        item = self.queue.pop(0)
        self.processing[item.id] = item
        item.status = ProcessingStatus.IN_PROGRESS
        item.started_at = time.time()

        return item

    async def _process_item(self, item: QueueItem) -> None:
        """Process a single queue item"""
        try:
            logger.info(f"Processing {item.product.product_name} (attempt {item.retry_count + 1})")

            # Select provider
            provider = self._select_provider(item.request)
            if not provider:
                raise ValueError("No suitable provider available")

            # Generate image
            if hasattr(provider, 'generate_image_async'):
                result = await provider.generate_image_async(item.request)
            else:
                # Fallback to sync method in executor
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor,
                    provider.generate_image,
                    item.request
                )

            # Handle result
            if result.status == ProcessingStatus.SUCCESS:
                self._handle_success(item, result)
            else:
                self._handle_failure(item, result.error_message)

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error processing {item.product.product_name}: {error_msg}")
            self._handle_failure(item, error_msg)

        finally:
            # Remove from processing
            self.processing.pop(item.id, None)
            item.completed_at = time.time()

            # Update progress
            self._update_progress()

            # Save checkpoint
            self._save_checkpoint()

    def _handle_success(self, item: QueueItem, result: GenerationResult) -> None:
        """Handle successful processing"""
        item.status = ProcessingStatus.SUCCESS
        item.result = result
        self.completed[item.id] = item

        # Update stats
        self.stats["processed"] += 1
        self.stats["success"] += 1
        if result.api_cost:
            self.stats["total_cost"] += result.api_cost

        logger.info(f"✅ Successfully processed {item.product.product_name}")

    def _handle_failure(self, item: QueueItem, error_message: str) -> None:
        """Handle processing failure"""
        item.retry_count += 1
        item.error_message = error_message

        if item.retry_count < item.max_retries:
            # Retry
            item.status = ProcessingStatus.PENDING
            item.started_at = None
            # Add back to queue with lower priority
            item.priority = max(0, item.priority - 1)
            self.queue.append(item)
            self.queue.sort(key=lambda x: (-x.priority, x.created_at))

            self.stats["retries"] += 1
            logger.warning(f"⏳ Retrying {item.product.product_name} (attempt {item.retry_count + 1})")

        else:
            # Final failure
            item.status = ProcessingStatus.FAILED
            self.failed[item.id] = item

            self.stats["processed"] += 1
            self.stats["failed"] += 1
            logger.error(f"❌ Failed to process {item.product.product_name}: {error_message}")

    def _select_provider(self, request: GenerationRequest) -> Optional[AIImageProvider]:
        """Select best provider for request"""
        # Try requested provider first
        if request.provider in self.providers:
            provider = self.providers[request.provider]
            is_valid, _ = provider.validate_request(request)
            if is_valid and provider.check_rate_limit():
                return provider

        # Try other available providers
        for provider_type, provider in self.providers.items():
            if provider_type != request.provider:
                is_valid, _ = provider.validate_request(request)
                if is_valid and provider.check_rate_limit():
                    # Update request provider
                    request.provider = provider_type
                    return provider

        return None

    def _create_generation_request(
        self,
        product: ProductData,
        config: Dict[str, Any]
    ) -> GenerationRequest:
        """Create generation request from product data"""
        return GenerationRequest(
            product=product,
            provider=product.provider or config.get('default_provider', ImageProvider.SEEDREAM_KIE),
            prompt=product.get_enhanced_prompt(),
            reference_images=product.get_reference_images(),
            guidance_scale=config.get('guidance_scale', 7.5),
            num_inference_steps=config.get('num_inference_steps', 20),
            size=config.get('size', 'landscape_4_3'),
            resolution=config.get('resolution', '2K')
        )

    def _calculate_priority(self, product: ProductData) -> int:
        """Calculate processing priority for product"""
        priority = 100  # Base priority

        # Higher priority for products with max_cost (budget sensitive)
        if product.max_cost:
            priority += 20

        # Higher priority for products with more reference images
        priority += len(product.get_reference_images()) * 5

        # Lower priority if overlay is needed (more processing time)
        if product.add_product_overlay:
            priority -= 10

        # Higher priority for specific providers (assuming they're preferred)
        if product.provider:
            priority += 15

        return priority

    def _update_progress(self) -> None:
        """Update and broadcast progress"""
        total = self.stats["total_items"]
        processed = self.stats["processed"]
        in_progress = len(self.processing)

        progress_data = {
            "total": total,
            "processed": processed,
            "in_progress": in_progress,
            "pending": len(self.queue),
            "success": self.stats["success"],
            "failed": self.stats["failed"],
            "retries": self.stats["retries"],
            "completion_percentage": (processed / total * 100) if total > 0 else 0,
            "total_cost": self.stats["total_cost"]
        }

        if self.progress_callback:
            self.progress_callback(progress_data)

    def _get_results(self) -> Dict[str, List[GenerationResult]]:
        """Get final processing results"""
        results = {
            "successful": [],
            "failed": [],
            "all": []
        }

        # Successful results
        for item in self.completed.values():
            if item.result:
                results["successful"].append(item.result)
                results["all"].append(item.result)

        # Failed results (create GenerationResult objects)
        for item in self.failed.values():
            failed_result = GenerationResult(
                product_name=item.product.product_name,
                brand_name=item.product.brand_name,
                provider_used=item.request.provider,
                status=ProcessingStatus.FAILED,
                error_message=item.error_message
            )
            results["failed"].append(failed_result)
            results["all"].append(failed_result)

        return results

    def _save_checkpoint(self) -> None:
        """Save processing checkpoint"""
        if not self.checkpoint_file:
            return

        try:
            checkpoint_data = {
                "stats": self.stats,
                "queue": [self._serialize_item(item) for item in self.queue],
                "processing": [self._serialize_item(item) for item in self.processing.values()],
                "completed": [self._serialize_item(item) for item in self.completed.values()],
                "failed": [self._serialize_item(item) for item in self.failed.values()]
            }

            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)

        except Exception as e:
            logger.warning(f"Failed to save checkpoint: {str(e)}")

    def _load_checkpoint(self) -> None:
        """Load processing checkpoint"""
        if not self.checkpoint_file or not self.checkpoint_file.exists():
            return

        try:
            with open(self.checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)

            # Restore stats
            self.stats.update(checkpoint_data.get("stats", {}))

            # Restore queues
            self.queue = [self._deserialize_item(item_data)
                         for item_data in checkpoint_data.get("queue", [])]

            # Restore completed items
            for item_data in checkpoint_data.get("completed", []):
                item = self._deserialize_item(item_data)
                self.completed[item.id] = item

            # Restore failed items
            for item_data in checkpoint_data.get("failed", []):
                item = self._deserialize_item(item_data)
                self.failed[item.id] = item

            logger.info(f"Restored checkpoint: {len(self.queue)} pending, {len(self.completed)} completed")

        except Exception as e:
            logger.warning(f"Failed to load checkpoint: {str(e)}")

    def _serialize_item(self, item: QueueItem) -> Dict[str, Any]:
        """Serialize queue item for checkpoint"""
        data = asdict(item)
        # Convert non-serializable fields
        if item.result:
            data["result"] = item.result.dict()
        return data

    def _deserialize_item(self, data: Dict[str, Any]) -> QueueItem:
        """Deserialize queue item from checkpoint"""
        # Convert back from dict
        if "result" in data and data["result"]:
            data["result"] = GenerationResult(**data["result"])

        # Handle enums
        if "status" in data:
            data["status"] = ProcessingStatus(data["status"])

        return QueueItem(**data)

    def get_statistics(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        elapsed_time = time.time() - (self.stats["start_time"] or time.time())

        return {
            **self.stats,
            "elapsed_time": elapsed_time,
            "items_per_minute": (self.stats["processed"] / (elapsed_time / 60)) if elapsed_time > 0 else 0,
            "estimated_completion": self._estimate_completion_time(),
            "current_queue_size": len(self.queue),
            "active_workers": len(self.processing)
        }

    def _estimate_completion_time(self) -> Optional[float]:
        """Estimate remaining completion time"""
        if self.stats["processed"] == 0 or not self.stats["start_time"]:
            return None

        elapsed = time.time() - self.stats["start_time"]
        rate = self.stats["processed"] / elapsed
        remaining = len(self.queue) + len(self.processing)

        if rate > 0:
            return remaining / rate
        return None

    def pause_processing(self) -> None:
        """Pause processing (for future implementation)"""
        logger.info("Pause requested - completing current items")
        # Implementation would involve setting a pause flag

    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        return {
            "pending": len(self.queue),
            "processing": len(self.processing),
            "completed": len(self.completed),
            "failed": len(self.failed),
            "total": self.stats["total_items"]
        }