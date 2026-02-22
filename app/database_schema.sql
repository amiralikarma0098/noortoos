-- دیتابیس تحلیل CRM - نسخه کامل
CREATE DATABASE IF NOT EXISTS crm_analyzer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE crm_analyzer;

-- جدول تحلیل‌ها - نسخه کامل
DROP TABLE IF EXISTS techniques;
DROP TABLE IF EXISTS objections;
DROP TABLE IF EXISTS weaknesses;
DROP TABLE IF EXISTS strengths;
DROP TABLE IF EXISTS top_customers;
DROP TABLE IF EXISTS active_users;
DROP TABLE IF EXISTS analyses;


-- ========================================
-- جداول احراز هویت و کاربران
-- ========================================

-- جدول کاربران
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role ENUM('admin', 'manager', 'analyst', 'viewer') DEFAULT 'viewer',
    department VARCHAR(100),
    position VARCHAR(100),
    phone VARCHAR(20),
    avatar_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- جدول نشست‌ها (برای مدیریت توکن‌ها)
CREATE TABLE IF NOT EXISTS sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- جدول لاگ فعالیت‌ها
CREATE TABLE IF NOT EXISTS activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INT,
    details JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- جدول تنظیمات کاربر
CREATE TABLE IF NOT EXISTS user_settings (
    user_id INT PRIMARY KEY,
    theme ENUM('light', 'dark', 'system') DEFAULT 'system',
    language VARCHAR(10) DEFAULT 'fa',
    notifications JSON,
    dashboard_config JSON,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ایجاد کاربر ادمین پیش‌فرض (رمز: Admin@123)
-- INSERT INTO users (username, email, password_hash, full_name, role) 
-- VALUES ('admin', 'admin@noortoos.ir', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj2NqKQqVxWC', 'مدیر سیستم', 'admin');



CREATE TABLE analyses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- اطلاعات فایل
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INT NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    
    -- زمان
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    analyzed_at DATETIME NOT NULL,
    
    -- امتیازها (0-10)
    score_total DECIMAL(3,1) DEFAULT 0,
    score_rapport DECIMAL(3,1) DEFAULT 0,
    score_needs DECIMAL(3,1) DEFAULT 0,
    score_value DECIMAL(3,1) DEFAULT 0,
    score_objection DECIMAL(3,1) DEFAULT 0,
    score_price DECIMAL(3,1) DEFAULT 0,
    score_closing DECIMAL(3,1) DEFAULT 0,
    score_followup DECIMAL(3,1) DEFAULT 0,
    score_empathy DECIMAL(3,1) DEFAULT 0,
    score_listening DECIMAL(3,1) DEFAULT 0,
    
    -- فیلدهای عددی اضافی
    lead_quality_percent DECIMAL(5,2) DEFAULT 0,
    open_questions_count INT DEFAULT 0,
    objections_count INT DEFAULT 0,
    objection_success_percent DECIMAL(5,2) DEFAULT 0,
    closing_attempts_count INT DEFAULT 0,
    customer_feeling_score DECIMAL(3,1) DEFAULT 0,
    closing_readiness_percent DECIMAL(5,2) DEFAULT 0,
    seller_technical_density_percent DECIMAL(5,2) DEFAULT 0,
    customer_technical_density_percent DECIMAL(5,2) DEFAULT 0,
    customer_price_sensitivity_percent DECIMAL(5,2) DEFAULT 0,
    customer_risk_sensitivity_percent DECIMAL(5,2) DEFAULT 0,
    customer_time_sensitivity_percent DECIMAL(5,2) DEFAULT 0,
    yes_ladder_count INT DEFAULT 0,
    
    -- DISC (0-10)
    disc_d DECIMAL(3,1) DEFAULT 0,
    disc_i DECIMAL(3,1) DEFAULT 0,
    disc_s DECIMAL(3,1) DEFAULT 0,
    disc_c DECIMAL(3,1) DEFAULT 0,
    
    -- اطلاعات متنی اصلی
    seller_name VARCHAR(255),
    seller_code VARCHAR(10),
    customer_name VARCHAR(255),
    call_duration VARCHAR(50),
    call_direction VARCHAR(50),
    call_stage VARCHAR(50),
    call_warmth VARCHAR(50),
    call_nature VARCHAR(50),
    product VARCHAR(255),
    seller_level VARCHAR(50),
    disc_type VARCHAR(10),
    disc_evidence TEXT,
    disc_interaction_guide TEXT,
    preferred_channel VARCHAR(100),
    customer_awareness_level VARCHAR(100),
    
    -- نسبت‌ها
    customer_talk_ratio VARCHAR(50),
    seller_talk_ratio VARCHAR(50),
    
    -- متن‌های طولانی
    summary TEXT,
    customer_personality_analysis TEXT,
    seller_individual_performance TEXT,
    call_type_readiness TEXT,
    next_action TEXT,
    
    -- دلایل کاهش امتیازها
    rapport_decrease_reasons TEXT,
    needs_decrease_reasons TEXT,
    value_decrease_reasons TEXT,
    objection_decrease_reasons TEXT,
    price_decrease_reasons TEXT,
    closing_decrease_reasons TEXT,
    followup_decrease_reasons TEXT,
    empathy_decrease_reasons TEXT,
    listening_decrease_reasons TEXT,
    
    -- دلایل کسب امتیازها
    rapport_increase_reasons TEXT,
    needs_increase_reasons TEXT,
    value_increase_reasons TEXT,
    objection_increase_reasons TEXT,
    price_increase_reasons TEXT,
    closing_increase_reasons TEXT,
    followup_increase_reasons TEXT,
    empathy_increase_reasons TEXT,
    listening_increase_reasons TEXT,
    
    -- آمار
    total_calls INT DEFAULT 0,
    successful_calls INT DEFAULT 0,
    no_answer_calls INT DEFAULT 0,
    referred_calls INT DEFAULT 0,
    
    -- بهترین‌ها با دلیل
    best_seller TEXT,
    best_seller_reason TEXT,
    best_customer TEXT,
    best_customer_reason TEXT,
    
    -- JSON کامل تحلیل
    full_analysis JSON NOT NULL,
    
    -- ایندکس‌ها
    INDEX idx_created_at (created_at),
    INDEX idx_file_name (file_name),
    INDEX idx_seller_name (seller_name),
    INDEX idx_customer_name (customer_name),
    INDEX idx_score_total (score_total)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول کاربران فعال
CREATE TABLE active_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    call_count INT DEFAULT 1,
    performance_note TEXT,
    
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE,
    INDEX idx_analysis_id (analysis_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول مشتریان پرتماس
CREATE TABLE top_customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    contact_count INT DEFAULT 1,
    interaction_quality TEXT,
    
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE,
    INDEX idx_analysis_id (analysis_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول نقاط قوت
CREATE TABLE strengths (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    strength TEXT NOT NULL,
    example TEXT,
    
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE,
    INDEX idx_analysis_id (analysis_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول نقاط ضعف
CREATE TABLE weaknesses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    weakness TEXT NOT NULL,
    improvement_suggestion TEXT,
    
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE,
    INDEX idx_analysis_id (analysis_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول اعتراضات
CREATE TABLE objections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    objection TEXT NOT NULL,
    response_quality VARCHAR(50),
    
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE,
    INDEX idx_analysis_id (analysis_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول تکنیک‌ها
CREATE TABLE techniques (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    technique TEXT NOT NULL,
    effectiveness VARCHAR(50),
    
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE,
    INDEX idx_analysis_id (analysis_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول کلمات کلیدی مثبت
CREATE TABLE positive_keywords (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    keyword VARCHAR(255) NOT NULL,
    context TEXT,
    
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE,
    INDEX idx_analysis_id (analysis_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول کلمات کلیدی منفی
CREATE TABLE negative_keywords (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    keyword VARCHAR(255) NOT NULL,
    context TEXT,
    
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE,
    INDEX idx_analysis_id (analysis_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول ریسک‌ها
CREATE TABLE risks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    risk TEXT NOT NULL,
    severity VARCHAR(50),
    mitigation TEXT,
    
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE,
    INDEX idx_analysis_id (analysis_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول پارامترهای رعایت نشده
CREATE TABLE missed_parameters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    parameter TEXT NOT NULL,
    impact TEXT,
    
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE,
    INDEX idx_analysis_id (analysis_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول اشتباهات رایج
CREATE TABLE common_mistakes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    mistake TEXT NOT NULL,
    frequency INT DEFAULT 1,
    correction TEXT,
    
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE,
    INDEX idx_analysis_id (analysis_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- جدول اصلی ارجاعیات
CREATE TABLE referral_analyses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    file_name VARCHAR(255),
    file_path VARCHAR(500),
    file_size INT,
    analyzed_at DATETIME,
    
    -- آمار کلی
    total_referrals INT,
    completed_count INT,
    pending_count INT,
    in_progress_count INT,
    seen_count INT,
    accepted_count INT,
    
    -- درصدها
    completion_rate FLOAT,
    pending_rate FLOAT,
    
    -- JSON کامل برای ذخیره تمام جزئیات
    full_analysis JSON,
    
    created_at DATETIME DEFAULT NOW()
);

-- جدول جزئیات وضعیت‌ها
CREATE TABLE referral_status_details (
    id INT PRIMARY KEY AUTO_INCREMENT,
    analysis_id INT,
    status_name VARCHAR(50),
    status_count INT,
    FOREIGN KEY (analysis_id) REFERENCES referral_analyses(id)
);

-- جدول موضوعات
CREATE TABLE referral_subjects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    analysis_id INT,
    subject_name VARCHAR(255),
    frequency INT,
    avg_response_time FLOAT,
    pending_count INT,
    FOREIGN KEY (analysis_id) REFERENCES referral_analyses(id)
);

-- جدول فرستنده‌ها و گیرنده‌ها
CREATE TABLE referral_units (
    id INT PRIMARY KEY AUTO_INCREMENT,
    analysis_id INT,
    unit_name VARCHAR(100),
    role ENUM('sender', 'receiver'),
    referral_count INT,
    pending_count INT,
    FOREIGN KEY (analysis_id) REFERENCES referral_analyses(id)
);

-- جدول مشتریان
CREATE TABLE referral_customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    analysis_id INT,
    customer_name VARCHAR(255),
    subscription_code VARCHAR(50),
    referral_count INT,
    subjects TEXT,
    FOREIGN KEY (analysis_id) REFERENCES referral_analyses(id)
);

-- جدول بینش‌ها و توصیه‌ها
CREATE TABLE referral_insights (
    id INT PRIMARY KEY AUTO_INCREMENT,
    analysis_id INT,
    insight_type ENUM('pattern', 'factor', 'recommendation'),
    insight_text TEXT,
    frequency INT,
    FOREIGN KEY (analysis_id) REFERENCES referral_analyses(id)
);




-- ====================================================
-- جداول آموزشگاه (Academy)
-- ====================================================

-- 1. جدول اساتید (Academy Masters)
CREATE TABLE IF NOT EXISTS `academy_masters` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `full_name` VARCHAR(100) NOT NULL,
    `expertise` VARCHAR(200),
    `department` ENUM('sales', 'services') NOT NULL,
    `bio` TEXT,
    `image_url` VARCHAR(500),
    `email` VARCHAR(100),
    `phone` VARCHAR(20),
    `education` JSON,  -- برای ذخیره تحصیلات به صورت JSON
    `experience` JSON, -- برای ذخیره سوابق به صورت JSON
    `courses_count` INT DEFAULT 0,
    `students_count` INT DEFAULT 0,
    `rating` DECIMAL(2,1) DEFAULT 0,
    `is_active` BOOLEAN DEFAULT TRUE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_department` (`department`),
    INDEX `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_persian_ci;

-- 2. جدول کارگاه‌های آموزشی (Academy Workshops)
CREATE TABLE IF NOT EXISTS `academy_workshops` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `title` VARCHAR(200) NOT NULL,
    `department` ENUM('sales', 'services') NOT NULL,
    `master_id` INT,
    `description` TEXT,
    `start_date` DATETIME,
    `end_date` DATETIME,
    `capacity` INT DEFAULT 0,
    `registered_count` INT DEFAULT 0,
    `workshop_type` ENUM('online', 'practical', 'theoretical') DEFAULT 'online',
    `status` ENUM('upcoming', 'ongoing', 'completed', 'cancelled') DEFAULT 'upcoming',
    `price` VARCHAR(50),
    `location` VARCHAR(200),
    `syllabus` JSON,  -- سرفصل‌های دوره
    `prerequisites` JSON,  -- پیش‌نیازها
    `target_audience` JSON,  -- مخاطبان هدف
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`master_id`) REFERENCES `academy_masters`(`id`) ON DELETE SET NULL,
    INDEX `idx_department` (`department`),
    INDEX `idx_status` (`status`),
    INDEX `idx_dates` (`start_date`, `end_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_persian_ci;

-- 3. جدول جلسات کارگاه (Workshop Sessions)
CREATE TABLE IF NOT EXISTS `academy_sessions` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `workshop_id` INT NOT NULL,
    `master_id` INT,
    `title` VARCHAR(200),
    `description` TEXT,
    `date` DATETIME,
    `duration` INT,  -- به دقیقه
    `material_url` VARCHAR(500),
    `video_url` VARCHAR(500),
    `meeting_link` VARCHAR(500),
    `status` ENUM('upcoming', 'completed', 'cancelled') DEFAULT 'upcoming',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`workshop_id`) REFERENCES `academy_workshops`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`master_id`) REFERENCES `academy_masters`(`id`) ON DELETE SET NULL,
    INDEX `idx_workshop` (`workshop_id`),
    INDEX `idx_date` (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_persian_ci;

-- 4. جدول ثبت‌نام در کارگاه‌ها (Workshop Registrations)
CREATE TABLE IF NOT EXISTS `academy_registrations` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `workshop_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    `registration_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `status` ENUM('registered', 'attended', 'completed', 'cancelled') DEFAULT 'registered',
    `attendance_percentage` DECIMAL(5,2) DEFAULT 0,
    `certificate_issued` BOOLEAN DEFAULT FALSE,
    `certificate_url` VARCHAR(500),
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`workshop_id`) REFERENCES `academy_workshops`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `unique_registration` (`workshop_id`, `user_id`),
    INDEX `idx_user` (`user_id`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_persian_ci;

-- 5. جدول سنجش و ارزیابی (Assessments)
CREATE TABLE IF NOT EXISTS `academy_assessments` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `title` VARCHAR(200) NOT NULL,
    `department` ENUM('sales', 'services') NOT NULL,
    `master_id` INT,
    `workshop_id` INT,
    `assessment_type` ENUM('quiz', 'practical', 'survey', 'final') DEFAULT 'quiz',
    `description` TEXT,
    `questions` JSON,  -- ذخیره سوالات به صورت JSON
    `max_score` INT DEFAULT 100,
    `passing_score` INT DEFAULT 70,
    `duration` INT,  -- به دقیقه
    `start_date` DATETIME,
    `end_date` DATETIME,
    `status` ENUM('draft', 'active', 'completed', 'archived') DEFAULT 'draft',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`master_id`) REFERENCES `academy_masters`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`workshop_id`) REFERENCES `academy_workshops`(`id`) ON DELETE CASCADE,
    INDEX `idx_department` (`department`),
    INDEX `idx_status` (`status`),
    INDEX `idx_dates` (`start_date`, `end_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_persian_ci;

-- 6. جدول نتایج سنجش (Assessment Results)
CREATE TABLE IF NOT EXISTS `academy_assessment_results` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `assessment_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    `score` DECIMAL(5,2),
    `answers` JSON,  -- ذخیره پاسخ‌ها
    `status` ENUM('passed', 'failed', 'pending') DEFAULT 'pending',
    `started_at` TIMESTAMP NULL,
    `completed_at` TIMESTAMP NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`assessment_id`) REFERENCES `academy_assessments`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `unique_assessment_user` (`assessment_id`, `user_id`),
    INDEX `idx_user` (`user_id`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_persian_ci;

-- 7. جدول پرسش و پاسخ (Q&A)
CREATE TABLE IF NOT EXISTS `academy_qa` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `workshop_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    `master_id` INT,
    `question` TEXT NOT NULL,
    `answer` TEXT,
    `is_answered` BOOLEAN DEFAULT FALSE,
    `answered_at` TIMESTAMP NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`workshop_id`) REFERENCES `academy_workshops`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`master_id`) REFERENCES `academy_masters`(`id`) ON DELETE SET NULL,
    INDEX `idx_workshop` (`workshop_id`),
    INDEX `idx_is_answered` (`is_answered`),
    INDEX `idx_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_persian_ci;

-- 8. جدول مکالمات چت (Chat Sessions)
CREATE TABLE IF NOT EXISTS `chat_sessions` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `user_id` INT NOT NULL,
    `title` VARCHAR(200),
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_user` (`user_id`),
    INDEX `idx_updated` (`updated_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_persian_ci;

-- 9. جدول پیام‌های چت (Chat Messages)
CREATE TABLE IF NOT EXISTS `chat_messages` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `session_id` INT NOT NULL,
    `role` ENUM('user', 'assistant', 'system') NOT NULL,
    `content` TEXT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`session_id`) REFERENCES `chat_sessions`(`id`) ON DELETE CASCADE,
    INDEX `idx_session` (`session_id`),
    INDEX `idx_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_persian_ci;

-- 10. جدول تقویم آموزشی (Schedule)
CREATE TABLE IF NOT EXISTS `academy_schedule` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `department` ENUM('sales', 'services') NOT NULL,
    `title` VARCHAR(200) NOT NULL,
    `description` TEXT,
    `event_date` DATETIME NOT NULL,
    `event_type` ENUM('workshop', 'assessment', 'session', 'holiday', 'other') DEFAULT 'workshop',
    `related_id` INT,  -- ID مربوط به رویداد (مثلاً workshop_id)
    `color` VARCHAR(20),
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_department` (`department`),
    INDEX `idx_date` (`event_date`),
    INDEX `idx_type` (`event_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_persian_ci;

-- ====================================================
-- درج داده‌های نمونه (Optional)
-- ====================================================

-- اساتید نمونه
INSERT INTO `academy_masters` (`full_name`, `expertise`, `department`, `bio`, `courses_count`, `students_count`, `rating`) VALUES
('دکتر علی محمدی', 'فروش و بازاریابی پیشرفته', 'sales', 'دکترای مدیریت بازاریابی با ۱۵ سال سابقه تدریس در سازمان‌های بزرگ', 12, 450, 4.8),
('مهندس سارا احمدی', 'مذاکرات فروش حرفه‌ای', 'sales', 'مشاور فروش شرکت‌های بزرگ با سابقه بیش از ۱۰۰۰ ساعت کارگاه آموزشی', 8, 320, 4.9),
('دکتر رضا حسینی', 'مدیریت ارتباط با مشتری', 'services', 'دکترای مدیریت خدمات با سابقه اجرایی در شرکت‌های بین‌المللی', 10, 380, 4.7),
('مهندس مریم کریمی', 'خدمات پس از فروش', 'services', 'کارشناس ارشد مدیریت خدمات با ۱۲ سال سابقه در صنعت خودرو', 6, 210, 4.6);

-- کارگاه‌های نمونه
INSERT INTO `academy_workshops` (`title`, `department`, `master_id`, `description`, `start_date`, `end_date`, `capacity`, `workshop_type`, `status`, `price`, `location`) VALUES
('کارگاه فروش حرفه‌ای', 'sales', 1, 'آموزش تکنیک‌های پیشرفته فروش و مذاکره', '2025-03-15 10:00:00', '2025-03-17 18:00:00', 30, 'online', 'upcoming', 'رایگان', 'آنلاین - اسکای روم'),
('مدیریت ارتباط با مشتری', 'services', 3, 'اصول و تکنیک‌های مدیریت ارتباط با مشتری', '2025-03-20 09:00:00', '2025-03-22 17:00:00', 25, 'practical', 'upcoming', '450,000 تومان', 'مشهد - بلوار وکیل‌آباد'),
('مذاکرات فروش پیشرفته', 'sales', 2, 'تکنیک‌های مذاکره در فروش B2B', '2025-02-10 10:00:00', '2025-02-12 18:00:00', 20, 'online', 'completed', 'رایگان', 'آنلاین - اسکای روم');