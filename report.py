from flask import Blueprint, request, jsonify, send_file
from src.models.user import db
from src.models.audit import Audit, Report
from src.services.pdf_generator import PDFGenerator
import os
from datetime import datetime

report_bp = Blueprint('report', __name__)

@report_bp.route('/reports/generate', methods=['POST'])
def generate_report():
    """Generate a PDF report for an audit"""
    try:
        data = request.get_json()
        
        if not data or 'audit_id' not in data:
            return jsonify({'error': 'Audit ID is required'}), 400
        
        audit_id = data['audit_id']
        audit = Audit.query.get_or_404(audit_id)
        
        if audit.status != 'completed':
            return jsonify({'error': 'Audit must be completed to generate report'}), 400
        
        # Check if report already exists
        existing_report = Report.query.filter_by(
            audit_id=audit_id,
            report_type='pdf'
        ).first()
        
        if existing_report and os.path.exists(existing_report.file_path):
            return jsonify({
                'report_id': existing_report.id,
                'file_path': existing_report.file_path,
                'created_at': existing_report.created_at.isoformat(),
                'download_count': existing_report.download_count
            })
        
        # Generate new report
        pdf_generator = PDFGenerator()
        
        # Prepare report data
        report_data = {
            'audit': {
                'id': audit.id,
                'url': audit.url,
                'domain': audit.website.domain,
                'overall_score': audit.overall_score,
                'completed_at': audit.completed_at,
                'website_title': audit.website.title
            },
            'details': [],
            'seo_metrics': None,
            'performance_metrics': None,
            'security_scan': None
        }
        
        # Add audit details
        for detail in audit.audit_details:
            report_data['details'].append({
                'category': detail.category,
                'check_name': detail.check_name,
                'status': detail.status,
                'score': detail.score,
                'max_score': detail.max_score,
                'message': detail.message,
                'recommendation': detail.recommendation,
                'priority': detail.priority
            })
        
        # Add SEO metrics
        if audit.seo_metrics:
            seo = audit.seo_metrics
            report_data['seo_metrics'] = {
                'page_title': seo.page_title,
                'meta_description': seo.meta_description,
                'h1_tags': seo.get_h1_tags(),
                'images_count': seo.images_count,
                'images_without_alt': seo.images_without_alt,
                'internal_links': seo.internal_links,
                'external_links': seo.external_links,
                'word_count': seo.word_count,
                'mobile_friendly': seo.mobile_friendly,
                'ssl_enabled': seo.ssl_enabled
            }
        
        # Add performance metrics
        if audit.performance_metrics:
            perf = audit.performance_metrics
            report_data['performance_metrics'] = {
                'performance_score': perf.performance_score,
                'accessibility_score': perf.accessibility_score,
                'best_practices_score': perf.best_practices_score,
                'seo_score': perf.seo_score,
                'first_contentful_paint': perf.first_contentful_paint,
                'largest_contentful_paint': perf.largest_contentful_paint,
                'speed_index': perf.speed_index
            }
        
        # Add security scan
        if audit.security_scans:
            security = audit.security_scans
            report_data['security_scan'] = {
                'ssl_grade': security.ssl_grade,
                'malware_detected': security.malware_detected,
                'security_score': security.security_score
            }
        
        # Generate PDF
        file_path = pdf_generator.generate_report(report_data, data.get('white_label_settings'))
        
        # Get file size
        file_size_kb = os.path.getsize(file_path) // 1024
        
        # Save report record
        report = Report(
            audit_id=audit_id,
            report_type='pdf',
            file_path=file_path,
            file_size_kb=file_size_kb,
            white_label_id=data.get('white_label_id')
        )
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'report_id': report.id,
            'file_path': file_path,
            'file_size_kb': file_size_kb,
            'created_at': report.created_at.isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate report: {str(e)}'}), 500

@report_bp.route('/reports/<int:report_id>/download', methods=['GET'])
def download_report(report_id):
    """Download a generated report"""
    try:
        report = Report.query.get_or_404(report_id)
        
        if not os.path.exists(report.file_path):
            return jsonify({'error': 'Report file not found'}), 404
        
        # Increment download count
        report.download_count += 1
        db.session.commit()
        
        # Generate filename
        audit = report.audit
        filename = f"seo_report_{audit.website.domain}_{audit.id}.pdf"
        
        return send_file(
            report.file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'Failed to download report: {str(e)}'}), 500

@report_bp.route('/reports', methods=['GET'])
def list_reports():
    """List generated reports"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        reports = Report.query.order_by(Report.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        result = {
            'reports': [],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': reports.total,
                'pages': reports.pages,
                'has_next': reports.has_next,
                'has_prev': reports.has_prev
            }
        }
        
        for report in reports.items:
            audit = report.audit
            result['reports'].append({
                'id': report.id,
                'audit_id': audit.id,
                'domain': audit.website.domain,
                'url': audit.url,
                'overall_score': audit.overall_score,
                'report_type': report.report_type,
                'file_size_kb': report.file_size_kb,
                'download_count': report.download_count,
                'created_at': report.created_at.isoformat()
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Failed to list reports: {str(e)}'}), 500

@report_bp.route('/reports/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    """Delete a report and its file"""
    try:
        report = Report.query.get_or_404(report_id)
        
        # Delete file if it exists
        if os.path.exists(report.file_path):
            os.remove(report.file_path)
        
        # Delete database record
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({'message': 'Report deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': f'Failed to delete report: {str(e)}'}), 500

