import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import json
from datetime import datetime, timedelta
from src.models.audit import SocialProfile, Website
from src.models.user import db

class SocialAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 30
        
        # Social media platforms to analyze
        self.platforms = {
            'facebook': {
                'base_url': 'https://www.facebook.com/',
                'search_patterns': [
                    r'facebook\.com/([^/\s"\']+)',
                    r'fb\.me/([^/\s"\']+)'
                ]
            },
            'twitter': {
                'base_url': 'https://twitter.com/',
                'search_patterns': [
                    r'twitter\.com/([^/\s"\']+)',
                    r't\.co/([^/\s"\']+)'
                ]
            },
            'linkedin': {
                'base_url': 'https://www.linkedin.com/',
                'search_patterns': [
                    r'linkedin\.com/company/([^/\s"\']+)',
                    r'linkedin\.com/in/([^/\s"\']+)'
                ]
            },
            'instagram': {
                'base_url': 'https://www.instagram.com/',
                'search_patterns': [
                    r'instagram\.com/([^/\s"\']+)'
                ]
            },
            'youtube': {
                'base_url': 'https://www.youtube.com/',
                'search_patterns': [
                    r'youtube\.com/channel/([^/\s"\']+)',
                    r'youtube\.com/c/([^/\s"\']+)',
                    r'youtube\.com/user/([^/\s"\']+)'
                ]
            },
            'pinterest': {
                'base_url': 'https://www.pinterest.com/',
                'search_patterns': [
                    r'pinterest\.com/([^/\s"\']+)'
                ]
            }
        }
    
    def analyze_social_presence(self, website_id, target_url):
        """Analyze social media presence for a website"""
        try:
            # Get the website content to look for social links
            response = self.session.get(target_url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            page_content = response.text
            
            # Find social media profiles
            discovered_profiles = self._discover_social_profiles(page_content, soup, target_url)
            
            # Analyze each discovered profile
            social_data = []
            for profile in discovered_profiles:
                try:
                    profile_data = self._analyze_social_profile(profile)
                    if profile_data:
                        social_data.append(profile_data)
                except Exception as e:
                    print(f"Error analyzing {profile['platform']} profile: {str(e)}")
                    continue
            
            # Save to database
            self._save_social_profiles(website_id, social_data)
            
            # Generate social media recommendations
            recommendations = self._generate_social_recommendations(social_data, soup)
            
            return {
                'total_profiles': len(social_data),
                'platforms_found': [profile['platform'] for profile in social_data],
                'profiles': social_data,
                'recommendations': recommendations,
                'social_signals': self._calculate_social_signals(social_data),
                'analysis_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Social media analysis failed: {str(e)}")
    
    def _discover_social_profiles(self, page_content, soup, target_url):
        """Discover social media profiles from website content"""
        profiles = []
        domain = urlparse(target_url).netloc
        
        # Method 1: Look for social media links in HTML
        for platform, config in self.platforms.items():
            for pattern in config['search_patterns']:
                matches = re.findall(pattern, page_content, re.IGNORECASE)
                for match in matches:
                    profile_url = f"{config['base_url']}{match}"
                    profiles.append({
                        'platform': platform,
                        'profile_url': profile_url,
                        'username': match,
                        'discovery_method': 'html_link'
                    })
        
        # Method 2: Look for social media meta tags
        social_meta_tags = soup.find_all('meta', attrs={'property': re.compile(r'^(og:|twitter:)')})
        for tag in social_meta_tags:
            content = tag.get('content', '')
            if 'facebook.com' in content:
                profiles.append({
                    'platform': 'facebook',
                    'profile_url': content,
                    'username': content.split('/')[-1],
                    'discovery_method': 'meta_tag'
                })
            elif 'twitter.com' in content:
                profiles.append({
                    'platform': 'twitter',
                    'profile_url': content,
                    'username': content.split('/')[-1],
                    'discovery_method': 'meta_tag'
                })
        
        # Method 3: Look for common social media widget patterns
        social_widgets = soup.find_all(['div', 'span', 'a'], class_=re.compile(r'(social|facebook|twitter|instagram|linkedin)', re.I))
        for widget in social_widgets:
            href = widget.get('href', '')
            if href:
                for platform, config in self.platforms.items():
                    if platform in href.lower():
                        profiles.append({
                            'platform': platform,
                            'profile_url': href,
                            'username': href.split('/')[-1],
                            'discovery_method': 'widget'
                        })
        
        # Remove duplicates
        unique_profiles = []
        seen_urls = set()
        for profile in profiles:
            if profile['profile_url'] not in seen_urls:
                unique_profiles.append(profile)
                seen_urls.add(profile['profile_url'])
        
        return unique_profiles
    
    def _analyze_social_profile(self, profile):
        """Analyze individual social media profile"""
        platform = profile['platform']
        profile_url = profile['profile_url']
        
        try:
            # For demo purposes, we'll simulate social media metrics
            # In a real implementation, you'd use official APIs:
            # - Facebook Graph API
            # - Twitter API v2
            # - LinkedIn API
            # - Instagram Basic Display API
            # - YouTube Data API
            
            # Simulate profile data based on platform
            if platform == 'facebook':
                return self._simulate_facebook_data(profile)
            elif platform == 'twitter':
                return self._simulate_twitter_data(profile)
            elif platform == 'linkedin':
                return self._simulate_linkedin_data(profile)
            elif platform == 'instagram':
                return self._simulate_instagram_data(profile)
            elif platform == 'youtube':
                return self._simulate_youtube_data(profile)
            elif platform == 'pinterest':
                return self._simulate_pinterest_data(profile)
            
        except Exception as e:
            print(f"Error analyzing {platform} profile {profile_url}: {str(e)}")
            return None
    
    def _simulate_facebook_data(self, profile):
        """Simulate Facebook profile data"""
        import random
        
        return {
            'platform': 'facebook',
            'profile_url': profile['profile_url'],
            'username': profile['username'],
            'followers_count': random.randint(100, 50000),
            'following_count': random.randint(50, 1000),
            'posts_count': random.randint(10, 500),
            'engagement_rate': round(random.uniform(1.0, 8.0), 2),
            'last_post_date': datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            'verified': random.choice([True, False]),
            'metrics': {
                'likes_avg': random.randint(10, 500),
                'comments_avg': random.randint(2, 50),
                'shares_avg': random.randint(1, 25),
                'posting_frequency': random.choice(['daily', 'weekly', 'monthly'])
            }
        }
    
    def _simulate_twitter_data(self, profile):
        """Simulate Twitter profile data"""
        import random
        
        return {
            'platform': 'twitter',
            'profile_url': profile['profile_url'],
            'username': profile['username'],
            'followers_count': random.randint(50, 100000),
            'following_count': random.randint(100, 5000),
            'posts_count': random.randint(50, 10000),
            'engagement_rate': round(random.uniform(0.5, 5.0), 2),
            'last_post_date': datetime.utcnow() - timedelta(days=random.randint(1, 7)),
            'verified': random.choice([True, False]),
            'metrics': {
                'retweets_avg': random.randint(5, 100),
                'likes_avg': random.randint(10, 500),
                'replies_avg': random.randint(1, 20),
                'posting_frequency': random.choice(['multiple_daily', 'daily', 'weekly'])
            }
        }
    
    def _simulate_linkedin_data(self, profile):
        """Simulate LinkedIn profile data"""
        import random
        
        return {
            'platform': 'linkedin',
            'profile_url': profile['profile_url'],
            'username': profile['username'],
            'followers_count': random.randint(100, 25000),
            'following_count': random.randint(200, 2000),
            'posts_count': random.randint(20, 200),
            'engagement_rate': round(random.uniform(2.0, 10.0), 2),
            'last_post_date': datetime.utcnow() - timedelta(days=random.randint(1, 14)),
            'verified': random.choice([True, False]),
            'metrics': {
                'likes_avg': random.randint(20, 200),
                'comments_avg': random.randint(5, 50),
                'shares_avg': random.randint(2, 30),
                'posting_frequency': random.choice(['weekly', 'bi-weekly', 'monthly'])
            }
        }
    
    def _simulate_instagram_data(self, profile):
        """Simulate Instagram profile data"""
        import random
        
        return {
            'platform': 'instagram',
            'profile_url': profile['profile_url'],
            'username': profile['username'],
            'followers_count': random.randint(200, 75000),
            'following_count': random.randint(100, 3000),
            'posts_count': random.randint(30, 1000),
            'engagement_rate': round(random.uniform(1.5, 12.0), 2),
            'last_post_date': datetime.utcnow() - timedelta(days=random.randint(1, 10)),
            'verified': random.choice([True, False]),
            'metrics': {
                'likes_avg': random.randint(50, 1000),
                'comments_avg': random.randint(5, 100),
                'stories_per_week': random.randint(3, 21),
                'posting_frequency': random.choice(['daily', 'every_other_day', 'weekly'])
            }
        }
    
    def _simulate_youtube_data(self, profile):
        """Simulate YouTube profile data"""
        import random
        
        return {
            'platform': 'youtube',
            'profile_url': profile['profile_url'],
            'username': profile['username'],
            'followers_count': random.randint(100, 500000),  # subscribers
            'following_count': 0,  # YouTube doesn't show subscriptions
            'posts_count': random.randint(10, 500),  # videos
            'engagement_rate': round(random.uniform(2.0, 15.0), 2),
            'last_post_date': datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            'verified': random.choice([True, False]),
            'metrics': {
                'views_avg': random.randint(500, 50000),
                'likes_avg': random.randint(20, 2000),
                'comments_avg': random.randint(5, 200),
                'upload_frequency': random.choice(['weekly', 'bi-weekly', 'monthly'])
            }
        }
    
    def _simulate_pinterest_data(self, profile):
        """Simulate Pinterest profile data"""
        import random
        
        return {
            'platform': 'pinterest',
            'profile_url': profile['profile_url'],
            'username': profile['username'],
            'followers_count': random.randint(50, 10000),
            'following_count': random.randint(100, 5000),
            'posts_count': random.randint(20, 2000),  # pins
            'engagement_rate': round(random.uniform(0.5, 3.0), 2),
            'last_post_date': datetime.utcnow() - timedelta(days=random.randint(1, 14)),
            'verified': random.choice([True, False]),
            'metrics': {
                'repins_avg': random.randint(5, 100),
                'likes_avg': random.randint(2, 50),
                'boards_count': random.randint(5, 50),
                'posting_frequency': random.choice(['daily', 'weekly', 'monthly'])
            }
        }
    
    def _save_social_profiles(self, website_id, social_data):
        """Save social profiles to database"""
        try:
            # Remove existing profiles for this website
            SocialProfile.query.filter_by(website_id=website_id).delete()
            
            # Add new profiles
            for profile_data in social_data:
                social_profile = SocialProfile(
                    website_id=website_id,
                    platform=profile_data['platform'],
                    profile_url=profile_data['profile_url'],
                    username=profile_data['username'],
                    followers_count=profile_data['followers_count'],
                    following_count=profile_data['following_count'],
                    posts_count=profile_data['posts_count'],
                    engagement_rate=profile_data['engagement_rate'],
                    last_post_date=profile_data['last_post_date'],
                    verified=profile_data['verified']
                )
                db.session.add(social_profile)
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to save social profiles: {str(e)}")
    
    def _generate_social_recommendations(self, social_data, soup):
        """Generate social media optimization recommendations"""
        recommendations = []
        
        # Check for Open Graph tags
        og_tags = soup.find_all('meta', attrs={'property': re.compile(r'^og:')})
        og_properties = {tag.get('property'): tag.get('content') for tag in og_tags}
        
        if not og_properties.get('og:title'):
            recommendations.append({
                'type': 'missing_og_title',
                'priority': 'high',
                'message': 'Add Open Graph title tag for better social media sharing',
                'recommendation': 'Add <meta property="og:title" content="Your Page Title"> to improve how your content appears when shared on social media'
            })
        
        if not og_properties.get('og:description'):
            recommendations.append({
                'type': 'missing_og_description',
                'priority': 'high',
                'message': 'Add Open Graph description tag',
                'recommendation': 'Add <meta property="og:description" content="Your page description"> to control how your content is described when shared'
            })
        
        if not og_properties.get('og:image'):
            recommendations.append({
                'type': 'missing_og_image',
                'priority': 'medium',
                'message': 'Add Open Graph image tag',
                'recommendation': 'Add <meta property="og:image" content="URL to your image"> to ensure an attractive image appears when your content is shared'
            })
        
        # Check for Twitter Card tags
        twitter_tags = soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')})
        twitter_properties = {tag.get('name'): tag.get('content') for tag in twitter_tags}
        
        if not twitter_properties.get('twitter:card'):
            recommendations.append({
                'type': 'missing_twitter_card',
                'priority': 'medium',
                'message': 'Add Twitter Card meta tags',
                'recommendation': 'Add Twitter Card meta tags to optimize how your content appears on Twitter'
            })
        
        # Analyze social presence
        platforms_found = [profile['platform'] for profile in social_data]
        important_platforms = ['facebook', 'twitter', 'linkedin', 'instagram']
        
        missing_platforms = [platform for platform in important_platforms if platform not in platforms_found]
        if missing_platforms:
            recommendations.append({
                'type': 'missing_social_platforms',
                'priority': 'low',
                'message': f'Consider establishing presence on: {", ".join(missing_platforms)}',
                'recommendation': 'Expand your social media presence to reach more audiences and improve brand visibility'
            })
        
        # Check engagement rates
        low_engagement_platforms = [
            profile['platform'] for profile in social_data 
            if profile['engagement_rate'] < 2.0
        ]
        
        if low_engagement_platforms:
            recommendations.append({
                'type': 'low_engagement',
                'priority': 'medium',
                'message': f'Low engagement rates detected on: {", ".join(low_engagement_platforms)}',
                'recommendation': 'Focus on creating more engaging content and interacting with your audience to improve engagement rates'
            })
        
        return recommendations
    
    def _calculate_social_signals(self, social_data):
        """Calculate overall social signals score"""
        if not social_data:
            return {
                'overall_score': 0,
                'total_followers': 0,
                'average_engagement': 0,
                'platform_diversity': 0,
                'activity_level': 'low'
            }
        
        total_followers = sum(profile['followers_count'] for profile in social_data)
        avg_engagement = sum(profile['engagement_rate'] for profile in social_data) / len(social_data)
        platform_count = len(social_data)
        
        # Calculate overall score (0-100)
        score = 0
        
        # Follower count score (40%)
        if total_followers > 10000:
            score += 40
        elif total_followers > 1000:
            score += 30
        elif total_followers > 100:
            score += 20
        else:
            score += 10
        
        # Engagement rate score (30%)
        if avg_engagement > 5:
            score += 30
        elif avg_engagement > 3:
            score += 25
        elif avg_engagement > 1:
            score += 15
        else:
            score += 5
        
        # Platform diversity score (20%)
        if platform_count >= 4:
            score += 20
        elif platform_count >= 3:
            score += 15
        elif platform_count >= 2:
            score += 10
        else:
            score += 5
        
        # Activity level score (10%)
        recent_posts = sum(1 for profile in social_data 
                          if profile['last_post_date'] and 
                          (datetime.utcnow() - profile['last_post_date']).days <= 7)
        
        if recent_posts >= len(social_data):
            score += 10
            activity_level = 'high'
        elif recent_posts >= len(social_data) // 2:
            score += 7
            activity_level = 'medium'
        else:
            score += 3
            activity_level = 'low'
        
        return {
            'overall_score': min(100, score),
            'total_followers': total_followers,
            'average_engagement': round(avg_engagement, 2),
            'platform_diversity': platform_count,
            'activity_level': activity_level
        }
    
    def get_social_metrics(self, website_id):
        """Get comprehensive social media metrics for a website"""
        try:
            profiles = SocialProfile.query.filter_by(website_id=website_id).all()
            
            if not profiles:
                return {
                    'total_profiles': 0,
                    'total_followers': 0,
                    'platforms': [],
                    'engagement_summary': {},
                    'growth_trends': [],
                    'top_performing_platforms': []
                }
            
            # Calculate metrics
            total_followers = sum(profile.followers_count or 0 for profile in profiles)
            platforms = [profile.platform for profile in profiles]
            
            # Engagement summary by platform
            engagement_summary = {}
            for profile in profiles:
                engagement_summary[profile.platform] = {
                    'followers': profile.followers_count,
                    'engagement_rate': float(profile.engagement_rate) if profile.engagement_rate else 0,
                    'posts': profile.posts_count,
                    'verified': profile.verified,
                    'last_post': profile.last_post_date.isoformat() if profile.last_post_date else None
                }
            
            # Top performing platforms
            top_platforms = sorted(
                [(p.platform, p.followers_count or 0, float(p.engagement_rate) if p.engagement_rate else 0) 
                 for p in profiles],
                key=lambda x: x[1] * x[2],  # followers * engagement
                reverse=True
            )
            
            return {
                'total_profiles': len(profiles),
                'total_followers': total_followers,
                'platforms': platforms,
                'engagement_summary': engagement_summary,
                'growth_trends': [],  # Would need historical data
                'top_performing_platforms': [
                    {'platform': platform, 'followers': followers, 'engagement': engagement}
                    for platform, followers, engagement in top_platforms
                ]
            }
            
        except Exception as e:
            raise Exception(f"Failed to get social metrics: {str(e)}")

