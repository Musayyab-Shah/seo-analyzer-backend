from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Website(db.Model):
    __tablename__ = 'websites'
    
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), unique=True, nullable=False)
    title = db.Column(db.String(500))
    description = db.Column(db.Text)
    favicon_url = db.Column(db.String(500))
    first_analyzed = db.Column(db.DateTime, default=datetime.utcnow)
    last_analyzed = db.Column(db.DateTime)
    total_audits = db.Column(db.Integer, default=0)
    average_score = db.Column(db.Numeric(5, 2))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    audits = db.relationship('Audit', backref='website', lazy=True, cascade='all, delete-orphan')
    backlinks = db.relationship('Backlink', backref='website', lazy=True, cascade='all, delete-orphan')
    social_profiles = db.relationship('SocialProfile', backref='website', lazy=True, cascade='all, delete-orphan')

class Audit(db.Model):
    __tablename__ = 'audits'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    website_id = db.Column(db.Integer, db.ForeignKey('websites.id'), nullable=False)
    url = db.Column(db.String(1000), nullable=False)
    audit_type = db.Column(db.String(50), default='full')
    overall_score = db.Column(db.Integer)
    status = db.Column(db.String(50), default='pending')
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    user_agent = db.Column(db.String(500))
    ip_address = db.Column(db.String(45))
    is_public = db.Column(db.Boolean, default=False)
    
    # Relationships
    audit_details = db.relationship('AuditDetail', backref='audit', lazy=True, cascade='all, delete-orphan')
    seo_metrics = db.relationship('SEOMetrics', backref='audit', uselist=False, cascade='all, delete-orphan')
    performance_metrics = db.relationship('PerformanceMetrics', backref='audit', uselist=False, cascade='all, delete-orphan')
    security_scans = db.relationship('SecurityScan', backref='audit', uselist=False, cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='audit', lazy=True, cascade='all, delete-orphan')

