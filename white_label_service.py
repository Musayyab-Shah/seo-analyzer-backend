import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from ..models.white_label import WhiteLabelConfig, ReportTemplate

class WhiteLabelService:
    """Service for managing white label configurations"""
    
    def __init__(self):
        self.config_file = "white_label_configs.json"
        self.upload_dir = "uploads/logos"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def _load_configs(self) -> Dict[str, Any]:
        """Load configurations from file"""
        if not os.path.exists(self.config_file):
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_configs(self, configs: Dict[str, Any]):
        """Save configurations to file"""
        with open(self.config_file, 'w') as f:
            json.dump(configs, f, indent=2, default=str)
    
    def create_config(self, user_id: int, config_data: Dict[str, Any]) -> WhiteLabelConfig:
        """Create a new white label configuration"""
        configs = self._load_configs()
        
        # Generate new ID
        config_id = max([int(k) for k in configs.keys()] + [0]) + 1
        
        # Create configuration
        config = WhiteLabelConfig.from_dict(config_data)
        config.id = config_id
        config.user_id = user_id
        config.created_at = datetime.now()
        config.updated_at = datetime.now()
        
        # Validate configuration
        errors = config.validate()
        if errors:
            raise ValueError(f"Configuration validation failed: {errors}")
        
        # Save configuration
        configs[str(config_id)] = config.to_dict()
        self._save_configs(configs)
        
        return config
    
    def get_config(self, config_id: int) -> Optional[WhiteLabelConfig]:
        """Get configuration by ID"""
        configs = self._load_configs()
        config_data = configs.get(str(config_id))
        
        if not config_data:
            return None
        
        return WhiteLabelConfig.from_dict(config_data)
    
    def get_user_config(self, user_id: int) -> Optional[WhiteLabelConfig]:
        """Get configuration for a specific user"""
        configs = self._load_configs()
        
        for config_data in configs.values():
            if config_data.get('user_id') == user_id:
                return WhiteLabelConfig.from_dict(config_data)
        
        return None
    
    def update_config(self, config_id: int, config_data: Dict[str, Any]) -> Optional[WhiteLabelConfig]:
        """Update an existing configuration"""
        configs = self._load_configs()
        
        if str(config_id) not in configs:
            return None
        
        # Get existing config
        existing_config = WhiteLabelConfig.from_dict(configs[str(config_id)])
        
        # Update fields
        for key, value in config_data.items():
            if hasattr(existing_config, key):
                setattr(existing_config, key, value)
        
        existing_config.updated_at = datetime.now()
        
        # Validate configuration
        errors = existing_config.validate()
        if errors:
            raise ValueError(f"Configuration validation failed: {errors}")
        
        # Save updated configuration
        configs[str(config_id)] = existing_config.to_dict()
        self._save_configs(configs)
        
        return existing_config
    
    def delete_config(self, config_id: int) -> bool:
        """Delete a configuration"""
        configs = self._load_configs()
        
        if str(config_id) not in configs:
            return False
        
        # Remove logo file if exists
        config_data = configs[str(config_id)]
        if config_data.get('logo_url'):
            logo_path = config_data['logo_url'].replace('/uploads/', '')
            full_path = os.path.join(self.upload_dir, logo_path)
            if os.path.exists(full_path):
                os.remove(full_path)
        
        # Remove configuration
        del configs[str(config_id)]
        self._save_configs(configs)
        
        return True
    
    def upload_logo(self, config_id: int, file_data: bytes, filename: str) -> str:
        """Upload logo file and return URL"""
        # Validate file type
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.svg', '.gif'}
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise ValueError(f"Invalid file type. Allowed: {', '.join(allowed_extensions)}")
        
        # Generate unique filename
        timestamp = int(datetime.now().timestamp())
        safe_filename = f"logo_{config_id}_{timestamp}{file_ext}"
        file_path = os.path.join(self.upload_dir, safe_filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Return URL
        return f"/uploads/logos/{safe_filename}"
    
    def get_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get all available report templates"""
        return ReportTemplate.list_templates()
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get specific template configuration"""
        return ReportTemplate.get_template(template_id)
    
    def apply_branding_to_html(self, html_content: str, config: WhiteLabelConfig) -> str:
        """Apply white label branding to HTML content"""
        # Replace placeholders with actual values
        replacements = {
            '{{COMPANY_NAME}}': config.company_name,
            '{{LOGO_URL}}': config.logo_url,
            '{{PRIMARY_COLOR}}': config.primary_color,
            '{{SECONDARY_COLOR}}': config.secondary_color,
            '{{ACCENT_COLOR}}': config.accent_color,
            '{{FONT_FAMILY}}': config.font_family,
            '{{FOOTER_TEXT}}': config.footer_text,
            '{{CUSTOM_CSS}}': config.get_css_variables(),
            '{{POWERED_BY}}': '' if not config.show_powered_by else 'Powered by SEO Analyzer Pro'
        }
        
        branded_html = html_content
        for placeholder, value in replacements.items():
            branded_html = branded_html.replace(placeholder, str(value))
        
        return branded_html
    
    def generate_preview_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate preview configuration for testing"""
        preview_config = WhiteLabelConfig.from_dict(config_data)
        
        return {
            'css_variables': preview_config.get_css_variables(),
            'company_name': preview_config.company_name,
            'logo_url': preview_config.logo_url,
            'footer_text': preview_config.footer_text,
            'show_powered_by': preview_config.show_powered_by
        }

