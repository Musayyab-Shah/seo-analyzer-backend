import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import time
from datetime import datetime
from src.models.audit import Backlink, Website
from src.models.user import db

class BacklinkAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 30
    
    def analyze_backlinks(self, website_id, target_url):
        """Analyze backlinks for a website"""
        try:
            # Get existing backlinks for comparison
            existing_backlinks = Backlink.query.filter_by(website_id=website_id).all()
            existing_urls = {bl.source_url for bl in existing_backlinks}
            
            # Discover new backlinks using multiple methods
            discovered_backlinks = []
            
            # Method 1: Search engine queries (simulated)
            search_backlinks = self._search_engine_backlinks(target_url)
            discovered_backlinks.extend(search_backlinks)
            
            # Method 2: Common backlink sources
            common_backlinks = self._check_common_sources(target_url)
            discovered_backlinks.extend(common_backlinks)
            
            # Method 3: Social media mentions
            social_backlinks = self._check_social_mentions(target_url)
            discovered_backlinks.extend(social_backlinks)
            
            # Process discovered backlinks
            new_backlinks = []
            updated_backlinks = []
            
            for backlink_data in discovered_backlinks:
                source_url = backlink_data['source_url']
                
                if source_url in existing_urls:
                    # Update existing backlink
                    existing_bl = next(bl for bl in existing_backlinks if bl.source_url == source_url)
                    existing_bl.last_seen = datetime.utcnow()
                    existing_bl.status = 'active'
                    updated_backlinks.append(existing_bl)
                else:
                    # Create new backlink
                    backlink = Backlink(
                        website_id=website_id,
                        source_domain=backlink_data['source_domain'],
                        source_url=source_url,
                        target_url=backlink_data['target_url'],
                        anchor_text=backlink_data.get('anchor_text'),
                        link_type=backlink_data.get('link_type', 'dofollow'),
                        domain_authority=backlink_data.get('domain_authority'),
                        page_authority=backlink_data.get('page_authority'),
                        spam_score=backlink_data.get('spam_score'),
                        link_context=backlink_data.get('link_context'),
                        is_internal=backlink_data.get('is_internal', False)
                    )
                    new_backlinks.append(backlink)
            
            # Mark missing backlinks as lost
            current_urls = {bl['source_url'] for bl in discovered_backlinks}
            for existing_bl in existing_backlinks:
                if existing_bl.source_url not in current_urls and existing_bl.status == 'active':
                    existing_bl.status = 'lost'
                    existing_bl.last_seen = datetime.utcnow()
                    updated_backlinks.append(existing_bl)
            
            # Save to database
            for backlink in new_backlinks:
                db.session.add(backlink)
            
            db.session.commit()
            
            return {
                'total_backlinks': len(existing_backlinks) + len(new_backlinks),
                'new_backlinks': len(new_backlinks),
                'lost_backlinks': len([bl for bl in updated_backlinks if bl.status == 'lost']),
                'active_backlinks': len([bl for bl in existing_backlinks + new_backlinks if bl.status == 'active']),
                'analysis_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Backlink analysis failed: {str(e)}")
    
    def _search_engine_backlinks(self, target_url):
        """Simulate search engine backlink discovery"""
        # In a real implementation, this would use APIs like:
        # - Ahrefs API
        # - SEMrush API
        # - Moz API
        # - Majestic API
        
        # For demo purposes, we'll simulate some backlinks
        domain = urlparse(target_url).netloc
        
        simulated_backlinks = [
            {
                'source_domain': 'example-blog.com',
                'source_url': f'https://example-blog.com/article-about-{domain.replace(".", "-")}',
                'target_url': target_url,
                'anchor_text': f'Visit {domain}',
                'link_type': 'dofollow',
                'domain_authority': 45,
                'page_authority': 38,
                'spam_score': 2,
                'link_context': f'This is a great resource: {domain}',
                'is_internal': False
            },
            {
                'source_domain': 'news-site.com',
                'source_url': f'https://news-site.com/industry-news-featuring-{domain.replace(".", "-")}',
                'target_url': target_url,
                'anchor_text': domain,
                'link_type': 'dofollow',
                'domain_authority': 62,
                'page_authority': 55,
                'spam_score': 1,
                'link_context': f'Industry leader {domain} announced...',
                'is_internal': False
            }
        ]
        
        return simulated_backlinks
    
    def _check_common_sources(self, target_url):
        """Check common backlink sources"""
        backlinks = []
        domain = urlparse(target_url).netloc
        
        # Check directory sites
        directory_sites = [
            'dmoz.org',
            'business.com',
            'yellowpages.com',
            'yelp.com'
        ]
        
        for directory in directory_sites:
            try:
                # Simulate checking if the site is listed
                # In reality, you'd make actual HTTP requests
                if self._simulate_directory_listing(domain, directory):
                    backlinks.append({
                        'source_domain': directory,
                        'source_url': f'https://{directory}/listing/{domain}',
                        'target_url': target_url,
                        'anchor_text': domain,
                        'link_type': 'dofollow',
                        'domain_authority': self._estimate_domain_authority(directory),
                        'page_authority': 30,
                        'spam_score': 0,
                        'link_context': f'Business listing for {domain}',
                        'is_internal': False
                    })
            except Exception:
                continue
        
        return backlinks
    
    def _check_social_mentions(self, target_url):
        """Check social media mentions that might contain backlinks"""
        backlinks = []
        domain = urlparse(target_url).netloc
        
        # Simulate social media backlinks
        social_platforms = [
            {'platform': 'twitter.com', 'da': 95},
            {'platform': 'facebook.com', 'da': 96},
            {'platform': 'linkedin.com', 'da': 98},
            {'platform': 'reddit.com', 'da': 91}
        ]
        
        for platform in social_platforms:
            # Simulate finding mentions
            if self._simulate_social_mention(domain, platform['platform']):
                backlinks.append({
                    'source_domain': platform['platform'],
                    'source_url': f'https://{platform["platform"]}/post/about-{domain.replace(".", "-")}',
                    'target_url': target_url,
                    'anchor_text': f'Check out {domain}',
                    'link_type': 'nofollow',  # Most social links are nofollow
                    'domain_authority': platform['da'],
                    'page_authority': 25,
                    'spam_score': 0,
                    'link_context': f'Social media mention of {domain}',
                    'is_internal': False
                })
        
        return backlinks
    
    def _simulate_directory_listing(self, domain, directory):
        """Simulate checking if domain is listed in directory"""
        # Simple simulation - in reality, you'd check actual listings
        import random
        return random.choice([True, False])
    
    def _simulate_social_mention(self, domain, platform):
        """Simulate checking for social media mentions"""
        # Simple simulation - in reality, you'd use social media APIs
        import random
        return random.choice([True, False])
    
    def _estimate_domain_authority(self, domain):
        """Estimate domain authority based on known values"""
        known_authorities = {
            'dmoz.org': 85,
            'business.com': 70,
            'yellowpages.com': 75,
            'yelp.com': 85,
            'twitter.com': 95,
            'facebook.com': 96,
            'linkedin.com': 98,
            'reddit.com': 91
        }
        return known_authorities.get(domain, 50)
    
    def get_backlink_metrics(self, website_id):
        """Get comprehensive backlink metrics for a website"""
        try:
            backlinks = Backlink.query.filter_by(website_id=website_id).all()
            
            if not backlinks:
                return {
                    'total_backlinks': 0,
                    'active_backlinks': 0,
                    'lost_backlinks': 0,
                    'dofollow_links': 0,
                    'nofollow_links': 0,
                    'average_domain_authority': 0,
                    'top_referring_domains': [],
                    'recent_backlinks': [],
                    'link_growth': []
                }
            
            # Calculate metrics
            active_backlinks = [bl for bl in backlinks if bl.status == 'active']
            lost_backlinks = [bl for bl in backlinks if bl.status == 'lost']
            dofollow_links = [bl for bl in backlinks if bl.link_type == 'dofollow']
            nofollow_links = [bl for bl in backlinks if bl.link_type == 'nofollow']
            
            # Average domain authority
            da_values = [bl.domain_authority for bl in backlinks if bl.domain_authority]
            avg_da = sum(da_values) / len(da_values) if da_values else 0
            
            # Top referring domains
            domain_counts = {}
            for bl in active_backlinks:
                domain_counts[bl.source_domain] = domain_counts.get(bl.source_domain, 0) + 1
            
            top_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Recent backlinks (last 30 days)
            from datetime import timedelta
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_backlinks = [bl for bl in backlinks if bl.discovered_date >= thirty_days_ago]
            
            return {
                'total_backlinks': len(backlinks),
                'active_backlinks': len(active_backlinks),
                'lost_backlinks': len(lost_backlinks),
                'dofollow_links': len(dofollow_links),
                'nofollow_links': len(nofollow_links),
                'average_domain_authority': round(avg_da, 1),
                'top_referring_domains': [{'domain': domain, 'count': count} for domain, count in top_domains],
                'recent_backlinks': len(recent_backlinks),
                'link_growth': self._calculate_link_growth(backlinks)
            }
            
        except Exception as e:
            raise Exception(f"Failed to get backlink metrics: {str(e)}")
    
    def _calculate_link_growth(self, backlinks):
        """Calculate link growth over time"""
        # Group backlinks by month
        monthly_counts = {}
        
        for bl in backlinks:
            month_key = bl.discovered_date.strftime('%Y-%m')
            monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
        
        # Convert to list of dictionaries for easier frontend consumption
        growth_data = []
        for month, count in sorted(monthly_counts.items()):
            growth_data.append({
                'month': month,
                'new_backlinks': count
            })
        
        return growth_data[-12:]  # Last 12 months
    
    def monitor_competitor_backlinks(self, competitor_urls, website_id):
        """Monitor competitor backlinks for opportunities"""
        try:
            opportunities = []
            
            for competitor_url in competitor_urls:
                # Analyze competitor's backlinks
                competitor_domain = urlparse(competitor_url).netloc
                
                # Simulate competitor backlink analysis
                # In reality, this would use backlink APIs
                competitor_backlinks = self._get_competitor_backlinks(competitor_url)
                
                # Find opportunities (domains linking to competitors but not to us)
                our_backlinks = Backlink.query.filter_by(website_id=website_id).all()
                our_domains = {bl.source_domain for bl in our_backlinks}
                
                for comp_bl in competitor_backlinks:
                    if comp_bl['source_domain'] not in our_domains:
                        opportunities.append({
                            'source_domain': comp_bl['source_domain'],
                            'source_url': comp_bl['source_url'],
                            'competitor_domain': competitor_domain,
                            'domain_authority': comp_bl.get('domain_authority', 0),
                            'link_type': comp_bl.get('link_type', 'unknown'),
                            'opportunity_score': self._calculate_opportunity_score(comp_bl)
                        })
            
            # Sort by opportunity score
            opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
            
            return {
                'total_opportunities': len(opportunities),
                'high_value_opportunities': len([op for op in opportunities if op['opportunity_score'] > 70]),
                'opportunities': opportunities[:50]  # Top 50 opportunities
            }
            
        except Exception as e:
            raise Exception(f"Competitor backlink monitoring failed: {str(e)}")
    
    def _get_competitor_backlinks(self, competitor_url):
        """Get backlinks for a competitor (simulated)"""
        domain = urlparse(competitor_url).netloc
        
        # Simulate competitor backlinks
        return [
            {
                'source_domain': 'industry-magazine.com',
                'source_url': f'https://industry-magazine.com/review-of-{domain.replace(".", "-")}',
                'domain_authority': 68,
                'link_type': 'dofollow'
            },
            {
                'source_domain': 'tech-blog.com',
                'source_url': f'https://tech-blog.com/comparison-including-{domain.replace(".", "-")}',
                'domain_authority': 55,
                'link_type': 'dofollow'
            }
        ]
    
    def _calculate_opportunity_score(self, backlink_data):
        """Calculate opportunity score for a potential backlink"""
        score = 0
        
        # Domain authority weight (40%)
        da = backlink_data.get('domain_authority', 0)
        score += (da / 100) * 40
        
        # Link type weight (30%)
        if backlink_data.get('link_type') == 'dofollow':
            score += 30
        elif backlink_data.get('link_type') == 'nofollow':
            score += 15
        
        # Relevance weight (30%) - simplified
        # In reality, you'd analyze content relevance
        score += 20  # Assume moderate relevance
        
        return min(100, score)

