import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Enable CORS for all routes
CORS(app, origins="*")

# Simple API endpoints for demo
@app.route('/api/audit/health', methods=['GET'])
def health_check():
    return jsonify({
        'success': True,
        'message': 'SEO Analyzer Pro API is running',
        'version': '1.0.0'
    })

@app.route('/api/audit/analyze', methods=['POST'])
def analyze_website():
    return jsonify({
        'success': True,
        'analysis': {
            'domain': 'example.com',
            'overall_score': 78,
            'metrics': {
                'technical_seo': {'score': 85, 'issues': 3},
                'performance': {'score': 72, 'issues': 5},
                'content': {'score': 80, 'issues': 2},
                'backlinks': {'count': 156, 'quality': 'Good'},
                'social': {'platforms': 4, 'engagement': 'Medium'},
                'security': {'score': 90, 'issues': 1}
            },
            'issues': [
                {'type': 'error', 'category': 'Performance', 'message': 'Large images not optimized', 'priority': 'high'},
                {'type': 'warning', 'category': 'Technical SEO', 'message': 'Missing meta description on 3 pages', 'priority': 'medium'}
            ]
        }
    })

@app.route('/api/payment/plans', methods=['GET'])
def get_pricing_plans():
    plans = {
        'starter': {
            'name': 'Starter',
            'description': 'Perfect for small businesses and freelancers',
            'monthly_price': 29,
            'annual_price': 290,
            'features': [
                '10 SEO audits per month',
                'Basic backlink monitoring',
                'Social media analysis',
                'Security scanning',
                'Email support',
                'PDF reports'
            ]
        },
        'professional': {
            'name': 'Professional',
            'description': 'Ideal for agencies and growing businesses',
            'monthly_price': 79,
            'annual_price': 790,
            'features': [
                '50 SEO audits per month',
                'Advanced backlink monitoring',
                'Competitor analysis',
                'White-label reports',
                'Priority support',
                'API access',
                'Custom branding',
                'Team collaboration'
            ]
        },
        'enterprise': {
            'name': 'Enterprise',
            'description': 'For large organizations with custom needs',
            'monthly_price': 199,
            'annual_price': 1990,
            'features': [
                'Unlimited SEO audits',
                'Advanced competitor tracking',
                'Custom integrations',
                'Dedicated account manager',
                'SLA guarantee',
                'Custom reporting',
                'Advanced analytics',
                'Phone support'
            ]
        }
    }
    
    return jsonify({
        'success': True,
        'plans': plans
    })

@app.route('/api/optimization/leads/capture', methods=['POST'])
def capture_lead():
    return jsonify({
        'success': True,
        'message': 'Lead captured successfully',
        'lead_id': 12345
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

