import pandas as pd
from pathlib import Path
from typing import List, Optional, Dict, Any
import structlog
from core.models import ProductData, ImageProvider, OverlayPosition


logger = structlog.get_logger()


class ExcelProcessor:
    """Process Excel files containing product information"""

    # Required columns
    REQUIRED_COLUMNS = ["product_name", "prompt", "brand_name"]

    # Optional columns with defaults
    OPTIONAL_COLUMNS = {
        "product_price": None,
        "product_url": None,
        "product_url_1": None,
        "product_url_2": None,
        "product_url_3": None,
        "model_url": None,
        "output_name": None,
        "provider": None,
        "max_cost": None,
        "add_product_overlay": False,
        "overlay_position": "bottom-left"
    }

    def __init__(self, file_path: str):
        """Initialize with Excel file path"""
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")

        self.df = None
        self.products: List[ProductData] = []
        self.errors: List[str] = []

    def load_and_validate(self) -> bool:
        """Load Excel file and validate structure"""
        try:
            # Load Excel file
            logger.info(f"Loading Excel file: {self.file_path}")
            self.df = pd.read_excel(self.file_path)

            # Check for required columns
            missing_columns = []
            for col in self.REQUIRED_COLUMNS:
                if col not in self.df.columns:
                    missing_columns.append(col)

            if missing_columns:
                error_msg = f"Missing required columns: {', '.join(missing_columns)}"
                self.errors.append(error_msg)
                logger.error(error_msg)
                return False

            # Add optional columns with defaults if not present
            for col, default_value in self.OPTIONAL_COLUMNS.items():
                if col not in self.df.columns:
                    self.df[col] = default_value
                    logger.debug(f"Added column '{col}' with default value: {default_value}")

            # Clean up NaN values
            self.df = self.df.fillna("")

            # Convert boolean columns
            if "add_product_overlay" in self.df.columns:
                self.df["add_product_overlay"] = self.df["add_product_overlay"].astype(bool)

            logger.info(f"Successfully loaded {len(self.df)} rows from Excel")
            return True

        except Exception as e:
            error_msg = f"Error loading Excel file: {str(e)}"
            self.errors.append(error_msg)
            logger.error(error_msg)
            return False

    def process_rows(self, start_row: int = 0, end_row: Optional[int] = None) -> List[ProductData]:
        """Process Excel rows into ProductData objects"""
        if self.df is None:
            raise ValueError("Excel file not loaded. Call load_and_validate() first.")

        products = []
        end_idx = end_row if end_row is not None else len(self.df)

        for idx in range(start_row, min(end_idx, len(self.df))):
            try:
                row = self.df.iloc[idx]
                product = self._row_to_product(row, idx + 1)  # +1 for 1-based row numbering
                if product:
                    products.append(product)
                    logger.debug(f"Processed row {idx + 1}: {product.product_name}")

            except Exception as e:
                error_msg = f"Error processing row {idx + 1}: {str(e)}"
                self.errors.append(error_msg)
                logger.error(error_msg)
                continue

        self.products = products
        logger.info(f"Successfully processed {len(products)} products")
        return products

    def _row_to_product(self, row: pd.Series, row_number: int) -> Optional[ProductData]:
        """Convert DataFrame row to ProductData object"""
        try:
            # Handle provider enum
            provider = None
            if row.get("provider"):
                try:
                    provider = ImageProvider(str(row["provider"]).strip().lower())
                except ValueError:
                    logger.warning(f"Invalid provider '{row['provider']}' in row {row_number}")

            # Handle overlay position enum
            overlay_position = OverlayPosition.BOTTOM_LEFT
            if row.get("overlay_position"):
                try:
                    overlay_position = OverlayPosition(str(row["overlay_position"]).strip().lower())
                except ValueError:
                    logger.warning(f"Invalid overlay position '{row['overlay_position']}' in row {row_number}")

            # Handle max_cost
            max_cost = None
            if row.get("max_cost"):
                try:
                    max_cost = float(row["max_cost"])
                except (ValueError, TypeError):
                    logger.warning(f"Invalid max_cost '{row['max_cost']}' in row {row_number}")

            # Create ProductData
            product = ProductData(
                row_number=row_number,
                product_name=str(row["product_name"]).strip(),
                prompt=str(row["prompt"]).strip(),
                brand_name=str(row["brand_name"]).strip(),
                product_price=str(row.get("product_price", "")).strip() or None,
                product_url=str(row.get("product_url", "")).strip() or None,
                product_url_1=str(row.get("product_url_1", "")).strip() or None,
                product_url_2=str(row.get("product_url_2", "")).strip() or None,
                product_url_3=str(row.get("product_url_3", "")).strip() or None,
                model_url=str(row.get("model_url", "")).strip() or None,
                output_name=str(row.get("output_name", "")).strip() or None,
                provider=provider,
                max_cost=max_cost,
                add_product_overlay=bool(row.get("add_product_overlay", False)),
                overlay_position=overlay_position
            )

            return product

        except Exception as e:
            logger.error(f"Failed to create ProductData from row {row_number}: {str(e)}")
            return None

    def validate_urls(self, products: Optional[List[ProductData]] = None) -> Dict[str, List[str]]:
        """Validate URLs in product data"""
        products_to_validate = products or self.products
        validation_results = {
            "valid": [],
            "invalid": [],
            "warnings": []
        }

        for product in products_to_validate:
            # Check all URLs
            urls_to_check = {
                "product_url": product.product_url,
                "product_url_1": product.product_url_1,
                "product_url_2": product.product_url_2,
                "product_url_3": product.product_url_3,
                "model_url": product.model_url
            }

            for field_name, url in urls_to_check.items():
                if url:
                    if not url.startswith(("http://", "https://")):
                        validation_results["invalid"].append(
                            f"Row {product.row_number} - {field_name}: Invalid URL format"
                        )
                    else:
                        validation_results["valid"].append(
                            f"Row {product.row_number} - {field_name}: {url}"
                        )

            # Check if product has any reference images
            if not product.get_reference_images():
                validation_results["warnings"].append(
                    f"Row {product.row_number} - No reference images provided"
                )

        return validation_results

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the loaded data"""
        if not self.products:
            return {}

        brands = {}
        providers = {}
        overlay_count = 0
        model_generation_needed = 0

        for product in self.products:
            # Count by brand
            brands[product.brand_name] = brands.get(product.brand_name, 0) + 1

            # Count by provider
            if product.provider:
                provider_name = product.provider.value
                providers[provider_name] = providers.get(provider_name, 0) + 1

            # Count overlays
            if product.add_product_overlay:
                overlay_count += 1

            # Count model generation needs
            if product.needs_model_generation():
                model_generation_needed += 1

        return {
            "total_products": len(self.products),
            "brands": brands,
            "providers": providers,
            "overlay_count": overlay_count,
            "model_generation_needed": model_generation_needed,
            "errors": len(self.errors)
        }

    def export_validation_report(self, output_path: str) -> None:
        """Export validation report to file"""
        report_path = Path(output_path)
        stats = self.get_statistics()

        with open(report_path, "w") as f:
            f.write("Excel Processing Report\n")
            f.write("=" * 50 + "\n\n")

            f.write(f"File: {self.file_path}\n")
            f.write(f"Total Products: {stats.get('total_products', 0)}\n\n")

            f.write("Brands:\n")
            for brand, count in stats.get("brands", {}).items():
                f.write(f"  - {brand}: {count} products\n")

            f.write("\nProviders Requested:\n")
            for provider, count in stats.get("providers", {}).items():
                f.write(f"  - {provider}: {count} products\n")

            f.write(f"\nProducts with overlay: {stats.get('overlay_count', 0)}\n")
            f.write(f"Products needing model generation: {stats.get('model_generation_needed', 0)}\n")

            if self.errors:
                f.write("\nErrors:\n")
                for error in self.errors:
                    f.write(f"  - {error}\n")

        logger.info(f"Validation report exported to: {report_path}")

    def create_sample_excel(self, output_path: str) -> None:
        """Create a sample Excel file with proper structure"""
        sample_data = {
            "product_name": ["Elegant Black Evening Dress", "Summer Beach Sandals", "Professional Blazer"],
            "prompt": [
                "Professional model wearing elegant black dress in modern office",
                "Model showcasing comfortable beach sandals on sandy beach",
                "Business professional wearing navy blazer in corporate setting"
            ],
            "brand_name": ["StyleCorp", "BeachWear Co", "BusinessPro"],
            "product_price": ["$149.99", "$49.99", "$299.99"],
            "product_url": [
                "https://stylecorp.com/dress-001",
                "https://beachwear.com/sandals-002",
                "https://businesspro.com/blazer-003"
            ],
            "product_url_1": [
                "https://example.com/dress1.jpg",
                "https://example.com/sandals1.jpg",
                "https://example.com/blazer1.jpg"
            ],
            "product_url_2": ["", "https://example.com/sandals2.jpg", ""],
            "product_url_3": ["", "", ""],
            "model_url": ["https://example.com/model1.jpg", "", ""],
            "output_name": ["", "beach_sandals_summer", ""],
            "provider": ["seedream_kie", "", "nano_banana"],
            "max_cost": [0.05, "", 0.03],
            "add_product_overlay": [True, True, False],
            "overlay_position": ["bottom-left", "bottom-right", ""]
        }

        df = pd.DataFrame(sample_data)
        df.to_excel(output_path, index=False)
        logger.info(f"Sample Excel file created: {output_path}")