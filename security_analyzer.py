import requests
import ssl
import socket
from urllib.parse import urlparse, urljoin
import re
from datetime import datetime, timedelta
import json
import hashlib

class SecurityAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 30
        
        # Security headers to check
        self.security_headers = {
            'strict-transport-security': {
                'name': 'HTTP Strict Transport Security (HSTS)',
                'importance': 'high',
                'description': 'Enforces secure HTTPS connections'
            },
            'content-security-policy': {
                'name': 'Content Security Policy (CSP)',
                'importance': 'high',
                'description': 'Prevents XSS and code injection attacks'
            },
            'x-frame-options': {
                'name': 'X-Frame-Options',
                'importance': 'medium',
                'description': 'Prevents clickjacking attacks'
            },
            'x-content-type-options': {
                'name': 'X-Content-Type-Options',
                'importance': 'medium',
                'description': 'Prevents MIME type sniffing'
            },
            'x-xss-protection': {
                'name': 'X-XSS-Protection',
                'importance': 'low',
                'description': 'Legacy XSS protection (deprecated but still useful)'
            },
            'referrer-policy': {
                'name': 'Referrer Policy',
                'importance': 'low',
                'description': 'Controls referrer information sent with requests'
            },
            'permissions-policy': {
                'name': 'Permissions Policy',
                'importance': 'medium',
                'description': 'Controls browser feature permissions'
            }
        }
        
        # Known malicious domains/IPs (simplified list)
        self.blacklist_sources = [
            'google_safe_browsing',
            'phishtank',
            'malware_domain_list',
            'spamhaus'
        ]
    
    def analyze_security(self, target_url):
        """Perform comprehensive security analysis"""
        try:
            parsed_url = urlparse(target_url)
            domain = parsed_url.netloc
            
            security_results = {
                'ssl_analysis': self._analyze_ssl(target_url),
                'security_headers': self._analyze_security_headers(target_url),
                'malware_scan': self._scan_for_malware(target_url),
                'blacklist_check': self._check_blacklists(domain),
                'vulnerability_scan': self._scan_vulnerabilities(target_url),
                'privacy_analysis': self._analyze_privacy(target_url),
                'overall_score': 0,
                'recommendations': [],
                'analysis_date': datetime.utcnow().isoformat()
            }
            
            # Calculate overall security score
            security_results['overall_score'] = self._calculate_security_score(security_results)
            
            # Generate recommendations
            security_results['recommendations'] = self._generate_security_recommendations(security_results)
            
            return security_results
            
        except Exception as e:
            raise Exception(f"Security analysis failed: {str(e)}")
    
    def _analyze_ssl(self, target_url):
        """Analyze SSL certificate and configuration"""
        try:
            parsed_url = urlparse(target_url)
            hostname = parsed_url.netloc
            port = 443
            
            if not target_url.startswith('https://'):
                return {
                    'enabled': False,
                    'grade': 'F',
                    'score': 0,
                    'issues': ['SSL not enabled - site uses HTTP instead of HTTPS'],
                    'certificate': None,
                    'protocols': [],
                    'cipher_suites': []
                }
            
            # Get SSL certificate information
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    protocol = ssock.version()
                    
                    # Parse certificate details
                    cert_info = {
                        'subject': dict(x[0] for x in cert['subject']),
                        'issuer': dict(x[0] for x in cert['issuer']),
                        'version': cert['version'],
                        'serial_number': cert['serialNumber'],
                        'not_before': cert['notBefore'],
                        'not_after': cert['notAfter'],
                        'signature_algorithm': cert.get('signatureAlgorithm', 'Unknown')
                    }
                    
                    # Check certificate validity
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after - datetime.utcnow()).days
                    
                    # Analyze SSL configuration
                    issues = []
                    score = 100
                    
                    # Check expiry
                    if days_until_expiry < 0:
                        issues.append('Certificate has expired')
                        score -= 50
                    elif days_until_expiry < 30:
                        issues.append(f'Certificate expires in {days_until_expiry} days')
                        score -= 20
                    
                    # Check protocol version
                    if protocol in ['TLSv1', 'TLSv1.1']:
                        issues.append(f'Outdated TLS protocol: {protocol}')
                        score -= 30
                    elif protocol == 'TLSv1.2':
                        score -= 5  # Slight deduction for not using TLS 1.3
                    
                    # Check cipher suite
                    if cipher and len(cipher) >= 3:
                        cipher_name = cipher[0]
                        if 'RC4' in cipher_name or 'DES' in cipher_name:
                            issues.append(f'Weak cipher suite: {cipher_name}')
                            score -= 25
                    
                    # Determine grade
                    if score >= 90:
                        grade = 'A+'
                    elif score >= 80:
                        grade = 'A'
                    elif score >= 70:
                        grade = 'B'
                    elif score >= 60:
                        grade = 'C'
                    elif score >= 50:
                        grade = 'D'
                    else:
                        grade = 'F'
                    
                    return {
                        'enabled': True,
                        'grade': grade,
                        'score': max(0, score),
                        'issues': issues,
                        'certificate': cert_info,
                        'protocol': protocol,
                        'cipher_suite': cipher[0] if cipher else None,
                        'days_until_expiry': days_until_expiry
                    }
                    
        except Exception as e:
            return {
                'enabled': False,
                'grade': 'F',
                'score': 0,
                'issues': [f'SSL analysis failed: {str(e)}'],
                'certificate': None,
                'protocol': None,
                'cipher_suite': None
            }
    
    def _analyze_security_headers(self, target_url):
        """Analyze HTTP security headers"""
        try:
            response = self.session.get(target_url, timeout=self.timeout)
            headers = response.headers
            
            header_analysis = {}
            total_score = 0
            max_score = 0
            
            for header_name, header_info in self.security_headers.items():
                max_score += self._get_header_max_score(header_info['importance'])
                
                if header_name.lower() in [h.lower() for h in headers.keys()]:
                    # Header is present
                    header_value = headers.get(header_name) or headers.get(header_name.title())
                    score = self._score_header_value(header_name, header_value)
                    total_score += score
                    
                    header_analysis[header_name] = {
                        'present': True,
                        'value': header_value,
                        'score': score,
                        'max_score': self._get_header_max_score(header_info['importance']),
                        'analysis': self._analyze_header_value(header_name, header_value)
                    }
                else:
                    # Header is missing
                    header_analysis[header_name] = {
                        'present': False,
                        'value': None,
                        'score': 0,
                        'max_score': self._get_header_max_score(header_info['importance']),
                        'analysis': f'Missing {header_info["name"]} header'
                    }
            
            overall_score = (total_score / max_score * 100) if max_score > 0 else 0
            
            return {
                'overall_score': round(overall_score, 1),
                'headers': header_analysis,
                'recommendations': self._get_header_recommendations(header_analysis)
            }
            
        except Exception as e:
            return {
                'overall_score': 0,
                'headers': {},
                'recommendations': [f'Failed to analyze security headers: {str(e)}']
            }
    
    def _scan_for_malware(self, target_url):
        """Scan for malware and malicious content"""
        try:
            # In a real implementation, you would integrate with:
            # - Google Safe Browsing API
            # - VirusTotal API
            # - URLVoid API
            # - PhishTank API
            
            # For demo purposes, we'll simulate malware scanning
            domain = urlparse(target_url).netloc
            
            # Simulate various checks
            scan_results = {
                'malware_detected': False,
                'phishing_detected': False,
                'suspicious_content': False,
                'blacklisted': False,
                'scan_engines': {
                    'google_safe_browsing': {'status': 'clean', 'last_scan': datetime.utcnow().isoformat()},
                    'virustotal': {'status': 'clean', 'detections': 0, 'total_engines': 70},
                    'phishtank': {'status': 'clean', 'verified': False},
                    'urlvoid': {'status': 'clean', 'detections': 0, 'total_engines': 30}
                },
                'content_analysis': {
                    'suspicious_scripts': 0,
                    'external_resources': 0,
                    'redirects': 0,
                    'iframe_count': 0
                }
            }
            
            # Perform basic content analysis
            try:
                response = self.session.get(target_url, timeout=self.timeout)
                content = response.text
                
                # Check for suspicious patterns
                suspicious_patterns = [
                    r'eval\s*\(',
                    r'document\.write\s*\(',
                    r'fromCharCode',
                    r'unescape\s*\(',
                    r'<script[^>]*src=["\'][^"\']*[^a-zA-Z0-9\-\._/]["\']'
                ]
                
                for pattern in suspicious_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        scan_results['content_analysis']['suspicious_scripts'] += len(matches)
                
                # Count external resources
                external_resources = re.findall(r'src=["\']https?://[^"\']*["\']', content)
                scan_results['content_analysis']['external_resources'] = len(external_resources)
                
                # Count iframes
                iframes = re.findall(r'<iframe[^>]*>', content, re.IGNORECASE)
                scan_results['content_analysis']['iframe_count'] = len(iframes)
                
                # Check for suspicious content
                if (scan_results['content_analysis']['suspicious_scripts'] > 5 or
                    scan_results['content_analysis']['external_resources'] > 20):
                    scan_results['suspicious_content'] = True
                
            except Exception:
                pass
            
            return scan_results
            
        except Exception as e:
            return {
                'malware_detected': False,
                'phishing_detected': False,
                'suspicious_content': False,
                'blacklisted': False,
                'scan_engines': {},
                'content_analysis': {},
                'error': str(e)
            }
    
    def _check_blacklists(self, domain):
        """Check domain against various blacklists"""
        try:
            # Simulate blacklist checking
            # In reality, you'd check against:
            # - Spamhaus
            # - SURBL
            # - URIBL
            # - Google Safe Browsing
            # - PhishTank
            
            blacklist_results = {}
            
            for source in self.blacklist_sources:
                # Simulate check
                blacklist_results[source] = {
                    'listed': False,
                    'last_checked': datetime.utcnow().isoformat(),
                    'status': 'clean'
                }
            
            # Calculate overall blacklist status
            total_lists = len(self.blacklist_sources)
            clean_lists = sum(1 for result in blacklist_results.values() if not result['listed'])
            
            return {
                'blacklisted': False,
                'clean_lists': clean_lists,
                'total_lists': total_lists,
                'reputation_score': (clean_lists / total_lists * 100) if total_lists > 0 else 100,
                'details': blacklist_results
            }
            
        except Exception as e:
            return {
                'blacklisted': False,
                'clean_lists': 0,
                'total_lists': 0,
                'reputation_score': 0,
                'details': {},
                'error': str(e)
            }
    
    def _scan_vulnerabilities(self, target_url):
        """Scan for common web vulnerabilities"""
        try:
            vulnerabilities = []
            
            # Check for common vulnerabilities
            response = self.session.get(target_url, timeout=self.timeout)
            headers = response.headers
            content = response.text
            
            # Check for information disclosure
            server_header = headers.get('Server', '')
            if server_header:
                if re.search(r'Apache/[\d\.]+', server_header) or re.search(r'nginx/[\d\.]+', server_header):
                    vulnerabilities.append({
                        'type': 'information_disclosure',
                        'severity': 'low',
                        'description': 'Server version information disclosed',
                        'evidence': f'Server header: {server_header}',
                        'recommendation': 'Hide server version information'
                    })
            
            # Check for missing security headers (already covered in header analysis)
            
            # Check for mixed content
            if target_url.startswith('https://'):
                http_resources = re.findall(r'src=["\']http://[^"\']*["\']', content)
                if http_resources:
                    vulnerabilities.append({
                        'type': 'mixed_content',
                        'severity': 'medium',
                        'description': 'Mixed content detected (HTTPS page loading HTTP resources)',
                        'evidence': f'{len(http_resources)} HTTP resources found',
                        'recommendation': 'Use HTTPS for all resources or use protocol-relative URLs'
                    })
            
            # Check for potential XSS vulnerabilities (basic check)
            if '<script>' in content.lower() and 'user' in content.lower():
                vulnerabilities.append({
                    'type': 'potential_xss',
                    'severity': 'high',
                    'description': 'Potential XSS vulnerability detected',
                    'evidence': 'Unescaped script tags found in content',
                    'recommendation': 'Implement proper input validation and output encoding'
                })
            
            # Check for clickjacking protection
            if 'x-frame-options' not in [h.lower() for h in headers.keys()]:
                vulnerabilities.append({
                    'type': 'clickjacking',
                    'severity': 'medium',
                    'description': 'No clickjacking protection detected',
                    'evidence': 'Missing X-Frame-Options header',
                    'recommendation': 'Add X-Frame-Options: DENY or SAMEORIGIN header'
                })
            
            return {
                'total_vulnerabilities': len(vulnerabilities),
                'high_severity': len([v for v in vulnerabilities if v['severity'] == 'high']),
                'medium_severity': len([v for v in vulnerabilities if v['severity'] == 'medium']),
                'low_severity': len([v for v in vulnerabilities if v['severity'] == 'low']),
                'vulnerabilities': vulnerabilities
            }
            
        except Exception as e:
            return {
                'total_vulnerabilities': 0,
                'high_severity': 0,
                'medium_severity': 0,
                'low_severity': 0,
                'vulnerabilities': [],
                'error': str(e)
            }
    
    def _analyze_privacy(self, target_url):
        """Analyze privacy-related aspects"""
        try:
            response = self.session.get(target_url, timeout=self.timeout)
            content = response.text
            
            privacy_analysis = {
                'cookies': self._analyze_cookies(response),
                'tracking_scripts': self._detect_tracking_scripts(content),
                'privacy_policy': self._check_privacy_policy(content, target_url),
                'gdpr_compliance': self._check_gdpr_compliance(content),
                'data_collection': self._analyze_data_collection(content)
            }
            
            return privacy_analysis
            
        except Exception as e:
            return {
                'cookies': {},
                'tracking_scripts': {},
                'privacy_policy': {},
                'gdpr_compliance': {},
                'data_collection': {},
                'error': str(e)
            }
    
    def _analyze_cookies(self, response):
        """Analyze cookies for privacy compliance"""
        cookies = response.cookies
        
        cookie_analysis = {
            'total_cookies': len(cookies),
            'secure_cookies': 0,
            'httponly_cookies': 0,
            'samesite_cookies': 0,
            'third_party_cookies': 0,
            'details': []
        }
        
        for cookie in cookies:
            cookie_info = {
                'name': cookie.name,
                'secure': cookie.secure,
                'httponly': cookie.has_nonstandard_attr('HttpOnly'),
                'samesite': cookie.get_nonstandard_attr('SameSite'),
                'domain': cookie.domain,
                'path': cookie.path
            }
            
            if cookie.secure:
                cookie_analysis['secure_cookies'] += 1
            if cookie_info['httponly']:
                cookie_analysis['httponly_cookies'] += 1
            if cookie_info['samesite']:
                cookie_analysis['samesite_cookies'] += 1
            
            cookie_analysis['details'].append(cookie_info)
        
        return cookie_analysis
    
    def _detect_tracking_scripts(self, content):
        """Detect tracking and analytics scripts"""
        tracking_patterns = {
            'google_analytics': r'google-analytics\.com|gtag\(',
            'facebook_pixel': r'facebook\.net|fbq\(',
            'google_tag_manager': r'googletagmanager\.com',
            'hotjar': r'hotjar\.com',
            'mixpanel': r'mixpanel\.com',
            'segment': r'segment\.(io|com)',
            'intercom': r'intercom\.io',
            'drift': r'drift\.com'
        }
        
        detected_trackers = {}
        
        for tracker, pattern in tracking_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                detected_trackers[tracker] = {
                    'detected': True,
                    'occurrences': len(matches)
                }
        
        return {
            'total_trackers': len(detected_trackers),
            'trackers': detected_trackers
        }
    
    def _check_privacy_policy(self, content, target_url):
        """Check for privacy policy"""
        privacy_keywords = ['privacy policy', 'privacy notice', 'data protection', 'cookie policy']
        
        found_links = []
        for keyword in privacy_keywords:
            pattern = rf'<a[^>]*href=["\']([^"\']*)["\'][^>]*>{keyword}</a>'
            matches = re.findall(pattern, content, re.IGNORECASE)
            found_links.extend(matches)
        
        return {
            'privacy_policy_found': len(found_links) > 0,
            'privacy_links': found_links,
            'keywords_found': len([k for k in privacy_keywords if k.lower() in content.lower()])
        }
    
    def _check_gdpr_compliance(self, content):
        """Check for GDPR compliance indicators"""
        gdpr_indicators = [
            'gdpr', 'general data protection regulation', 'cookie consent',
            'data subject rights', 'right to be forgotten', 'data controller'
        ]
        
        found_indicators = [indicator for indicator in gdpr_indicators 
                           if indicator.lower() in content.lower()]
        
        return {
            'gdpr_indicators_found': len(found_indicators),
            'indicators': found_indicators,
            'likely_compliant': len(found_indicators) >= 2
        }
    
    def _analyze_data_collection(self, content):
        """Analyze potential data collection points"""
        form_inputs = re.findall(r'<input[^>]*type=["\']([^"\']*)["\'][^>]*>', content, re.IGNORECASE)
        
        sensitive_inputs = ['email', 'password', 'tel', 'credit', 'ssn', 'phone']
        sensitive_found = [inp for inp in form_inputs if any(sens in inp.lower() for sens in sensitive_inputs)]
        
        return {
            'total_form_inputs': len(form_inputs),
            'sensitive_inputs': len(sensitive_found),
            'input_types': list(set(form_inputs))
        }
    
    def _get_header_max_score(self, importance):
        """Get maximum score for a security header based on importance"""
        scores = {'high': 20, 'medium': 15, 'low': 10}
        return scores.get(importance, 10)
    
    def _score_header_value(self, header_name, header_value):
        """Score a security header value"""
        importance = self.security_headers[header_name]['importance']
        max_score = self._get_header_max_score(importance)
        
        if not header_value:
            return 0
        
        # Basic scoring - in reality, you'd have more sophisticated analysis
        if header_name == 'strict-transport-security':
            if 'max-age' in header_value and 'includeSubDomains' in header_value:
                return max_score
            elif 'max-age' in header_value:
                return max_score * 0.8
            else:
                return max_score * 0.5
        
        # For other headers, give full score if present
        return max_score
    
    def _analyze_header_value(self, header_name, header_value):
        """Analyze security header value"""
        if not header_value:
            return f'Missing {header_name} header'
        
        if header_name == 'strict-transport-security':
            if 'max-age' not in header_value:
                return 'HSTS header missing max-age directive'
            elif 'includeSubDomains' not in header_value:
                return 'HSTS header should include includeSubDomains'
            else:
                return 'HSTS header properly configured'
        
        return f'{header_name} header present'
    
    def _get_header_recommendations(self, header_analysis):
        """Get recommendations for security headers"""
        recommendations = []
        
        for header_name, analysis in header_analysis.items():
            if not analysis['present']:
                header_info = self.security_headers[header_name]
                recommendations.append(
                    f"Add {header_info['name']} header: {header_info['description']}"
                )
        
        return recommendations
    
    def _calculate_security_score(self, security_results):
        """Calculate overall security score"""
        score = 0
        max_score = 100
        
        # SSL score (30%)
        ssl_score = security_results['ssl_analysis']['score']
        score += (ssl_score / 100) * 30
        
        # Security headers score (25%)
        headers_score = security_results['security_headers']['overall_score']
        score += (headers_score / 100) * 25
        
        # Malware/blacklist score (25%)
        malware_clean = not security_results['malware_scan']['malware_detected']
        blacklist_clean = not security_results['blacklist_check']['blacklisted']
        if malware_clean and blacklist_clean:
            score += 25
        elif malware_clean or blacklist_clean:
            score += 12.5
        
        # Vulnerability score (20%)
        vuln_results = security_results['vulnerability_scan']
        if vuln_results['high_severity'] == 0:
            if vuln_results['medium_severity'] == 0:
                score += 20
            else:
                score += 15
        elif vuln_results['high_severity'] <= 2:
            score += 10
        else:
            score += 5
        
        return min(100, round(score, 1))
    
    def _generate_security_recommendations(self, security_results):
        """Generate security recommendations"""
        recommendations = []
        
        # SSL recommendations
        ssl_analysis = security_results['ssl_analysis']
        if not ssl_analysis['enabled']:
            recommendations.append({
                'type': 'ssl',
                'priority': 'critical',
                'title': 'Enable HTTPS',
                'description': 'Install an SSL certificate and redirect all HTTP traffic to HTTPS'
            })
        elif ssl_analysis['grade'] in ['C', 'D', 'F']:
            recommendations.append({
                'type': 'ssl',
                'priority': 'high',
                'title': 'Improve SSL Configuration',
                'description': 'Update SSL configuration to use modern protocols and cipher suites'
            })
        
        # Security headers recommendations
        headers_recommendations = security_results['security_headers']['recommendations']
        for rec in headers_recommendations:
            recommendations.append({
                'type': 'headers',
                'priority': 'medium',
                'title': 'Security Headers',
                'description': rec
            })
        
        # Vulnerability recommendations
        vulnerabilities = security_results['vulnerability_scan']['vulnerabilities']
        for vuln in vulnerabilities:
            priority = 'high' if vuln['severity'] == 'high' else 'medium'
            recommendations.append({
                'type': 'vulnerability',
                'priority': priority,
                'title': vuln['type'].replace('_', ' ').title(),
                'description': vuln['recommendation']
            })
        
        return recommendations

