from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.audit import Website, SecurityScan, Audit
from src.services.security_analyzer import SecurityAnalyzer
from datetime import datetime
import traceback

security_bp = Blueprint('security', __name__)

@security_bp.route('/security/analyze', methods=['POST'])
def analyze_security():
    """Perform security analysis for a website"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url'].strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Get or create website record
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower()
        
        website = Website.query.filter_by(domain=domain).first()
        if not website:
            website = Website(domain=domain)
            db.session.add(website)
            db.session.flush()
        
        # Perform security analysis
        analyzer = SecurityAnalyzer()
        result = analyzer.analyze_security(url)
        
        # Save security scan results if audit_id is provided
        audit_id = data.get('audit_id')
        if audit_id:
            audit = Audit.query.get(audit_id)
            if audit:
                # Save security scan to database
                security_scan = SecurityScan(
                    audit_id=audit_id,
                    ssl_grade=result['ssl_analysis']['grade'],
                    malware_detected=result['malware_scan']['malware_detected'],
                    security_score=result['overall_score']
                )
                
                # Set JSON fields
                security_scan.set_ssl_certificate(result['ssl_analysis'].get('certificate', {}))
                security_scan.set_blacklist_status(result['blacklist_check'])
                security_scan.set_security_headers(result['security_headers']['headers'])
                security_scan.set_vulnerabilities(result['vulnerability_scan']['vulnerabilities'])
                
                db.session.add(security_scan)
                db.session.commit()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Security analysis failed: {str(e)}'}), 500

@security_bp.route('/security/ssl-check', methods=['POST'])
def check_ssl():
    """Check SSL certificate details for a website"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url'].strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        analyzer = SecurityAnalyzer()
        ssl_result = analyzer._analyze_ssl(url)
        
        return jsonify({
            'url': url,
            'ssl_analysis': ssl_result,
            'analysis_date': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'SSL check failed: {str(e)}'}), 500

