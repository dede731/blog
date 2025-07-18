from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

# 导入敏感词模型
from app.models.sensitive_word import SensitiveWord
# 导入友情链接模型
from app.models.friend_link import FriendLink
# 导入公告模型
from app.models.announcement import Announcement

# 文章标签关联表
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(255), default='default.jpg')
    bio = db.Column(db.Text)
    website = db.Column(db.String(255))
    location = db.Column(db.String(100))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    likes = db.relationship('Like', backref='user', lazy='dynamic')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(255))  # 专栏封面
    is_active = db.Column(db.Boolean, default=True)  # 是否启用
    sort_order = db.Column(db.Integer, default=0)  # 排序
    posts = db.relationship('Post', backref='category', lazy='dynamic')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_post_count(self):
        """获取专栏文章数量"""
        return self.posts.filter_by(is_published=True).count()
    
    def get_latest_post(self):
        """获取最新文章"""
        return self.posts.filter_by(is_published=True).order_by(Post.created_at.desc()).first()

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Tag {self.name}>'

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), index=True)
    content = db.Column(db.Text)
    summary = db.Column(db.String(255))
    slug = db.Column(db.String(255), unique=True, index=True)
    cover_image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    is_published = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)
    featured = db.Column(db.Boolean, default=False)
    allow_comments = db.Column(db.Boolean, default=True)
    meta_description = db.Column(db.String(160))
    meta_keywords = db.Column(db.String(255))
    
    # 关联关系
    tags = db.relationship('Tag', secondary=post_tags, lazy='subquery',
                          backref=db.backref('posts', lazy=True))
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy='dynamic', cascade='all, delete-orphan')

    def get_like_count(self):
        return self.likes.count()

    def is_liked_by(self, user, guest_ip=None):
        if user and not user.is_anonymous:
            return self.likes.filter_by(user_id=user.id).first() is not None
        elif guest_ip:
            return self.likes.filter_by(guest_ip=guest_ip).first() is not None
        else:
            return False

    def get_comment_count(self):
        return self.comments.filter_by(approved=True).count()

    def increment_views(self):
        self.views += 1
        db.session.add(self)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'content': self.content,
            'slug': self.slug,
            'author': self.author.username,
            'category': self.category.name if self.category else None,
            'tags': [tag.name for tag in self.tags],
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'views': self.views,
            'likes': self.get_like_count(),
            'comments': self.get_comment_count()
        }

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    approved = db.Column(db.Boolean, default=True)
    
    # 自引用关系，支持评论回复
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'author': self.author.username,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'replies_count': self.replies.count()
        }

class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 注册用户ID，访客为空
    guest_ip = db.Column(db.String(45), nullable=True)  # 访客IP地址，注册用户为空
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 确保用户对同一篇文章只能点赞一次（注册用户或访客）
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),
        db.UniqueConstraint('guest_ip', 'post_id', name='unique_guest_post_like'),
        db.CheckConstraint('(user_id IS NOT NULL AND guest_ip IS NULL) OR (user_id IS NULL AND guest_ip IS NOT NULL)', name='check_user_or_guest')
    )

class Newsletter(db.Model):
    __tablename__ = 'newsletters'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class SiteConfig(db.Model):
    __tablename__ = 'site_configs'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GuestbookMessage(db.Model):
    __tablename__ = 'guestbook_messages'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_visible = db.Column(db.Boolean, default=True)
    
    # 关联关系
    author = db.relationship('User', backref=db.backref('guestbook_messages', lazy='dynamic'))
    replies = db.relationship('GuestbookReply', backref='message', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<GuestbookMessage {self.id}>'    

class GuestbookReply(db.Model):
    __tablename__ = 'guestbook_replies'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message_id = db.Column(db.Integer, db.ForeignKey('guestbook_messages.id'))
    is_visible = db.Column(db.Boolean, default=True)
    
    # 关联关系
    author = db.relationship('User', backref=db.backref('guestbook_replies', lazy='dynamic'))
    
    def __repr__(self):
        return f'<GuestbookReply {self.id}>'