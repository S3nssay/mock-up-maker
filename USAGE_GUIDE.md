# 🚀 Complete Usage Guide

## 🎯 **COMPLETED FEATURES**

The Excel to Seedream Image Generator is now **FULLY FUNCTIONAL** with all major components implemented:

### ✅ **Core Components**
- **Multi-Provider Support**: Seedream (Kie.ai, AI/ML API, BytePlus) + Nano Banana
- **Advanced Queue Management**: Concurrent processing with retry logic
- **Product Overlay Engine**: Professional advertisement overlays with QR codes
- **Brand Organization**: Automatic file organization by brand
- **Cost Tracking**: Real-time cost monitoring with budget controls
- **Resume Capability**: Checkpoint system for interrupted processing

### ✅ **Advanced Features**
- **Async Processing**: High-performance concurrent image generation
- **Smart Provider Fallback**: Automatic failover between providers
- **Overlay Customization**: Multiple positions, styles, and brand themes
- **Progress Tracking**: Real-time updates with ETAs and statistics
- **Comprehensive Validation**: Excel structure and URL validation
- **Error Handling**: Robust error recovery with detailed reporting

---

## 🛠️ **Setup Instructions**

### 1. **Installation**
```bash
cd excel_seedream_generator
pip install -r requirements.txt
```

### 2. **Configuration**
Copy and edit the environment file:
```bash
cp .env.template .env
# Edit .env with your API keys
```

### 3. **API Keys Setup**
Add your API keys to `.env`:
```bash
# Seedream Providers
SEEDREAM_KIE_API_KEY=your_kie_api_key_here
SEEDREAM_AIML_API_KEY=your_aiml_api_key_here
SEEDREAM_BYTEPLUS_API_KEY=your_byteplus_api_key_here

# Alternative Provider
NANO_BANANA_API_KEY=your_nano_banana_key_here

# Primary Provider
AI_IMAGE_PROVIDER=seedream_kie
```

---

## 📊 **Excel Format Requirements**

### Required Columns:
- `product_name`: Product name for file naming
- `prompt`: Text prompt for image generation
- `brand_name`: Brand/company name

### Optional Columns:
- `product_price`: Price display (e.g., "$99.99")
- `product_url`: Product page URL
- `product_url_1`: First product image URL
- `product_url_2`: Second product image URL
- `product_url_3`: Third product image URL
- `model_url`: Model/person image URL
- `output_name`: Custom filename override
- `provider`: Specific provider to use
- `max_cost`: Maximum cost per image ($)
- `add_product_overlay`: Add product overlay (true/false)
- `overlay_position`: Position (bottom-left, top-right, etc.)

---

## 🎮 **Command Usage**

### **Basic Commands**

#### **Create Sample Excel**
```bash
python src/main.py create-sample examples/my_products.xlsx
```

#### **Validate Configuration**
```bash
python src/main.py validate-config
```

#### **Validate Excel File**
```bash
python src/main.py validate-excel examples/comprehensive_test.xlsx
```

#### **Test Providers**
```bash
python src/main.py test-providers
python src/main.py test-providers --provider nano_banana
```

### **Image Generation Commands**

#### **Basic Generation**
```bash
python src/main.py process examples/simple_test.xlsx
```

#### **With Custom Output Directory**
```bash
python src/main.py process examples/comprehensive_test.xlsx \
  --output-dir ./my_campaign_2024
```

#### **Enable Product Overlays**
```bash
python src/main.py process examples/comprehensive_test.xlsx \
  --enable-overlays \
  --output-dir ./campaign_with_ads
```

#### **Specific Provider**
```bash
python src/main.py process examples/comprehensive_test.xlsx \
  --provider nano_banana \
  --concurrent 5
```

#### **Advanced Usage**
```bash
python src/main.py process examples/comprehensive_test.xlsx \
  --output-dir ./premium_campaign \
  --enable-overlays \
  --concurrent 5 \
  --provider seedream_kie \
  --start-row 2 \
  --end-row 8
```

#### **Dry Run (Validation Only)**
```bash
python src/main.py process examples/comprehensive_test.xlsx --dry-run
```

---

## 📁 **Output Structure**

Generated files are organized as:
```
your_output_dir/
├── brands/
│   ├── Nike/
│   │   ├── original/           # Generated images
│   │   │   ├── Nike_Air_Max_270_20250926.png
│   │   │   └── Nike_Dri_FIT_TShirt_20250926.png
│   │   └── ads/               # Images with overlays
│   │       ├── Nike_Air_Max_270_ad_20250926.png
│   │       └── Nike_Dri_FIT_TShirt_ad_20250926.png
│   ├── Adidas/
│   └── Apple/
├── catalog/
│   ├── results.xlsx           # Complete processing results
│   ├── brand_summary.xlsx     # Brand-wise breakdown
│   └── cost_analysis.xlsx     # Cost analysis
└── logs/
    └── processing_20250926.log
```

