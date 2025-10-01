"""
Configuration management for llmswap.

Provides git-like configuration commands and user preference management.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from .exceptions import ConfigurationError


class LLMSwapConfig:
    """Configuration manager for llmswap settings."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Custom config file path (optional)
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config_dir = Path(self.config_path).parent
        self._config_data = {}
        self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        config_home = os.getenv('LLMSWAP_CONFIG_HOME', 
                               os.path.expanduser('~/.llmswap'))
        return os.path.join(config_home, 'config.yaml')
    
    def _ensure_config_dir(self):
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Set secure permissions (user read/write only)
        try:
            os.chmod(self.config_dir, 0o700)
        except OSError:
            pass  # Windows doesn't support chmod
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            'provider': {
                'default': 'auto',
                'fallback_order': ['anthropic', 'openai', 'gemini', 'cohere', 
                                 'perplexity', 'watsonx', 'groq', 'ollama'],
                'models': {
                    'anthropic': 'claude-sonnet-4-5',
                    'openai': 'gpt-4o',
                    'gemini': 'gemini-1.5-pro',
                    'groq': 'llama-3.3-70b-versatile',
                    'cohere': 'command-r-plus-08-2024',
                    'perplexity': 'sonar-pro',
                    'watsonx': 'granite-13b-chat',
                    'ollama': 'llama3.1'
                }
            },
            'output': {
                'default_dir': '~/Documents/llmswap-generated',
                'auto_save': True,
                'file_naming': 'timestamp',
                'permissions': '644',
                'formats': {
                    'code': '.md',
                    'docs': '.md',
                    'scripts': '.sh'
                }
            },
            'chat': {
                'auto_clear': False,
                'context_limit': 50,
                'provider_switch_warning': True,
                'show_token_count': True,
                'show_cost': True
            },
            'performance': {
                'cache': {
                    'enabled': False,  # Security-first default
                    'ttl': 3600,
                    'max_size_mb': 100
                },
                'analytics': {
                    'enabled': False,  # Privacy-first default
                    'retention_days': 30
                },
                'network': {
                    'timeout': 30,
                    'retry_attempts': 3,
                    'concurrent_limit': 5
                }
            },
            'security': {
                'api_key_validation': True,
                'secure_storage': True,
                'privacy_mode': False,
                'logging': {
                    'level': 'INFO',
                    'file': '~/.llmswap/logs/llmswap.log',
                    'max_size_mb': 10
                }
            },
            'cli': {
                'quiet_mode': False,
                'color_output': True,
                'progress_bars': True,
                'confirmation_prompts': True
            },
            'integrations': {
                'editor': 'auto',
                'browser': 'auto',
                'git_integration': True
            },
            'aliases': {},
            'advanced': {
                'experimental_features': False,
                'debug_mode': False,
                'telemetry': False,
                'auto_update_check': True
            }
        }
    
    def _load_config(self):
        """Load configuration from file, creating with defaults if not exists."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self._config_data = yaml.safe_load(f) or {}
            else:
                # First run - create config file with defaults
                print(f"🔧 Creating config file at {self.config_path}")
                self._config_data = self._get_default_config()
                self._save_config()
                print("✅ Default configuration created")
        except Exception as e:
            raise ConfigurationError(f"Failed to load config: {e}")
        
        # Always merge with defaults to handle new settings
        self._config_data = self._merge_with_defaults(self._config_data)
    
    def _merge_with_defaults(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user configuration with defaults."""
        defaults = self._get_default_config()
        
        def deep_merge(default: Dict, user: Dict) -> Dict:
            result = default.copy()
            for key, value in user.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        return deep_merge(defaults, user_config)
    
    def _save_config(self):
        """Save configuration to file."""
        self._ensure_config_dir()
        
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self._config_data, f, default_flow_style=False, indent=2)
            
            # Set secure permissions
            try:
                os.chmod(self.config_path, 0o600)
            except OSError:
                pass  # Windows doesn't support chmod
                
        except Exception as e:
            raise ConfigurationError(f"Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key.
        
        Args:
            key: Configuration key (e.g., 'provider.default')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value by dot-notation key.
        
        Args:
            key: Configuration key (e.g., 'provider.default')
            value: Value to set
        """
        keys = key.split('.')
        config = self._config_data
        
        # Navigate to parent of target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        self._save_config()
    
    def unset(self, key: str):
        """Remove configuration value by dot-notation key.
        
        Args:
            key: Configuration key to remove
        """
        keys = key.split('.')
        config = self._config_data
        
        try:
            # Navigate to parent of target key
            for k in keys[:-1]:
                config = config[k]
            
            # Remove the key
            if keys[-1] in config:
                del config[keys[-1]]
                self._save_config()
        except (KeyError, TypeError):
            pass  # Key doesn't exist, no need to remove
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section.
        
        Args:
            section: Section name (e.g., 'provider')
            
        Returns:
            Configuration section as dictionary
        """
        return self.get(section, {})
    
    def reset(self, section: Optional[str] = None):
        """Reset configuration to defaults.
        
        Args:
            section: Optional section to reset (resets all if None)
        """
        if section:
            defaults = self._get_default_config()
            if section in defaults:
                self._config_data[section] = defaults[section]
        else:
            self._config_data = self._get_default_config()
        
        self._save_config()
    
    def export_config(self, file_path: str):
        """Export configuration to file.
        
        Args:
            file_path: Path to export file
        """
        try:
            with open(file_path, 'w') as f:
                yaml.dump(self._config_data, f, default_flow_style=False, indent=2)
        except Exception as e:
            raise ConfigurationError(f"Failed to export config: {e}")
    
    def import_config(self, file_path: str, merge: bool = False):
        """Import configuration from file.
        
        Args:
            file_path: Path to import file
            merge: If True, merge with existing config; if False, replace
        """
        try:
            with open(file_path, 'r') as f:
                imported_config = yaml.safe_load(f) or {}
            
            if merge:
                self._config_data = self._merge_with_defaults(imported_config)
            else:
                self._config_data = imported_config
            
            # Ensure defaults are applied
            self._config_data = self._merge_with_defaults(self._config_data)
            self._save_config()
            
        except Exception as e:
            raise ConfigurationError(f"Failed to import config: {e}")
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues.
        
        Returns:
            List of validation error messages
        """
        issues = []
        
        # Validate provider settings
        provider_default = self.get('provider.default')
        if provider_default not in ['auto'] + self.get('provider.fallback_order', []):
            issues.append(f"Invalid default provider: {provider_default}")
        
        # Validate output directory
        output_dir = self.get('output.default_dir')
        if output_dir:
            expanded_dir = os.path.expanduser(output_dir)
            if not os.path.exists(os.path.dirname(expanded_dir)):
                issues.append(f"Output directory parent does not exist: {output_dir}")
        
        # Validate numeric settings
        numeric_settings = [
            ('performance.cache.ttl', int),
            ('performance.cache.max_size_mb', int),
            ('performance.network.timeout', int),
            ('performance.network.retry_attempts', int),
            ('performance.network.concurrent_limit', int),
            ('chat.context_limit', int)
        ]
        
        for setting, expected_type in numeric_settings:
            value = self.get(setting)
            if value is not None and not isinstance(value, expected_type):
                issues.append(f"Invalid type for {setting}: expected {expected_type.__name__}")
        
        return issues
    
    def doctor(self) -> Dict[str, Any]:
        """Check configuration health and suggest fixes.
        
        Returns:
            Dictionary with diagnosis and suggested fixes
        """
        issues = self.validate()
        suggestions = []
        
        # Check for common misconfigurations
        if not self.get('performance.cache.enabled') and self.get('performance.analytics.enabled'):
            suggestions.append("Consider enabling cache for better analytics data")
        
        if self.get('provider.default') == 'auto' and not os.getenv('ANTHROPIC_API_KEY'):
            suggestions.append("Set a specific default provider or configure API keys")
        
        return {
            'issues': issues,
            'suggestions': suggestions,
            'config_path': self.config_path,
            'config_exists': os.path.exists(self.config_path)
        }
    
    def list_all(self) -> Dict[str, Any]:
        """Get complete configuration."""
        return self._config_data.copy()


# Global config instance
_global_config = None

def get_config() -> LLMSwapConfig:
    """Get global configuration instance."""
    global _global_config
    if _global_config is None:
        _global_config = LLMSwapConfig()
    return _global_config