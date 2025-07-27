from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.audit import Website, SocialProfile
from src.services.social_analyzer import SocialAnalyzer
from datetime import datetime
import traceback

social_bp = Blueprint('social', __name__)

@social_bp.route('/social/analyze', methods=['POST'])
def analyze_social_presence():
    """Analyze social media presence for a website"""
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
        
        # Analyze social presence
        analyzer = SocialAnalyzer()
        result = analyzer.analyze_social_presence(website.id, url)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Social media analysis failed: {str(e)}'}), 500

@social_bp.route('/social/website/<int:website_id>', methods=['GET'])
def get_website_social_profiles(website_id):
    """Get social media profiles for a specific website"""
    try:
        website = Website.query.get_or_404(website_id)
        
        profiles = SocialProfile.query.filter_by(website_id=website_id).all()
        
        result = {
            'website': {
                'id': website.id,
                'domain': website.domain
            },
            'profiles': []
        }
        
        for profile in profiles:
            result['profiles'].append({
                'id': profile.id,
                'platform': profile.platform,
                'profile_url': profile.profile_url,
                'username': profile.username,
                'followers_count': profile.followers_count,
                'following_count': profile.following_count,
                'posts_count': profile.posts_count,
                'engagement_rate': float(profile.engagement_rate) if profile.engagement_rate else 0,
                'last_post_date': profile.last_post_date.isoformat() if profile.last_post_date else None,
                'verified': profile.verified,
                'created_at': profile.created_at.isoformat(),
                'updated_at': profile.updated_at.isoformat()
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get social profiles: {str(e)}'}), 500

@social_bp.route('/social/metrics/<int:website_id>', methods=['GET'])
def get_social_metrics(website_id):
    """Get comprehensive social media metrics for a website"""
    try:
        website = Website.query.get_or_404(website_id)
        
        analyzer = SocialAnalyzer()
        metrics = analyzer.get_social_metrics(website_id)
        
        return jsonify({
            'website': {
                'id': website.id,
                'domain': website.domain
            },
            'metrics': metrics
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get social metrics: {str(e)}'}), 500

@social_bp.route('/social/platforms', methods=['GET'])
def get_platform_statistics():
    """Get statistics across all social media platforms"""
    try:
        from sqlalchemy import func
        
        # Get platform statistics
        platform_stats = db.session.query(
            SocialProfile.platform,
            func.count(SocialProfile.id).label('profile_count'),
            func.sum(SocialProfile.followers_count).label('total_followers'),
            func.avg(SocialProfile.engagement_rate).label('avg_engagement')
        ).group_by(SocialProfile.platform).all()
        
        # Get top profiles by followers
        top_profiles = SocialProfile.query.order_by(
            SocialProfile.followers_count.desc()
        ).limit(10).all()
        
        # Get recent social activity
        recent_profiles = SocialProfile.query.order_by(
            SocialProfile.updated_at.desc()
        ).limit(20).all()
        
        result = {
            'platform_statistics': [
                {
                    'platform': platform,
                    'profile_count': count,
                    'total_followers': int(total_followers) if total_followers else 0,
                    'average_engagement': round(float(avg_engagement), 2) if avg_engagement else 0
                }
                for platform, count, total_followers, avg_engagement in platform_stats
            ],
            'top_profiles': [
                {
                    'id': profile.id,
                    'platform': profile.platform,
                    'username': profile.username,
                    'domain': profile.website.domain,
                    'followers_count': profile.followers_count,
                    'engagement_rate': float(profile.engagement_rate) if profile.engagement_rate else 0,
                    'verified': profile.verified
                }
                for profile in top_profiles
            ],
            'recent_activity': [
                {
                    'id': profile.id,
                    'platform': profile.platform,
                    'username': profile.username,
                    'domain': profile.website.domain,
                    'updated_at': profile.updated_at.isoformat()
                }
                for profile in recent_profiles
            ]
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get platform statistics: {str(e)}'}), 500

@social_bp.route('/social/profile/<int:profile_id>', methods=['PUT'])
def update_social_profile(profile_id):
    """Update social media profile information"""
    try:
        profile = SocialProfile.query.get_or_404(profile_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        if 'followers_count' in data:
            profile.followers_count = data['followers_count']
        if 'following_count' in data:
            profile.following_count = data['following_count']
        if 'posts_count' in data:
            profile.posts_count = data['posts_count']
        if 'engagement_rate' in data:
            profile.engagement_rate = data['engagement_rate']
        if 'verified' in data:
            profile.verified = data['verified']
        if 'last_post_date' in data:
            if data['last_post_date']:
                profile.last_post_date = datetime.fromisoformat(data['last_post_date'].replace('Z', '+00:00'))
            else:
                profile.last_post_date = None
        
        profile.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'id': profile.id,
            'platform': profile.platform,
            'message': 'Social profile updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update social profile: {str(e)}'}), 500

@social_bp.route('/social/profile/<int:profile_id>', methods=['DELETE'])
def delete_social_profile(profile_id):
    """Delete a social media profile record"""
    try:
        profile = SocialProfile.query.get_or_404(profile_id)
        
        db.session.delete(profile)
        db.session.commit()
        
        return jsonify({'message': 'Social profile deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete social profile: {str(e)}'}), 500

@social_bp.route('/social/engagement-analysis', methods=['GET'])
def analyze_engagement_trends():
    """Analyze engagement trends across platforms"""
    try:
        from sqlalchemy import func
        
        # Get engagement data by platform
        engagement_data = db.session.query(
            SocialProfile.platform,
            func.avg(SocialProfile.engagement_rate).label('avg_engagement'),
            func.min(SocialProfile.engagement_rate).label('min_engagement'),
            func.max(SocialProfile.engagement_rate).label('max_engagement'),
            func.count(SocialProfile.id).label('profile_count')
        ).group_by(SocialProfile.platform).all()
        
        # Calculate benchmarks
        benchmarks = {
            'facebook': {'good': 3.0, 'average': 1.5, 'poor': 0.5},
            'instagram': {'good': 5.0, 'average': 2.5, 'poor': 1.0},
            'twitter': {'good': 2.0, 'average': 1.0, 'poor': 0.3},
            'linkedin': {'good': 4.0, 'average': 2.0, 'poor': 0.8},
            'youtube': {'good': 8.0, 'average': 4.0, 'poor': 1.5},
            'pinterest': {'good': 1.5, 'average': 0.8, 'poor': 0.2}
        }
        
        result = {
            'engagement_analysis': [],
            'benchmarks': benchmarks,
            'insights': []
        }
        
        for platform, avg_eng, min_eng, max_eng, count in engagement_data:
            avg_engagement = float(avg_eng) if avg_eng else 0
            
            # Determine performance level
            benchmark = benchmarks.get(platform, {'good': 3.0, 'average': 1.5, 'poor': 0.5})
            if avg_engagement >= benchmark['good']:
                performance = 'excellent'
            elif avg_engagement >= benchmark['average']:
                performance = 'good'
            elif avg_engagement >= benchmark['poor']:
                performance = 'average'
            else:
                performance = 'poor'
            
            result['engagement_analysis'].append({
                'platform': platform,
                'average_engagement': round(avg_engagement, 2),
                'min_engagement': round(float(min_eng), 2) if min_eng else 0,
                'max_engagement': round(float(max_eng), 2) if max_eng else 0,
                'profile_count': count,
                'performance_level': performance
            })
        
        # Generate insights
        if engagement_data:
            best_platform = max(engagement_data, key=lambda x: float(x[1]) if x[1] else 0)
            worst_platform = min(engagement_data, key=lambda x: float(x[1]) if x[1] else 0)
            
            result['insights'] = [
                f"Best performing platform: {best_platform[0]} with {float(best_platform[1]):.2f}% average engagement",
                f"Platform needing attention: {worst_platform[0]} with {float(worst_platform[1]):.2f}% average engagement",
                f"Total profiles analyzed: {sum(row[4] for row in engagement_data)}"
            ]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Failed to analyze engagement trends: {str(e)}'}), 500

@social_bp.route('/social/export/<int:website_id>', methods=['GET'])
def export_social_data(website_id):
    """Export social media data as CSV"""
    try:
        website = Website.query.get_or_404(website_id)
        profiles = SocialProfile.query.filter_by(website_id=website_id).all()
        
        # Create CSV data
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Platform', 'Username', 'Profile URL', 'Followers', 'Following',
            'Posts', 'Engagement Rate', 'Verified', 'Last Post Date',
            'Created At', 'Updated At'
        ])
        
        # Write data
        for profile in profiles:
            writer.writerow([
                profile.platform,
                profile.username or '',
                profile.profile_url or '',
                profile.followers_count or 0,
                profile.following_count or 0,
                profile.posts_count or 0,
                float(profile.engagement_rate) if profile.engagement_rate else 0,
                'Yes' if profile.verified else 'No',
                profile.last_post_date.isoformat() if profile.last_post_date else '',
                profile.created_at.isoformat(),
                profile.updated_at.isoformat()
            ])
        
        output.seek(0)
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=social_profiles_{website.domain}_{datetime.now().strftime("%Y%m%d")}.csv'
            }
        )
        
    except Exception as e:
        return jsonify({'error': f'Failed to export social data: {str(e)}'}), 500