---

## 🎨 **Product Overlay Features**

### **Overlay Positions**
- `bottom-left`: Bottom left corner (default)
- `bottom-right`: Bottom right corner
- `top-left`: Top left corner
- `top-right`: Top right corner
- `center-bottom`: Center bottom
- `center-top`: Center top

### **Included Information**
- Product name (large, bold)
- Brand name (medium)
- Price (large, gold color)
- QR code linking to product URL
- Smart background color detection

### **Brand Styling**
Automatic styling based on brand:
- **Nike/Adidas**: Modern, sporty theme
- **Apple**: Minimal, clean theme
- **Luxury Brands**: Elegant, sophisticated theme
- **Default**: Professional theme

---

## 💰 **Cost Management**

### **Per-Image Cost Limits**
Set in Excel `max_cost` column:
```excel
max_cost: 0.05  # Maximum $0.05 per image
```

### **Global Budget Control**
Set in `.env`:
```bash
MAX_COST_PER_IMAGE=0.05
TOTAL_BUDGET_LIMIT=100.0
```

### **Provider Costs** (Approximate)
- **Seedream (Kie.ai)**: $0.0175 per image
- **Nano Banana**: $0.02 per image
- **Seedream (AI/ML API)**: $0.025 per image
- **Seedream (BytePlus)**: $0.03 per image

---

## ⚡ **Performance Optimization**

### **Concurrent Processing**
```bash
--concurrent 5  # Process 5 images simultaneously
```

### **Provider Selection Strategy**
1. Use specified provider in Excel `provider` column
2. Fallback to configured alternatives
3. Cost-based selection if budget constraints
4. Load balancing across available providers

### **Rate Limiting**
- **Automatic**: Respects each provider's rate limits
- **Smart Queuing**: Optimal request scheduling
- **Retry Logic**: Exponential backoff on failures

---

## 🧪 **Testing the Application**

### **Test Files Created**
1. **`simple_test.xlsx`**: 3 products for basic testing
2. **`comprehensive_test.xlsx`**: 10 products with all features
3. **`brand_focused_test.xlsx`**: Nike, Adidas, Apple products

### **Test Commands**
```bash
# Basic functionality test
python src/main.py process examples/simple_test.xlsx --dry-run

# Full feature test
python src/main.py process examples/comprehensive_test.xlsx \
  --output-dir ./test_output --enable-overlays

# Provider comparison test
python src/main.py process examples/brand_focused_test.xlsx \
  --provider nano_banana --concurrent 3
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **"No API providers configured"**
- Check API keys in `.env` file
- Run `python src/main.py validate-config`

#### **"Excel validation failed"**
- Ensure required columns exist: `product_name`, `prompt`, `brand_name`
- Run `python src/main.py validate-excel your_file.xlsx`

#### **Rate limiting errors**
- Reduce `--concurrent` parameter
- Check provider-specific rate limits

#### **Overlay generation fails**
- Ensure PIL/Pillow is properly installed
- Check if original image was generated successfully

### **Debug Mode**
Set environment variable for detailed logging:
```bash
export LOG_LEVEL=DEBUG
python src/main.py process examples/simple_test.xlsx
```

---

## 📈 **Production Recommendations**

### **For Large Batches (100+ products)**
1. Use `--concurrent 3` (balance speed vs stability)
2. Enable checkpoint system (automatic)
3. Monitor costs with budget limits
4. Use provider fallback for reliability

### **For High-Quality Outputs**
1. Use Seedream providers for best results
2. Enable product overlays for professional ads
3. Provide high-quality reference images
4. Use descriptive, detailed prompts

### **For Cost Optimization**
1. Set `max_cost` limits per product
2. Use Nano Banana for budget-friendly option
3. Monitor real-time costs during processing
4. Use batch processing for volume discounts

---

## 🎯 **Success Metrics**

The application is designed to achieve:
- **95%+ Success Rate**: For valid inputs
- **Sub-10 minute processing**: For 100 products
- **Cost Transparency**: Real-time cost tracking
- **Professional Quality**: Publication-ready images
- **Brand Consistency**: Automatic brand styling

---

## 🆘 **Support**

### **Getting API Keys**
- **Kie.ai**: https://kie.ai → Developer Dashboard
- **Nano Banana**: https://nano-banana.com → API Access
- **AI/ML API**: https://aimlapi.com → API Keys
- **BytePlus**: https://www.byteplus.com → AI Services

### **Documentation**
- Full documentation in `README.md`
- Code examples in `examples/` directory
- Configuration templates in `config/` directory

---

**🎉 The Excel to Seedream Image Generator is now COMPLETE and ready for production use!**