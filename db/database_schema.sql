-- SEOptimer Alternative Database Schema
-- Comprehensive database design for SEO analysis platform

-- Users table for authentication and account management
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    company_name VARCHAR(255),
    subscription_tier VARCHAR(50) DEFAULT 'free',
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    api_key VARCHAR(255) UNIQUE,
    monthly_audit_limit INTEGER DEFAULT 10,
    monthly_audits_used INTEGER DEFAULT 0,
    reset_date DATE
);

-- White label settings for custom branding
CREATE TABLE white_label_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    brand_name VARCHAR(255),
    logo_url VARCHAR(500),
    primary_color VARCHAR(7) DEFAULT '#007bff',
    secondary_color VARCHAR(7) DEFAULT '#6c757d',
    accent_color VARCHAR(7) DEFAULT '#28a745',
    font_family VARCHAR(100) DEFAULT 'Arial, sans-serif',
    custom_css TEXT,
    footer_text TEXT,
    contact_email VARCHAR(255),
    website_url VARCHAR(500),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Websites registry for tracking analyzed sites
CREATE TABLE websites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(500),
    description TEXT,
    favicon_url VARCHAR(500),
    first_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_analyzed TIMESTAMP,
    total_audits INTEGER DEFAULT 0,
    average_score DECIMAL(5,2),
    is_active BOOLEAN DEFAULT TRUE
);

-- Main audits table for tracking analysis requests
CREATE TABLE audits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    website_id INTEGER NOT NULL,
    url VARCHAR(1000) NOT NULL,
    audit_type VARCHAR(50) DEFAULT 'full',
    overall_score INTEGER,
    status VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    user_agent VARCHAR(500),
    ip_address VARCHAR(45),
    is_public BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE
);

-- Detailed audit results for each check category
CREATE TABLE audit_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_id INTEGER NOT NULL,
    category VARCHAR(100) NOT NULL,
    check_name VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'pass', 'fail', 'warning', 'info'
    score INTEGER,
    max_score INTEGER,
    message TEXT,
    recommendation TEXT,
    technical_details JSON,
    priority VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (audit_id) REFERENCES audits(id) ON DELETE CASCADE
);

-- SEO metrics and technical data
CREATE TABLE seo_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_id INTEGER NOT NULL,
    page_title VARCHAR(500),
    meta_description TEXT,
    h1_tags JSON,
    h2_tags JSON,
    h3_tags JSON,
    images_count INTEGER,
    images_without_alt INTEGER,
    internal_links INTEGER,
    external_links INTEGER,
    word_count INTEGER,
    page_size_kb DECIMAL(10,2),
    load_time_ms INTEGER,
    mobile_friendly BOOLEAN,
    ssl_enabled BOOLEAN,
    robots_txt_exists BOOLEAN,
    sitemap_exists BOOLEAN,
    canonical_url VARCHAR(1000),
    schema_markup JSON,
    social_tags JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (audit_id) REFERENCES audits(id) ON DELETE CASCADE
);

-- Performance metrics
CREATE TABLE performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_id INTEGER NOT NULL,
    first_contentful_paint INTEGER,
    largest_contentful_paint INTEGER,
    first_input_delay INTEGER,
    cumulative_layout_shift DECIMAL(5,3),
    speed_index INTEGER,
    time_to_interactive INTEGER,
    total_blocking_time INTEGER,
    performance_score INTEGER,
    accessibility_score INTEGER,
    best_practices_score INTEGER,
    seo_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (audit_id) REFERENCES audits(id) ON DELETE CASCADE
);

-- Backlinks tracking and monitoring
CREATE TABLE backlinks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    website_id INTEGER NOT NULL,
    source_domain VARCHAR(255) NOT NULL,
    source_url VARCHAR(1000) NOT NULL,
    target_url VARCHAR(1000) NOT NULL,
    anchor_text TEXT,
    link_type VARCHAR(50), -- 'dofollow', 'nofollow', 'ugc', 'sponsored'
    discovered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'lost', 'broken'
    domain_authority INTEGER,
    page_authority INTEGER,
    spam_score INTEGER,
    link_context TEXT,
    is_internal BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE
);

-- Social media profiles and metrics
CREATE TABLE social_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    website_id INTEGER NOT NULL,
    platform VARCHAR(50) NOT NULL, -- 'facebook', 'twitter', 'linkedin', 'instagram', etc.
    profile_url VARCHAR(500),
    username VARCHAR(100),
    followers_count INTEGER,
    following_count INTEGER,
    posts_count INTEGER,
    engagement_rate DECIMAL(5,2),
    last_post_date TIMESTAMP,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE
);

