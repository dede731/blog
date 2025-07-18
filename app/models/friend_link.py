from datetime import datetime
from app import db

class FriendLink(db.Model):
    __tablename__ = 'friend_links'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    logo = db.Column(db.String(255))
    order = db.Column(db.Integer, default=0)  # 用于排序
    is_active = db.Column(db.Boolean, default=True)  # 是否显示
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FriendLink {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'description': self.description,
            'logo': self.logo,
            'order': self.order,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }