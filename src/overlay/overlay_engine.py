import time
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import qrcode
import structlog
from core.models import ProductData, OverlayPosition, OverlayConfig
from overlay.color_analyzer import ColorAnalyzer
from overlay.style_manager import StyleManager


logger = structlog.get_logger()


class OverlayEngine:
    """Engine for creating product advertisement overlays on generated images"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize overlay engine with configuration"""
        self.config = config or self._get_default_config()
        self.style_manager = StyleManager()
        self.color_analyzer = ColorAnalyzer()

        # Load fonts
        self._load_fonts()

    def create_product_overlay(
        self,
        image_path: str,
        product: ProductData,
        output_path: str,
        overlay_config: Optional[OverlayConfig] = None
    ) -> Optional[str]:
        """Create product advertisement overlay on image"""
        start_time = time.time()

        try:
            # Load image
            img = Image.open(image_path).convert('RGB')

            # Use provided config or default
            config = overlay_config or self._create_overlay_config(product)

            if not config.enabled:
                logger.info(f"Overlay disabled for {product.product_name}")
                return None

            # Create overlay
            overlay_img = self._create_overlay(img, product, config)

            # Save result
            overlay_img.save(output_path, 'PNG', quality=95)

            processing_time = time.time() - start_time
            logger.info(f"Created overlay for {product.product_name} in {processing_time:.2f}s")

            return output_path

        except Exception as e:
            logger.error(f"Failed to create overlay for {product.product_name}: {str(e)}")
            return None

    def _create_overlay(
        self,
        img: Image.Image,
        product: ProductData,
        config: OverlayConfig
    ) -> Image.Image:
        """Create the actual overlay on the image"""
        # Create a copy to work with
        result_img = img.copy()

        # Create overlay layer
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Calculate overlay area
        overlay_area = self._calculate_overlay_area(img.size, config)

        # Analyze background color in overlay area
        bg_color = self._analyze_overlay_background(img, overlay_area)
        optimal_colors = self.color_analyzer.get_optimal_text_colors(bg_color)

        # Draw background
        self._draw_overlay_background(draw, overlay_area, config, bg_color)

        # Add product information
        text_y = self._add_product_text(
            draw, overlay_area, product, config, optimal_colors
        )

        # Add QR code if enabled and URL available
        if config.qr_enabled and product.product_url:
            self._add_qr_code(overlay, product.product_url, config)

        # Composite overlay onto image
        result_img = Image.alpha_composite(
            result_img.convert('RGBA'), overlay
        ).convert('RGB')

        return result_img

    def _calculate_overlay_area(
        self,
        img_size: Tuple[int, int],
        config: OverlayConfig
    ) -> Tuple[int, int, int, int]:
        """Calculate overlay area coordinates (x1, y1, x2, y2)"""
        width, height = img_size
        padding = config.padding

        # Estimate overlay dimensions
        overlay_width = min(width * 0.4, 400)  # Max 40% of width or 400px
        overlay_height = min(height * 0.3, 200)  # Max 30% of height or 200px

        if config.position == OverlayPosition.BOTTOM_LEFT:
            x1 = padding
            y1 = height - overlay_height - padding
            x2 = x1 + overlay_width
            y2 = height - padding

        elif config.position == OverlayPosition.BOTTOM_RIGHT:
            x1 = width - overlay_width - padding
            y1 = height - overlay_height - padding
            x2 = width - padding
            y2 = height - padding

        elif config.position == OverlayPosition.TOP_LEFT:
            x1 = padding
            y1 = padding
            x2 = x1 + overlay_width
            y2 = y1 + overlay_height

        elif config.position == OverlayPosition.TOP_RIGHT:
            x1 = width - overlay_width - padding
            y1 = padding
            x2 = width - padding
            y2 = y1 + overlay_height

        elif config.position == OverlayPosition.CENTER_BOTTOM:
            x1 = (width - overlay_width) // 2
            y1 = height - overlay_height - padding
            x2 = x1 + overlay_width
            y2 = height - padding

        elif config.position == OverlayPosition.CENTER_TOP:
            x1 = (width - overlay_width) // 2
            y1 = padding
            x2 = x1 + overlay_width
            y2 = y1 + overlay_height

        else:  # Custom position
            if config.custom_x is not None and config.custom_y is not None:
                x1 = config.custom_x
                y1 = config.custom_y
                x2 = min(x1 + overlay_width, width - padding)
                y2 = min(y1 + overlay_height, height - padding)
            else:
                # Fallback to bottom-left
                return self._calculate_overlay_area(img_size,
                    OverlayConfig(position=OverlayPosition.BOTTOM_LEFT, padding=config.padding))

        return (int(x1), int(y1), int(x2), int(y2))

    def _analyze_overlay_background(
        self,
        img: Image.Image,
        overlay_area: Tuple[int, int, int, int]
    ) -> Tuple[int, int, int]:
        """Analyze the background color in the overlay area"""
        x1, y1, x2, y2 = overlay_area

        # Crop the overlay area
        overlay_region = img.crop((x1, y1, x2, y2))

        # Get average color
        avg_color = self.color_analyzer.get_dominant_color(overlay_region)

        return avg_color

    def _draw_overlay_background(
        self,
        draw: ImageDraw.Draw,
        overlay_area: Tuple[int, int, int, int],
        config: OverlayConfig,
        bg_color: Tuple[int, int, int]
    ) -> None:
        """Draw the overlay background"""
        x1, y1, x2, y2 = overlay_area

        # Convert background color from hex
        bg_rgba = self._hex_to_rgba(config.background_color, config.background_opacity)

        # Draw rounded rectangle if border_radius > 0
        if config.border_radius > 0:
            self._draw_rounded_rectangle(
                draw, (x1, y1, x2, y2), bg_rgba, config.border_radius
            )
        else:
            draw.rectangle((x1, y1, x2, y2), fill=bg_rgba)

    def _draw_rounded_rectangle(
        self,
        draw: ImageDraw.Draw,
        bbox: Tuple[int, int, int, int],
        fill: Tuple[int, int, int, int],
        radius: int
    ) -> None:
        """Draw rounded rectangle"""
        x1, y1, x2, y2 = bbox

        # Draw main rectangle
        draw.rectangle((x1 + radius, y1, x2 - radius, y2), fill=fill)
        draw.rectangle((x1, y1 + radius, x2, y2 - radius), fill=fill)

        # Draw corners
        draw.pieslice((x1, y1, x1 + 2*radius, y1 + 2*radius), 180, 270, fill=fill)
        draw.pieslice((x2 - 2*radius, y1, x2, y1 + 2*radius), 270, 360, fill=fill)
        draw.pieslice((x1, y2 - 2*radius, x1 + 2*radius, y2), 90, 180, fill=fill)
        draw.pieslice((x2 - 2*radius, y2 - 2*radius, x2, y2), 0, 90, fill=fill)

    def _add_product_text(
        self,
        draw: ImageDraw.Draw,
        overlay_area: Tuple[int, int, int, int],
        product: ProductData,
        config: OverlayConfig,
        optimal_colors: Dict[str, str]
    ) -> int:
        """Add product text information to overlay"""
        x1, y1, x2, y2 = overlay_area

        current_y = y1 + 10
        text_x = x1 + 15
        max_width = (x2 - x1) - 30  # Leave margin for text

        # Product name
        if product.product_name:
            font = self._get_font('product_name', config.product_name_size, config.product_name_bold)
            color = config.product_name_color or optimal_colors.get('primary', '#FFFFFF')

            # Wrap text if too long
            wrapped_text = self._wrap_text(product.product_name, font, max_width)
            for line in wrapped_text:
                draw.text((text_x, current_y), line, font=font, fill=color)
                current_y += font.getbbox(line)[3] - font.getbbox(line)[1] + 5

        # Brand name
        if product.brand_name:
            current_y += 8  # Extra space
            font = self._get_font('brand_name', config.brand_name_size, False)
            color = config.brand_name_color or optimal_colors.get('secondary', '#CCCCCC')

            draw.text((text_x, current_y), f"by {product.brand_name}", font=font, fill=color)
            current_y += font.getbbox(product.brand_name)[3] - font.getbbox(product.brand_name)[1] + 5

        # Price
        if product.product_price:
            current_y += 8  # Extra space
            font = self._get_font('price', config.price_size, config.price_bold)
            color = config.price_color or optimal_colors.get('accent', '#FFD700')

            draw.text((text_x, current_y), product.product_price, font=font, fill=color)
            current_y += font.getbbox(product.product_price)[3] - font.getbbox(product.product_price)[1] + 5

        return current_y

    def _add_qr_code(
        self,
        overlay: Image.Image,
        url: str,
        config: OverlayConfig
    ) -> None:
        """Add QR code to overlay"""
        try:
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=3,
                border=1,
            )
            qr.add_data(url)
            qr.make(fit=True)

            # Create QR code image
            qr_img = qr.make_image(fill_color="white", back_color="transparent")
            qr_img = qr_img.resize((config.qr_size, config.qr_size), Image.Resampling.LANCZOS)

            # Position QR code
            overlay_width, overlay_height = overlay.size

            if config.qr_position == "bottom-right":
                qr_x = overlay_width - config.qr_size - 15
                qr_y = overlay_height - config.qr_size - 15
            elif config.qr_position == "top-right":
                qr_x = overlay_width - config.qr_size - 15
                qr_y = 15
            elif config.qr_position == "bottom-left":
                qr_x = 15
                qr_y = overlay_height - config.qr_size - 15
            else:  # top-left
                qr_x = 15
                qr_y = 15

            # Paste QR code
            if qr_img.mode != 'RGBA':
                qr_img = qr_img.convert('RGBA')

            overlay.paste(qr_img, (int(qr_x), int(qr_y)), qr_img)

        except Exception as e:
            logger.warning(f"Failed to add QR code: {str(e)}")

    def _wrap_text(self, text: str, font: ImageFont.ImageFont, max_width: int) -> list:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            text_width = bbox[2] - bbox[0]

            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Single word is too long, add it anyway
                    lines.append(word)

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def _load_fonts(self) -> None:
        """Load fonts for text rendering"""
        self.fonts = {
            'default': self._load_font_with_fallback("arial.ttf", 16),
            'bold': self._load_font_with_fallback("arialbd.ttf", 16),
        }

    def _load_font_with_fallback(self, font_name: str, size: int) -> ImageFont.ImageFont:
        """Load font with fallback to default"""
        try:
            # Try to load from assets directory first
            assets_font = Path("assets/fonts") / font_name
            if assets_font.exists():
                return ImageFont.truetype(str(assets_font), size)

            # Try system font
            return ImageFont.truetype(font_name, size)

        except Exception:
            # Fallback to default font
            try:
                return ImageFont.load_default()
            except Exception:
                # Last resort - create a basic font
                return ImageFont.load_default()

    def _get_font(self, text_type: str, size: int, bold: bool = False) -> ImageFont.ImageFont:
        """Get font for specific text type"""
        font_key = 'bold' if bold else 'default'
        base_font = self.fonts.get(font_key, self.fonts['default'])

        # Scale font if different size needed
        if hasattr(base_font, 'font_variant'):
            try:
                return base_font.font_variant(size=size)
            except:
                pass

        # Try to create font with specific size
        try:
            font_name = "arialbd.ttf" if bold else "arial.ttf"
            return self._load_font_with_fallback(font_name, size)
        except:
            return base_font

    def _hex_to_rgba(self, hex_color: str, opacity: float) -> Tuple[int, int, int, int]:
        """Convert hex color to RGBA tuple"""
        hex_color = hex_color.lstrip('#')

        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        else:
            r = g = b = 0

        alpha = int(255 * opacity)
        return (r, g, b, alpha)

    def _create_overlay_config(self, product: ProductData) -> OverlayConfig:
        """Create overlay config from product data"""
        return OverlayConfig(
            enabled=product.add_product_overlay,
            position=product.overlay_position or OverlayPosition.BOTTOM_LEFT,
            **self.config.get("overlay", {})
        )

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "overlay": {
                "enabled": True,
                "background_color": "#000000",
                "background_opacity": 0.8,
                "padding": 20,
                "border_radius": 10,
                "product_name_size": 28,
                "product_name_color": "#FFFFFF",
                "product_name_bold": True,
                "brand_name_size": 18,
                "brand_name_color": "#CCCCCC",
                "price_size": 32,
                "price_color": "#FFD700",
                "price_bold": True,
                "qr_enabled": True,
                "qr_size": 80,
                "qr_position": "bottom-right"
            }
        }