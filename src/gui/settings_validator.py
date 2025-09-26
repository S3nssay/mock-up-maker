import re
import requests
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import asyncio
import aiohttp
from urllib.parse import urlparse


class SettingsValidator:
    """Validate settings and API configurations"""

    def __init__(self):
        """Initialize validator"""
        self.validation_results = {
            'errors': [],
            'warnings': [],
            'info': []
        }

    def validate_all_settings(self, settings_dict: Dict[str, str]) -> Dict[str, List[str]]:
        """Validate all settings and return categorized results"""
        self.validation_results = {'errors': [], 'warnings': [], 'info': []}

        # Validate API keys
        self._validate_api_keys(settings_dict)

        # Validate generation settings
        self._validate_generation_settings(settings_dict)

        # Validate output settings
        self._validate_output_settings(settings_dict)

        # Validate overlay settings
        self._validate_overlay_settings(settings_dict)

        # Validate cost settings
        self._validate_cost_settings(settings_dict)

        return self.validation_results

    def _validate_api_keys(self, settings: Dict[str, str]) -> None:
        """Validate API key configurations"""
        api_keys = {
            'SEEDREAM_KIE_API_KEY': 'Seedream via Kie.ai',
            'SEEDREAM_AIML_API_KEY': 'Seedream via AI/ML API',
            'SEEDREAM_BYTEPLUS_API_KEY': 'Seedream via BytePlus',
            'NANO_BANANA_API_KEY': 'Nano Banana'
        }

        configured_keys = []
        for key, name in api_keys.items():
            api_key = settings.get(key, '').strip()
            if api_key:
                # Validate key format
                if self._validate_api_key_format(key, api_key):
                    configured_keys.append(name)
                else:
                    self.validation_results['warnings'].append(
                        f"{name} API key format appears invalid"
                    )

        # Check if at least one key is configured
        if not configured_keys:
            self.validation_results['errors'].append(
                "No API keys configured. You need at least one provider to generate images."
            )
        elif len(configured_keys) == 1:
            self.validation_results['warnings'].append(
                f"Only {configured_keys[0]} configured. Consider adding backup providers for reliability."
            )
        else:
            self.validation_results['info'].append(
                f"Multiple providers configured: {', '.join(configured_keys)}"
            )

        # Validate primary provider
        primary_provider = settings.get('AI_IMAGE_PROVIDER', '').strip()
        if primary_provider:
            provider_key_map = {
                'seedream_kie': 'SEEDREAM_KIE_API_KEY',
                'seedream_aiml': 'SEEDREAM_AIML_API_KEY',
                'seedream_byteplus': 'SEEDREAM_BYTEPLUS_API_KEY',
                'nano_banana': 'NANO_BANANA_API_KEY'
            }

            required_key = provider_key_map.get(primary_provider)
            if required_key and not settings.get(required_key, '').strip():
                self.validation_results['errors'].append(
                    f"Primary provider '{primary_provider}' selected but no API key configured"
                )

    def _validate_api_key_format(self, key_type: str, api_key: str) -> bool:
        """Validate API key format based on provider"""
        if not api_key or len(api_key) < 10:
            return False

        # Basic validation patterns (these are examples - adjust based on actual providers)
        patterns = {
            'SEEDREAM_KIE_API_KEY': r'^[a-zA-Z0-9_-]{20,}$',
            'SEEDREAM_AIML_API_KEY': r'^[a-zA-Z0-9_-]{20,}$',
            'SEEDREAM_BYTEPLUS_API_KEY': r'^[a-zA-Z0-9_-]{20,}$',
            'NANO_BANANA_API_KEY': r'^[a-zA-Z0-9_-]{15,}$'
        }

        pattern = patterns.get(key_type)
        if pattern:
            return bool(re.match(pattern, api_key))

        return True  # If no pattern defined, assume valid

    def _validate_generation_settings(self, settings: Dict[str, str]) -> None:
        """Validate generation-related settings"""
        # Validate concurrent requests
        concurrent = settings.get('CONCURRENT_REQUESTS', '3')
        try:
            concurrent_int = int(concurrent)
            if concurrent_int < 1:
                self.validation_results['errors'].append("Concurrent requests must be at least 1")
            elif concurrent_int > 10:
                self.validation_results['warnings'].append(
                    "High concurrent requests (>10) may cause rate limiting"
                )
        except ValueError:
            self.validation_results['errors'].append(
                f"Invalid concurrent requests value: {concurrent}"
            )

        # Validate guidance scale
        guidance = settings.get('GUIDANCE_SCALE', '7.5')
        try:
            guidance_float = float(guidance)
            if not (1.0 <= guidance_float <= 20.0):
                self.validation_results['warnings'].append(
                    "Guidance scale outside recommended range (1.0-20.0)"
                )
        except ValueError:
            self.validation_results['errors'].append(
                f"Invalid guidance scale value: {guidance}"
            )

        # Validate inference steps
        steps = settings.get('NUM_INFERENCE_STEPS', '20')
        try:
            steps_int = int(steps)
            if not (10 <= steps_int <= 100):
                self.validation_results['warnings'].append(
                    "Inference steps outside recommended range (10-100)"
                )
        except ValueError:
            self.validation_results['errors'].append(
                f"Invalid inference steps value: {steps}"
            )

        # Validate resolution and size
        resolution = settings.get('DEFAULT_RESOLUTION', '2K')
        if resolution not in ['HD', 'FHD', '2K', '4K']:
            self.validation_results['errors'].append(
                f"Invalid resolution: {resolution}"
            )

        size = settings.get('DEFAULT_IMAGE_SIZE', 'landscape_4_3')
        valid_sizes = ['landscape_4_3', 'landscape_16_9', 'portrait_3_4', 'portrait_9_16', 'square']
        if size not in valid_sizes:
            self.validation_results['errors'].append(
                f"Invalid image size: {size}"
            )

    def _validate_output_settings(self, settings: Dict[str, str]) -> None:
        """Validate output-related settings"""
        # Validate output directory
        output_dir = settings.get('OUTPUT_DIR', './product_ads')
        try:
            output_path = Path(output_dir)
            if output_path.exists() and not output_path.is_dir():
                self.validation_results['errors'].append(
                    f"Output path exists but is not a directory: {output_dir}"
                )
            elif not output_path.parent.exists():
                self.validation_results['warnings'].append(
                    f"Parent directory does not exist: {output_path.parent}"
                )
        except Exception as e:
            self.validation_results['errors'].append(
                f"Invalid output directory path: {output_dir}"
            )

        # Validate image format
        image_format = settings.get('IMAGE_FORMAT', 'PNG')
        if image_format not in ['PNG', 'JPEG', 'WEBP']:
            self.validation_results['errors'].append(
                f"Invalid image format: {image_format}"
            )

    def _validate_overlay_settings(self, settings: Dict[str, str]) -> None:
        """Validate overlay-related settings"""
        # Validate overlay position
        position = settings.get('DEFAULT_OVERLAY_POSITION', 'bottom-left')
        valid_positions = ['bottom-left', 'bottom-right', 'top-left', 'top-right', 'center-bottom', 'center-top']
        if position not in valid_positions:
            self.validation_results['errors'].append(
                f"Invalid overlay position: {position}"
            )

        # Validate overlay opacity
        opacity = settings.get('OVERLAY_BACKGROUND_OPACITY', '0.8')
        try:
            opacity_float = float(opacity)
            if not (0.0 <= opacity_float <= 1.0):
                self.validation_results['errors'].append(
                    "Overlay opacity must be between 0.0 and 1.0"
                )
        except ValueError:
            self.validation_results['errors'].append(
                f"Invalid overlay opacity value: {opacity}"
            )

        # Validate QR code size
        qr_size = settings.get('QR_CODE_SIZE', '100')
        try:
            qr_int = int(qr_size)
            if not (50 <= qr_int <= 500):
                self.validation_results['warnings'].append(
                    "QR code size outside recommended range (50-500 pixels)"
                )
        except ValueError:
            self.validation_results['errors'].append(
                f"Invalid QR code size: {qr_size}"
            )

    def _validate_cost_settings(self, settings: Dict[str, str]) -> None:
        """Validate cost control settings"""
        # Validate max cost per image
        max_cost = settings.get('MAX_COST_PER_IMAGE', '0.05')
        try:
            max_cost_float = float(max_cost)
            if max_cost_float <= 0:
                self.validation_results['errors'].append(
                    "Max cost per image must be positive"
                )
            elif max_cost_float > 1.0:
                self.validation_results['warnings'].append(
                    "Max cost per image is very high (>$1.00)"
                )
        except ValueError:
            self.validation_results['errors'].append(
                f"Invalid max cost per image: {max_cost}"
            )

        # Validate total budget
        total_budget = settings.get('TOTAL_BUDGET_LIMIT', '100.0')
        try:
            budget_float = float(total_budget)
            if budget_float <= 0:
                self.validation_results['errors'].append(
                    "Total budget limit must be positive"
                )

            # Compare with max cost per image
            if max_cost:
                try:
                    max_cost_float = float(max_cost)
                    if max_cost_float >= budget_float:
                        self.validation_results['warnings'].append(
                            "Max cost per image is greater than or equal to total budget"
                        )
                except ValueError:
                    pass  # Already handled above

        except ValueError:
            self.validation_results['errors'].append(
                f"Invalid total budget limit: {total_budget}"
            )

    async def test_api_connectivity(self, api_key: str, provider_type: str) -> Tuple[bool, str]:
        """Test API connectivity for a provider"""
        try:
            # This is a simplified test - in reality, you'd make actual API calls
            # to test endpoints for each provider

            if not api_key or len(api_key) < 10:
                return False, "Invalid API key format"

            if provider_type == 'SEEDREAM_KIE_API_KEY':
                return await self._test_kie_connectivity(api_key)
            elif provider_type == 'NANO_BANANA_API_KEY':
                return await self._test_nano_banana_connectivity(api_key)
            elif provider_type == 'SEEDREAM_AIML_API_KEY':
                return await self._test_aiml_connectivity(api_key)
            elif provider_type == 'SEEDREAM_BYTEPLUS_API_KEY':
                return await self._test_byteplus_connectivity(api_key)
            else:
                return False, "Unknown provider type"

        except Exception as e:
            return False, f"Connection test failed: {str(e)}"

    async def _test_kie_connectivity(self, api_key: str) -> Tuple[bool, str]:
        """Test Kie.ai API connectivity"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }

                # Simple endpoint test (adjust URL as needed)
                async with session.get(
                    'https://api.kie.ai/v1/status',  # Example endpoint
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        return True, "Connection successful"
                    elif response.status == 401:
                        return False, "Invalid API key"
                    else:
                        return False, f"API returned status {response.status}"

        except aiohttp.ClientTimeout:
            return False, "Connection timeout"
        except aiohttp.ClientConnectorError:
            return False, "Cannot connect to API endpoint"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    async def _test_nano_banana_connectivity(self, api_key: str) -> Tuple[bool, str]:
        """Test Nano Banana API connectivity"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }

                # Simple endpoint test (adjust URL as needed)
                async with session.get(
                    'https://api.nano-banana.com/v1/health',  # Example endpoint
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        return True, "Connection successful"
                    elif response.status == 401:
                        return False, "Invalid API key"
                    else:
                        return False, f"API returned status {response.status}"

        except aiohttp.ClientTimeout:
            return False, "Connection timeout"
        except aiohttp.ClientConnectorError:
            return False, "Cannot connect to API endpoint"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    async def _test_aiml_connectivity(self, api_key: str) -> Tuple[bool, str]:
        """Test AI/ML API connectivity"""
        # Similar implementation for AI/ML API
        # This is a placeholder - implement actual endpoint testing
        await asyncio.sleep(1)  # Simulate API call
        return True, "Connection test simulated (implement actual test)"

    async def _test_byteplus_connectivity(self, api_key: str) -> Tuple[bool, str]:
        """Test BytePlus API connectivity"""
        # Similar implementation for BytePlus API
        # This is a placeholder - implement actual endpoint testing
        await asyncio.sleep(1)  # Simulate API call
        return True, "Connection test simulated (implement actual test)"

    def validate_file_paths(self, settings: Dict[str, str]) -> List[str]:
        """Validate file paths and permissions"""
        issues = []

        # Check output directory
        output_dir = settings.get('OUTPUT_DIR', './product_ads')
        try:
            output_path = Path(output_dir)

            # Try to create directory if it doesn't exist
            if not output_path.exists():
                try:
                    output_path.mkdir(parents=True, exist_ok=True)
                    issues.append(f"INFO: Created output directory: {output_dir}")
                except PermissionError:
                    issues.append(f"ERROR: Permission denied creating directory: {output_dir}")
                except Exception as e:
                    issues.append(f"ERROR: Cannot create directory {output_dir}: {str(e)}")

            # Test write permissions
            if output_path.exists():
                test_file = output_path / '.write_test'
                try:
                    test_file.write_text('test')
                    test_file.unlink()
                    issues.append(f"INFO: Write permissions OK for: {output_dir}")
                except PermissionError:
                    issues.append(f"ERROR: No write permissions for: {output_dir}")
                except Exception as e:
                    issues.append(f"WARNING: Write test failed for {output_dir}: {str(e)}")

        except Exception as e:
            issues.append(f"ERROR: Invalid output directory path: {output_dir}")

        return issues

    def get_validation_summary(self) -> Dict[str, int]:
        """Get summary of validation results"""
        return {
            'errors': len(self.validation_results['errors']),
            'warnings': len(self.validation_results['warnings']),
            'info': len(self.validation_results['info'])
        }