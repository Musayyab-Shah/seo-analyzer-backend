import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

class LeadGenerationService:
    """Service for lead generation and conversion optimization"""
    
    def __init__(self):
        self.leads_file = "leads.json"
        self.email_templates_dir = "email_templates"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        os.makedirs(self.email_templates_dir, exist_ok=True)
    
    def _load_leads(self) -> Dict[str, Any]:
        """Load leads from file"""
        if not os.path.exists(self.leads_file):
            return {}
        
        try:
            with open(self.leads_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_leads(self, leads: Dict[str, Any]):
        """Save leads to file"""
        with open(self.leads_file, 'w') as f:
            json.dump(leads, f, indent=2, default=str)
    
    def capture_lead(self, email: str, source: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Capture a new lead"""
        leads = self._load_leads()
        
        # Generate lead ID
        lead_id = max([int(k) for k in leads.keys()] + [0]) + 1
        
        # Create lead record
        lead = {
            'id': lead_id,
            'email': email,
            'source': source,
            'status': 'new',
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'last_contact': None,
            'conversion_score': self._calculate_conversion_score(source, metadata),
            'tags': self._generate_tags(source, metadata)
        }
        
        # Check if email already exists
        existing_lead = self._find_lead_by_email(email)
        if existing_lead:
            # Update existing lead
            existing_lead['source'] = source
            existing_lead['metadata'].update(metadata or {})
            existing_lead['updated_at'] = datetime.now().isoformat()
            existing_lead['conversion_score'] = max(
                existing_lead.get('conversion_score', 0),
                lead['conversion_score']
            )
            existing_lead['tags'] = list(set(existing_lead.get('tags', []) + lead['tags']))
            
            leads[str(existing_lead['id'])] = existing_lead
            self._save_leads(leads)
            
            return existing_lead
        
        # Save new lead
        leads[str(lead_id)] = lead
        self._save_leads(leads)
        
        # Send welcome email
        self._send_welcome_email(lead)
        
        return lead
    
    def _find_lead_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find lead by email address"""
        leads = self._load_leads()
        
        for lead in leads.values():
            if lead.get('email', '').lower() == email.lower():
                return lead
        
        return None
    
    def _calculate_conversion_score(self, source: str, metadata: Optional[Dict[str, Any]]) -> int:
        """Calculate conversion score based on lead source and metadata"""
        score = 0
        
        # Base score by source
        source_scores = {
            'audit_form': 50,
            'pricing_page': 70,
            'contact_form': 60,
            'newsletter': 30,
            'free_trial': 80,
            'demo_request': 90,
            'whitepaper_download': 40,
            'webinar_signup': 65
        }
        
        score += source_scores.get(source, 25)
        
        if metadata:
            # Company size indicator
            if metadata.get('company_size') in ['51-200', '201-500', '500+']:
                score += 20
            
            # Industry relevance
            relevant_industries = ['marketing', 'advertising', 'digital agency', 'seo', 'web development']
            if any(industry in metadata.get('industry', '').lower() for industry in relevant_industries):
                score += 15
            
            # Budget indicator
            if metadata.get('budget') in ['$1000-5000', '$5000+']:
                score += 25
            
            # Urgency
            if metadata.get('urgency') in ['immediate', 'within_month']:
                score += 20
            
            # Website traffic
            if metadata.get('monthly_traffic', 0) > 10000:
                score += 10
        
        return min(score, 100)  # Cap at 100
    
    def _generate_tags(self, source: str, metadata: Optional[Dict[str, Any]]) -> List[str]:
        """Generate tags for lead categorization"""
        tags = [source]
        
        if metadata:
            # Add company size tag
            if metadata.get('company_size'):
                tags.append(f"company_{metadata['company_size'].replace('-', '_').replace('+', 'plus')}")
            
            # Add industry tag
            if metadata.get('industry'):
                tags.append(f"industry_{metadata['industry'].lower().replace(' ', '_')}")
            
            # Add budget tag
            if metadata.get('budget'):
                tags.append(f"budget_{metadata['budget'].replace('$', '').replace('-', '_').replace('+', 'plus')}")
            
            # Add urgency tag
            if metadata.get('urgency'):
                tags.append(f"urgency_{metadata['urgency']}")
        
        return tags
    
    def update_lead_status(self, lead_id: int, status: str, notes: Optional[str] = None) -> bool:
        """Update lead status"""
        leads = self._load_leads()
        
        if str(lead_id) not in leads:
            return False
        
        lead = leads[str(lead_id)]
        lead['status'] = status
        lead['updated_at'] = datetime.now().isoformat()
        
        if notes:
            if 'notes' not in lead:
                lead['notes'] = []
            lead['notes'].append({
                'note': notes,
                'created_at': datetime.now().isoformat()
            })
        
        leads[str(lead_id)] = lead
        self._save_leads(leads)
        
        return True
    
    def get_leads(self, status: Optional[str] = None, source: Optional[str] = None, 
                  limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get leads with optional filtering"""
        leads = self._load_leads()
        lead_list = list(leads.values())
        
        # Apply filters
        if status:
            lead_list = [lead for lead in lead_list if lead.get('status') == status]
        
        if source:
            lead_list = [lead for lead in lead_list if lead.get('source') == source]
        
        # Sort by conversion score and creation date
        lead_list.sort(
            key=lambda x: (x.get('conversion_score', 0), x.get('created_at', '')),
            reverse=True
        )
        
        # Apply limit
        if limit:
            lead_list = lead_list[:limit]
        
        return lead_list
    
    def get_lead_analytics(self) -> Dict[str, Any]:
        """Get lead generation analytics"""
        leads = self._load_leads()
        lead_list = list(leads.values())
        
        if not lead_list:
            return {
                'total_leads': 0,
                'conversion_rate': 0,
                'avg_conversion_score': 0,
                'leads_by_source': {},
                'leads_by_status': {},
                'monthly_growth': 0
            }
        
        # Calculate metrics
        total_leads = len(lead_list)
        converted_leads = len([lead for lead in lead_list if lead.get('status') == 'converted'])
        conversion_rate = (converted_leads / total_leads) * 100 if total_leads > 0 else 0
        
        avg_conversion_score = sum(lead.get('conversion_score', 0) for lead in lead_list) / total_leads
        
        # Group by source
        leads_by_source = {}
        for lead in lead_list:
            source = lead.get('source', 'unknown')
            leads_by_source[source] = leads_by_source.get(source, 0) + 1
        
        # Group by status
        leads_by_status = {}
        for lead in lead_list:
            status = lead.get('status', 'unknown')
            leads_by_status[status] = leads_by_status.get(status, 0) + 1
        
        # Calculate monthly growth (simplified)
        current_month_leads = len([
            lead for lead in lead_list
            if lead.get('created_at', '').startswith(datetime.now().strftime('%Y-%m'))
        ])
        
        return {
            'total_leads': total_leads,
            'conversion_rate': round(conversion_rate, 2),
            'avg_conversion_score': round(avg_conversion_score, 2),
            'leads_by_source': leads_by_source,
            'leads_by_status': leads_by_status,
            'current_month_leads': current_month_leads,
            'high_value_leads': len([lead for lead in lead_list if lead.get('conversion_score', 0) >= 70])
        }
    
    def _send_welcome_email(self, lead: Dict[str, Any]) -> bool:
        """Send welcome email to new lead"""
        try:
            # In a real implementation, you would use a proper email service
            # For demo purposes, we'll just log the email
            email_content = self._generate_welcome_email(lead)
            
            # Log email (in production, send via SMTP or email service)
            print(f"Welcome email sent to {lead['email']}")
            print(f"Subject: {email_content['subject']}")
            print(f"Body: {email_content['body'][:100]}...")
            
            return True
            
        except Exception as e:
            print(f"Failed to send welcome email: {str(e)}")
            return False
    
    def _generate_welcome_email(self, lead: Dict[str, Any]) -> Dict[str, str]:
        """Generate welcome email content"""
        source = lead.get('source', 'website')
        
        if source == 'audit_form':
            subject = "Your SEO Audit is Ready!"
            body = f"""
            Hi there,
            
            Thank you for requesting an SEO audit! We've analyzed your website and found some interesting insights.
            
            Here's what we discovered:
            • Technical SEO opportunities
            • Content optimization suggestions
            • Performance improvements
            
            Ready to see the full report? Click here to view your detailed analysis.
            
            Best regards,
            The SEO Analyzer Pro Team
            """
        elif source == 'pricing_page':
            subject = "Ready to Boost Your SEO?"
            body = f"""
            Hi there,
            
            Thanks for your interest in SEO Analyzer Pro! We're excited to help you improve your website's search rankings.
            
            As a special welcome offer, you can start with a 14-day free trial of our Professional plan.
            
            What you'll get:
            • 50 SEO audits per month
            • Advanced backlink monitoring
            • White-label reports
            • Priority support
            
            Start your free trial today!
            
            Best regards,
            The SEO Analyzer Pro Team
            """
        else:
            subject = "Welcome to SEO Analyzer Pro!"
            body = f"""
            Hi there,
            
            Welcome to SEO Analyzer Pro! We're thrilled to have you join our community of SEO professionals.
            
            Here are some resources to get you started:
            • Free SEO audit tool
            • SEO best practices guide
            • Video tutorials
            
            If you have any questions, don't hesitate to reach out!
            
            Best regards,
            The SEO Analyzer Pro Team
            """
        
        return {
            'subject': subject,
            'body': body.strip()
        }
    
    def create_lead_magnet_form(self, form_type: str, title: str, description: str, 
                               fields: List[Dict[str, str]]) -> Dict[str, Any]:
        """Create a lead magnet form configuration"""
        form_config = {
            'type': form_type,
            'title': title,
            'description': description,
            'fields': fields,
            'created_at': datetime.now().isoformat(),
            'conversion_tracking': {
                'views': 0,
                'submissions': 0,
                'conversion_rate': 0
            }
        }
        
        return form_config
    
    def track_form_view(self, form_id: str) -> None:
        """Track form view for analytics"""
        # In a real implementation, this would update form analytics
        pass
    
    def track_form_submission(self, form_id: str, lead_data: Dict[str, Any]) -> None:
        """Track form submission and capture lead"""
        # Capture the lead
        email = lead_data.get('email')
        if email:
            self.capture_lead(
                email=email,
                source=f"form_{form_id}",
                metadata=lead_data
            )
        
        # Update form analytics
        # In a real implementation, this would update conversion tracking

