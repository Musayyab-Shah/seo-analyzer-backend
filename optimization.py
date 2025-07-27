from flask import Blueprint, request, jsonify
from datetime import datetime

from ..services.cache_service import cache, seo_cache
from ..services.lead_generation_service import LeadGenerationService

optimization_bp = Blueprint('optimization', __name__, url_prefix='/api/optimization')

lead_service = LeadGenerationService()

@optimization_bp.route('/cache/stats', methods=['GET'])
def get_cache_stats():
    """Get cache statistics"""
    try:
        stats = cache.get_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get cache stats: {str(e)}'
        }), 500

@optimization_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear cache"""
    try:
        cache.clear()
        
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to clear cache: {str(e)}'
        }), 500

@optimization_bp.route('/cache/cleanup', methods=['POST'])
def cleanup_cache():
    """Clean up expired cache entries"""
    try:
        expired_count = cache.cleanup_expired()
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {expired_count} expired entries'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to cleanup cache: {str(e)}'
        }), 500

@optimization_bp.route('/leads/capture', methods=['POST'])
def capture_lead():
    """Capture a new lead"""
    try:
        data = request.get_json()
        
        email = data.get('email')
        source = data.get('source', 'website')
        metadata = data.get('metadata', {})
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        # Capture lead
        lead = lead_service.capture_lead(email, source, metadata)
        
        return jsonify({
            'success': True,
            'lead': lead
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to capture lead: {str(e)}'
        }), 500

@optimization_bp.route('/leads', methods=['GET'])
def get_leads():
    """Get leads with optional filtering"""
    try:
        status = request.args.get('status')
        source = request.args.get('source')
        limit = request.args.get('limit', type=int)
        
        leads = lead_service.get_leads(status=status, source=source, limit=limit)
        
        return jsonify({
            'success': True,
            'leads': leads,
            'count': len(leads)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get leads: {str(e)}'
        }), 500

@optimization_bp.route('/leads/<int:lead_id>/status', methods=['PUT'])
def update_lead_status(lead_id):
    """Update lead status"""
    try:
        data = request.get_json()
        
        status = data.get('status')
        notes = data.get('notes')
        
        if not status:
            return jsonify({
                'success': False,
                'error': 'Status is required'
            }), 400
        
        success = lead_service.update_lead_status(lead_id, status, notes)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Lead not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Lead status updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to update lead status: {str(e)}'
        }), 500

@optimization_bp.route('/leads/analytics', methods=['GET'])
def get_lead_analytics():
    """Get lead generation analytics"""
    try:
        analytics = lead_service.get_lead_analytics()
        
        return jsonify({
            'success': True,
            'analytics': analytics
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get lead analytics: {str(e)}'
        }), 500

@optimization_bp.route('/forms/lead-magnet', methods=['POST'])
def create_lead_magnet_form():
    """Create a lead magnet form"""
    try:
        data = request.get_json()
        
        form_type = data.get('type', 'newsletter')
        title = data.get('title', 'Subscribe to our newsletter')
        description = data.get('description', 'Get the latest SEO tips and insights')
        fields = data.get('fields', [
            {'name': 'email', 'type': 'email', 'label': 'Email Address', 'required': True}
        ])
        
        form_config = lead_service.create_lead_magnet_form(
            form_type=form_type,
            title=title,
            description=description,
            fields=fields
        )
        
        return jsonify({
            'success': True,
            'form': form_config
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to create form: {str(e)}'
        }), 500

@optimization_bp.route('/forms/<form_id>/submit', methods=['POST'])
def submit_lead_form(form_id):
    """Submit a lead generation form"""
    try:
        data = request.get_json()
        
        # Track form submission
        lead_service.track_form_submission(form_id, data)
        
        return jsonify({
            'success': True,
            'message': 'Form submitted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to submit form: {str(e)}'
        }), 500

@optimization_bp.route('/performance/metrics', methods=['GET'])
def get_performance_metrics():
    """Get application performance metrics"""
    try:
        # Simulate performance metrics
        metrics = {
            'response_times': {
                'avg_response_time': 245,  # ms
                'p95_response_time': 450,  # ms
                'p99_response_time': 800   # ms
            },
            'throughput': {
                'requests_per_second': 125,
                'requests_per_minute': 7500
            },
            'error_rates': {
                'error_rate': 0.02,  # 2%
                'success_rate': 0.98  # 98%
            },
            'resource_usage': {
                'cpu_usage': 35,      # %
                'memory_usage': 68,   # %
                'disk_usage': 45      # %
            },
            'cache_performance': cache.get_stats(),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get performance metrics: {str(e)}'
        }), 500

@optimization_bp.route('/seo/optimize-content', methods=['POST'])
def optimize_content():
    """Optimize content for SEO and conversion"""
    try:
        data = request.get_json()
        
        content = data.get('content', '')
        target_keywords = data.get('keywords', [])
        content_type = data.get('type', 'blog_post')
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'Content is required'
            }), 400
        
        # Simulate content optimization
        optimization_suggestions = {
            'seo_score': 78,
            'readability_score': 85,
            'keyword_density': {
                keyword: round(content.lower().count(keyword.lower()) / len(content.split()) * 100, 2)
                for keyword in target_keywords
            },
            'suggestions': [
                {
                    'type': 'seo',
                    'priority': 'high',
                    'message': 'Add target keyword to the first paragraph',
                    'impact': 'Improves keyword relevance and ranking potential'
                },
                {
                    'type': 'readability',
                    'priority': 'medium',
                    'message': 'Break up long paragraphs for better readability',
                    'impact': 'Reduces bounce rate and improves user engagement'
                },
                {
                    'type': 'conversion',
                    'priority': 'high',
                    'message': 'Add a clear call-to-action at the end',
                    'impact': 'Increases conversion rate and lead generation'
                }
            ],
            'optimized_title_suggestions': [
                f"Ultimate Guide to {target_keywords[0] if target_keywords else 'SEO'} in 2024",
                f"How to Master {target_keywords[0] if target_keywords else 'SEO'}: Complete Tutorial",
                f"{target_keywords[0].title() if target_keywords else 'SEO'} Best Practices That Actually Work"
            ],
            'meta_description_suggestion': f"Learn {target_keywords[0] if target_keywords else 'SEO'} best practices with our comprehensive guide. Improve your rankings and drive more traffic to your website."
        }
        
        return jsonify({
            'success': True,
            'optimization': optimization_suggestions
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to optimize content: {str(e)}'
        }), 500

@optimization_bp.route('/conversion/ab-test', methods=['POST'])
def create_ab_test():
    """Create an A/B test for conversion optimization"""
    try:
        data = request.get_json()
        
        test_name = data.get('name', 'Untitled Test')
        element_type = data.get('element_type', 'button')
        variants = data.get('variants', [])
        
        if len(variants) < 2:
            return jsonify({
                'success': False,
                'error': 'At least 2 variants are required for A/B testing'
            }), 400
        
        # Create A/B test configuration
        ab_test = {
            'id': f"test_{int(datetime.now().timestamp())}",
            'name': test_name,
            'element_type': element_type,
            'variants': variants,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'traffic_split': 100 // len(variants),  # Equal split
            'metrics': {
                'impressions': 0,
                'conversions': 0,
                'conversion_rate': 0
            }
        }
        
        return jsonify({
            'success': True,
            'test': ab_test
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to create A/B test: {str(e)}'
        }), 500

@optimization_bp.route('/conversion/cro-suggestions', methods=['GET'])
def get_cro_suggestions():
    """Get conversion rate optimization suggestions"""
    try:
        page_type = request.args.get('page_type', 'landing_page')
        
        # Generate CRO suggestions based on page type
        suggestions = {
            'landing_page': [
                {
                    'element': 'headline',
                    'suggestion': 'Make headline more specific and benefit-focused',
                    'impact': 'high',
                    'effort': 'low'
                },
                {
                    'element': 'cta_button',
                    'suggestion': 'Use action-oriented text like "Start Free Trial"',
                    'impact': 'high',
                    'effort': 'low'
                },
                {
                    'element': 'social_proof',
                    'suggestion': 'Add customer testimonials or logos',
                    'impact': 'medium',
                    'effort': 'medium'
                },
                {
                    'element': 'form',
                    'suggestion': 'Reduce form fields to essential information only',
                    'impact': 'high',
                    'effort': 'low'
                }
            ],
            'pricing_page': [
                {
                    'element': 'pricing_table',
                    'suggestion': 'Highlight most popular plan with visual emphasis',
                    'impact': 'high',
                    'effort': 'low'
                },
                {
                    'element': 'features',
                    'suggestion': 'Focus on benefits rather than features',
                    'impact': 'medium',
                    'effort': 'medium'
                },
                {
                    'element': 'guarantee',
                    'suggestion': 'Add money-back guarantee or free trial',
                    'impact': 'high',
                    'effort': 'low'
                }
            ]
        }
        
        page_suggestions = suggestions.get(page_type, suggestions['landing_page'])
        
        return jsonify({
            'success': True,
            'suggestions': page_suggestions,
            'page_type': page_type
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get CRO suggestions: {str(e)}'
        }), 500

# Error handlers
@optimization_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@optimization_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Method not allowed'
    }), 405

@optimization_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

