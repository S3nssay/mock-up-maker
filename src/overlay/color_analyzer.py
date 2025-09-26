import numpy as np
from PIL import Image
from typing import Tuple, Dict
import colorsys


class ColorAnalyzer:
    """Analyze image colors to determine optimal text colors for overlays"""

    def get_dominant_color(self, image: Image.Image) -> Tuple[int, int, int]:
        """Get the dominant color from an image"""
        # Resize image for faster processing
        img = image.resize((150, 150))
        img_array = np.array(img)

        # Reshape to 1D array of pixels
        pixels = img_array.reshape(-1, 3)

        # Use k-means clustering to find dominant color
        # For simplicity, we'll use the mean color as approximation
        dominant_color = np.mean(pixels, axis=0).astype(int)

        return tuple(dominant_color)

    def get_optimal_text_colors(self, background_color: Tuple[int, int, int]) -> Dict[str, str]:
        """Get optimal text colors based on background color"""
        r, g, b = background_color

        # Calculate luminance
        luminance = self._calculate_luminance(r, g, b)

        if luminance > 128:  # Light background
            return {
                'primary': '#000000',      # Black for primary text
                'secondary': '#333333',    # Dark gray for secondary
                'accent': '#FF4444',       # Red for accent (price)
            }
        else:  # Dark background
            return {
                'primary': '#FFFFFF',      # White for primary text
                'secondary': '#CCCCCC',    # Light gray for secondary
                'accent': '#FFD700',       # Gold for accent (price)
            }

    def _calculate_luminance(self, r: int, g: int, b: int) -> float:
        """Calculate perceived luminance of a color"""
        # Convert to 0-1 range
        r_norm = r / 255.0
        g_norm = g / 255.0
        b_norm = b / 255.0

        # Apply gamma correction
        def gamma_correct(c):
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        r_linear = gamma_correct(r_norm)
        g_linear = gamma_correct(g_norm)
        b_linear = gamma_correct(b_norm)

        # Calculate luminance using ITU-R BT.709 coefficients
        luminance = 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear

        return luminance * 255

    def get_contrast_ratio(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
        """Calculate contrast ratio between two colors"""
        lum1 = self._calculate_luminance(*color1)
        lum2 = self._calculate_luminance(*color2)

        # Ensure lum1 is the lighter color
        if lum1 < lum2:
            lum1, lum2 = lum2, lum1

        return (lum1 + 0.05) / (lum2 + 0.05)

    def is_high_contrast(self, background: Tuple[int, int, int], text: Tuple[int, int, int]) -> bool:
        """Check if text has good contrast against background"""
        contrast_ratio = self.get_contrast_ratio(background, text)
        return contrast_ratio >= 4.5  # WCAG AA standard

    def adjust_color_for_contrast(
        self,
        text_color: Tuple[int, int, int],
        background: Tuple[int, int, int],
        target_contrast: float = 4.5
    ) -> Tuple[int, int, int]:
        """Adjust text color to meet contrast requirements"""
        current_contrast = self.get_contrast_ratio(text_color, background)

        if current_contrast >= target_contrast:
            return text_color

        # Convert to HSV for easier manipulation
        h, s, v = colorsys.rgb_to_hsv(text_color[0]/255, text_color[1]/255, text_color[2]/255)

        # Adjust brightness
        bg_luminance = self._calculate_luminance(*background)

        if bg_luminance > 128:  # Light background, make text darker
            v = max(0, v - 0.3)
        else:  # Dark background, make text lighter
            v = min(1, v + 0.3)

        # Convert back to RGB
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        adjusted_color = (int(r * 255), int(g * 255), int(b * 255))

        return adjusted_color

    def get_complementary_color(self, color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Get complementary color for accent purposes"""
        r, g, b = color

        # Convert to HSV
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

        # Get complementary hue (180 degrees opposite)
        comp_h = (h + 0.5) % 1.0

        # Adjust saturation and value for better visibility
        comp_s = min(1.0, s + 0.2)
        comp_v = max(0.3, min(0.9, 1.0 - v))

        # Convert back to RGB
        comp_r, comp_g, comp_b = colorsys.hsv_to_rgb(comp_h, comp_s, comp_v)

        return (int(comp_r * 255), int(comp_g * 255), int(comp_b * 255))

    def analyze_image_regions(self, image: Image.Image, num_regions: int = 9) -> Dict[str, Tuple[int, int, int]]:
        """Analyze different regions of an image for color information"""
        width, height = image.size
        regions = {}

        # Define region grid
        region_width = width // 3
        region_height = height // 3

        region_names = [
            'top-left', 'top-center', 'top-right',
            'middle-left', 'middle-center', 'middle-right',
            'bottom-left', 'bottom-center', 'bottom-right'
        ]

        for i, region_name in enumerate(region_names):
            row = i // 3
            col = i % 3

            x1 = col * region_width
            y1 = row * region_height
            x2 = min(x1 + region_width, width)
            y2 = min(y1 + region_height, height)

            # Crop region and get dominant color
            region_img = image.crop((x1, y1, x2, y2))
            regions[region_name] = self.get_dominant_color(region_img)

        return regions