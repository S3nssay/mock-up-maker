from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator, HttpUrl


class ImageProvider(str, Enum):
    SEEDREAM_KIE = "seedream_kie"
    SEEDREAM_AIML = "seedream_aiml"
    SEEDREAM_BYTEPLUS = "seedream_byteplus"
    NANO_BANANA = "nano_banana"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class OverlayPosition(str, Enum):
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"
    CENTER_BOTTOM = "center-bottom"
    CENTER_TOP = "center-top"
    CUSTOM = "custom"


class ProductData(BaseModel):
    """Model for product data from Excel"""
    row_number: int
    product_name: str
    prompt: str
    brand_name: str
    product_price: Optional[str] = None
    product_url: Optional[str] = None
    product_url_1: Optional[str] = None
    product_url_2: Optional[str] = None
    product_url_3: Optional[str] = None
    model_url: Optional[str] = None
    output_name: Optional[str] = None
    provider: Optional[ImageProvider] = None
    max_cost: Optional[float] = None
    add_product_overlay: bool = False
    overlay_position: Optional[OverlayPosition] = OverlayPosition.BOTTOM_LEFT

    @validator('product_name', 'prompt', 'brand_name')
    def validate_required_strings(cls, v):
        if not v or not v.strip():
            raise ValueError("Required field cannot be empty")
        return v.strip()

    @validator('max_cost')
    def validate_max_cost(cls, v):
        if v is not None and v <= 0:
            raise ValueError("max_cost must be positive")
        return v

    def get_reference_images(self) -> List[str]:
        """Get list of all reference image URLs"""
        images = []
        for url in [self.product_url_1, self.product_url_2, self.product_url_3, self.model_url]:
            if url and url.strip():
                images.append(url.strip())
        return images

    def get_product_images(self) -> List[str]:
        """Get list of product image URLs (excluding model)"""
        images = []
        for url in [self.product_url_1, self.product_url_2, self.product_url_3]:
            if url and url.strip():
                images.append(url.strip())
        return images

    def needs_model_generation(self) -> bool:
        """Check if model needs to be generated"""
        return not self.model_url or not self.model_url.strip()

    def get_enhanced_prompt(self) -> str:
        """Get enhanced prompt for model generation if needed"""
        if self.needs_model_generation():
            return f"Professional model wearing {self.prompt}. Full body shot with natural pose and lighting."
        return self.prompt


class GenerationRequest(BaseModel):
    """Request model for image generation"""
    product: ProductData
    provider: ImageProvider
    prompt: str
    reference_images: List[str] = Field(default_factory=list)
    guidance_scale: float = 7.5
    num_inference_steps: int = 20
    size: str = "landscape_4_3"
    resolution: str = "2K"

    def to_api_payload(self) -> Dict[str, Any]:
        """Convert to API-specific payload"""
        return {
            "prompt": self.prompt,
            "images": self.reference_images,
            "guidance_scale": self.guidance_scale,
            "num_inference_steps": self.num_inference_steps,
            "size": self.size,
            "resolution": self.resolution
        }


class GenerationResult(BaseModel):
    """Result model for image generation"""
    product_name: str
    brand_name: str
    task_id: Optional[str] = None
    image_url: Optional[str] = None
    local_image_path: Optional[str] = None
    ad_image_path: Optional[str] = None
    provider_used: ImageProvider
    status: ProcessingStatus
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    overlay_time: Optional[float] = None
    api_cost: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    def to_excel_row(self) -> Dict[str, Any]:
        """Convert to Excel row format"""
        return {
            "product_name": self.product_name,
            "brand_name": self.brand_name,
            "generated_image": self.local_image_path,
            "ad_image": self.ad_image_path,
            "processing_time": self.processing_time,
            "overlay_time": self.overlay_time,
            "api_cost": self.api_cost,
            "provider_used": self.provider_used.value if self.provider_used else None,
            "status": self.status.value,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat()
        }


class OverlayConfig(BaseModel):
    """Configuration for product overlay"""
    enabled: bool = True
    position: OverlayPosition = OverlayPosition.BOTTOM_LEFT
    custom_x: Optional[int] = None
    custom_y: Optional[int] = None

    # Text styling
    product_name_size: int = 28
    product_name_color: str = "#FFFFFF"
    product_name_bold: bool = True

    brand_name_size: int = 18
    brand_name_color: str = "#CCCCCC"

    price_size: int = 32
    price_color: str = "#FFD700"
    price_bold: bool = True

    # Background
    background_color: str = "#000000"
    background_opacity: float = 0.8
    padding: int = 20
    border_radius: int = 10

    # QR Code
    qr_enabled: bool = True
    qr_size: int = 80
    qr_position: str = "bottom-right"


class BatchProcessingResult(BaseModel):
    """Result for entire batch processing"""
    total_rows: int
    successful: int
    failed: int
    skipped: int
    total_cost: float
    total_time: float
    results: List[GenerationResult]
    output_directory: str
    results_file: str

    def get_summary(self) -> str:
        """Get processing summary"""
        success_rate = (self.successful / self.total_rows * 100) if self.total_rows > 0 else 0
        return (
            f"Processing Complete:\n"
            f"  Total: {self.total_rows} products\n"
            f"  Success: {self.successful} ({success_rate:.1f}%)\n"
            f"  Failed: {self.failed}\n"
            f"  Skipped: {self.skipped}\n"
            f"  Total Cost: ${self.total_cost:.2f}\n"
            f"  Time: {self.total_time:.1f}s\n"
            f"  Results: {self.results_file}"
        )

    def get_brand_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """Get cost and count breakdown by brand"""
        brands = {}
        for result in self.results:
            brand = result.brand_name
            if brand not in brands:
                brands[brand] = {
                    "count": 0,
                    "successful": 0,
                    "failed": 0,
                    "cost": 0.0
                }

            brands[brand]["count"] += 1
            if result.status == ProcessingStatus.SUCCESS:
                brands[brand]["successful"] += 1
                brands[brand]["cost"] += result.api_cost or 0.0
            elif result.status == ProcessingStatus.FAILED:
                brands[brand]["failed"] += 1

        return brands