-- Security scan results
CREATE TABLE security_scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_id INTEGER NOT NULL,
    ssl_certificate JSON,
    ssl_grade VARCHAR(5),
    ssl_expires_at TIMESTAMP,
    malware_detected BOOLEAN DEFAULT FALSE,
    blacklist_status JSON,
    security_headers JSON,
    vulnerabilities JSON,
    security_score INTEGER,
    scan_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (audit_id) REFERENCES audits(id) ON DELETE CASCADE
);

-- Generated reports tracking
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_id INTEGER NOT NULL,
    user_id INTEGER,
    report_type VARCHAR(50) DEFAULT 'pdf', -- 'pdf', 'html', 'json'
    file_path VARCHAR(500),
    file_size_kb INTEGER,
    white_label_id INTEGER,
    download_count INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (audit_id) REFERENCES audits(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (white_label_id) REFERENCES white_label_settings(id) ON DELETE SET NULL
);

-- Subscription management
CREATE TABLE subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plan_name VARCHAR(100) NOT NULL,
    plan_type VARCHAR(50) NOT NULL, -- 'monthly', 'yearly'
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'cancelled', 'expired', 'suspended'
    paypal_subscription_id VARCHAR(255),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    auto_renew BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Payment transactions
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subscription_id INTEGER,
    paypal_payment_id VARCHAR(255),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) NOT NULL, -- 'pending', 'completed', 'failed', 'refunded'
    payment_method VARCHAR(50) DEFAULT 'paypal',
    transaction_fee DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE SET NULL
);

-- Lead generation and tracking
CREATE TABLE leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, -- The agency/consultant who owns the lead
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    company_name VARCHAR(255),
    phone VARCHAR(50),
    website_url VARCHAR(500),
    audit_id INTEGER,
    source VARCHAR(100), -- 'embedded_widget', 'landing_page', 'api'
    status VARCHAR(50) DEFAULT 'new', -- 'new', 'contacted', 'qualified', 'converted', 'lost'
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (audit_id) REFERENCES audits(id) ON DELETE SET NULL
);

-- API usage tracking
CREATE TABLE api_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER,
    response_time_ms INTEGER,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- System settings and configuration
CREATE TABLE system_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(50) DEFAULT 'string', -- 'string', 'integer', 'boolean', 'json'
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance optimization
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_api_key ON users(api_key);
CREATE INDEX idx_audits_user_id ON audits(user_id);
CREATE INDEX idx_audits_website_id ON audits(website_id);
CREATE INDEX idx_audits_status ON audits(status);
CREATE INDEX idx_audits_created_at ON audits(started_at);
CREATE INDEX idx_audit_details_audit_id ON audit_details(audit_id);
CREATE INDEX idx_audit_details_category ON audit_details(category);
CREATE INDEX idx_backlinks_website_id ON backlinks(website_id);
CREATE INDEX idx_backlinks_source_domain ON backlinks(source_domain);
CREATE INDEX idx_backlinks_status ON backlinks(status);
CREATE INDEX idx_social_profiles_website_id ON social_profiles(website_id);
CREATE INDEX idx_social_profiles_platform ON social_profiles(platform);
CREATE INDEX idx_reports_audit_id ON reports(audit_id);
CREATE INDEX idx_reports_user_id ON reports(user_id);
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_leads_user_id ON leads(user_id);
CREATE INDEX idx_leads_email ON leads(email);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX idx_api_usage_created_at ON api_usage(created_at);

-- Insert default system settings
INSERT INTO system_settings (setting_key, setting_value, setting_type, description, is_public) VALUES
('site_name', 'SEO Analyzer Pro', 'string', 'Application name', TRUE),
('site_description', 'Professional SEO Analysis and Reporting Tool', 'string', 'Application description', TRUE),
('max_free_audits_per_month', '10', 'integer', 'Maximum free audits per user per month', FALSE),
('audit_timeout_seconds', '300', 'integer', 'Maximum time for audit completion', FALSE),
('report_retention_days', '90', 'integer', 'Days to keep generated reports', FALSE),
('enable_registration', 'true', 'boolean', 'Allow new user registration', TRUE),
('maintenance_mode', 'false', 'boolean', 'Enable maintenance mode', TRUE),
('paypal_client_id', '', 'string', 'PayPal client ID for payments', FALSE),
('paypal_environment', 'sandbox', 'string', 'PayPal environment (sandbox/live)', FALSE),
('smtp_host', '', 'string', 'SMTP server for email sending', FALSE),
('smtp_port', '587', 'integer', 'SMTP server port', FALSE),
('default_audit_checks', '["seo", "performance", "security", "social"]', 'json', 'Default audit check categories', FALSE);

