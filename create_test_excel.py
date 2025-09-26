#!/usr/bin/env python3
"""
Create comprehensive test Excel files for the application
"""

import pandas as pd
from pathlib import Path


def create_comprehensive_test():
    """Create comprehensive test Excel file"""

    data = {
        "product_name": [
            "Elegant Black Evening Dress",
            "Summer Beach Sandals",
            "Professional Navy Blazer",
            "Luxury Gold Watch",
            "Casual Denim Jacket",
            "Sport Running Shoes",
            "Designer Handbag",
            "Wireless Headphones",
            "Organic Coffee Beans",
            "Smart Fitness Tracker"
        ],
        "prompt": [
            "Professional model wearing elegant black dress in modern office setting with warm lighting",
            "Model showcasing comfortable beach sandals on sandy beach with ocean waves in background",
            "Business professional wearing navy blazer in corporate boardroom setting",
            "Elegant gold watch displayed on marble surface with dramatic lighting",
            "Young person wearing casual denim jacket in urban street setting",
            "Athletic model wearing running shoes in gym environment with fitness equipment",
            "Model carrying designer handbag in upscale shopping district",
            "Person using wireless headphones while working in modern office space",
            "Coffee beans in rustic setting with steaming coffee cup and natural lighting",
            "Active person wearing fitness tracker during outdoor workout session"
        ],
        "brand_name": [
            "StyleCorp",
            "BeachWear Co",
            "BusinessPro",
            "TimeCorp",
            "UrbanWear",
            "AthletePro",
            "LuxBags",
            "TechSound",
            "BrewCorp",
            "FitTech"
        ],
        "product_price": [
            "$149.99",
            "$49.99",
            "$299.99",
            "$999.99",
            "$89.99",
            "$129.99",
            "$449.99",
            "$199.99",
            "$24.99",
            "$149.99"
        ],
        "product_url": [
            "https://stylecorp.com/dress-001",
            "https://beachwear.com/sandals-002",
            "https://businesspro.com/blazer-003",
            "https://timecorp.com/watch-004",
            "https://urbanwear.com/jacket-005",
            "https://athletepro.com/shoes-006",
            "https://luxbags.com/bag-007",
            "https://techsound.com/headphones-008",
            "https://brewcorp.com/coffee-009",
            "https://fittech.com/tracker-010"
        ],
        "product_url_1": [
            "https://images.unsplash.com/photo-1539109136881-3be0616acf4b",
            "https://images.unsplash.com/photo-1543163521-1bf539c55dd2",
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d",
            "https://images.unsplash.com/photo-1523275335684-37898b6baf30",
            "https://images.unsplash.com/photo-1551698618-1dfe5d97d256",
            "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
            "https://images.unsplash.com/photo-1553062407-98eeb64c6a62",
            "https://images.unsplash.com/photo-1505740420928-5e560c06d30e",
            "https://images.unsplash.com/photo-1447933601403-0c6688de566e",
            "https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6"
        ],
        "product_url_2": [
            "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1",
            "",
            "https://images.unsplash.com/photo-1594938298603-c8148c4dae35",
            "",
            "",
            "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa",
            "",
            "",
            "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085",
            ""
        ],
        "product_url_3": [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            ""
        ],
        "model_url": [
            "https://images.unsplash.com/photo-1488426862026-3ee34a7d66df",
            "",
            "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e",
            "",
            "",
            "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b",
            "",
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d",
            "",
            "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b"
        ],
        "output_name": [
            "",
            "",
            "custom_blazer_shot",
            "",
            "",
            "",
            "",
            "headphones_lifestyle",
            "coffee_beans_premium",
            ""
        ],
        "provider": [
            "seedream_kie",
            "nano_banana",
            "seedream_kie",
            "seedream_aiml",
            "",
            "nano_banana",
            "seedream_byteplus",
            "",
            "seedream_kie",
            ""
        ],
        "max_cost": [
            0.05,
            0.03,
            "",
            0.04,
            0.02,
            "",
            0.06,
            0.03,
            "",
            0.04
        ],
        "add_product_overlay": [
            True,
            True,
            True,
            False,
            True,
            True,
            True,
            False,
            True,
            True
        ],
        "overlay_position": [
            "bottom-left",
            "bottom-right",
            "top-right",
            "",
            "center-bottom",
            "bottom-left",
            "top-left",
            "",
            "bottom-right",
            "center-bottom"
        ]
    }

    df = pd.DataFrame(data)

    # Create examples directory
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)

    # Save to Excel
    excel_path = examples_dir / "comprehensive_test.xlsx"
    df.to_excel(excel_path, index=False, engine='openpyxl')

    print(f"Created comprehensive test file: {excel_path}")
    return excel_path


