from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.audit import Website, Backlink
from src.services.backlink_analyzer import BacklinkAnalyzer
from datetime import datetime
import traceback

backlink_bp = Blueprint('backlink', __name__)

@backlink_bp.route('/backlinks/analyze', methods=['POST'])
def analyze_backlinks():
    """Analyze backlinks for a website"""
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
        
        # Analyze backlinks
        analyzer = BacklinkAnalyzer()
        result = analyzer.analyze_backlinks(website.id, url)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Backlink analysis failed: {str(e)}'}), 500

@backlink_bp.route('/backlinks/website/<int:website_id>', methods=['GET'])
def get_website_backlinks(website_id):
    """Get backlinks for a specific website"""
    try:
        website = Website.query.get_or_404(website_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status_filter = request.args.get('status', 'all')
        
        query = Backlink.query.filter_by(website_id=website_id)
        
        if status_filter != 'all':
            query = query.filter_by(status=status_filter)
        
        backlinks = query.order_by(Backlink.discovered_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        result = {
            'website': {
                'id': website.id,
                'domain': website.domain
            },
            'backlinks': [],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': backlinks.total,
                'pages': backlinks.pages,
                'has_next': backlinks.has_next,
                'has_prev': backlinks.has_prev
            }
        }
        
        for backlink in backlinks.items:
            result['backlinks'].append({
                'id': backlink.id,
                'source_domain': backlink.source_domain,
                'source_url': backlink.source_url,
                'target_url': backlink.target_url,
                'anchor_text': backlink.anchor_text,
                'link_type': backlink.link_type,
                'status': backlink.status,
                'domain_authority': backlink.domain_authority,
                'page_authority': backlink.page_authority,
                'spam_score': backlink.spam_score,
                'discovered_date': backlink.discovered_date.isoformat(),
                'last_seen': backlink.last_seen.isoformat() if backlink.last_seen else None,
                'is_internal': backlink.is_internal
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get backlinks: {str(e)}'}), 500

@backlink_bp.route('/backlinks/metrics/<int:website_id>', methods=['GET'])
def get_backlink_metrics(website_id):
    """Get comprehensive backlink metrics for a website"""
    try:
        website = Website.query.get_or_404(website_id)
        
        analyzer = BacklinkAnalyzer()
        metrics = analyzer.get_backlink_metrics(website_id)
        
        return jsonify({
            'website': {
                'id': website.id,
                'domain': website.domain
            },
            'metrics': metrics
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get backlink metrics: {str(e)}'}), 500

@backlink_bp.route('/backlinks/competitors', methods=['POST'])
def analyze_competitor_backlinks():
    """Analyze competitor backlinks for opportunities"""
    try:
        data = request.get_json()
        
        if not data or 'website_id' not in data or 'competitor_urls' not in data:
            return jsonify({'error': 'Website ID and competitor URLs are required'}), 400
        
        website_id = data['website_id']
        competitor_urls = data['competitor_urls']
        
        if not isinstance(competitor_urls, list) or len(competitor_urls) == 0:
            return jsonify({'error': 'At least one competitor URL is required'}), 400
        
        website = Website.query.get_or_404(website_id)
        
        analyzer = BacklinkAnalyzer()
        opportunities = analyzer.monitor_competitor_backlinks(competitor_urls, website_id)
        
        return jsonify({
            'website': {
                'id': website.id,
                'domain': website.domain
            },
            'competitors_analyzed': len(competitor_urls),
            'opportunities': opportunities
        })
        
    except Exception as e:
        return jsonify({'error': f'Competitor analysis failed: {str(e)}'}), 500

@backlink_bp.route('/backlinks/domain-stats', methods=['GET'])
def get_domain_backlink_stats():
    """Get backlink statistics across all domains"""
    try:
        # Get top domains by backlink count
        from sqlalchemy import func
        
        top_domains = db.session.query(
            Website.domain,
            func.count(Backlink.id).label('backlink_count'),
            func.avg(Backlink.domain_authority).label('avg_domain_authority')
        ).join(Backlink).group_by(Website.domain)\
         .order_by(func.count(Backlink.id).desc()).limit(10).all()
        
        # Get recent backlink activity
        recent_backlinks = Backlink.query.order_by(Backlink.discovered_date.desc()).limit(20).all()
        
        # Calculate overall statistics
        total_backlinks = Backlink.query.count()
        active_backlinks = Backlink.query.filter_by(status='active').count()
        lost_backlinks = Backlink.query.filter_by(status='lost').count()
        
        result = {
            'total_backlinks': total_backlinks,
            'active_backlinks': active_backlinks,
            'lost_backlinks': lost_backlinks,
            'top_domains': [
                {
                    'domain': domain,
                    'backlink_count': count,
                    'avg_domain_authority': round(float(avg_da), 1) if avg_da else 0
                }
                for domain, count, avg_da in top_domains
            ],
            'recent_activity': [
                {
                    'id': bl.id,
                    'source_domain': bl.source_domain,
                    'target_domain': bl.website.domain,
                    'anchor_text': bl.anchor_text,
                    'status': bl.status,
                    'discovered_date': bl.discovered_date.isoformat()
                }
                for bl in recent_backlinks
            ]
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get domain stats: {str(e)}'}), 500

@backlink_bp.route('/backlinks/<int:backlink_id>', methods=['PUT'])
def update_backlink(backlink_id):
    """Update backlink information"""
    try:
        backlink = Backlink.query.get_or_404(backlink_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        if 'status' in data:
            backlink.status = data['status']
        if 'anchor_text' in data:
            backlink.anchor_text = data['anchor_text']
        if 'link_type' in data:
            backlink.link_type = data['link_type']
        if 'domain_authority' in data:
            backlink.domain_authority = data['domain_authority']
        if 'page_authority' in data:
            backlink.page_authority = data['page_authority']
        if 'spam_score' in data:
            backlink.spam_score = data['spam_score']
        
        backlink.last_seen = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'id': backlink.id,
            'status': backlink.status,
            'message': 'Backlink updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update backlink: {str(e)}'}), 500

@backlink_bp.route('/backlinks/<int:backlink_id>', methods=['DELETE'])
def delete_backlink(backlink_id):
    """Delete a backlink record"""
    try:
        backlink = Backlink.query.get_or_404(backlink_id)
        
        db.session.delete(backlink)
        db.session.commit()
        
        return jsonify({'message': 'Backlink deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete backlink: {str(e)}'}), 500

@backlink_bp.route('/backlinks/export/<int:website_id>', methods=['GET'])
def export_backlinks(website_id):
    """Export backlinks data as CSV"""
    try:
        website = Website.query.get_or_404(website_id)
        backlinks = Backlink.query.filter_by(website_id=website_id).all()
        
        # Create CSV data
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Source Domain', 'Source URL', 'Target URL', 'Anchor Text',
            'Link Type', 'Status', 'Domain Authority', 'Page Authority',
            'Spam Score', 'Discovered Date', 'Last Seen'
        ])
        
        # Write data
        for bl in backlinks:
            writer.writerow([
                bl.source_domain,
                bl.source_url,
                bl.target_url,
                bl.anchor_text or '',
                bl.link_type or '',
                bl.status,
                bl.domain_authority or '',
                bl.page_authority or '',
                bl.spam_score or '',
                bl.discovered_date.isoformat() if bl.discovered_date else '',
                bl.last_seen.isoformat() if bl.last_seen else ''
            ])
        
        output.seek(0)
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=backlinks_{website.domain}_{datetime.now().strftime("%Y%m%d")}.csv'
            }
        )
        
    except Exception as e:
        return jsonify({'error': f'Failed to export backlinks: {str(e)}'}), 500

