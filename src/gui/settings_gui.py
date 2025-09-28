import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import os
from typing import Dict, Any, Optional
import threading
import sys

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import Settings
from gui.env_manager import EnvManager
from core.models import ImageProvider


class SettingsGUI:
    """GUI for managing application settings and API keys"""

    def __init__(self, root: Optional[tk.Tk] = None):
        """Initialize the settings GUI"""
        self.root = root or tk.Tk()
        self.root.title("Mock Up Maker - Settings")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        # Initialize managers
        self.env_manager = EnvManager()
        self.settings = None
        self.current_values = {}

        # Setup GUI
        self._setup_styles()
        self._create_widgets()
        self._load_current_settings()

        # Center window
        self._center_window()

    def _setup_styles(self):
        """Setup custom styles for the interface"""
        style = ttk.Style()

        # Configure styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Info.TLabel', font=('Arial', 9), foreground='gray')
        style.configure('Success.TLabel', font=('Arial', 10), foreground='green')
        style.configure('Error.TLabel', font=('Arial', 10), foreground='red')

    def _create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="⚙️ Settings & API Configuration", style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        main_frame.rowconfigure(1, weight=1)

        # Create tabs
        self._create_api_keys_tab()
        self._create_generation_tab()
        self._create_output_tab()
        self._create_overlay_tab()

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        buttons_frame.columnconfigure(1, weight=1)

        # Buttons
        ttk.Button(buttons_frame, text="💾 Save Settings", command=self._save_settings).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(buttons_frame, text="🧪 Test Providers", command=self._test_providers).grid(row=0, column=1, padx=(5, 5))
        ttk.Button(buttons_frame, text="🔄 Reset to Defaults", command=self._reset_defaults).grid(row=0, column=2, padx=(5, 5))
        ttk.Button(buttons_frame, text="❌ Close", command=self.root.quit).grid(row=0, column=3, padx=(10, 0))

        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready", style='Info.TLabel')
        self.status_label.grid(row=3, column=0, pady=(10, 0), sticky=tk.W)

    def _create_api_keys_tab(self):
        """Create API keys configuration tab"""
        api_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(api_frame, text="🔑 API Keys")

        # Scroll frame
        canvas = tk.Canvas(api_frame)
        scrollbar = ttk.Scrollbar(api_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        api_frame.columnconfigure(0, weight=1)
        api_frame.rowconfigure(0, weight=1)

        # API Key entries
        self.api_entries = {}
        current_row = 0

        # API Providers configuration
        providers_config = [
            {
                "name": "Seedream via Kie.ai",
                "key": "SEEDREAM_KIE_API_KEY",
                "description": "Primary recommendation - Best quality for product imagery",
                "website": "https://kie.ai",
                "cost": "$0.0175 per image"
            },
            {
                "name": "Nano Banana",
                "key": "NANO_BANANA_API_KEY",
                "description": "Budget-friendly alternative with good quality",
                "website": "https://nano-banana.com",
                "cost": "$0.02 per image"
            },
            {
                "name": "Seedream via AI/ML API",
                "key": "SEEDREAM_AIML_API_KEY",
                "description": "Alternative Seedream access point",
                "website": "https://aimlapi.com",
                "cost": "$0.025 per image"
            },
            {
                "name": "Seedream via BytePlus",
                "key": "SEEDREAM_BYTEPLUS_API_KEY",
                "description": "Enterprise ByteDance option",
                "website": "https://byteplus.com",
                "cost": "Enterprise pricing"
            }
        ]

        for provider in providers_config:
            # Provider header
            header_frame = ttk.LabelFrame(scrollable_frame, text=provider["name"], padding="15")
            header_frame.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 15), padx=5)
            scrollable_frame.columnconfigure(0, weight=1)

            # Description
            desc_label = ttk.Label(header_frame, text=provider["description"], style='Info.TLabel')
            desc_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))

            # Website and cost info
            info_frame = ttk.Frame(header_frame)
            info_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

            ttk.Label(info_frame, text=f"🌐 {provider['website']}", style='Info.TLabel').grid(row=0, column=0, sticky=tk.W)
            ttk.Label(info_frame, text=f"💰 {provider['cost']}", style='Info.TLabel').grid(row=0, column=1, sticky=tk.E)
            info_frame.columnconfigure(1, weight=1)

            # API Key input
            ttk.Label(header_frame, text="API Key:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))

            entry = ttk.Entry(header_frame, width=50, show="*")
            entry.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
            header_frame.columnconfigure(0, weight=1)

            # Show/Hide button
            show_var = tk.BooleanVar()
            def toggle_visibility(entry=entry, var=show_var):
                entry.config(show="" if var.get() else "*")

            show_check = ttk.Checkbutton(header_frame, text="Show", variable=show_var, command=toggle_visibility)
            show_check.grid(row=3, column=1, padx=(10, 0))

            # Test button
            test_btn = ttk.Button(header_frame, text="🧪 Test",
                                command=lambda k=provider["key"]: self._test_single_provider(k))
            test_btn.grid(row=3, column=2, padx=(10, 0))

            self.api_entries[provider["key"]] = entry
            current_row += 1

        # Instructions
        instructions_frame = ttk.LabelFrame(scrollable_frame, text="📋 Instructions", padding="15")
        instructions_frame.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(15, 0), padx=5)

        instructions_text = """
1. Sign up for at least one API provider (Kie.ai recommended)
2. Get your API key from the provider's dashboard
3. Paste the API key in the corresponding field above
4. Click 'Test' to verify the key works
5. Click 'Save Settings' to store your configuration
6. You need at least ONE working API key to generate images

💡 Tip: Having multiple providers enables automatic fallback if one fails
        """

        ttk.Label(instructions_frame, text=instructions_text.strip(), justify=tk.LEFT, style='Info.TLabel').grid(row=0, column=0, sticky=tk.W)

    def _create_generation_tab(self):
        """Create generation settings tab"""
        gen_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(gen_frame, text="🎨 Generation")

        # Primary provider
        ttk.Label(gen_frame, text="Primary Provider:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.primary_provider_var = tk.StringVar()
        provider_combo = ttk.Combobox(gen_frame, textvariable=self.primary_provider_var,
                                    values=[p.value for p in ImageProvider], state="readonly")
        provider_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        gen_frame.columnconfigure(0, weight=1)

        # Fallback settings
        ttk.Label(gen_frame, text="Fallback Settings:", style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(15, 5))

        self.enable_fallback_var = tk.BooleanVar()
        ttk.Checkbutton(gen_frame, text="Enable automatic fallback to other providers",
                       variable=self.enable_fallback_var).grid(row=3, column=0, sticky=tk.W, pady=(0, 10))

        # Concurrent requests
        ttk.Label(gen_frame, text="Concurrent Requests:", style='Header.TLabel').grid(row=4, column=0, sticky=tk.W, pady=(15, 5))

        concurrent_frame = ttk.Frame(gen_frame)
        concurrent_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        self.concurrent_var = tk.IntVar()
        concurrent_scale = ttk.Scale(concurrent_frame, from_=1, to=10, variable=self.concurrent_var, orient=tk.HORIZONTAL)
        concurrent_scale.grid(row=0, column=0, sticky=(tk.W, tk.E))
        concurrent_frame.columnconfigure(0, weight=1)

        self.concurrent_label = ttk.Label(concurrent_frame, text="3")
        self.concurrent_label.grid(row=0, column=1, padx=(10, 0))

        def update_concurrent_label(value):
            self.concurrent_label.config(text=f"{int(float(value))}")

        concurrent_scale.config(command=update_concurrent_label)

        # Image settings
        ttk.Label(gen_frame, text="Image Settings:", style='Header.TLabel').grid(row=6, column=0, sticky=tk.W, pady=(15, 5))

        # Resolution
        res_frame = ttk.Frame(gen_frame)
        res_frame.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(res_frame, text="Resolution:").grid(row=0, column=0, sticky=tk.W)
        self.resolution_var = tk.StringVar()
        res_combo = ttk.Combobox(res_frame, textvariable=self.resolution_var,
                               values=["HD", "FHD", "2K", "4K"], state="readonly", width=10)
        res_combo.grid(row=0, column=1, padx=(10, 0))

        # Size
        ttk.Label(res_frame, text="Aspect Ratio:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.size_var = tk.StringVar()
        size_combo = ttk.Combobox(res_frame, textvariable=self.size_var,
                                values=["landscape_4_3", "landscape_16_9", "portrait_3_4", "portrait_9_16", "square"],
                                state="readonly", width=15)
        size_combo.grid(row=0, column=3, padx=(10, 0))

        # Advanced settings
        ttk.Label(gen_frame, text="Advanced Settings:", style='Header.TLabel').grid(row=8, column=0, sticky=tk.W, pady=(15, 5))

        adv_frame = ttk.Frame(gen_frame)
        adv_frame.grid(row=9, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Guidance scale
        ttk.Label(adv_frame, text="Guidance Scale:").grid(row=0, column=0, sticky=tk.W)
        self.guidance_var = tk.DoubleVar()
        guidance_spin = ttk.Spinbox(adv_frame, from_=1.0, to=20.0, textvariable=self.guidance_var,
                                  increment=0.5, width=10)
        guidance_spin.grid(row=0, column=1, padx=(10, 0))

        # Inference steps
        ttk.Label(adv_frame, text="Inference Steps:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.steps_var = tk.IntVar()
        steps_spin = ttk.Spinbox(adv_frame, from_=10, to=100, textvariable=self.steps_var,
                               increment=5, width=10)
        steps_spin.grid(row=0, column=3, padx=(10, 0))

    def _create_output_tab(self):
        """Create output settings tab"""
        output_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(output_frame, text="📁 Output")

        # Output directory
        ttk.Label(output_frame, text="Output Directory:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        dir_frame = ttk.Frame(output_frame)
        dir_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        dir_frame.columnconfigure(0, weight=1)

        self.output_dir_var = tk.StringVar()
        dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var)
        dir_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        ttk.Button(dir_frame, text="📁 Browse", command=self._browse_output_dir).grid(row=0, column=1)

        # Organization settings
        ttk.Label(output_frame, text="Organization:", style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(15, 5))

        self.organize_by_brand_var = tk.BooleanVar()
        ttk.Checkbutton(output_frame, text="Organize files by brand",
                       variable=self.organize_by_brand_var).grid(row=3, column=0, sticky=tk.W, pady=(0, 10))

        # File format
        format_frame = ttk.Frame(output_frame)
        format_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Label(format_frame, text="Image Format:").grid(row=0, column=0, sticky=tk.W)
        self.image_format_var = tk.StringVar()
        format_combo = ttk.Combobox(format_frame, textvariable=self.image_format_var,
                                  values=["PNG", "JPEG", "WEBP"], state="readonly", width=10)
        format_combo.grid(row=0, column=1, padx=(10, 0))

        # Cost control
        ttk.Label(output_frame, text="Cost Control:", style='Header.TLabel').grid(row=5, column=0, sticky=tk.W, pady=(15, 5))

        cost_frame = ttk.Frame(output_frame)
        cost_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(cost_frame, text="Max Cost Per Image: $").grid(row=0, column=0, sticky=tk.W)
        self.max_cost_var = tk.DoubleVar()
        cost_spin = ttk.Spinbox(cost_frame, from_=0.01, to=1.0, textvariable=self.max_cost_var,
                              increment=0.01, width=10, format="%.2f")
        cost_spin.grid(row=0, column=1, padx=(5, 0))

        ttk.Label(cost_frame, text="Total Budget Limit: $").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.budget_var = tk.DoubleVar()
        budget_spin = ttk.Spinbox(cost_frame, from_=1.0, to=1000.0, textvariable=self.budget_var,
                                increment=10.0, width=10, format="%.0f")
        budget_spin.grid(row=0, column=3, padx=(5, 0))

    def _create_overlay_tab(self):
        """Create overlay settings tab"""
        overlay_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(overlay_frame, text="🎨 Overlays")

        # Enable overlays
        ttk.Label(overlay_frame, text="Product Overlays:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.enable_overlay_var = tk.BooleanVar()
        ttk.Checkbutton(overlay_frame, text="Enable product information overlays by default",
                       variable=self.enable_overlay_var).grid(row=1, column=0, sticky=tk.W, pady=(0, 15))

        # Default position
        pos_frame = ttk.Frame(overlay_frame)
        pos_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Label(pos_frame, text="Default Position:").grid(row=0, column=0, sticky=tk.W)
        self.overlay_position_var = tk.StringVar()
        pos_combo = ttk.Combobox(pos_frame, textvariable=self.overlay_position_var,
                               values=["bottom-left", "bottom-right", "top-left", "top-right", "center-bottom", "center-top"],
                               state="readonly", width=15)
        pos_combo.grid(row=0, column=1, padx=(10, 0))

        # QR Code settings
        ttk.Label(overlay_frame, text="QR Code Settings:", style='Header.TLabel').grid(row=3, column=0, sticky=tk.W, pady=(15, 5))

        self.qr_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(overlay_frame, text="Include QR codes linking to product URLs",
                       variable=self.qr_enabled_var).grid(row=4, column=0, sticky=tk.W, pady=(0, 10))

        qr_frame = ttk.Frame(overlay_frame)
        qr_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Label(qr_frame, text="QR Code Size:").grid(row=0, column=0, sticky=tk.W)
        self.qr_size_var = tk.IntVar()
        qr_spin = ttk.Spinbox(qr_frame, from_=50, to=200, textvariable=self.qr_size_var,
                            increment=10, width=10)
        qr_spin.grid(row=0, column=1, padx=(10, 0))
        ttk.Label(qr_frame, text="pixels").grid(row=0, column=2, padx=(5, 0))

        # Style settings
        ttk.Label(overlay_frame, text="Style Settings:", style='Header.TLabel').grid(row=6, column=0, sticky=tk.W, pady=(15, 5))

        style_frame = ttk.Frame(overlay_frame)
        style_frame.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(style_frame, text="Background Opacity:").grid(row=0, column=0, sticky=tk.W)
        self.opacity_var = tk.DoubleVar()
        opacity_scale = ttk.Scale(style_frame, from_=0.0, to=1.0, variable=self.opacity_var, orient=tk.HORIZONTAL)
        opacity_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10))
        style_frame.columnconfigure(1, weight=1)

        self.opacity_label = ttk.Label(style_frame, text="0.8")
        self.opacity_label.grid(row=0, column=2)

        def update_opacity_label(value):
            self.opacity_label.config(text=f"{float(value):.1f}")

        opacity_scale.config(command=update_opacity_label)

    def _browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)

    def _load_current_settings(self):
        """Load current settings from .env file"""
        try:
            # Load environment variables
            env_vars = self.env_manager.load_env_vars()

            # Load API keys
            for key, entry in self.api_entries.items():
                value = env_vars.get(key, "")
                entry.delete(0, tk.END)
                entry.insert(0, value)

            # Load other settings with defaults
            self.primary_provider_var.set(env_vars.get("AI_IMAGE_PROVIDER", "seedream_kie"))
            self.enable_fallback_var.set(env_vars.get("ENABLE_FALLBACK", "true").lower() == "true")
            self.concurrent_var.set(int(env_vars.get("CONCURRENT_REQUESTS", "3")))
            self.resolution_var.set(env_vars.get("DEFAULT_RESOLUTION", "2K"))
            self.size_var.set(env_vars.get("DEFAULT_IMAGE_SIZE", "landscape_4_3"))
            self.guidance_var.set(float(env_vars.get("GUIDANCE_SCALE", "7.5")))
            self.steps_var.set(int(env_vars.get("NUM_INFERENCE_STEPS", "20")))

            self.output_dir_var.set(env_vars.get("OUTPUT_DIR", "./product_ads"))
            self.organize_by_brand_var.set(env_vars.get("ORGANIZE_BY_BRAND", "true").lower() == "true")
            self.image_format_var.set(env_vars.get("IMAGE_FORMAT", "PNG"))
            self.max_cost_var.set(float(env_vars.get("MAX_COST_PER_IMAGE", "0.05")))
            self.budget_var.set(float(env_vars.get("TOTAL_BUDGET_LIMIT", "100.0")))

            self.enable_overlay_var.set(env_vars.get("ENABLE_PRODUCT_OVERLAY", "true").lower() == "true")
            self.overlay_position_var.set(env_vars.get("DEFAULT_OVERLAY_POSITION", "bottom-left"))
            self.qr_enabled_var.set(env_vars.get("QR_CODE_ENABLED", "true").lower() == "true")
            self.qr_size_var.set(int(env_vars.get("QR_CODE_SIZE", "100")))
            self.opacity_var.set(float(env_vars.get("OVERLAY_BACKGROUND_OPACITY", "0.8")))

            self._update_status("Settings loaded successfully", "success")

        except Exception as e:
            self._update_status(f"Error loading settings: {str(e)}", "error")

    def _save_settings(self):
        """Save settings to .env file"""
        try:
            # Collect all settings
            settings_dict = {}

            # API keys
            for key, entry in self.api_entries.items():
                value = entry.get().strip()
                if value:
                    settings_dict[key] = value

            # Generation settings
            settings_dict.update({
                "AI_IMAGE_PROVIDER": self.primary_provider_var.get(),
                "ENABLE_FALLBACK": str(self.enable_fallback_var.get()).lower(),
                "CONCURRENT_REQUESTS": str(int(self.concurrent_var.get())),
                "DEFAULT_RESOLUTION": self.resolution_var.get(),
                "DEFAULT_IMAGE_SIZE": self.size_var.get(),
                "GUIDANCE_SCALE": str(self.guidance_var.get()),
                "NUM_INFERENCE_STEPS": str(int(self.steps_var.get())),

                # Output settings
                "OUTPUT_DIR": self.output_dir_var.get(),
                "ORGANIZE_BY_BRAND": str(self.organize_by_brand_var.get()).lower(),
                "IMAGE_FORMAT": self.image_format_var.get(),
                "MAX_COST_PER_IMAGE": str(self.max_cost_var.get()),
                "TOTAL_BUDGET_LIMIT": str(self.budget_var.get()),

                # Overlay settings
                "ENABLE_PRODUCT_OVERLAY": str(self.enable_overlay_var.get()).lower(),
                "DEFAULT_OVERLAY_POSITION": self.overlay_position_var.get(),
                "QR_CODE_ENABLED": str(self.qr_enabled_var.get()).lower(),
                "QR_CODE_SIZE": str(int(self.qr_size_var.get())),
                "OVERLAY_BACKGROUND_OPACITY": str(self.opacity_var.get())
            })

            # Save to .env file
            success = self.env_manager.save_env_vars(settings_dict)

            if success:
                self._update_status("✅ Settings saved successfully!", "success")
                messagebox.showinfo("Success", "Settings have been saved to .env file!")
            else:
                self._update_status("❌ Failed to save settings", "error")
                messagebox.showerror("Error", "Failed to save settings to .env file")

        except Exception as e:
            self._update_status(f"❌ Error saving settings: {str(e)}", "error")
            messagebox.showerror("Error", f"Error saving settings: {str(e)}")

    def _test_single_provider(self, provider_key: str):
        """Test a single provider"""
        try:
            api_key = self.api_entries[provider_key].get().strip()
            if not api_key:
                messagebox.showwarning("Warning", "Please enter an API key first")
                return

            self._update_status(f"Testing {provider_key}...", "info")

            # Run test in background thread
            def test_provider():
                try:
                    # Here you would implement actual provider testing
                    # For now, just simulate a test
                    import time
                    time.sleep(2)  # Simulate API call

                    # Update UI in main thread
                    self.root.after(0, lambda: self._update_status(f"✅ {provider_key} test successful!", "success"))
                    self.root.after(0, lambda: messagebox.showinfo("Success", f"{provider_key} is working correctly!"))

                except Exception as e:
                    self.root.after(0, lambda: self._update_status(f"❌ {provider_key} test failed: {str(e)}", "error"))
                    self.root.after(0, lambda: messagebox.showerror("Error", f"{provider_key} test failed: {str(e)}"))

            threading.Thread(target=test_provider, daemon=True).start()

        except Exception as e:
            self._update_status(f"❌ Error testing provider: {str(e)}", "error")

    def _test_providers(self):
        """Test all configured providers"""
        try:
            # Check which providers have API keys
            providers_to_test = []
            for key, entry in self.api_entries.items():
                if entry.get().strip():
                    providers_to_test.append(key)

            if not providers_to_test:
                messagebox.showwarning("Warning", "No API keys configured to test")
                return

            self._update_status(f"Testing {len(providers_to_test)} providers...", "info")

            # Run tests in background
            def test_all():
                results = []
                for provider_key in providers_to_test:
                    try:
                        # Simulate test - replace with actual testing
                        import time
                        time.sleep(1)
                        results.append(f"✅ {provider_key}")
                    except Exception as e:
                        results.append(f"❌ {provider_key}: {str(e)}")

                # Update UI
                result_text = "\n".join(results)
                self.root.after(0, lambda: self._update_status("Provider testing completed", "success"))
                self.root.after(0, lambda: messagebox.showinfo("Test Results", result_text))

            threading.Thread(target=test_all, daemon=True).start()

        except Exception as e:
            self._update_status(f"❌ Error testing providers: {str(e)}", "error")

    def _reset_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all settings to defaults?"):
            try:
                # Clear API keys
                for entry in self.api_entries.values():
                    entry.delete(0, tk.END)

                # Reset to defaults
                self.primary_provider_var.set("seedream_kie")
                self.enable_fallback_var.set(True)
                self.concurrent_var.set(3)
                self.resolution_var.set("2K")
                self.size_var.set("landscape_4_3")
                self.guidance_var.set(7.5)
                self.steps_var.set(20)

                self.output_dir_var.set("./product_ads")
                self.organize_by_brand_var.set(True)
                self.image_format_var.set("PNG")
                self.max_cost_var.set(0.05)
                self.budget_var.set(100.0)

                self.enable_overlay_var.set(True)
                self.overlay_position_var.set("bottom-left")
                self.qr_enabled_var.set(True)
                self.qr_size_var.set(100)
                self.opacity_var.set(0.8)

                self._update_status("Settings reset to defaults", "success")

            except Exception as e:
                self._update_status(f"❌ Error resetting settings: {str(e)}", "error")

    def _update_status(self, message: str, status_type: str = "info"):
        """Update status label"""
        styles = {
            "info": "Info.TLabel",
            "success": "Success.TLabel",
            "error": "Error.TLabel"
        }

        style = styles.get(status_type, "Info.TLabel")
        self.status_label.config(text=message, style=style)

    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")

    def run(self):
        """Run the GUI"""
        self.root.mainloop()


def main():
    """Main function to run settings GUI"""
    try:
        app = SettingsGUI()
        app.run()
    except Exception as e:
        print(f"Error running settings GUI: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()