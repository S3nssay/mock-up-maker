# Excel to Seedream Image Generator

A powerful Python application that processes Excel spreadsheets containing product information and generates AI images using ByteDance's Seedream 4.0 API through multiple providers (Kie.ai, AI/ML API, BytePlus, and Nano Banana).

## 🚀 Features

- **Batch Processing**: Generate multiple product images from a single Excel file
- **Multi-Provider Support**: Seedream via Kie.ai, AI/ML API, BytePlus, and Nano Banana
- **Product-Focused**: Specialized for e-commerce and marketing imagery
- **Smart Organization**: Automatically organize outputs by brand
- **Overlay System**: Add product information overlays to generated images
- **Reference Images**: Support up to 3 product images + 1 model image per generation
- **Cost Tracking**: Monitor API costs with detailed breakdown by brand
- **Resume Capability**: Continue interrupted processing

## 📋 Requirements

- Python 3.9+
- API keys for one or more providers:
  - Seedream via Kie.ai
  - Seedream via AI/ML API
  - Seedream via BytePlus
  - Nano Banana

## 🛠️ Installation & Setup

### **Quick Setup (Recommended)**

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API keys using GUI**:
   ```bash
   python settings_launcher.py
   ```

   **OR via CLI**:
   ```bash
   python src/main.py settings
   ```

3. **Test your setup**:
   ```bash
   python src/main.py validate-config
   ```

### **Manual Setup**

1. **Create configuration file**:
   ```bash
   python src/main.py config-manager --create-env
   ```

2. **Edit .env file manually**:
   ```bash
   # Edit .env with your API keys and settings
   SEEDREAM_KIE_API_KEY=your_key_here
   NANO_BANANA_API_KEY=your_key_here
   ```

3. **Validate configuration**:
   ```bash
   python src/main.py validate-config
   ```

## 📊 Excel Format

Your Excel file should contain these columns:

### Required Columns
- `product_name`: Product name for file naming
- `prompt`: Text prompt for image generation
- `brand_name`: Brand/company name

### Optional Columns
- `product_price`: Price (e.g., "$99.99")
- `product_url`: Product page URL
- `product_url_1`: First product image URL
- `product_url_2`: Second product image URL
- `product_url_3`: Third product image URL
- `model_url`: Model/person image URL
- `output_name`: Custom filename override
- `provider`: Specific provider to use
- `max_cost`: Maximum cost per image ($)
- `add_product_overlay`: Add product info overlay (true/false)
- `overlay_position`: Overlay position (bottom-left, top-right, etc.)

### Example Row
```
product_name: "Elegant Black Evening Dress"
prompt: "Professional model wearing elegant black dress in modern office setting"
brand_name: "StyleCorp"
product_price: "$149.99"
product_url: "https://stylecorp.com/dress-001"
product_url_1: "https://example.com/dress1.jpg"
model_url: "https://example.com/model.jpg"
add_product_overlay: true
overlay_position: "bottom-left"
```

## 🎯 Usage

### Basic Commands

**Configure settings (GUI)**:
```bash
python settings_launcher.py
```

**Generate a sample Excel file**:
```bash
python src/main.py create-sample sample_products.xlsx
```

**Validate configuration**:
```bash
python src/main.py validate-config
```

**Process Excel file**:
```bash
python src/main.py process products.xlsx --output-dir ./my_campaign
```

**Dry run (validation only)**:
```bash
python src/main.py process products.xlsx --dry-run
```

**Manage configuration**:
```bash
python src/main.py config-manager --create-env --backup
```

### Advanced Usage

**Process specific rows**:
```bash
python src/main.py process products.xlsx --start-row 5 --end-row 20
```

**Custom output directory**:
```bash
python src/main.py process products.xlsx --output-dir ./campaign_2024
```

## 🏗️ Architecture

The application follows a modular architecture:

```
excel_seedream_generator/
├── src/
│   ├── config/          # Configuration management
│   ├── processors/      # Excel processing
│   ├── api/            # AI provider implementations
│   ├── core/           # Core business logic
│   └── utils/          # Utilities
├── tests/              # Unit tests
├── assets/             # Fonts, templates
├── config/             # Configuration files
└── examples/           # Sample files
```

### Key Components

- **ExcelProcessor**: Loads and validates Excel files
- **AIImageProvider**: Abstract base for all providers
- **OutputManager**: Handles file organization and results
- **ProductOverlay**: Generates advertisement overlays
- **ConfigManager**: Centralized configuration

## 📁 Output Structure

Generated files are organized as:

```
your_output_dir/
├── brands/
│   ├── StyleCorp/
│   │   ├── original/       # Original generated images
│   │   │   └── StyleCorp_Elegant_Black_Dress_20250926.png
│   │   └── ads/           # Images with product overlays
│   │       └── StyleCorp_Elegant_Black_Dress_ad_20250926.png
│   └── TechWear/
├── catalog/
│   ├── results.xlsx       # Complete processing results
│   ├── brand_summary.xlsx # Brand-wise breakdown
│   └── cost_analysis.xlsx # Cost analysis
└── logs/
    └── processing_20250926.log
```

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Primary provider
AI_IMAGE_PROVIDER=seedream_kie

# API Keys
SEEDREAM_KIE_API_KEY=your_key_here
NANO_BANANA_API_KEY=your_key_here

# Generation settings
DEFAULT_RESOLUTION=2K
CONCURRENT_REQUESTS=3
GUIDANCE_SCALE=7.5

# Output settings
OUTPUT_DIR=./product_ads
ORGANIZE_BY_BRAND=true

# Cost control
MAX_COST_PER_IMAGE=0.05
TOTAL_BUDGET_LIMIT=100.0
```

### Provider Fallback
```bash
ENABLE_FALLBACK=true
FALLBACK_ORDER=seedream_kie,nano_banana,seedream_aiml
```

## 🎨 Image Generation Logic

### When `model_url` is provided:
- Uses model image as person reference
- Combines with product images
- Generates scene with model wearing/using products

### When `model_url` is empty:
- Enhances prompt to request model generation
- Auto-generates appropriate model for products
- Creates professional product photography

## 💰 Cost Management

- **Per-image limits**: Set `max_cost` in Excel or globally
- **Budget tracking**: Monitor total spend across brands
- **Cost estimation**: Preview costs before generation
- **Brand breakdown**: Detailed cost analysis per brand

## 🔧 Provider Configuration

### Kie.ai (Seedream)
```python
SEEDREAM_KIE_API_KEY=your_kie_api_key
# Endpoint: https://api.kie.ai/v1/seedream
# Features: Multi-reference, 4K, $0.0175/image
```

### Nano Banana
```python
NANO_BANANA_API_KEY=your_nano_banana_key
NANO_BANANA_ENDPOINT=https://api.nano-banana.com/v1
# Features: Multi-reference, 2K, $0.02/image
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## 📈 Monitoring & Logs

- **Structured logging**: JSON logs with context
- **Progress tracking**: Real-time progress bars
- **Error handling**: Detailed error messages
- **Performance metrics**: Processing time tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs via GitHub Issues
- **Documentation**: Full docs at [project-docs-url]
- **API Support**: Contact provider support for API issues

## 🔮 Roadmap

- [ ] Web interface for easy file upload
- [ ] Real-time progress tracking via websockets
- [ ] Advanced overlay templates
- [ ] Batch optimization algorithms
- [ ] Integration with cloud storage
- [ ] Webhook notifications
- [ ] A/B testing capabilities

---

**Built with ❤️ for e-commerce and marketing teams who need high-quality product imagery at scale.**