def create_simple_test():
    """Create simple test Excel file with just 3 products"""

    data = {
        "product_name": [
            "Classic White T-Shirt",
            "Blue Jeans",
            "Red Sneakers"
        ],
        "prompt": [
            "Model wearing classic white t-shirt in casual setting",
            "Person wearing blue jeans in outdoor park setting",
            "Athletic model showcasing red sneakers during workout"
        ],
        "brand_name": [
            "BasicWear",
            "DenimCo",
            "SneakerBrand"
        ],
        "product_price": [
            "$19.99",
            "$79.99",
            "$99.99"
        ],
        "product_url": [
            "https://basicwear.com/tshirt-001",
            "https://denimco.com/jeans-002",
            "https://sneakerbrand.com/shoes-003"
        ],
        "product_url_1": [
            "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab",
            "https://images.unsplash.com/photo-1542272604-787c3835535d",
            "https://images.unsplash.com/photo-1549298916-b41d501d3772"
        ],
        "product_url_2": ["", "", ""],
        "product_url_3": ["", "", ""],
        "model_url": [
            "",
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d",
            ""
        ],
        "output_name": ["", "", ""],
        "provider": ["", "seedream_kie", "nano_banana"],
        "max_cost": ["", "", ""],
        "add_product_overlay": [True, True, False],
        "overlay_position": ["bottom-left", "bottom-right", ""]
    }

    df = pd.DataFrame(data)

    # Create examples directory
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)

    # Save to Excel
    excel_path = examples_dir / "simple_test.xlsx"
    df.to_excel(excel_path, index=False, engine='openpyxl')

    print(f"Created simple test file: {excel_path}")
    return excel_path


def create_brand_focused_test():
    """Create test file focused on specific brands"""

    data = {
        "product_name": [
            "Nike Air Max 270",
            "Nike Dri-FIT T-Shirt",
            "Adidas Ultraboost 22",
            "Adidas Trefoil Hoodie",
            "Apple AirPods Pro",
            "Apple iPhone Case"
        ],
        "prompt": [
            "Athletic model wearing Nike Air Max 270 during outdoor run",
            "Fitness enthusiast in Nike Dri-FIT t-shirt at gym",
            "Runner wearing Adidas Ultraboost shoes on city street",
            "Casual model in Adidas Trefoil hoodie in urban setting",
            "Professional using Apple AirPods Pro in modern office",
            "Person holding iPhone with premium case in lifestyle setting"
        ],
        "brand_name": [
            "Nike",
            "Nike",
            "Adidas",
            "Adidas",
            "Apple",
            "Apple"
        ],
        "product_price": [
            "$150.00",
            "$35.00",
            "$180.00",
            "$70.00",
            "$249.00",
            "$49.00"
        ],
        "product_url": [
            "https://nike.com/air-max-270",
            "https://nike.com/dri-fit-tshirt",
            "https://adidas.com/ultraboost-22",
            "https://adidas.com/trefoil-hoodie",
            "https://apple.com/airpods-pro",
            "https://apple.com/iphone-case"
        ],
        "product_url_1": [
            "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
            "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab",
            "https://images.unsplash.com/photo-1549298916-b41d501d3772",
            "https://images.unsplash.com/photo-1556821840-3a9fbc86339e",
            "https://images.unsplash.com/photo-1505740420928-5e560c06d30e",
            "https://images.unsplash.com/photo-1512499617640-c74ae3a79d37"
        ],
        "product_url_2": ["", "", "", "", "", ""],
        "product_url_3": ["", "", "", "", "", ""],
        "model_url": [
            "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b",
            "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b",
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d",
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d",
            "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e",
            "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e"
        ],
        "output_name": ["", "", "", "", "", ""],
        "provider": ["", "", "", "", "", ""],
        "max_cost": ["", "", "", "", "", ""],
        "add_product_overlay": [True, True, True, True, True, True],
        "overlay_position": ["bottom-left", "bottom-left", "bottom-left", "bottom-left", "bottom-left", "bottom-left"]
    }

    df = pd.DataFrame(data)

    # Create examples directory
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)

    # Save to Excel
    excel_path = examples_dir / "brand_focused_test.xlsx"
    df.to_excel(excel_path, index=False, engine='openpyxl')

    print(f"Created brand-focused test file: {excel_path}")
    return excel_path


if __name__ == "__main__":
    print("Creating comprehensive test Excel files...")

    create_simple_test()
    create_comprehensive_test()
    create_brand_focused_test()

    print("\nAll test files created in examples/ directory!")
    print("\nUsage examples:")
    print("python src/main.py process examples/simple_test.xlsx --dry-run")
    print("python src/main.py process examples/comprehensive_test.xlsx --output-dir ./test_output --enable-overlays")
    print("python src/main.py process examples/brand_focused_test.xlsx --concurrent 5 --provider nano_banana")