@social_bp.route('/social/recommendations/<int:website_id>', methods=['GET'])
def get_social_recommendations(website_id):
    """Get social media optimization recommendations"""
    try:
        website = Website.query.get_or_404(website_id)
        profiles = SocialProfile.query.filter_by(website_id=website_id).all()
        
        recommendations = []
        
        # Check platform presence
        existing_platforms = {profile.platform for profile in profiles}
        important_platforms = {'facebook', 'twitter', 'linkedin', 'instagram'}
        missing_platforms = important_platforms - existing_platforms
        
        if missing_platforms:
            recommendations.append({
                'type': 'platform_expansion',
                'priority': 'medium',
                'title': 'Expand Platform Presence',
                'description': f"Consider creating profiles on: {', '.join(missing_platforms)}",
                'action': 'Create new social media profiles to reach wider audiences'
            })
        
        # Check engagement rates
        low_engagement_profiles = [
            profile for profile in profiles 
            if profile.engagement_rate and float(profile.engagement_rate) < 2.0
        ]
        
        if low_engagement_profiles:
            platforms = [profile.platform for profile in low_engagement_profiles]
            recommendations.append({
                'type': 'engagement_improvement',
                'priority': 'high',
                'title': 'Improve Engagement',
                'description': f"Low engagement detected on: {', '.join(platforms)}",
                'action': 'Focus on creating more engaging content and interacting with followers'
            })
        
        # Check posting frequency
        inactive_profiles = []
        for profile in profiles:
            if profile.last_post_date:
                days_since_post = (datetime.utcnow() - profile.last_post_date).days
                if days_since_post > 30:
                    inactive_profiles.append(profile)
        
        if inactive_profiles:
            platforms = [profile.platform for profile in inactive_profiles]
            recommendations.append({
                'type': 'posting_frequency',
                'priority': 'medium',
                'title': 'Increase Posting Frequency',
                'description': f"Inactive profiles detected on: {', '.join(platforms)}",
                'action': 'Maintain regular posting schedule to keep audience engaged'
            })
        
        # Check verification status
        unverified_large_profiles = [
            profile for profile in profiles 
            if not profile.verified and profile.followers_count and profile.followers_count > 10000
        ]
        
        if unverified_large_profiles:
            platforms = [profile.platform for profile in unverified_large_profiles]
            recommendations.append({
                'type': 'verification',
                'priority': 'low',
                'title': 'Seek Verification',
                'description': f"Large unverified profiles on: {', '.join(platforms)}",
                'action': 'Apply for verification badges to increase credibility'
            })
        
        return jsonify({
            'website': {
                'id': website.id,
                'domain': website.domain
            },
            'total_recommendations': len(recommendations),
            'recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get social recommendations: {str(e)}'}), 500

