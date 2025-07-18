from datetime import datetime
from app import db

class SensitiveWord(db.Model):
    """敏感词模型
    
    用于存储系统中的敏感词，支持对评论和留言进行过滤。
    """
    __tablename__ = 'sensitive_words'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # 关联关系
    creator = db.relationship('User', backref=db.backref('sensitive_words', lazy='dynamic'))
    
    def __repr__(self):
        return f'<SensitiveWord {self.word}>'