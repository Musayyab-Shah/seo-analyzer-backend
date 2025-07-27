import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import ssl
import socket
import time
import re
from datetime import datetime
import json

class SEOAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 30
    
    def analyze_website(self, url):
        """Perform comprehensive SEO analysis of a website"""
        start_time = time.time()
        
        try:
            # Fetch the webpage
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Calculate load time
            load_time_ms = int((time.time() - start_time) * 1000)
            
            # Perform all analysis checks
            analysis_result = {
                'overall_score': 0,
                'page_title': self._get_page_title(soup),
                'meta_description': self._get_meta_description(soup),
                'details': {},
                'seo_metrics': self._analyze_seo_metrics(url, response, soup, load_time_ms),
                'performance_metrics': self._analyze_performance(url, response, load_time_ms),
                'security_scan': self._analyze_security(url, response)
            }
            
            # Perform detailed checks
            analysis_result['details']['seo'] = self._check_seo_factors(url, soup, response)
            analysis_result['details']['technical'] = self._check_technical_factors(url, soup, response)
            analysis_result['details']['content'] = self._check_content_factors(soup)
            analysis_result['details']['performance'] = self._check_performance_factors(response, load_time_ms)
            analysis_result['details']['mobile'] = self._check_mobile_factors(soup)
            
            # Calculate overall score
            analysis_result['overall_score'] = self._calculate_overall_score(analysis_result['details'])
            
            return analysis_result
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch website: {str(e)}")
        except Exception as e:
            raise Exception(f"Analysis failed: {str(e)}")
    
    def _get_page_title(self, soup):
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else None
    
    def _get_meta_description(self, soup):
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '').strip() if meta_desc else None
    
    def _analyze_seo_metrics(self, url, response, soup, load_time_ms):
        """Analyze SEO-specific metrics"""
        # Extract heading tags
        h1_tags = [h.get_text().strip() for h in soup.find_all('h1')]
        h2_tags = [h.get_text().strip() for h in soup.find_all('h2')]
        h3_tags = [h.get_text().strip() for h in soup.find_all('h3')]
        
        # Count images and alt attributes
        images = soup.find_all('img')
        images_count = len(images)
        images_without_alt = len([img for img in images if not img.get('alt')])
        
        # Count links
        internal_links = 0
        external_links = 0
        parsed_url = urlparse(url)
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http'):
                link_domain = urlparse(href).netloc
                if link_domain == parsed_url.netloc:
                    internal_links += 1
                else:
                    external_links += 1
            elif href.startswith('/'):
                internal_links += 1
        
        # Count words
        text_content = soup.get_text()
        word_count = len(re.findall(r'\b\w+\b', text_content))
        
        # Page size
        page_size_kb = len(response.content) / 1024
        
        # Check SSL
        ssl_enabled = url.startswith('https://')
        
        # Check robots.txt and sitemap
        robots_txt_exists = self._check_robots_txt(url)
        sitemap_exists = self._check_sitemap(url)
        
        # Get canonical URL
        canonical_link = soup.find('link', rel='canonical')
        canonical_url = canonical_link.get('href') if canonical_link else None
        
        # Extract schema markup
        schema_markup = self._extract_schema_markup(soup)
        
        # Extract social tags
        social_tags = self._extract_social_tags(soup)
        
        return {
            'page_title': self._get_page_title(soup),
            'meta_description': self._get_meta_description(soup),
            'h1_tags': h1_tags,
            'h2_tags': h2_tags,
            'h3_tags': h3_tags,
            'images_count': images_count,
            'images_without_alt': images_without_alt,
            'internal_links': internal_links,
            'external_links': external_links,
            'word_count': word_count,
            'page_size_kb': round(page_size_kb, 2),
            'load_time_ms': load_time_ms,
            'mobile_friendly': self._check_mobile_friendly(soup),
            'ssl_enabled': ssl_enabled,
            'robots_txt_exists': robots_txt_exists,
            'sitemap_exists': sitemap_exists,
            'canonical_url': canonical_url,
            'schema_markup': schema_markup,
            'social_tags': social_tags
        }
    
    def _analyze_performance(self, url, response, load_time_ms):
        """Analyze performance metrics"""
        # Basic performance scoring
        performance_score = 100
        
        # Penalize slow load times
        if load_time_ms > 3000:
            performance_score -= 30
        elif load_time_ms > 2000:
            performance_score -= 20
        elif load_time_ms > 1000:
            performance_score -= 10
        
        # Check compression
        if 'gzip' not in response.headers.get('content-encoding', ''):
            performance_score -= 10
        
        # Check caching headers
        if 'cache-control' not in response.headers:
            performance_score -= 10
        
        return {
            'first_contentful_paint': load_time_ms,  # Simplified
            'largest_contentful_paint': load_time_ms + 500,  # Estimated
            'first_input_delay': 50,  # Estimated
            'cumulative_layout_shift': 0.1,  # Estimated
            'speed_index': load_time_ms,
            'time_to_interactive': load_time_ms + 1000,  # Estimated
            'total_blocking_time': 100,  # Estimated
            'performance_score': max(0, performance_score),
            'accessibility_score': 85,  # Would need more detailed analysis
            'best_practices_score': 90,  # Would need more detailed analysis
            'seo_score': 80  # Would need more detailed analysis
        }
    
    def _analyze_security(self, url, response):
        """Analyze security aspects"""
        security_score = 100
        ssl_grade = 'A'
        ssl_certificate = {}
        blacklist_status = {}
        security_headers = {}
        vulnerabilities = {}
        
        # Check SSL
        if not url.startswith('https://'):
            security_score -= 50
            ssl_grade = 'F'
        else:
            # Get SSL certificate info
            try:
                hostname = urlparse(url).netloc
                context = ssl.create_default_context()
                with socket.create_connection((hostname, 443), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cert = ssock.getpeercert()
                        ssl_certificate = {
                            'subject': dict(x[0] for x in cert['subject']),
                            'issuer': dict(x[0] for x in cert['issuer']),
                            'version': cert['version'],
                            'serial_number': cert['serialNumber'],
                            'not_before': cert['notBefore'],
                            'not_after': cert['notAfter']
                        }
            except Exception:
                security_score -= 20
                ssl_grade = 'C'
        
        # Check security headers
        headers_to_check = [
            'strict-transport-security',
            'content-security-policy',
            'x-frame-options',
            'x-content-type-options',
            'referrer-policy'
        ]
        
        for header in headers_to_check:
            if header in response.headers:
                security_headers[header] = response.headers[header]
            else:
                security_score -= 5
        
        return {
            'ssl_certificate': ssl_certificate,
            'ssl_grade': ssl_grade,
            'ssl_expires_at': None,  # Would extract from certificate
            'malware_detected': False,  # Would need external service
            'blacklist_status': blacklist_status,
            'security_headers': security_headers,
            'vulnerabilities': vulnerabilities,
            'security_score': max(0, security_score)
        }
    
    def _check_seo_factors(self, url, soup, response):
        """Check SEO-related factors"""
        checks = {}
        
        # Title tag check
        title = soup.find('title')
        if title:
            title_text = title.get_text().strip()
            if len(title_text) == 0:
                checks['title_tag'] = {
                    'status': 'fail',
                    'score': 0,
                    'max_score': 10,
                    'message': 'Title tag is empty',
                    'recommendation': 'Add a descriptive title tag to your page',
                    'priority': 'high'
                }
            elif len(title_text) > 60:
                checks['title_tag'] = {
                    'status': 'warning',
                    'score': 7,
                    'max_score': 10,
                    'message': f'Title tag is too long ({len(title_text)} characters)',
                    'recommendation': 'Keep title tags under 60 characters for better display in search results',
                    'priority': 'medium'
                }
            else:
                checks['title_tag'] = {
                    'status': 'pass',
                    'score': 10,
                    'max_score': 10,
                    'message': f'Title tag length is optimal ({len(title_text)} characters)',
                    'recommendation': None,
                    'priority': 'low'
                }
        else:
            checks['title_tag'] = {
                'status': 'fail',
                'score': 0,
                'max_score': 10,
                'message': 'Title tag is missing',
                'recommendation': 'Add a title tag to your page',
                'priority': 'critical'
            }
        
        # Meta description check
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            desc_content = meta_desc.get('content', '').strip()
            if len(desc_content) == 0:
                checks['meta_description'] = {
                    'status': 'fail',
                    'score': 0,
                    'max_score': 10,
                    'message': 'Meta description is empty',
                    'recommendation': 'Add a compelling meta description',
                    'priority': 'high'
                }
            elif len(desc_content) > 160:
                checks['meta_description'] = {
                    'status': 'warning',
                    'score': 7,
                    'max_score': 10,
                    'message': f'Meta description is too long ({len(desc_content)} characters)',
                    'recommendation': 'Keep meta descriptions under 160 characters',
                    'priority': 'medium'
                }
            else:
                checks['meta_description'] = {
                    'status': 'pass',
                    'score': 10,
                    'max_score': 10,
                    'message': f'Meta description length is optimal ({len(desc_content)} characters)',
                    'recommendation': None,
                    'priority': 'low'
                }
        else:
            checks['meta_description'] = {
                'status': 'fail',
                'score': 0,
                'max_score': 10,
                'message': 'Meta description is missing',
                'recommendation': 'Add a meta description to improve click-through rates',
                'priority': 'high'
            }
        
        # H1 tag check
        h1_tags = soup.find_all('h1')
        if len(h1_tags) == 0:
            checks['h1_tag'] = {
                'status': 'fail',
                'score': 0,
                'max_score': 10,
                'message': 'No H1 tag found',
                'recommendation': 'Add an H1 tag to clearly define the main topic of your page',
                'priority': 'high'
            }
        elif len(h1_tags) > 1:
            checks['h1_tag'] = {
                'status': 'warning',
                'score': 5,
                'max_score': 10,
                'message': f'Multiple H1 tags found ({len(h1_tags)})',
                'recommendation': 'Use only one H1 tag per page for better SEO',
                'priority': 'medium'
            }
        else:
            checks['h1_tag'] = {
                'status': 'pass',
                'score': 10,
                'max_score': 10,
                'message': 'Single H1 tag found',
                'recommendation': None,
                'priority': 'low'
            }
        
        return checks
    
    def _check_technical_factors(self, url, soup, response):
        """Check technical SEO factors"""
        checks = {}
        
        # SSL check
        if url.startswith('https://'):
            checks['ssl_certificate'] = {
                'status': 'pass',
                'score': 10,
                'max_score': 10,
                'message': 'SSL certificate is present',
                'recommendation': None,
                'priority': 'low'
            }
        else:
            checks['ssl_certificate'] = {
                'status': 'fail',
                'score': 0,
                'max_score': 10,
                'message': 'No SSL certificate found',
                'recommendation': 'Install an SSL certificate to secure your website',
                'priority': 'critical'
            }
        
        # Robots.txt check
        robots_exists = self._check_robots_txt(url)
        if robots_exists:
            checks['robots_txt'] = {
                'status': 'pass',
                'score': 5,
                'max_score': 5,
                'message': 'Robots.txt file found',
                'recommendation': None,
                'priority': 'low'
            }
        else:
            checks['robots_txt'] = {
                'status': 'warning',
                'score': 0,
                'max_score': 5,
                'message': 'Robots.txt file not found',
                'recommendation': 'Create a robots.txt file to guide search engine crawlers',
                'priority': 'medium'
            }
        
        # Sitemap check
        sitemap_exists = self._check_sitemap(url)
        if sitemap_exists:
            checks['xml_sitemap'] = {
                'status': 'pass',
                'score': 5,
                'max_score': 5,
                'message': 'XML sitemap found',
                'recommendation': None,
                'priority': 'low'
            }
        else:
            checks['xml_sitemap'] = {
                'status': 'warning',
                'score': 0,
                'max_score': 5,
                'message': 'XML sitemap not found',
                'recommendation': 'Create an XML sitemap to help search engines index your content',
                'priority': 'medium'
            }
        
        return checks
    
    def _check_content_factors(self, soup):
        """Check content-related factors"""
        checks = {}
        
        # Image alt attributes
        images = soup.find_all('img')
        images_without_alt = [img for img in images if not img.get('alt')]
        
        if len(images) == 0:
            checks['image_alt_attributes'] = {
                'status': 'info',
                'score': 5,
                'max_score': 5,
                'message': 'No images found on page',
                'recommendation': None,
                'priority': 'low'
            }
        elif len(images_without_alt) == 0:
            checks['image_alt_attributes'] = {
                'status': 'pass',
                'score': 10,
                'max_score': 10,
                'message': 'All images have alt attributes',
                'recommendation': None,
                'priority': 'low'
            }
        else:
            checks['image_alt_attributes'] = {
                'status': 'warning',
                'score': 5,
                'max_score': 10,
                'message': f'{len(images_without_alt)} out of {len(images)} images missing alt attributes',
                'recommendation': 'Add descriptive alt attributes to all images for better accessibility and SEO',
                'priority': 'medium'
            }
        
        # Word count
        text_content = soup.get_text()
        word_count = len(re.findall(r'\b\w+\b', text_content))
        
        if word_count < 300:
            checks['content_length'] = {
                'status': 'warning',
                'score': 3,
                'max_score': 10,
                'message': f'Content is quite short ({word_count} words)',
                'recommendation': 'Consider adding more comprehensive content (aim for 300+ words)',
                'priority': 'medium'
            }
        elif word_count < 500:
            checks['content_length'] = {
                'status': 'pass',
                'score': 7,
                'max_score': 10,
                'message': f'Content length is adequate ({word_count} words)',
                'recommendation': 'Consider expanding content for better SEO value',
                'priority': 'low'
            }
        else:
            checks['content_length'] = {
                'status': 'pass',
                'score': 10,
                'max_score': 10,
                'message': f'Content length is good ({word_count} words)',
                'recommendation': None,
                'priority': 'low'
            }
        
        return checks
    
    def _check_performance_factors(self, response, load_time_ms):
        """Check performance-related factors"""
        checks = {}
        
        # Page load time
        if load_time_ms < 1000:
            checks['page_load_time'] = {
                'status': 'pass',
                'score': 10,
                'max_score': 10,
                'message': f'Page loads quickly ({load_time_ms}ms)',
                'recommendation': None,
                'priority': 'low'
            }
        elif load_time_ms < 3000:
            checks['page_load_time'] = {
                'status': 'warning',
                'score': 7,
                'max_score': 10,
                'message': f'Page load time is acceptable ({load_time_ms}ms)',
                'recommendation': 'Consider optimizing images and scripts to improve load time',
                'priority': 'medium'
            }
        else:
            checks['page_load_time'] = {
                'status': 'fail',
                'score': 3,
                'max_score': 10,
                'message': f'Page loads slowly ({load_time_ms}ms)',
                'recommendation': 'Optimize images, enable compression, and minimize scripts',
                'priority': 'high'
            }
        
        # Compression
        if 'gzip' in response.headers.get('content-encoding', ''):
            checks['gzip_compression'] = {
                'status': 'pass',
                'score': 5,
                'max_score': 5,
                'message': 'GZIP compression is enabled',
                'recommendation': None,
                'priority': 'low'
            }
        else:
            checks['gzip_compression'] = {
                'status': 'fail',
                'score': 0,
                'max_score': 5,
                'message': 'GZIP compression is not enabled',
                'recommendation': 'Enable GZIP compression to reduce page size',
                'priority': 'medium'
            }
        
        return checks
    
    def _check_mobile_factors(self, soup):
        """Check mobile-related factors"""
        checks = {}
        
        # Viewport meta tag
        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        if viewport_meta:
            checks['viewport_meta_tag'] = {
                'status': 'pass',
                'score': 10,
                'max_score': 10,
                'message': 'Viewport meta tag is present',
                'recommendation': None,
                'priority': 'low'
            }
        else:
            checks['viewport_meta_tag'] = {
                'status': 'fail',
                'score': 0,
                'max_score': 10,
                'message': 'Viewport meta tag is missing',
                'recommendation': 'Add a viewport meta tag for mobile responsiveness',
                'priority': 'high'
            }
        
        return checks
    
    def _check_robots_txt(self, url):
        """Check if robots.txt exists"""
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            response = self.session.get(robots_url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def _check_sitemap(self, url):
        """Check if XML sitemap exists"""
        try:
            parsed_url = urlparse(url)
            sitemap_urls = [
                f"{parsed_url.scheme}://{parsed_url.netloc}/sitemap.xml",
                f"{parsed_url.scheme}://{parsed_url.netloc}/sitemap_index.xml"
            ]
            
            for sitemap_url in sitemap_urls:
                response = self.session.get(sitemap_url, timeout=10)
                if response.status_code == 200:
                    return True
            return False
        except:
            return False
    
    def _check_mobile_friendly(self, soup):
        """Check if page is mobile-friendly"""
        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        return viewport_meta is not None
    
    def _extract_schema_markup(self, soup):
        """Extract structured data/schema markup"""
        schema_data = {}
        
        # JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        if json_ld_scripts:
            schema_data['json_ld'] = []
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    schema_data['json_ld'].append(data)
                except:
                    pass
        
        # Microdata
        microdata_items = soup.find_all(attrs={'itemscope': True})
        if microdata_items:
            schema_data['microdata'] = len(microdata_items)
        
        return schema_data
    
    def _extract_social_tags(self, soup):
        """Extract social media meta tags"""
        social_tags = {}
        
        # Open Graph tags
        og_tags = soup.find_all('meta', attrs={'property': re.compile(r'^og:')})
        if og_tags:
            social_tags['open_graph'] = {}
            for tag in og_tags:
                property_name = tag.get('property', '').replace('og:', '')
                social_tags['open_graph'][property_name] = tag.get('content', '')
        
        # Twitter Card tags
        twitter_tags = soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')})
        if twitter_tags:
            social_tags['twitter'] = {}
            for tag in twitter_tags:
                name = tag.get('name', '').replace('twitter:', '')
                social_tags['twitter'][name] = tag.get('content', '')
        
        return social_tags
    
    def _calculate_overall_score(self, details):
        """Calculate overall SEO score based on all checks"""
        total_score = 0
        max_total_score = 0
        
        for category, checks in details.items():
            for check_name, check_data in checks.items():
                if 'score' in check_data and 'max_score' in check_data:
                    total_score += check_data['score']
                    max_total_score += check_data['max_score']
        
        if max_total_score == 0:
            return 0
        
        return round((total_score / max_total_score) * 100)