class AuditDetail(db.Model):
    __tablename__ = 'audit_details'
    
    id = db.Column(db.Integer, primary_key=True)
    audit_id = db.Column(db.Integer, db.ForeignKey('audits.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    check_name = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'pass', 'fail', 'warning', 'info'
    score = db.Column(db.Integer)
    max_score = db.Column(db.Integer)
    message = db.Column(db.Text)
    recommendation = db.Column(db.Text)
    technical_details = db.Column(db.Text)  # JSON string
    priority = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high', 'critical'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_technical_details(self, data):
        self.technical_details = json.dumps(data)
    
    def get_technical_details(self):
        if self.technical_details:
            return json.loads(self.technical_details)
        return {}

class SEOMetrics(db.Model):
    __tablename__ = 'seo_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    audit_id = db.Column(db.Integer, db.ForeignKey('audits.id'), nullable=False)
    page_title = db.Column(db.String(500))
    meta_description = db.Column(db.Text)
    h1_tags = db.Column(db.Text)  # JSON string
    h2_tags = db.Column(db.Text)  # JSON string
    h3_tags = db.Column(db.Text)  # JSON string
    images_count = db.Column(db.Integer)
    images_without_alt = db.Column(db.Integer)
    internal_links = db.Column(db.Integer)
    external_links = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    page_size_kb = db.Column(db.Numeric(10, 2))
    load_time_ms = db.Column(db.Integer)
    mobile_friendly = db.Column(db.Boolean)
    ssl_enabled = db.Column(db.Boolean)
    robots_txt_exists = db.Column(db.Boolean)
    sitemap_exists = db.Column(db.Boolean)
    canonical_url = db.Column(db.String(1000))
    schema_markup = db.Column(db.Text)  # JSON string
    social_tags = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_h1_tags(self, tags):
        self.h1_tags = json.dumps(tags)
    
    def get_h1_tags(self):
        if self.h1_tags:
            return json.loads(self.h1_tags)
        return []
    
    def set_h2_tags(self, tags):
        self.h2_tags = json.dumps(tags)
    
    def get_h2_tags(self):
        if self.h2_tags:
            return json.loads(self.h2_tags)
        return []
    
    def set_h3_tags(self, tags):
        self.h3_tags = json.dumps(tags)
    
    def get_h3_tags(self):
        if self.h3_tags:
            return json.loads(self.h3_tags)
        return []
    
    def set_schema_markup(self, data):
        self.schema_markup = json.dumps(data)
    
    def get_schema_markup(self):
        if self.schema_markup:
            return json.loads(self.schema_markup)
        return {}
    
    def set_social_tags(self, data):
        self.social_tags = json.dumps(data)
    
    def get_social_tags(self):
        if self.social_tags:
            return json.loads(self.social_tags)
        return {}

class PerformanceMetrics(db.Model):
    __tablename__ = 'performance_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    audit_id = db.Column(db.Integer, db.ForeignKey('audits.id'), nullable=False)
    first_contentful_paint = db.Column(db.Integer)
    largest_contentful_paint = db.Column(db.Integer)
    first_input_delay = db.Column(db.Integer)
    cumulative_layout_shift = db.Column(db.Numeric(5, 3))
    speed_index = db.Column(db.Integer)
    time_to_interactive = db.Column(db.Integer)
    total_blocking_time = db.Column(db.Integer)
    performance_score = db.Column(db.Integer)
    accessibility_score = db.Column(db.Integer)
    best_practices_score = db.Column(db.Integer)
    seo_score = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Backlink(db.Model):
    __tablename__ = 'backlinks'
    
    id = db.Column(db.Integer, primary_key=True)
    website_id = db.Column(db.Integer, db.ForeignKey('websites.id'), nullable=False)
    source_domain = db.Column(db.String(255), nullable=False)
    source_url = db.Column(db.String(1000), nullable=False)
    target_url = db.Column(db.String(1000), nullable=False)
    anchor_text = db.Column(db.Text)
    link_type = db.Column(db.String(50))  # 'dofollow', 'nofollow', 'ugc', 'sponsored'
    discovered_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # 'active', 'lost', 'broken'
    domain_authority = db.Column(db.Integer)
    page_authority = db.Column(db.Integer)
    spam_score = db.Column(db.Integer)
    link_context = db.Column(db.Text)
    is_internal = db.Column(db.Boolean, default=False)

class SocialProfile(db.Model):
    __tablename__ = 'social_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    website_id = db.Column(db.Integer, db.ForeignKey('websites.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # 'facebook', 'twitter', 'linkedin', 'instagram', etc.
    profile_url = db.Column(db.String(500))
    username = db.Column(db.String(100))
    followers_count = db.Column(db.Integer)
    following_count = db.Column(db.Integer)
    posts_count = db.Column(db.Integer)
    engagement_rate = db.Column(db.Numeric(5, 2))
    last_post_date = db.Column(db.DateTime)
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class SecurityScan(db.Model):
    __tablename__ = 'security_scans'
    
    id = db.Column(db.Integer, primary_key=True)
    audit_id = db.Column(db.Integer, db.ForeignKey('audits.id'), nullable=False)
    ssl_certificate = db.Column(db.Text)  # JSON string
    ssl_grade = db.Column(db.String(5))
    ssl_expires_at = db.Column(db.DateTime)
    malware_detected = db.Column(db.Boolean, default=False)
    blacklist_status = db.Column(db.Text)  # JSON string
    security_headers = db.Column(db.Text)  # JSON string
    vulnerabilities = db.Column(db.Text)  # JSON string
    security_score = db.Column(db.Integer)
    scan_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_ssl_certificate(self, data):
        self.ssl_certificate = json.dumps(data)
    
    def get_ssl_certificate(self):
        if self.ssl_certificate:
            return json.loads(self.ssl_certificate)
        return {}
    
    def set_blacklist_status(self, data):
        self.blacklist_status = json.dumps(data)
    
    def get_blacklist_status(self):
        if self.blacklist_status:
            return json.loads(self.blacklist_status)
        return {}
    
    def set_security_headers(self, data):
        self.security_headers = json.dumps(data)
    
    def get_security_headers(self):
        if self.security_headers:
            return json.loads(self.security_headers)
        return {}
    
    def set_vulnerabilities(self, data):
        self.vulnerabilities = json.dumps(data)
    
    def get_vulnerabilities(self):
        if self.vulnerabilities:
            return json.loads(self.vulnerabilities)
        return {}

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    audit_id = db.Column(db.Integer, db.ForeignKey('audits.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    report_type = db.Column(db.String(50), default='pdf')  # 'pdf', 'html', 'json'
    file_path = db.Column(db.String(500))
    file_size_kb = db.Column(db.Integer)
    white_label_id = db.Column(db.Integer)
    download_count = db.Column(db.Integer, default=0)
    is_public = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