@security_bp.route('/security/headers-check', methods=['POST'])
def check_security_headers():
    """Check security headers for a website"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url'].strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        analyzer = SecurityAnalyzer()
        headers_result = analyzer._analyze_security_headers(url)
        
        return jsonify({
            'url': url,
            'security_headers': headers_result,
            'analysis_date': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Security headers check failed: {str(e)}'}), 500

@security_bp.route('/security/malware-scan', methods=['POST'])
def scan_malware():
    """Scan website for malware and malicious content"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url'].strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        analyzer = SecurityAnalyzer()
        malware_result = analyzer._scan_for_malware(url)
        
        return jsonify({
            'url': url,
            'malware_scan': malware_result,
            'analysis_date': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Malware scan failed: {str(e)}'}), 500

@security_bp.route('/security/vulnerability-scan', methods=['POST'])
def scan_vulnerabilities():
    """Scan website for common vulnerabilities"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url'].strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        analyzer = SecurityAnalyzer()
        vuln_result = analyzer._scan_vulnerabilities(url)
        
        return jsonify({
            'url': url,
            'vulnerability_scan': vuln_result,
            'analysis_date': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Vulnerability scan failed: {str(e)}'}), 500

@security_bp.route('/security/privacy-analysis', methods=['POST'])
def analyze_privacy():
    """Analyze privacy-related aspects of a website"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url'].strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        analyzer = SecurityAnalyzer()
        privacy_result = analyzer._analyze_privacy(url)
        
        return jsonify({
            'url': url,
            'privacy_analysis': privacy_result,
            'analysis_date': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Privacy analysis failed: {str(e)}'}), 500

@security_bp.route('/security/audit/<int:audit_id>', methods=['GET'])
def get_security_scan(audit_id):
    """Get security scan results for a specific audit"""
    try:
        audit = Audit.query.get_or_404(audit_id)
        security_scan = SecurityScan.query.filter_by(audit_id=audit_id).first()
        
        if not security_scan:
            return jsonify({'error': 'No security scan found for this audit'}), 404
        
        result = {
            'audit_id': audit_id,
            'website': {
                'id': audit.website.id,
                'domain': audit.website.domain,
                'url': audit.url
            },
            'security_scan': {
                'id': security_scan.id,
                'ssl_certificate': security_scan.get_ssl_certificate(),
                'ssl_grade': security_scan.ssl_grade,
                'ssl_expires_at': security_scan.ssl_expires_at.isoformat() if security_scan.ssl_expires_at else None,
                'malware_detected': security_scan.malware_detected,
                'blacklist_status': security_scan.get_blacklist_status(),
                'security_headers': security_scan.get_security_headers(),
                'vulnerabilities': security_scan.get_vulnerabilities(),
                'security_score': security_scan.security_score,
                'scan_timestamp': security_scan.scan_timestamp.isoformat()
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get security scan: {str(e)}'}), 500

@security_bp.route('/security/statistics', methods=['GET'])
def get_security_statistics():
    """Get security statistics across all scanned websites"""
    try:
        from sqlalchemy import func
        
        # Get overall statistics
        total_scans = SecurityScan.query.count()
        malware_detections = SecurityScan.query.filter_by(malware_detected=True).count()
        
        # Get SSL grade distribution
        ssl_grades = db.session.query(
            SecurityScan.ssl_grade,
            func.count(SecurityScan.id).label('count')
        ).group_by(SecurityScan.ssl_grade).all()
        
        # Get average security scores
        avg_security_score = db.session.query(
            func.avg(SecurityScan.security_score)
        ).scalar()
        
        # Get recent security scans
        recent_scans = db.session.query(SecurityScan, Audit, Website)\
            .join(Audit, SecurityScan.audit_id == Audit.id)\
            .join(Website, Audit.website_id == Website.id)\
            .order_by(SecurityScan.scan_timestamp.desc())\
            .limit(10).all()
        
        # Get security score distribution
        score_ranges = [
            ('90-100', SecurityScan.query.filter(SecurityScan.security_score >= 90).count()),
            ('80-89', SecurityScan.query.filter(SecurityScan.security_score.between(80, 89)).count()),
            ('70-79', SecurityScan.query.filter(SecurityScan.security_score.between(70, 79)).count()),
            ('60-69', SecurityScan.query.filter(SecurityScan.security_score.between(60, 69)).count()),
            ('0-59', SecurityScan.query.filter(SecurityScan.security_score < 60).count())
        ]
        
        result = {
            'total_scans': total_scans,
            'malware_detections': malware_detections,
            'malware_rate': round((malware_detections / total_scans * 100), 2) if total_scans > 0 else 0,
            'average_security_score': round(float(avg_security_score), 1) if avg_security_score else 0,
            'ssl_grade_distribution': [
                {'grade': grade, 'count': count}
                for grade, count in ssl_grades
            ],
            'security_score_distribution': [
                {'range': range_name, 'count': count}
                for range_name, count in score_ranges
            ],
            'recent_scans': [
                {
                    'scan_id': scan.id,
                    'domain': website.domain,
                    'security_score': scan.security_score,
                    'ssl_grade': scan.ssl_grade,
                    'malware_detected': scan.malware_detected,
                    'scan_timestamp': scan.scan_timestamp.isoformat()
                }
                for scan, audit, website in recent_scans
            ]
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get security statistics: {str(e)}'}), 500

@security_bp.route('/security/recommendations/<int:audit_id>', methods=['GET'])
def get_security_recommendations(audit_id):
    """Get security recommendations for a specific audit"""
    try:
        audit = Audit.query.get_or_404(audit_id)
        security_scan = SecurityScan.query.filter_by(audit_id=audit_id).first()
        
        if not security_scan:
            return jsonify({'error': 'No security scan found for this audit'}), 404
        
        recommendations = []
        
        # SSL recommendations
        if security_scan.ssl_grade in ['C', 'D', 'F']:
            recommendations.append({
                'type': 'ssl_improvement',
                'priority': 'high' if security_scan.ssl_grade == 'F' else 'medium',
                'title': 'Improve SSL Configuration',
                'description': f'Current SSL grade: {security_scan.ssl_grade}',
                'action': 'Update SSL configuration to use modern protocols and cipher suites'
            })
        
        # Malware recommendations
        if security_scan.malware_detected:
            recommendations.append({
                'type': 'malware_cleanup',
                'priority': 'critical',
                'title': 'Malware Detected',
                'description': 'Malicious content found on your website',
                'action': 'Immediately clean infected files and scan for vulnerabilities'
            })
        
        # Security headers recommendations
        security_headers = security_scan.get_security_headers()
        missing_headers = []
        
        important_headers = [
            'strict-transport-security',
            'content-security-policy',
            'x-frame-options',
            'x-content-type-options'
        ]
        
        for header in important_headers:
            if header not in security_headers:
                missing_headers.append(header)
        
        if missing_headers:
            recommendations.append({
                'type': 'security_headers',
                'priority': 'medium',
                'title': 'Add Security Headers',
                'description': f'Missing headers: {", ".join(missing_headers)}',
                'action': 'Implement missing security headers to improve protection'
            })
        
        # Vulnerability recommendations
        vulnerabilities = security_scan.get_vulnerabilities()
        high_severity_vulns = [v for v in vulnerabilities if v.get('severity') == 'high']
        
        if high_severity_vulns:
            recommendations.append({
                'type': 'vulnerability_fix',
                'priority': 'high',
                'title': 'Fix High Severity Vulnerabilities',
                'description': f'{len(high_severity_vulns)} high severity issues found',
                'action': 'Address high severity vulnerabilities immediately'
            })
        
        return jsonify({
            'audit_id': audit_id,
            'website': {
                'id': audit.website.id,
                'domain': audit.website.domain
            },
            'security_score': security_scan.security_score,
            'total_recommendations': len(recommendations),
            'recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get security recommendations: {str(e)}'}), 500

@security_bp.route('/security/export/<int:audit_id>', methods=['GET'])
def export_security_report(audit_id):
    """Export security analysis report as JSON"""
    try:
        audit = Audit.query.get_or_404(audit_id)
        security_scan = SecurityScan.query.filter_by(audit_id=audit_id).first()
        
        if not security_scan:
            return jsonify({'error': 'No security scan found for this audit'}), 404
        
        report_data = {
            'audit_info': {
                'audit_id': audit_id,
                'domain': audit.website.domain,
                'url': audit.url,
                'scan_date': security_scan.scan_timestamp.isoformat()
            },
            'security_analysis': {
                'overall_score': security_scan.security_score,
                'ssl_analysis': {
                    'grade': security_scan.ssl_grade,
                    'certificate': security_scan.get_ssl_certificate(),
                    'expires_at': security_scan.ssl_expires_at.isoformat() if security_scan.ssl_expires_at else None
                },
                'malware_scan': {
                    'malware_detected': security_scan.malware_detected,
                    'blacklist_status': security_scan.get_blacklist_status()
                },
                'security_headers': security_scan.get_security_headers(),
                'vulnerabilities': security_scan.get_vulnerabilities()
            },
            'generated_at': datetime.utcnow().isoformat()
        }
        
        from flask import Response
        import json
        
        return Response(
            json.dumps(report_data, indent=2),
            mimetype='application/json',
            headers={
                'Content-Disposition': f'attachment; filename=security_report_{audit.website.domain}_{audit_id}.json'
            }
        )
        
    except Exception as e:
        return jsonify({'error': f'Failed to export security report: {str(e)}'}), 500

