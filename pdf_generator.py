from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from datetime import datetime
import os

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#34495e'),
            borderWidth=1,
            borderColor=colors.HexColor('#3498db'),
            borderPadding=5,
            backColor=colors.HexColor('#ecf0f1')
        ))
        
        # Subheading style
        self.styles.add(ParagraphStyle(
            name='CustomSubheading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            textColor=colors.HexColor('#2c3e50')
        ))
        
        # Score style
        self.styles.add(ParagraphStyle(
            name='ScoreStyle',
            parent=self.styles['Normal'],
            fontSize=36,
            textColor=colors.HexColor('#27ae60'),
            alignment=TA_CENTER,
            spaceAfter=20
        ))
    
    def generate_report(self, report_data, white_label_settings=None):
        """Generate a comprehensive SEO report PDF"""
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        domain = report_data['audit']['domain'].replace('.', '_')
        filename = f"seo_report_{domain}_{timestamp}.pdf"
        file_path = os.path.join(reports_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build story (content)
        story = []
        
        # Add cover page
        self._add_cover_page(story, report_data, white_label_settings)
        
        # Add executive summary
        self._add_executive_summary(story, report_data)
        
        # Add detailed analysis
        self._add_detailed_analysis(story, report_data)
        
        # Add recommendations
        self._add_recommendations(story, report_data)
        
        # Add technical details
        self._add_technical_details(story, report_data)
        
        # Build PDF
        doc.build(story)
        
        return file_path
    
    def _add_cover_page(self, story, report_data, white_label_settings):
        """Add cover page to the report"""
        audit = report_data['audit']
        
        # Company logo and branding (if white label)
        if white_label_settings:
            # Add logo if provided
            if white_label_settings.get('logo_url'):
                # In a real implementation, you'd download and add the logo
                pass
            
            # Company name
            company_name = white_label_settings.get('brand_name', 'SEO Analyzer Pro')
        else:
            company_name = 'SEO Analyzer Pro'
        
        # Title
        story.append(Paragraph(f"SEO Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Website info
        story.append(Paragraph(f"<b>Website:</b> {audit['domain']}", self.styles['Normal']))
        story.append(Paragraph(f"<b>URL:</b> {audit['url']}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Analysis Date:</b> {audit['completed_at'].strftime('%B %d, %Y')}", self.styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Overall score
        score = audit['overall_score'] or 0
        score_color = self._get_score_color(score)
        story.append(Paragraph(f"Overall SEO Score", self.styles['CustomSubheading']))
        story.append(Paragraph(f"<font color='{score_color}'>{score}/100</font>", self.styles['ScoreStyle']))
        
        # Score interpretation
        interpretation = self._get_score_interpretation(score)
        story.append(Paragraph(interpretation, self.styles['Normal']))
        
        story.append(Spacer(1, 50))
        
        # Generated by
        story.append(Paragraph(f"Generated by {company_name}", self.styles['Normal']))
        story.append(Paragraph(f"Report ID: {audit['id']}", self.styles['Normal']))
        
        story.append(PageBreak())
    
    def _add_executive_summary(self, story, report_data):
        """Add executive summary section"""
        story.append(Paragraph("Executive Summary", self.styles['CustomHeading']))
        
        audit = report_data['audit']
        score = audit['overall_score'] or 0
        
        # Summary text
        summary_text = f"""
        This report provides a comprehensive SEO analysis of {audit['domain']}. 
        The website received an overall SEO score of {score}/100, indicating 
        {self._get_score_interpretation(score).lower()}.
        
        Our analysis examined over 50 SEO factors across multiple categories including 
        on-page optimization, technical SEO, content quality, performance, and mobile-friendliness.
        """
        
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Key metrics table
        if report_data.get('seo_metrics'):
            seo = report_data['seo_metrics']
            
            key_metrics_data = [
                ['Metric', 'Value', 'Status'],
                ['Page Title Length', f"{len(seo.get('page_title', ''))}" if seo.get('page_title') else 'Missing', 
                 '✓' if seo.get('page_title') and len(seo['page_title']) <= 60 else '⚠'],
                ['Meta Description', 'Present' if seo.get('meta_description') else 'Missing',
                 '✓' if seo.get('meta_description') else '✗'],
                ['SSL Certificate', 'Enabled' if seo.get('ssl_enabled') else 'Disabled',
                 '✓' if seo.get('ssl_enabled') else '✗'],
                ['Mobile Friendly', 'Yes' if seo.get('mobile_friendly') else 'No',
                 '✓' if seo.get('mobile_friendly') else '✗'],
                ['Page Load Time', f"{seo.get('load_time_ms', 0)}ms",
                 '✓' if seo.get('load_time_ms', 0) < 3000 else '⚠']
            ]
            
            key_metrics_table = Table(key_metrics_data, colWidths=[2*inch, 2*inch, 1*inch])
            key_metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(Paragraph("Key Metrics Overview", self.styles['CustomSubheading']))
            story.append(key_metrics_table)
        
        story.append(PageBreak())
    
    def _add_detailed_analysis(self, story, report_data):
        """Add detailed analysis section"""
        story.append(Paragraph("Detailed Analysis", self.styles['CustomHeading']))
        
        details = report_data.get('details', {})
        
        for category, checks in details.items():
            if not checks:
                continue
                
            # Category header
            category_title = category.replace('_', ' ').title()
            story.append(Paragraph(category_title, self.styles['CustomSubheading']))
            
            # Create table for checks
            table_data = [['Check', 'Status', 'Score', 'Message']]
            
            for check_name, check_data in checks.items():
                status_symbol = self._get_status_symbol(check_data.get('status', 'info'))
                score_text = f"{check_data.get('score', 0)}/{check_data.get('max_score', 0)}"
                message = check_data.get('message', '')
                
                # Truncate long messages
                if len(message) > 60:
                    message = message[:57] + '...'
                
                table_data.append([
                    check_name.replace('_', ' ').title(),
                    status_symbol,
                    score_text,
                    message
                ])
            
            # Create and style table
            table = Table(table_data, colWidths=[2*inch, 0.7*inch, 0.8*inch, 2.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (2, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
        
        story.append(PageBreak())
    
    def _add_recommendations(self, story, report_data):
        """Add recommendations section"""
        story.append(Paragraph("Recommendations", self.styles['CustomHeading']))
        
        # Collect all recommendations
        recommendations = []
        details = report_data.get('details', {})
        
        for category, checks in details.items():
            for check_name, check_data in checks.items():
                if check_data.get('recommendation') and check_data.get('status') in ['fail', 'warning']:
                    recommendations.append({
                        'priority': check_data.get('priority', 'medium'),
                        'check': check_name.replace('_', ' ').title(),
                        'recommendation': check_data['recommendation'],
                        'category': category.replace('_', ' ').title()
                    })
        
        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        if recommendations:
            # Group by priority
            current_priority = None
            for rec in recommendations:
                if rec['priority'] != current_priority:
                    current_priority = rec['priority']
                    priority_title = f"{current_priority.title()} Priority Issues"
                    story.append(Paragraph(priority_title, self.styles['CustomSubheading']))
                
                # Add recommendation
                rec_text = f"<b>{rec['check']} ({rec['category']}):</b> {rec['recommendation']}"
                story.append(Paragraph(rec_text, self.styles['Normal']))
                story.append(Spacer(1, 10))
        else:
            story.append(Paragraph("Great job! No critical issues were found.", self.styles['Normal']))
        
        story.append(PageBreak())
    
    def _add_technical_details(self, story, report_data):
        """Add technical details section"""
        story.append(Paragraph("Technical Details", self.styles['CustomHeading']))
        
        # SEO Metrics
        if report_data.get('seo_metrics'):
            story.append(Paragraph("SEO Metrics", self.styles['CustomSubheading']))
            seo = report_data['seo_metrics']
            
            seo_details = [
                ['Metric', 'Value'],
                ['Page Title', seo.get('page_title', 'Not found')],
                ['Meta Description', seo.get('meta_description', 'Not found')],
                ['H1 Tags', str(len(seo.get('h1_tags', [])))],
                ['Images Count', str(seo.get('images_count', 0))],
                ['Images without Alt', str(seo.get('images_without_alt', 0))],
                ['Internal Links', str(seo.get('internal_links', 0))],
                ['External Links', str(seo.get('external_links', 0))],
                ['Word Count', str(seo.get('word_count', 0))],
                ['Page Size', f"{seo.get('page_size_kb', 0):.1f} KB"],
                ['Load Time', f"{seo.get('load_time_ms', 0)} ms"]
            ]
            
            seo_table = Table(seo_details, colWidths=[2.5*inch, 3*inch])
            seo_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            
            story.append(seo_table)
            story.append(Spacer(1, 20))
        
        # Performance Metrics
        if report_data.get('performance_metrics'):
            story.append(Paragraph("Performance Metrics", self.styles['CustomSubheading']))
            perf = report_data['performance_metrics']
            
            perf_details = [
                ['Metric', 'Score'],
                ['Performance Score', f"{perf.get('performance_score', 0)}/100"],
                ['Accessibility Score', f"{perf.get('accessibility_score', 0)}/100"],
                ['Best Practices Score', f"{perf.get('best_practices_score', 0)}/100"],
                ['SEO Score', f"{perf.get('seo_score', 0)}/100"]
            ]
            
            perf_table = Table(perf_details, colWidths=[2.5*inch, 3*inch])
            perf_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            
            story.append(perf_table)
            story.append(Spacer(1, 20))
        
        # Security Information
        if report_data.get('security_scan'):
            story.append(Paragraph("Security Analysis", self.styles['CustomSubheading']))
            security = report_data['security_scan']
            
            security_details = [
                ['Security Aspect', 'Status'],
                ['SSL Grade', security.get('ssl_grade', 'Unknown')],
                ['Malware Detected', 'No' if not security.get('malware_detected') else 'Yes'],
                ['Security Score', f"{security.get('security_score', 0)}/100"]
            ]
            
            security_table = Table(security_details, colWidths=[2.5*inch, 3*inch])
            security_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            
            story.append(security_table)
    
    def _get_score_color(self, score):
        """Get color based on score"""
        if score >= 80:
            return '#27ae60'  # Green
        elif score >= 60:
            return '#f39c12'  # Orange
        else:
            return '#e74c3c'  # Red
    
    def _get_score_interpretation(self, score):
        """Get text interpretation of score"""
        if score >= 90:
            return "Excellent SEO performance with minimal issues to address."
        elif score >= 80:
            return "Good SEO performance with some room for improvement."
        elif score >= 60:
            return "Average SEO performance with several areas needing attention."
        elif score >= 40:
            return "Below average SEO performance requiring significant improvements."
        else:
            return "Poor SEO performance needing immediate attention across multiple areas."
    
    def _get_status_symbol(self, status):
        """Get symbol for status"""
        symbols = {
            'pass': '✓',
            'fail': '✗',
            'warning': '⚠',
            'info': 'ℹ'
        }
        return symbols.get(status, '?')

