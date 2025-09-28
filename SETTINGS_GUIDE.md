# 🔧 **Settings GUI - Complete Guide**

## ✅ **FEATURE COMPLETED!**

Mock Up Maker now includes a **comprehensive settings GUI** that makes API key management and configuration effortless!

---

## 🚀 **Quick Start**

### **Option 1: Standalone Launcher (Easiest)**
```bash
python settings_launcher.py
```

### **Option 2: Via Main CLI**
```bash
python src/main.py settings
```

### **Option 3: Configuration Manager**
```bash
python src/main.py config-manager --create-env
```

---

## 🎨 **Settings GUI Features**

### **📱 Modern Interface**
- **Tabbed Layout**: Organized settings across multiple tabs
- **Rich UI**: Professional interface with tooltips and validation
- **Real-time Validation**: Instant feedback on settings
- **Progress Tracking**: Visual indicators for testing and saving

### **🔑 API Keys Tab**
- **All Providers Supported**:
  - Seedream via Kie.ai (recommended)
  - Nano Banana (budget-friendly)
  - Seedream via AI/ML API
  - Seedream via BytePlus
- **Secure Input**: Password fields with show/hide toggle
- **Individual Testing**: Test each provider independently
- **Cost Information**: Shows cost per image for each provider
- **Quick Links**: Direct links to sign up pages

### **🎨 Generation Tab**
- **Primary Provider Selection**: Choose your preferred provider
- **Fallback Configuration**: Enable automatic provider switching
- **Concurrent Requests**: Slider for performance tuning
- **Image Settings**: Resolution and aspect ratio selection
- **Advanced Options**: Guidance scale and inference steps

### **📁 Output Tab**
- **Directory Browser**: Easy output directory selection
- **Organization Options**: Brand-based file organization
- **Format Selection**: Choose image format (PNG, JPEG, WEBP)
- **Cost Control**: Budget limits and per-image costs

### **🎨 Overlays Tab**
- **Overlay Configuration**: Enable/disable product overlays
- **Position Selection**: Choose overlay placement
- **QR Code Settings**: Size and inclusion options
- **Style Controls**: Opacity and appearance settings

---

## 💾 **Configuration Management**

### **Automatic .env Management**
- **Smart Backup**: Automatic backup before changes
- **Template Integration**: Uses .env.template as base
- **Comment Preservation**: Maintains helpful comments
- **Format Validation**: Ensures proper .env format

### **Settings Validation**
- **Real-time Checks**: Validate as you type
- **API Key Format**: Verify key formats for each provider
- **Numeric Ranges**: Ensure values are within safe limits
- **Path Validation**: Check directory permissions

### **Testing & Verification**
- **Individual Provider Tests**: Test each API key separately
- **Bulk Testing**: Test all configured providers
- **Connection Verification**: Check API endpoint accessibility
- **Error Reporting**: Detailed error messages and solutions

---

## 🔧 **Command Reference**

### **Settings Commands**
```bash
# Open settings GUI (standalone)
python settings_launcher.py

# Open settings GUI (via CLI)
python src/main.py settings

# Create .env from template
python src/main.py config-manager --create-env

# Create backup of current .env
python src/main.py config-manager --backup

# Validate current configuration
python src/main.py validate-config

# Test API providers
python src/main.py test-providers
```

---

## 📊 **What Gets Configured**

### **API Settings**
```bash
# Primary provider
AI_IMAGE_PROVIDER=seedream_kie

# API keys for all providers
SEEDREAM_KIE_API_KEY=your_key_here
NANO_BANANA_API_KEY=your_key_here
SEEDREAM_AIML_API_KEY=your_key_here
SEEDREAM_BYTEPLUS_API_KEY=your_key_here

# Fallback configuration
ENABLE_FALLBACK=true
FALLBACK_ORDER=seedream_kie,nano_banana
```

### **Generation Settings**
```bash
# Performance tuning
CONCURRENT_REQUESTS=3
DEFAULT_RESOLUTION=2K
DEFAULT_IMAGE_SIZE=landscape_4_3

# AI parameters
GUIDANCE_SCALE=7.5
NUM_INFERENCE_STEPS=20
```

### **Output Settings**
```bash
# File organization
OUTPUT_DIR=./product_ads
ORGANIZE_BY_BRAND=true
IMAGE_FORMAT=PNG

# Cost control
MAX_COST_PER_IMAGE=0.05
TOTAL_BUDGET_LIMIT=100.0
```

### **Overlay Settings**
```bash
# Product overlays
ENABLE_PRODUCT_OVERLAY=true
DEFAULT_OVERLAY_POSITION=bottom-left
OVERLAY_BACKGROUND_OPACITY=0.8

# QR codes
QR_CODE_ENABLED=true
QR_CODE_SIZE=100
```

---

## 🛠️ **Troubleshooting**

### **GUI Won't Open**
```bash
# Check if tkinter is available
python -c "import tkinter; print('GUI available')"

# If not available, use manual setup
python src/main.py config-manager --create-env
# Then edit .env file manually
```

### **API Keys Not Saving**
1. Check file permissions in project directory
2. Ensure .env.template exists
3. Try running as administrator (Windows)
4. Manual backup: `python src/main.py config-manager --backup`

### **Provider Tests Failing**
1. Verify API key is correct (copy-paste from provider)
2. Check internet connection
3. Verify provider endpoints are accessible
4. Check if API key has required permissions

### **Configuration Validation Errors**
```bash
# Get detailed validation report
python src/main.py validate-config

# Check .env file format
python src/main.py config-manager
```

---

## 🎯 **Best Practices**

### **API Key Management**
1. **Use GUI for Setup**: Easiest and most reliable method
2. **Test After Setup**: Always test providers after configuration
3. **Multiple Providers**: Configure at least 2 providers for reliability
4. **Regular Backups**: Use `--backup` option before major changes

### **Security**
1. **Keep Keys Private**: Never commit .env file to version control
2. **Regular Rotation**: Update API keys periodically
3. **Minimal Permissions**: Use API keys with minimum required permissions
4. **Backup Management**: Store backups securely

### **Performance Optimization**
1. **Concurrent Requests**: Start with 3, increase gradually
2. **Primary Provider**: Use fastest/most reliable as primary
3. **Fallback Order**: Order by reliability and cost
4. **Cost Limits**: Set appropriate budget controls

---

## 📋 **Quick Setup Checklist**

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run settings GUI: `python settings_launcher.py`
- [ ] Add at least one API key
- [ ] Test provider connectivity
- [ ] Save settings
- [ ] Validate configuration: `python src/main.py validate-config`
- [ ] Test with sample data: `python src/main.py process examples/simple_test.xlsx --dry-run`

---

## 🎉 **You're Ready!**

With the settings GUI configured, you can now:

✅ **Generate Mockups**: Create professional product mockups from Excel data
✅ **Professional Results**: High-quality marketing imagery
✅ **Cost Control**: Stay within budget with monitoring
✅ **Reliable Processing**: Automatic fallback between providers
✅ **Easy Management**: GUI-based configuration updates

**Mock Up Maker is now fully configured and ready for production use!** 🚀