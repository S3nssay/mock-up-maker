import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import yaml
from core.models import ImageProvider, OverlayPosition


class Settings:
    """Central configuration management"""

    def __init__(self, env_file: Optional[str] = None):
        """Initialize settings from environment variables and config files"""
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        # API Settings
        self.ai_image_provider = ImageProvider(
            os.getenv("AI_IMAGE_PROVIDER", "seedream_kie")
        )

        # API Keys
        self.seedream_kie_api_key = os.getenv("SEEDREAM_KIE_API_KEY", "")
        self.seedream_aiml_api_key = os.getenv("SEEDREAM_AIML_API_KEY", "")
        self.seedream_byteplus_api_key = os.getenv("SEEDREAM_BYTEPLUS_API_KEY", "")
        self.nano_banana_api_key = os.getenv("NANO_BANANA_API_KEY", "")
        self.nano_banana_endpoint = os.getenv(
            "NANO_BANANA_ENDPOINT", "https://api.nano-banana.com/v1"
        )

        # Generation Settings
        self.default_image_size = os.getenv("DEFAULT_IMAGE_SIZE", "landscape_4_3")
        self.default_resolution = os.getenv("DEFAULT_RESOLUTION", "2K")
        self.concurrent_requests = int(os.getenv("CONCURRENT_REQUESTS", "3"))
        self.guidance_scale = float(os.getenv("GUIDANCE_SCALE", "7.5"))
        self.num_inference_steps = int(os.getenv("NUM_INFERENCE_STEPS", "20"))

        # Fallback Settings
        self.enable_fallback = os.getenv("ENABLE_FALLBACK", "true").lower() == "true"
        self.fallback_order = os.getenv(
            "FALLBACK_ORDER", "seedream_kie,nano_banana,seedream_aiml"
        ).split(",")

        # Output Settings
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./product_ads"))
        self.image_format = os.getenv("IMAGE_FORMAT", "PNG")
        self.results_filename = os.getenv("RESULTS_FILENAME", "results.xlsx")
        self.organize_by_brand = os.getenv("ORGANIZE_BY_BRAND", "true").lower() == "true"

        # Overlay Settings
        self.enable_product_overlay = os.getenv("ENABLE_PRODUCT_OVERLAY", "true").lower() == "true"
        self.default_overlay_position = os.getenv("DEFAULT_OVERLAY_POSITION", "bottom-left")
        self.overlay_font_size = int(os.getenv("OVERLAY_FONT_SIZE", "24"))
        self.overlay_background_opacity = float(os.getenv("OVERLAY_BACKGROUND_OPACITY", "0.8"))
        self.qr_code_size = int(os.getenv("QR_CODE_SIZE", "100"))

        # Brand Customization
        self.default_brand_color = os.getenv("DEFAULT_BRAND_COLOR", "#000000")
        self.default_font_family = os.getenv("DEFAULT_FONT_FAMILY", "Arial")
        self.watermark_enabled = os.getenv("WATERMARK_ENABLED", "false").lower() == "true"

        # Cost Control
        self.max_cost_per_image = float(os.getenv("MAX_COST_PER_IMAGE", "0.05"))
        self.total_budget_limit = float(os.getenv("TOTAL_BUDGET_LIMIT", "100.0"))

        # Retry Settings
        self.max_retry_attempts = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
        self.retry_delay_seconds = int(os.getenv("RETRY_DELAY_SECONDS", "2"))

        # Load additional config files
        self.provider_configs = self._load_provider_configs()
        self.overlay_configs = self._load_overlay_configs()

    def _load_provider_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load provider-specific configurations"""
        configs = {
            ImageProvider.SEEDREAM_KIE: {
                "name": "Seedream via Kie.ai",
                "api_key": self.seedream_kie_api_key,
                "endpoint": "https://api.kie.ai/v1/seedream",
                "supports_multi_reference": True,
                "max_resolution": "4K",
                "cost_per_image": 0.0175,
                "rate_limit": 100,
                "max_reference_images": 4
            },
            ImageProvider.NANO_BANANA: {
                "name": "Nano Banana",
                "api_key": self.nano_banana_api_key,
                "endpoint": self.nano_banana_endpoint,
                "supports_multi_reference": True,
                "max_resolution": "2K",
                "cost_per_image": 0.02,
                "rate_limit": 60,
                "max_reference_images": 3
            },
            ImageProvider.SEEDREAM_AIML: {
                "name": "Seedream via AI/ML API",
                "api_key": self.seedream_aiml_api_key,
                "endpoint": "https://api.aimlapi.com/v1/seedream",
                "supports_multi_reference": True,
                "max_resolution": "4K",
                "cost_per_image": 0.025,
                "rate_limit": 80,
                "max_reference_images": 4
            },
            ImageProvider.SEEDREAM_BYTEPLUS: {
                "name": "Seedream via BytePlus",
                "api_key": self.seedream_byteplus_api_key,
                "endpoint": "https://api.byteplus.com/v1/seedream",
                "supports_multi_reference": True,
                "max_resolution": "4K",
                "cost_per_image": 0.03,
                "rate_limit": 120,
                "max_reference_images": 4
            }
        }

        # Try to load custom config file if it exists
        config_file = Path("config/providers.yaml")
        if config_file.exists():
            with open(config_file) as f:
                custom_configs = yaml.safe_load(f)
                if custom_configs:
                    configs.update(custom_configs)

        return configs

    def _load_overlay_configs(self) -> Dict[str, Any]:
        """Load overlay configuration"""
        default_config = {
            "enabled": self.enable_product_overlay,
            "default_position": self.default_overlay_position,
            "background_style": "semi_transparent",
            "font": {
                "product_name": {
                    "size": 28,
                    "weight": "bold",
                    "color": "#FFFFFF"
                },
                "brand_name": {
                    "size": 18,
                    "weight": "regular",
                    "color": "#CCCCCC"
                },
                "price": {
                    "size": 32,
                    "weight": "bold",
                    "color": "#FFD700"
                }
            },
            "padding": 20,
            "line_spacing": 8,
            "background_opacity": self.overlay_background_opacity,
            "background_color": "#000000",
            "border_radius": 10,
            "qr_code": {
                "enabled": True,
                "size": self.qr_code_size,
                "position": "bottom-right",
                "border": 4
            }
        }

        # Try to load custom overlay config
        config_file = Path("config/overlay.yaml")
        if config_file.exists():
            with open(config_file) as f:
                custom_config = yaml.safe_load(f)
                if custom_config:
                    default_config.update(custom_config)

        return default_config

    def get_provider_config(self, provider: ImageProvider) -> Dict[str, Any]:
        """Get configuration for specific provider"""
        return self.provider_configs.get(provider, {})

    def get_available_providers(self) -> List[ImageProvider]:
        """Get list of providers with valid API keys"""
        available = []
        for provider, config in self.provider_configs.items():
            if config.get("api_key"):
                available.append(provider)
        return available

    def get_fallback_providers(self) -> List[ImageProvider]:
        """Get ordered list of fallback providers"""
        if not self.enable_fallback:
            return []

        available = self.get_available_providers()
        fallback = []

        for provider_name in self.fallback_order:
            try:
                provider = ImageProvider(provider_name.strip())
                if provider in available:
                    fallback.append(provider)
            except ValueError:
                continue

        return fallback

    def validate(self) -> List[str]:
        """Validate configuration and return list of warnings/errors"""
        issues = []

        # Check if at least one API key is configured
        if not self.get_available_providers():
            issues.append("ERROR: No API keys configured. Please set at least one provider API key.")

        # Check output directory
        if not self.output_dir.parent.exists():
            issues.append(f"WARNING: Parent directory {self.output_dir.parent} does not exist.")

        # Check cost limits
        if self.max_cost_per_image >= self.total_budget_limit:
            issues.append("WARNING: max_cost_per_image >= total_budget_limit")

        # Check concurrent requests
        if self.concurrent_requests > 10:
            issues.append("WARNING: concurrent_requests > 10 may cause rate limiting")

        return issues

    def create_output_structure(self, base_dir: Optional[Path] = None) -> Path:
        """Create output directory structure"""
        output_base = base_dir or self.output_dir

        # Create base directory
        output_base.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (output_base / "brands").mkdir(exist_ok=True)
        (output_base / "catalog").mkdir(exist_ok=True)
        (output_base / "logs").mkdir(exist_ok=True)

        return output_base

    def get_brand_output_dir(self, brand_name: str, base_dir: Optional[Path] = None) -> tuple[Path, Path]:
        """Get output directories for a specific brand"""
        output_base = base_dir or self.output_dir
        brand_dir = output_base / "brands" / self._sanitize_dirname(brand_name)

        # Create brand directories
        original_dir = brand_dir / "original"
        ads_dir = brand_dir / "ads"

        original_dir.mkdir(parents=True, exist_ok=True)
        ads_dir.mkdir(parents=True, exist_ok=True)

        return original_dir, ads_dir

    @staticmethod
    def _sanitize_dirname(name: str) -> str:
        """Sanitize directory name"""
        invalid_chars = '<>:"|?*'
        for char in invalid_chars:
            name = name.replace(char, "_")
        return name.strip()


# Global settings instance
settings = Settings()