from typing import Dict, Any, Tuple, Optional
from pathlib import Path
import yaml
from core.models import OverlayPosition


class StyleManager:
    """Manage styling configurations for overlays"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize style manager with optional config file"""
        self.config_path = Path(config_path) if config_path else Path("config/overlay.yaml")
        self.styles = self._load_styles()
        self.brand_styles = self._load_brand_styles()

    def _load_styles(self) -> Dict[str, Any]:
        """Load default overlay styles"""
        default_styles = {
            "templates": {
                "elegant": {
                    "background_color": "#000000",
                    "background_opacity": 0.85,
                    "border_radius": 15,
                    "product_name": {
                        "size": 32,
                        "color": "#FFFFFF",
                        "weight": "bold",
                        "font_family": "Georgia"
                    },
                    "brand_name": {
                        "size": 18,
                        "color": "#D4AF37",
                        "weight": "normal",
                        "font_family": "Georgia"
                    },
                    "price": {
                        "size": 28,
                        "color": "#FFD700",
                        "weight": "bold",
                        "font_family": "Georgia"
                    }
                },
                "modern": {
                    "background_color": "#1a1a1a",
                    "background_opacity": 0.9,
                    "border_radius": 8,
                    "product_name": {
                        "size": 28,
                        "color": "#FFFFFF",
                        "weight": "bold",
                        "font_family": "Arial"
                    },
                    "brand_name": {
                        "size": 16,
                        "color": "#888888",
                        "weight": "normal",
                        "font_family": "Arial"
                    },
                    "price": {
                        "size": 24,
                        "color": "#FF4444",
                        "weight": "bold",
                        "font_family": "Arial"
                    }
                },
                "minimal": {
                    "background_color": "#FFFFFF",
                    "background_opacity": 0.95,
                    "border_radius": 5,
                    "product_name": {
                        "size": 24,
                        "color": "#333333",
                        "weight": "normal",
                        "font_family": "Helvetica"
                    },
                    "brand_name": {
                        "size": 14,
                        "color": "#666666",
                        "weight": "normal",
                        "font_family": "Helvetica"
                    },
                    "price": {
                        "size": 20,
                        "color": "#000000",
                        "weight": "bold",
                        "font_family": "Helvetica"
                    }
                },
                "luxury": {
                    "background_color": "#2C1810",
                    "background_opacity": 0.9,
                    "border_radius": 12,
                    "product_name": {
                        "size": 30,
                        "color": "#F5E6D3",
                        "weight": "bold",
                        "font_family": "Times New Roman"
                    },
                    "brand_name": {
                        "size": 16,
                        "color": "#D4AF37",
                        "weight": "italic",
                        "font_family": "Times New Roman"
                    },
                    "price": {
                        "size": 26,
                        "color": "#DAA520",
                        "weight": "bold",
                        "font_family": "Times New Roman"
                    }
                }
            },
            "positions": {
                "bottom-left": {
                    "padding_x": 20,
                    "padding_y": 20,
                    "anchor": "bottom-left"
                },
                "bottom-right": {
                    "padding_x": 20,
                    "padding_y": 20,
                    "anchor": "bottom-right"
                },
                "top-left": {
                    "padding_x": 20,
                    "padding_y": 20,
                    "anchor": "top-left"
                },
                "top-right": {
                    "padding_x": 20,
                    "padding_y": 20,
                    "anchor": "top-right"
                },
                "center-bottom": {
                    "padding_x": 0,
                    "padding_y": 30,
                    "anchor": "center-bottom"
                }
            }
        }

        # Try to load from config file if exists
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    custom_styles = yaml.safe_load(f)
                    if custom_styles:
                        # Merge with defaults
                        default_styles.update(custom_styles)
            except Exception as e:
                print(f"Warning: Could not load custom styles: {e}")

        return default_styles

    def _load_brand_styles(self) -> Dict[str, Dict[str, Any]]:
        """Load brand-specific style overrides"""
        brand_config_path = Path("config/brand_styles.yaml")

        default_brand_styles = {
            "Nike": {
                "template": "modern",
                "brand_color": "#FF4444",
                "background_color": "#000000"
            },
            "Apple": {
                "template": "minimal",
                "brand_color": "#007AFF",
                "background_color": "#F8F8F8"
            },
            "Louis Vuitton": {
                "template": "luxury",
                "brand_color": "#8B4513",
                "background_color": "#1a1a1a"
            },
            "Gucci": {
                "template": "luxury",
                "brand_color": "#006B3C",
                "background_color": "#2C1810"
            },
            "Adidas": {
                "template": "modern",
                "brand_color": "#FFFFFF",
                "background_color": "#000000"
            }
        }

        # Try to load from config file
        if brand_config_path.exists():
            try:
                with open(brand_config_path, 'r') as f:
                    custom_brand_styles = yaml.safe_load(f)
                    if custom_brand_styles:
                        default_brand_styles.update(custom_brand_styles)
            except Exception as e:
                print(f"Warning: Could not load brand styles: {e}")

        return default_brand_styles

    def get_style_for_brand(self, brand_name: str, template_name: Optional[str] = None) -> Dict[str, Any]:
        """Get style configuration for a specific brand"""
        # Check if brand has specific styling
        brand_config = self.brand_styles.get(brand_name, {})

        # Determine template to use
        if template_name:
            template = template_name
        elif 'template' in brand_config:
            template = brand_config['template']
        else:
            template = self._auto_select_template(brand_name)

        # Get base template
        base_style = self.styles.get("templates", {}).get(template, self.styles["templates"]["modern"])

        # Apply brand-specific overrides
        style = self._deep_merge_dicts(base_style.copy(), brand_config)

        return style

    def _auto_select_template(self, brand_name: str) -> str:
        """Auto-select appropriate template based on brand name"""
        luxury_keywords = ["louis vuitton", "gucci", "prada", "chanel", "hermès", "dior", "versace"]
        tech_keywords = ["apple", "samsung", "sony", "microsoft", "google"]
        sports_keywords = ["nike", "adidas", "puma", "under armour", "reebok"]

        brand_lower = brand_name.lower()

        if any(keyword in brand_lower for keyword in luxury_keywords):
            return "luxury"
        elif any(keyword in brand_lower for keyword in tech_keywords):
            return "minimal"
        elif any(keyword in brand_lower for keyword in sports_keywords):
            return "modern"
        else:
            return "elegant"  # Default

    def get_position_config(self, position: OverlayPosition) -> Dict[str, Any]:
        """Get position-specific configuration"""
        position_str = position.value if hasattr(position, 'value') else str(position)
        return self.styles.get("positions", {}).get(position_str, self.styles["positions"]["bottom-left"])

    def get_available_templates(self) -> list:
        """Get list of available style templates"""
        return list(self.styles.get("templates", {}).keys())

    def get_template_preview(self, template_name: str) -> Dict[str, Any]:
        """Get preview of a template's key characteristics"""
        template = self.styles.get("templates", {}).get(template_name, {})

        return {
            "name": template_name,
            "background_color": template.get("background_color", "#000000"),
            "primary_text_color": template.get("product_name", {}).get("color", "#FFFFFF"),
            "accent_color": template.get("price", {}).get("color", "#FFD700"),
            "style": "luxurious" if "luxury" in template_name else
                    "clean" if "minimal" in template_name else
                    "contemporary" if "modern" in template_name else "classic"
        }

    def create_custom_style(
        self,
        base_template: str,
        overrides: Dict[str, Any],
        save_as: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a custom style based on existing template"""
        base_style = self.styles.get("templates", {}).get(base_template, {})
        custom_style = self._deep_merge_dicts(base_style.copy(), overrides)

        if save_as:
            # Save to styles
            if "templates" not in self.styles:
                self.styles["templates"] = {}
            self.styles["templates"][save_as] = custom_style

            # Optionally save to file
            self._save_custom_style(save_as, custom_style)

        return custom_style

    def _deep_merge_dicts(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = dict1.copy()

        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_dicts(result[key], value)
            else:
                result[key] = value

        return result

    def _save_custom_style(self, name: str, style: Dict[str, Any]) -> None:
        """Save custom style to config file"""
        try:
            # Ensure config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Load existing config or create new
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f) or {}
            else:
                config = {}

            # Add custom style
            if "templates" not in config:
                config["templates"] = {}
            config["templates"][name] = style

            # Save back to file
            with open(self.config_path, 'w') as f:
                yaml.safe_dump(config, f, default_flow_style=False, indent=2)

        except Exception as e:
            print(f"Warning: Could not save custom style: {e}")

    def validate_style(self, style: Dict[str, Any]) -> Tuple[bool, list]:
        """Validate style configuration"""
        errors = []

        # Check required fields
        required_fields = ["background_color", "product_name", "brand_name", "price"]
        for field in required_fields:
            if field not in style:
                errors.append(f"Missing required field: {field}")

        # Validate colors (hex format)
        color_fields = ["background_color"]
        for field in color_fields:
            if field in style:
                color = style[field]
                if not self._is_valid_hex_color(color):
                    errors.append(f"Invalid hex color for {field}: {color}")

        # Validate nested color fields
        for text_type in ["product_name", "brand_name", "price"]:
            if text_type in style and isinstance(style[text_type], dict):
                if "color" in style[text_type]:
                    color = style[text_type]["color"]
                    if not self._is_valid_hex_color(color):
                        errors.append(f"Invalid hex color for {text_type}.color: {color}")

        return len(errors) == 0, errors

    def _is_valid_hex_color(self, color: str) -> bool:
        """Validate hex color format"""
        if not isinstance(color, str):
            return False

        color = color.strip().lstrip('#')
        if len(color) not in [3, 6]:
            return False

        try:
            int(color, 16)
            return True
        except ValueError:
            return False