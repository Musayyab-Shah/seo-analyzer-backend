from datetime import datetime
from typing import Optional, Dict, Any
import json

class WhiteLabelConfig:
    """White label configuration for branded reports and interface"""
    
    def __init__(self):
        self.id: Optional[int] = None
        self.user_id: Optional[int] = None
        self.company_name: str = ""
        self.logo_url: str = ""
        self.primary_color: str = "#3b82f6"
        self.secondary_color: str = "#1e40af"
        self.accent_color: str = "#f59e0b"
        self.font_family: str = "Inter"
        self.custom_css: str = ""
        self.footer_text: str = ""
        self.contact_info: Dict[str, Any] = {}
        self.social_links: Dict[str, str] = {}
        self.report_template: str = "professional"
        self.show_powered_by: bool = True
        self.custom_domain: str = ""
        self.created_at: Optional[datetime] = None
        self.updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'logo_url': self.logo_url,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'accent_color': self.accent_color,
            'font_family': self.font_family,
            'custom_css': self.custom_css,
            'footer_text': self.footer_text,
            'contact_info': self.contact_info,
            'social_links': self.social_links,
            'report_template': self.report_template,
            'show_powered_by': self.show_powered_by,
            'custom_domain': self.custom_domain,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WhiteLabelConfig':
        """Create instance from dictionary"""
        config = cls()
        config.id = data.get('id')
        config.user_id = data.get('user_id')
        config.company_name = data.get('company_name', '')
        config.logo_url = data.get('logo_url', '')
        config.primary_color = data.get('primary_color', '#3b82f6')
        config.secondary_color = data.get('secondary_color', '#1e40af')
        config.accent_color = data.get('accent_color', '#f59e0b')
        config.font_family = data.get('font_family', 'Inter')
        config.custom_css = data.get('custom_css', '')
        config.footer_text = data.get('footer_text', '')
        config.contact_info = data.get('contact_info', {})
        config.social_links = data.get('social_links', {})
        config.report_template = data.get('report_template', 'professional')
        config.show_powered_by = data.get('show_powered_by', True)
        config.custom_domain = data.get('custom_domain', '')
        
        if data.get('created_at'):
            config.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            config.updated_at = datetime.fromisoformat(data['updated_at'])
            
        return config
    
    def get_css_variables(self) -> str:
        """Generate CSS variables for theming"""
        return f"""
        :root {{
            --primary-color: {self.primary_color};
            --secondary-color: {self.secondary_color};
            --accent-color: {self.accent_color};
            --font-family: '{self.font_family}', sans-serif;
        }}
        
        {self.custom_css}
        """
    
    def validate(self) -> Dict[str, str]:
        """Validate configuration and return errors"""
        errors = {}
        
        if not self.company_name.strip():
            errors['company_name'] = 'Company name is required'
        
        # Validate color formats
        color_fields = ['primary_color', 'secondary_color', 'accent_color']
        for field in color_fields:
            color = getattr(self, field)
            if not color.startswith('#') or len(color) != 7:
                errors[field] = f'{field.replace("_", " ").title()} must be a valid hex color'
        
        return errors

class ReportTemplate:
    """Report template configuration"""
    
    TEMPLATES = {
        'professional': {
            'name': 'Professional',
            'description': 'Clean, corporate design perfect for client presentations',
            'layout': 'standard',
            'color_scheme': 'blue',
            'sections': [
                'executive_summary',
                'technical_seo',
                'performance',
                'content_analysis',
                'backlinks',
                'social_media',
                'security',
                'recommendations'
            ]
        },
        'modern': {
            'name': 'Modern',
            'description': 'Contemporary design with bold colors and graphics',
            'layout': 'grid',
            'color_scheme': 'gradient',
            'sections': [
                'executive_summary',
                'technical_seo',
                'performance',
                'content_analysis',
                'backlinks',
                'social_media',
                'security',
                'recommendations'
            ]
        },
        'minimal': {
            'name': 'Minimal',
            'description': 'Simple, clean layout focusing on data and insights',
            'layout': 'simple',
            'color_scheme': 'monochrome',
            'sections': [
                'executive_summary',
                'technical_seo',
                'performance',
                'recommendations'
            ]
        }
    }
    
    @classmethod
    def get_template(cls, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template configuration by ID"""
        return cls.TEMPLATES.get(template_id)
    
    @classmethod
    def list_templates(cls) -> Dict[str, Dict[str, Any]]:
        """List all available templates"""
        return cls.TEMPLATES

