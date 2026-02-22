# modules/academy/models.py
from modules.database import db
from datetime import datetime

class AcademyMaster(db.Model):
    __tablename__ = 'academy_masters'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    expertise = db.Column(db.String(200))
    department = db.Column(db.Enum('sales', 'services'), nullable=False)
    bio = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    education = db.Column(db.JSON)
    experience = db.Column(db.JSON)
    courses_count = db.Column(db.Integer, default=0)
    students_count = db.Column(db.Integer, default=0)
    rating = db.Column(db.Numeric(2,1), default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    workshops = db.relationship('AcademyWorkshop', backref='master', lazy=True)
    sessions = db.relationship('AcademySession', backref='master', lazy=True)
    assessments = db.relationship('AcademyAssessment', backref='master', lazy=True)
    qas = db.relationship('AcademyQA', backref='master', lazy=True)


class AcademyWorkshop(db.Model):
    __tablename__ = 'academy_workshops'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    department = db.Column(db.Enum('sales', 'services'), nullable=False)
    master_id = db.Column(db.Integer, db.ForeignKey('academy_masters.id'))
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    capacity = db.Column(db.Integer, default=0)
    registered_count = db.Column(db.Integer, default=0)
    workshop_type = db.Column(db.Enum('online', 'practical', 'theoretical'), default='online')
    status = db.Column(db.Enum('upcoming', 'ongoing', 'completed', 'cancelled'), default='upcoming')
    price = db.Column(db.String(50))
    location = db.Column(db.String(200))
    syllabus = db.Column(db.JSON)
    prerequisites = db.Column(db.JSON)
    target_audience = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    sessions = db.relationship('AcademySession', backref='workshop', lazy=True, cascade='all, delete-orphan')
    registrations = db.relationship('AcademyRegistration', backref='workshop', lazy=True, cascade='all, delete-orphan')
    assessments = db.relationship('AcademyAssessment', backref='workshop', lazy=True)
    qas = db.relationship('AcademyQA', backref='workshop', lazy=True, cascade='all, delete-orphan')


class AcademySession(db.Model):
    __tablename__ = 'academy_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    workshop_id = db.Column(db.Integer, db.ForeignKey('academy_workshops.id'), nullable=False)
    master_id = db.Column(db.Integer, db.ForeignKey('academy_masters.id'))
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    date = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # به دقیقه
    material_url = db.Column(db.String(500))
    video_url = db.Column(db.String(500))
    meeting_link = db.Column(db.String(500))
    status = db.Column(db.Enum('upcoming', 'completed', 'cancelled'), default='upcoming')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AcademyRegistration(db.Model):
    __tablename__ = 'academy_registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    workshop_id = db.Column(db.Integer, db.ForeignKey('academy_workshops.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('registered', 'attended', 'completed', 'cancelled'), default='registered')
    attendance_percentage = db.Column(db.Numeric(5,2), default=0)
    certificate_issued = db.Column(db.Boolean, default=False)
    certificate_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('workshop_id', 'user_id', name='unique_registration'),)


class AcademyAssessment(db.Model):
    __tablename__ = 'academy_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    department = db.Column(db.Enum('sales', 'services'), nullable=False)
    master_id = db.Column(db.Integer, db.ForeignKey('academy_masters.id'))
    workshop_id = db.Column(db.Integer, db.ForeignKey('academy_workshops.id'))
    assessment_type = db.Column(db.Enum('quiz', 'practical', 'survey', 'final'), default='quiz')
    description = db.Column(db.Text)
    questions = db.Column(db.JSON)
    max_score = db.Column(db.Integer, default=100)
    passing_score = db.Column(db.Integer, default=70)
    duration = db.Column(db.Integer)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.Enum('draft', 'active', 'completed', 'archived'), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    results = db.relationship('AcademyAssessmentResult', backref='assessment', lazy=True, cascade='all, delete-orphan')


class AcademyAssessmentResult(db.Model):
    __tablename__ = 'academy_assessment_results'
    
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('academy_assessments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Numeric(5,2))
    answers = db.Column(db.JSON)
    status = db.Column(db.Enum('passed', 'failed', 'pending'), default='pending')
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('assessment_id', 'user_id', name='unique_assessment_user'),)


class AcademyQA(db.Model):
    __tablename__ = 'academy_qa'
    
    id = db.Column(db.Integer, primary_key=True)
    workshop_id = db.Column(db.Integer, db.ForeignKey('academy_workshops.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    master_id = db.Column(db.Integer, db.ForeignKey('academy_masters.id'))
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text)
    is_answered = db.Column(db.Boolean, default=False)
    answered_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade='all, delete-orphan')


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    role = db.Column(db.Enum('user', 'assistant', 'system'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AcademySchedule(db.Model):
    __tablename__ = 'academy_schedule'
    
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.Enum('sales', 'services'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    event_type = db.Column(db.Enum('workshop', 'assessment', 'session', 'holiday', 'other'), default='workshop')
    related_id = db.Column(db.Integer)
    color = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)