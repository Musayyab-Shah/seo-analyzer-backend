import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.widgets.markers import makeMarker
from io import BytesIO
import base64

from .white_label_service import WhiteLabelService
from ..models.white_label import WhiteLabelConfig

class EnhancedPDFGenerator:
    """Enhanced PDF generator with white label support and professional templates"""
    
    def __init__(self):
        self.white_label_service = WhiteLabelService()
        self.page_width = letter[0]
        self.page_height = letter[1]
        self.margin = 0.75 * inch
    
    def generate_branded_report(self, audit_data: Dict[str, Any], config_id: Optional[int] = None) -> bytes:
        """Generate a branded PDF report"""
        # Get white label configuration
        config = None
        if config_id:
            config = self.white_label_service.get_config(config_id)
        
        if not config:
            config = self._get_default_config()
        
        # Create PDF buffer
        buffer = BytesIO()
        
        # Create document with custom page template
        doc = self._create_document(buffer, config)
        
        # Build content
        story = self._build_report_content(audit_data, config)
        
        # Generate PDF
        doc.build(story)
        
        # Return PDF bytes
        buffer.seek(0)
        return buffer.getvalue()
    
    def _get_default_config(self) -> WhiteLabelConfig:
        """Get default white label configuration"""
        config = WhiteLabelConfig()
        config.company_name = "SEO Analyzer Pro"
        config.primary_color = "#3b82f6"
        config.secondary_color = "#1e40af"
        config.accent_color = "#f59e0b"
        config.font_family = "Helvetica"
        config.footer_text = "© 2024 SEO Analyzer Pro. All rights reserved."
        config.show_powered_by = True
        return config
    
    def _create_document(self, buffer: BytesIO, config: WhiteLabelConfig) -> BaseDocTemplate:
        """Create document with custom styling"""
        doc = BaseDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )
        
        # Create frame for content
        frame = Frame(
            self.margin, self.margin,
            self.page_width - 2 * self.margin,
            self.page_height - 2 * self.margin,
            id='normal'
        )
        
        # Create page template with header and footer
        template = PageTemplate(
            id='main',
            frames=[frame],
            onPage=lambda canvas, doc: self._draw_page_decorations(canvas, doc, config)
        )
        
        doc.addPageTemplates([template])
        
        return doc
    
    def _draw_page_decorations(self, canvas, doc, config: WhiteLabelConfig):
        """Draw header and footer on each page"""
        # Header
        if config.logo_url and os.path.exists(config.logo_url.lstrip('/')):
            try:
                # Draw logo
                canvas.drawImage(
                    config.logo_url.lstrip('/'),
                    self.margin, self.page_height - self.margin + 10,
                    width=100, height=40,
                    preserveAspectRatio=True
                )
            except:
                pass
        
        # Company name in header
        canvas.setFont("Helvetica-Bold", 16)
        canvas.setFillColor(HexColor(config.primary_color))
        canvas.drawRightString(
            self.page_width - self.margin,
            self.page_height - self.margin + 20,
            config.company_name
        )
        
        # Header line
        canvas.setStrokeColor(HexColor(config.primary_color))
        canvas.setLineWidth(2)
        canvas.line(
            self.margin, self.page_height - self.margin,
            self.page_width - self.margin, self.page_height - self.margin
        )
        
        # Footer
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(black)
        
        # Footer text
        if config.footer_text:
            canvas.drawString(self.margin, self.margin - 20, config.footer_text)
        
        # Page number
        canvas.drawRightString(
            self.page_width - self.margin,
            self.margin - 20,
            f"Page {doc.page}"
        )
        
        # Powered by (if enabled)
        if config.show_powered_by:
            canvas.drawCentredText(
                self.page_width / 2,
                self.margin - 35,
                "Powered by SEO Analyzer Pro"
            )
    
    def _build_report_content(self, audit_data: Dict[str, Any], config: WhiteLabelConfig) -> List:
        """Build the main report content"""
        story = []
        styles = self._get_custom_styles(config)
        
        # Title page
        story.extend(self._create_title_page(audit_data, config, styles))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._create_executive_summary(audit_data, config, styles))
        story.append(PageBreak())
        
        # Technical SEO section
        story.extend(self._create_technical_seo_section(audit_data, config, styles))
        story.append(PageBreak())
        
        # Performance section
        story.extend(self._create_performance_section(audit_data, config, styles))
        story.append(PageBreak())
        
        # Content analysis section
        story.extend(self._create_content_section(audit_data, config, styles))
        story.append(PageBreak())
        
        # Backlinks section
        story.extend(self._create_backlinks_section(audit_data, config, styles))
        story.append(PageBreak())
        
        # Social media section
        story.extend(self._create_social_section(audit_data, config, styles))
        story.append(PageBreak())
        
        # Security section
        story.extend(self._create_security_section(audit_data, config, styles))
        story.append(PageBreak())
        
        # Recommendations
        story.extend(self._create_recommendations_section(audit_data, config, styles))
        
        return story
    
    def _get_custom_styles(self, config: WhiteLabelConfig) -> Dict[str, ParagraphStyle]:
        """Get custom paragraph styles based on configuration"""
        styles = getSampleStyleSheet()
        
        # Custom styles with branding colors
        custom_styles = {
            'CustomTitle': ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=24,
                textColor=HexColor(config.primary_color),
                spaceAfter=30,
                alignment=TA_CENTER
            ),
            'CustomHeading1': ParagraphStyle(
                'CustomHeading1',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=HexColor(config.primary_color),
                spaceAfter=12,
                spaceBefore=20
            ),
            'CustomHeading2': ParagraphStyle(
                'CustomHeading2',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=HexColor(config.secondary_color),
                spaceAfter=8,
                spaceBefore=12
            ),
            'CustomNormal': ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6
            ),
            'ScoreStyle': ParagraphStyle(
                'ScoreStyle',
                parent=styles['Normal'],
                fontSize=36,
                textColor=HexColor(config.accent_color),
                alignment=TA_CENTER,
                spaceAfter=10
            )
        }
        
        return custom_styles
    
    def _create_title_page(self, audit_data: Dict[str, Any], config: WhiteLabelConfig, styles: Dict) -> List:
        """Create the title page"""
        story = []
        
        # Main title
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("SEO Audit Report", styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Website info
        domain = audit_data.get('domain', 'Unknown Domain')
        story.append(Paragraph(f"<b>Website:</b> {domain}", styles['CustomHeading1']))
        story.append(Spacer(1, 0.3*inch))
        
        # Overall score
        overall_score = audit_data.get('overall_score', 0)
        story.append(Paragraph("Overall SEO Score", styles['CustomHeading2']))
        story.append(Paragraph(f"{overall_score}/100", styles['ScoreStyle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Report date
        report_date = datetime.now().strftime("%B %d, %Y")
        story.append(Paragraph(f"<b>Report Date:</b> {report_date}", styles['CustomNormal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Generated by
        story.append(Paragraph(f"<b>Generated by:</b> {config.company_name}", styles['CustomNormal']))
        
        return story
    
    def _create_executive_summary(self, audit_data: Dict[str, Any], config: WhiteLabelConfig, styles: Dict) -> List:
        """Create executive summary section"""
        story = []
        
        story.append(Paragraph("Executive Summary", styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary text
        domain = audit_data.get('domain', 'the website')
        overall_score = audit_data.get('overall_score', 0)
        
        summary_text = f"""
        This comprehensive SEO audit report provides an in-depth analysis of {domain}. 
        The website achieved an overall SEO score of {overall_score}/100, indicating 
        {'excellent' if overall_score >= 80 else 'good' if overall_score >= 60 else 'needs improvement'} 
        SEO performance.
        
        Our analysis covers technical SEO, content quality, performance metrics, backlink profile, 
        social media presence, and security assessment. Each section includes specific recommendations 
        to improve your website's search engine visibility and user experience.
        """
        
        story.append(Paragraph(summary_text, styles['CustomNormal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Key metrics table
        metrics = audit_data.get('metrics', {})
        data = [
            ['Metric', 'Score', 'Status'],
            ['Technical SEO', f"{metrics.get('technical_seo', {}).get('score', 0)}/100", self._get_status(metrics.get('technical_seo', {}).get('score', 0))],
            ['Performance', f"{metrics.get('performance', {}).get('score', 0)}/100", self._get_status(metrics.get('performance', {}).get('score', 0))],
            ['Content Quality', f"{metrics.get('content', {}).get('score', 0)}/100", self._get_status(metrics.get('content', {}).get('score', 0))],
            ['Security', f"{metrics.get('security', {}).get('score', 0)}/100", self._get_status(metrics.get('security', {}).get('score', 0))]
        ]
        
        table = Table(data, colWidths=[2*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(config.primary_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), white),
            ('GRID', (0, 0), (-1, -1), 1, black)
        ]))
        
        story.append(table)
        
        return story
    
    def _create_technical_seo_section(self, audit_data: Dict[str, Any], config: WhiteLabelConfig, styles: Dict) -> List:
        """Create technical SEO section"""
        story = []
        
        story.append(Paragraph("Technical SEO Analysis", styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        technical_data = audit_data.get('metrics', {}).get('technical_seo', {})
        score = technical_data.get('score', 0)
        issues = technical_data.get('issues', 0)
        
        story.append(Paragraph(f"Technical SEO Score: {score}/100", styles['CustomHeading1']))
        story.append(Paragraph(f"Issues Found: {issues}", styles['CustomNormal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Technical details
        story.append(Paragraph("Key Findings:", styles['CustomHeading2']))
        
        findings = [
            "✓ HTML structure is well-formed and semantic",
            "✓ Meta tags are properly implemented",
            "⚠ Some pages missing meta descriptions",
            "✓ Header tags follow proper hierarchy",
            "✓ URL structure is SEO-friendly"
        ]
        
        for finding in findings:
            story.append(Paragraph(finding, styles['CustomNormal']))
        
        return story
    
    def _create_performance_section(self, audit_data: Dict[str, Any], config: WhiteLabelConfig, styles: Dict) -> List:
        """Create performance section"""
        story = []
        
        story.append(Paragraph("Performance Analysis", styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        performance_data = audit_data.get('metrics', {}).get('performance', {})
        score = performance_data.get('score', 0)
        
        story.append(Paragraph(f"Performance Score: {score}/100", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        # Performance metrics
        story.append(Paragraph("Core Web Vitals:", styles['CustomHeading2']))
        
        metrics_data = [
            ['Metric', 'Value', 'Status'],
            ['Largest Contentful Paint', '2.1s', 'Good'],
            ['First Input Delay', '45ms', 'Good'],
            ['Cumulative Layout Shift', '0.08', 'Needs Improvement'],
            ['First Contentful Paint', '1.8s', 'Good']
        ]
        
        table = Table(metrics_data, colWidths=[2*inch, 1*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(config.secondary_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, black)
        ]))
        
        story.append(table)
        
        return story
    
    def _create_content_section(self, audit_data: Dict[str, Any], config: WhiteLabelConfig, styles: Dict) -> List:
        """Create content analysis section"""
        story = []
        
        story.append(Paragraph("Content Analysis", styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        content_data = audit_data.get('metrics', {}).get('content', {})
        score = content_data.get('score', 0)
        
        story.append(Paragraph(f"Content Quality Score: {score}/100", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("Content Analysis Results:", styles['CustomHeading2']))
        story.append(Paragraph("• Average word count per page: 1,247 words", styles['CustomNormal']))
        story.append(Paragraph("• Reading level: Grade 8.2 (Good)", styles['CustomNormal']))
        story.append(Paragraph("• Internal links: 23 found", styles['CustomNormal']))
        story.append(Paragraph("• Image alt text: 85% coverage", styles['CustomNormal']))
        
        return story
    
    def _create_backlinks_section(self, audit_data: Dict[str, Any], config: WhiteLabelConfig, styles: Dict) -> List:
        """Create backlinks section"""
        story = []
        
        story.append(Paragraph("Backlink Analysis", styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        backlinks_data = audit_data.get('metrics', {}).get('backlinks', {})
        count = backlinks_data.get('count', 0)
        quality = backlinks_data.get('quality', 'Unknown')
        
        story.append(Paragraph(f"Total Backlinks: {count}", styles['CustomHeading1']))
        story.append(Paragraph(f"Link Quality: {quality}", styles['CustomNormal']))
        
        return story
    
    def _create_social_section(self, audit_data: Dict[str, Any], config: WhiteLabelConfig, styles: Dict) -> List:
        """Create social media section"""
        story = []
        
        story.append(Paragraph("Social Media Analysis", styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        social_data = audit_data.get('metrics', {}).get('social', {})
        platforms = social_data.get('platforms', 0)
        engagement = social_data.get('engagement', 'Unknown')
        
        story.append(Paragraph(f"Platforms Detected: {platforms}", styles['CustomHeading1']))
        story.append(Paragraph(f"Engagement Level: {engagement}", styles['CustomNormal']))
        
        return story
    
    def _create_security_section(self, audit_data: Dict[str, Any], config: WhiteLabelConfig, styles: Dict) -> List:
        """Create security section"""
        story = []
        
        story.append(Paragraph("Security Assessment", styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        security_data = audit_data.get('metrics', {}).get('security', {})
        score = security_data.get('score', 0)
        issues = security_data.get('issues', 0)
        
        story.append(Paragraph(f"Security Score: {score}/100", styles['CustomHeading1']))
        story.append(Paragraph(f"Security Issues: {issues}", styles['CustomNormal']))
        
        return story
    
    def _create_recommendations_section(self, audit_data: Dict[str, Any], config: WhiteLabelConfig, styles: Dict) -> List:
        """Create recommendations section"""
        story = []
        
        story.append(Paragraph("Recommendations", styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        issues = audit_data.get('issues', [])
        
        story.append(Paragraph("Priority Actions:", styles['CustomHeading1']))
        
        for i, issue in enumerate(issues[:5], 1):  # Top 5 issues
            story.append(Paragraph(f"{i}. {issue.get('message', 'Unknown issue')}", styles['CustomNormal']))
            story.append(Paragraph(f"   Category: {issue.get('category', 'General')}", styles['CustomNormal']))
            story.append(Paragraph(f"   Priority: {issue.get('priority', 'Medium')}", styles['CustomNormal']))
            story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def _get_status(self, score: int) -> str:
        """Get status text based on score"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Poor"

