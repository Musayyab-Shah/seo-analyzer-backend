from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.audit import Website, Audit
from sqlalchemy import desc

website_bp = Blueprint('website', __name__)

@website_bp.route('/websites', methods=['GET'])
def list_websites():
    """List websites with their audit statistics"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        search = request.args.get('search', '').strip()
        
        query = Website.query
        
        if search:
            query = query.filter(Website.domain.contains(search))
        
        websites = query.order_by(desc(Website.last_analyzed)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        result = {
            'websites': [],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': websites.total,
                'pages': websites.pages,
                'has_next': websites.has_next,
                'has_prev': websites.has_prev
            }
        }
        
        for website in websites.items:
            # Get latest audit
            latest_audit = Audit.query.filter_by(website_id=website.id)\
                .order_by(desc(Audit.started_at)).first()
            
            result['websites'].append({
                'id': website.id,
                'domain': website.domain,
                'title': website.title,
                'description': website.description,
                'favicon_url': website.favicon_url,
                'first_analyzed': website.first_analyzed.isoformat() if website.first_analyzed else None,
                'last_analyzed': website.last_analyzed.isoformat() if website.last_analyzed else None,
                'total_audits': website.total_audits,
                'average_score': float(website.average_score) if website.average_score else None,
                'latest_audit': {
                    'id': latest_audit.id,
                    'overall_score': latest_audit.overall_score,
                    'status': latest_audit.status,
                    'started_at': latest_audit.started_at.isoformat()
                } if latest_audit else None
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Failed to list websites: {str(e)}'}), 500

@website_bp.route('/websites/<int:website_id>', methods=['GET'])
def get_website(website_id):
    """Get website details with audit history"""
    try:
        website = Website.query.get_or_404(website_id)
        
        # Get audit history
        audits = Audit.query.filter_by(website_id=website.id)\
            .order_by(desc(Audit.started_at)).limit(10).all()
        
        result = {
            'id': website.id,
            'domain': website.domain,
            'title': website.title,
            'description': website.description,
            'favicon_url': website.favicon_url,
            'first_analyzed': website.first_analyzed.isoformat() if website.first_analyzed else None,
            'last_analyzed': website.last_analyzed.isoformat() if website.last_analyzed else None,
            'total_audits': website.total_audits,
            'average_score': float(website.average_score) if website.average_score else None,
            'recent_audits': []
        }
        
        for audit in audits:
            result['recent_audits'].append({
                'id': audit.id,
                'url': audit.url,
                'overall_score': audit.overall_score,
                'status': audit.status,
                'started_at': audit.started_at.isoformat(),
                'completed_at': audit.completed_at.isoformat() if audit.completed_at else None
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get website: {str(e)}'}), 500

@website_bp.route('/websites/<int:website_id>/audits', methods=['GET'])
def get_website_audits(website_id):
    """Get all audits for a specific website"""
    try:
        website = Website.query.get_or_404(website_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        audits = Audit.query.filter_by(website_id=website.id)\
            .order_by(desc(Audit.started_at)).paginate(
                page=page, per_page=per_page, error_out=False
            )
        
        result = {
            'website': {
                'id': website.id,
                'domain': website.domain,
                'title': website.title
            },
            'audits': [],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': audits.total,
                'pages': audits.pages,
                'has_next': audits.has_next,
                'has_prev': audits.has_prev
            }
        }
        
        for audit in audits.items:
            result['audits'].append({
                'id': audit.id,
                'url': audit.url,
                'overall_score': audit.overall_score,
                'status': audit.status,
                'audit_type': audit.audit_type,
                'started_at': audit.started_at.isoformat(),
                'completed_at': audit.completed_at.isoformat() if audit.completed_at else None,
                'error_message': audit.error_message
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get website audits: {str(e)}'}), 500

@website_bp.route('/websites/stats', methods=['GET'])
def get_website_stats():
    """Get overall website statistics"""
    try:
        total_websites = Website.query.count()
        total_audits = Audit.query.count()
        completed_audits = Audit.query.filter_by(status='completed').count()
        failed_audits = Audit.query.filter_by(status='failed').count()
        
        # Get average scores
        avg_score_result = db.session.query(db.func.avg(Audit.overall_score))\
            .filter(Audit.overall_score.isnot(None)).scalar()
        
        # Get recent activity
        recent_audits = Audit.query.order_by(desc(Audit.started_at)).limit(5).all()
        
        result = {
            'total_websites': total_websites,
            'total_audits': total_audits,
            'completed_audits': completed_audits,
            'failed_audits': failed_audits,
            'success_rate': round((completed_audits / total_audits * 100), 2) if total_audits > 0 else 0,
            'average_score': round(float(avg_score_result), 2) if avg_score_result else 0,
            'recent_activity': []
        }
        
        for audit in recent_audits:
            result['recent_activity'].append({
                'id': audit.id,
                'domain': audit.website.domain,
                'url': audit.url,
                'overall_score': audit.overall_score,
                'status': audit.status,
                'started_at': audit.started_at.isoformat()
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get website stats: {str(e)}'}), 500

