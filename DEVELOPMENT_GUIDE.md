# Trace_vlog 开发指南

## 📋 目录

- [开发环境搭建](#开发环境搭建)
- [项目结构](#项目结构)
- [代码规范](#代码规范)
- [开发工作流](#开发工作流)
- [测试指南](#测试指南)
- [调试技巧](#调试技巧)
- [性能优化](#性能优化)
- [部署流程](#部署流程)
- [常见问题](#常见问题)

## 🛠️ 开发环境搭建

### 1. 系统要求

- **Python**: 3.8+
- **数据库**: SQLite (开发) / MySQL/PostgreSQL (生产)
- **缓存**: Redis (可选，用于缓存和会话)
- **Node.js**: 16+ (用于前端资源构建)
- **Git**: 版本控制

### 2. 环境配置

#### 克隆项目
```bash
git clone https://github.com/your-username/Trace_vlog.git
cd Trace_vlog
```

#### 创建虚拟环境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 安装依赖
```bash
# Python 依赖
pip install -r requirements.txt

# 开发依赖
pip install -r requirements-dev.txt

# 前端依赖 (如果有)
npm install
```

#### 环境变量配置
创建 `.env` 文件：
```bash
# 基础配置
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# 数据库配置
DATABASE_URL=sqlite:///blog.db

# Redis 配置 (可选)
REDIS_URL=redis://localhost:6379/0

# 邮件配置
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# 文件上传配置
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# 调试配置
DEBUG=True
TESTING=False
```

#### 数据库初始化
```bash
# 初始化数据库
flask db init

# 创建迁移
flask db migrate -m "Initial migration"

# 应用迁移
flask db upgrade

# 创建管理员账户
python create_admin.py
```

### 3. IDE 配置

#### VS Code 推荐配置
创建 `.vscode/settings.json`：
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "editor.formatOnSave": true,
    "editor.rulers": [88],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/venv": true,
        "**/.pytest_cache": true
    }
}
```

推荐扩展：
- Python
- Flask Snippets
- SQLite Viewer
- GitLens
- Prettier
- Auto Rename Tag

## 📁 项目结构

```
Trace_vlog/
├── app/                    # 应用主目录
│   ├── __init__.py        # 应用工厂
│   ├── models.py          # 数据模型
│   ├── auth/              # 认证蓝图
│   │   ├── __init__.py
│   │   ├── routes.py      # 认证路由
│   │   └── forms.py       # 认证表单
│   ├── main/              # 主要功能蓝图
│   │   ├── __init__.py
│   │   ├── routes.py      # 主要路由
│   │   └── forms.py       # 主要表单
│   ├── admin/             # 管理后台蓝图
│   │   ├── __init__.py
│   │   ├── routes.py      # 管理路由
│   │   └── forms.py       # 管理表单
│   ├── api/               # API 蓝图
│   │   ├── __init__.py
│   │   └── routes.py      # API 路由
│   ├── templates/         # 模板文件
│   │   ├── base.html      # 基础模板
│   │   ├── auth/          # 认证模板
│   │   ├── main/          # 主要模板
│   │   └── admin/         # 管理模板
│   ├── static/            # 静态文件
│   │   ├── css/           # 样式文件
│   │   ├── js/            # JavaScript 文件
│   │   ├── img/           # 图片文件
│   │   └── uploads/       # 上传文件
│   └── utils/             # 工具模块
│       ├── __init__.py
│       ├── sensitive_word_filter.py
│       ├── email.py
│       └── helpers.py
├── migrations/            # 数据库迁移文件
├── tests/                 # 测试文件
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_main.py
│   └── test_models.py
├── config.py              # 配置文件
├── run.py                 # 应用入口
├── requirements.txt       # 生产依赖
├── requirements-dev.txt   # 开发依赖
├── .env.example          # 环境变量示例
├── .gitignore            # Git 忽略文件
├── README.md             # 项目说明
├── DEPLOYMENT.md         # 部署文档
├── PROJECT_DOCS.md       # 项目文档
└── DEVELOPMENT_GUIDE.md  # 开发指南
```

## 📝 代码规范

### 1. Python 代码规范

#### PEP 8 标准
- 使用 4 个空格缩进
- 行长度限制为 88 字符
- 函数和类之间空两行
- 导入语句按标准库、第三方库、本地库分组

#### 命名规范
```python
# 变量和函数：小写字母 + 下划线
user_name = "admin"
def get_user_posts():
    pass

# 类名：大驼峰命名
class UserModel:
    pass

# 常量：大写字母 + 下划线
MAX_FILE_SIZE = 1024 * 1024

# 私有变量/方法：前缀下划线
class User:
    def __init__(self):
        self._private_var = None
    
    def _private_method(self):
        pass
```

#### 文档字符串
```python
def search_posts(query, category_id=None, page=1, per_page=10):
    """
    搜索文章
    
    Args:
        query (str): 搜索关键词
        category_id (int, optional): 分类ID
        page (int): 页码，默认为1
        per_page (int): 每页数量，默认为10
    
    Returns:
        Pagination: 分页对象，包含搜索结果
    
    Raises:
        ValueError: 当搜索参数无效时
    
    Example:
        >>> posts = search_posts("Python", category_id=1)
        >>> print(posts.items)
    """
    pass
```

#### 类型注解
```python
from typing import List, Optional, Dict, Any

def get_posts_by_category(category_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """获取指定分类的文章"""
    pass

class PostService:
    def __init__(self, db_session: Any) -> None:
        self.db = db_session
    
    def create_post(self, title: str, content: str, author_id: int) -> Optional[int]:
        """创建文章，返回文章ID"""
        pass
```

### 2. HTML/CSS 规范

#### HTML 规范
```html
<!-- 使用语义化标签 -->
<article class="post-card">
    <header class="post-header">
        <h2 class="post-title">{{ post.title }}</h2>
        <time class="post-date" datetime="{{ post.created_at.isoformat() }}">
            {{ post.created_at.strftime('%Y-%m-%d') }}
        </time>
    </header>
    
    <main class="post-content">
        <p class="post-summary">{{ post.summary }}</p>
    </main>
    
    <footer class="post-footer">
        <a href="{{ url_for('main.post_detail', id=post.id) }}" class="read-more">
            阅读更多
        </a>
    </footer>
</article>
```

#### CSS 规范
```css
/* BEM 命名规范 */
.post-card {
    /* 块 */
}

.post-card__title {
    /* 元素 */
}

.post-card--featured {
    /* 修饰符 */
}

/* 使用 CSS 自定义属性 */
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --font-size-base: 1rem;
    --line-height-base: 1.5;
}

.btn-primary {
    background-color: var(--primary-color);
    font-size: var(--font-size-base);
    line-height: var(--line-height-base);
}
```

### 3. JavaScript 规范

#### ES6+ 语法
```javascript
// 使用 const/let 而不是 var
const API_BASE_URL = '/api';
let currentPage = 1;

// 使用箭头函数
const fetchPosts = async (page = 1) => {
    try {
        const response = await fetch(`${API_BASE_URL}/posts?page=${page}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('获取文章失败:', error);
        throw error;
    }
};

// 使用解构赋值
const { posts, pagination } = await fetchPosts();

// 使用模板字符串
const postHtml = `
    <article class="post-card">
        <h3>${post.title}</h3>
        <p>${post.summary}</p>
    </article>
`;
```

#### 类和模块
```javascript
// 使用 ES6 类
class SearchManager {
    constructor(inputSelector, suggestionsSelector) {
        this.input = document.querySelector(inputSelector);
        this.suggestions = document.querySelector(suggestionsSelector);
        this.debounceTimer = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
    }
    
    bindEvents() {
        this.input.addEventListener('input', this.handleInput.bind(this));
    }
    
    handleInput = (event) => {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.fetchSuggestions(event.target.value);
        }, 300);
    }
    
    async fetchSuggestions(query) {
        // 实现搜索建议逻辑
    }
}

// 模块导出
export default SearchManager;
```

## 🔄 开发工作流

### 1. Git 工作流

#### 分支策略
```bash
# 主分支
main          # 生产环境代码
develop       # 开发环境代码

# 功能分支
feature/search-functionality
feature/user-authentication
feature/admin-dashboard

# 修复分支
hotfix/security-patch
hotfix/critical-bug-fix

# 发布分支
release/v1.0.0
release/v1.1.0
```

#### 提交规范
```bash
# 提交消息格式
<type>(<scope>): <subject>

<body>

<footer>

# 类型说明
feat:     新功能
fix:      修复bug
docs:     文档更新
style:    代码格式调整
refactor: 代码重构
test:     测试相关
chore:    构建过程或辅助工具的变动

# 示例
feat(search): 添加全文搜索功能

- 实现多关键词搜索
- 添加搜索建议功能
- 优化搜索结果排序

Closes #123
```

#### 开发流程
```bash
# 1. 从 develop 分支创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# 2. 开发功能
# ... 编写代码 ...

# 3. 提交代码
git add .
git commit -m "feat(feature): 添加新功能"

# 4. 推送到远程
git push origin feature/new-feature

# 5. 创建 Pull Request
# 在 GitHub/GitLab 上创建 PR，请求合并到 develop

# 6. 代码审查和合并
# 经过代码审查后合并到 develop

# 7. 删除功能分支
git checkout develop
git pull origin develop
git branch -d feature/new-feature
```

### 2. 代码审查

#### 审查清单
- [ ] 代码符合项目规范
- [ ] 功能实现正确
- [ ] 测试覆盖充分
- [ ] 性能影响可接受
- [ ] 安全性考虑
- [ ] 文档更新完整
- [ ] 无明显的代码异味

#### 审查工具
```bash
# 代码质量检查
flake8 app/
pylint app/
black --check app/

# 安全检查
bandit -r app/

# 测试覆盖率
pytest --cov=app tests/
```

## 🧪 测试指南

### 1. 测试结构

```
tests/
├── conftest.py           # 测试配置和夹具
├── test_models.py        # 模型测试
├── test_auth.py          # 认证测试
├── test_main.py          # 主要功能测试
├── test_admin.py         # 管理功能测试
├── test_api.py           # API 测试
└── test_utils.py         # 工具函数测试
```

### 2. 测试配置

#### conftest.py
```python
import pytest
import tempfile
import os
from app import create_app, db
from app.models import User, Post, Category
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'

@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """创建测试命令行运行器"""
    return app.test_cli_runner()

@pytest.fixture
def auth(client):
    """认证助手"""
    class AuthActions:
        def __init__(self, client):
            self._client = client
        
        def login(self, username='admin', password='password'):
            return self._client.post('/auth/login', data={
                'username': username,
                'password': password
            })
        
        def logout(self):
            return self._client.get('/auth/logout')
    
    return AuthActions(client)

@pytest.fixture
def user():
    """创建测试用户"""
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def admin_user():
    """创建管理员用户"""
    admin = User(username='admin', email='admin@example.com', is_admin=True)
    admin.set_password('password')
    db.session.add(admin)
    db.session.commit()
    return admin

@pytest.fixture
def post(user):
    """创建测试文章"""
    post = Post(
        title='Test Post',
        content='This is a test post content.',
        summary='Test summary',
        author=user,
        is_published=True
    )
    db.session.add(post)
    db.session.commit()
    return post
```

### 3. 单元测试示例

#### test_models.py
```python
import pytest
from app.models import User, Post, Comment
from app import db

class TestUser:
    def test_password_hashing(self, app):
        """测试密码加密"""
        with app.app_context():
            user = User(username='test', email='test@example.com')
            user.set_password('password')
            
            assert user.password_hash is not None
            assert user.password_hash != 'password'
            assert user.check_password('password') is True
            assert user.check_password('wrong') is False
    
    def test_user_repr(self, app):
        """测试用户字符串表示"""
        with app.app_context():
            user = User(username='test', email='test@example.com')
            assert repr(user) == '<User test>'

class TestPost:
    def test_post_creation(self, app, user):
        """测试文章创建"""
        with app.app_context():
            post = Post(
                title='Test Post',
                content='Test content',
                author=user
            )
            db.session.add(post)
            db.session.commit()
            
            assert post.id is not None
            assert post.title == 'Test Post'
            assert post.author == user
            assert post.is_published is True  # 默认值
    
    def test_post_to_dict(self, app, post):
        """测试文章序列化"""
        with app.app_context():
            data = post.to_dict()
            
            assert 'id' in data
            assert 'title' in data
            assert 'author' in data
            assert data['title'] == post.title
```

#### test_auth.py
```python
import pytest
from flask import url_for
from app.models import User
from app import db

class TestAuth:
    def test_register_get(self, client):
        """测试注册页面访问"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'注册' in response.data
    
    def test_register_post_success(self, client, app):
        """测试成功注册"""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password',
            'password2': 'password'
        })
        
        assert response.status_code == 302  # 重定向
        
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@example.com'
    
    def test_register_post_duplicate_username(self, client, user):
        """测试重复用户名注册"""
        response = client.post('/auth/register', data={
            'username': user.username,
            'email': 'different@example.com',
            'password': 'password',
            'password2': 'password'
        })
        
        assert response.status_code == 200
        assert b'用户名已存在' in response.data
    
    def test_login_success(self, client, user):
        """测试成功登录"""
        response = client.post('/auth/login', data={
            'username': user.username,
            'password': 'password'
        })
        
        assert response.status_code == 302
    
    def test_login_invalid_credentials(self, client, user):
        """测试无效凭据登录"""
        response = client.post('/auth/login', data={
            'username': user.username,
            'password': 'wrong'
        })
        
        assert response.status_code == 200
        assert b'用户名或密码错误' in response.data
    
    def test_logout(self, client, auth):
        """测试登出"""
        auth.login()
        response = auth.logout()
        assert response.status_code == 302
```

### 4. 集成测试示例

#### test_main.py
```python
import pytest
from flask import url_for
from app.models import Post, Category
from app import db

class TestMainViews:
    def test_index_page(self, client, post):
        """测试首页"""
        response = client.get('/')
        assert response.status_code == 200
        assert post.title.encode() in response.data
    
    def test_post_detail(self, client, post):
        """测试文章详情页"""
        response = client.get(f'/post/{post.id}')
        assert response.status_code == 200
        assert post.title.encode() in response.data
        assert post.content.encode() in response.data
    
    def test_search_functionality(self, client, post):
        """测试搜索功能"""
        response = client.get('/search?q=Test')
        assert response.status_code == 200
        assert post.title.encode() in response.data
    
    def test_create_post_requires_login(self, client):
        """测试创建文章需要登录"""
        response = client.get('/create')
        assert response.status_code == 302  # 重定向到登录页
    
    def test_create_post_success(self, client, auth, user):
        """测试成功创建文章"""
        auth.login()
        
        response = client.post('/create', data={
            'title': 'New Post',
            'content': 'This is a new post content.',
            'summary': 'New post summary',
            'is_published': True
        })
        
        assert response.status_code == 302
        
        # 验证文章已创建
        post = Post.query.filter_by(title='New Post').first()
        assert post is not None
        assert post.author == user
```

### 5. API 测试示例

#### test_api.py
```python
import pytest
import json
from app.models import Post

class TestAPI:
    def test_search_suggestions_api(self, client, post):
        """测试搜索建议 API"""
        response = client.get('/api/search/suggestions?q=Test')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'suggestions' in data
        assert isinstance(data['suggestions'], list)
    
    def test_popular_posts_api(self, client, post):
        """测试热门文章 API"""
        response = client.get('/api/search/popular')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'popular_searches' in data
    
    def test_posts_api_pagination(self, client, post):
        """测试文章 API 分页"""
        response = client.get('/api/posts?page=1&per_page=10')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'posts' in data
        assert 'pagination' in data
        assert 'has_more' in data
```

### 6. 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_auth.py

# 运行特定测试类
pytest tests/test_models.py::TestUser

# 运行特定测试方法
pytest tests/test_auth.py::TestAuth::test_login_success

# 显示详细输出
pytest -v

# 生成覆盖率报告
pytest --cov=app --cov-report=html

# 并行运行测试
pytest -n auto
```

## 🐛 调试技巧

### 1. Flask 调试模式

```python
# config.py
class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = 'development'

# 启用调试工具栏
from flask_debugtoolbar import DebugToolbarExtension

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    if app.debug:
        toolbar = DebugToolbarExtension(app)
    
    return app
```

### 2. 日志配置

```python
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    if not app.debug and not app.testing:
        # 文件日志
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/blog.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Blog startup')

# 在代码中使用日志
from flask import current_app

def some_function():
    try:
        # 一些操作
        current_app.logger.info('操作成功')
    except Exception as e:
        current_app.logger.error(f'操作失败: {str(e)}')
        raise
```

### 3. 数据库调试

```python
# 启用 SQL 查询日志
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# 在视图中调试查询
from flask_sqlalchemy import get_debug_queries

@main.after_app_request
def after_request(response):
    if current_app.debug:
        for query in get_debug_queries():
            if query.duration >= 0.01:  # 慢查询阈值
                current_app.logger.warning(
                    f'Slow query: {query.statement}\n'
                    f'Parameters: {query.parameters}\n'
                    f'Duration: {query.duration}s\n'
                    f'Context: {query.context}'
                )
    return response
```

### 4. 性能分析

```python
# 使用 Flask-Profiler
from flask_profiler import Profiler

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    if app.debug:
        app.config['flask_profiler'] = {
            "enabled": True,
            "storage": {
                "engine": "sqlite"
            },
            "basicAuth": {
                "enabled": True,
                "username": "admin",
                "password": "admin"
            },
            "ignore": [
                "^/static/.*"
            ]
        }
        
        Profiler(app)
    
    return app
```

## 🚀 部署流程

### 1. 预部署检查

```bash
# 代码质量检查
flake8 app/
pylint app/

# 安全检查
bandit -r app/

# 测试
pytest --cov=app

# 依赖检查
pip check
safety check
```

### 2. 构建脚本

创建 `scripts/build.sh`：
```bash
#!/bin/bash

set -e

echo "开始构建..."

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
flask db upgrade

# 收集静态文件
flask assets build

# 创建必要目录
mkdir -p app/static/uploads
mkdir -p logs

echo "构建完成!"
```

### 3. 部署脚本

创建 `scripts/deploy.sh`：
```bash
#!/bin/bash

set -e

echo "开始部署..."

# 备份数据库
python scripts/backup_db.py

# 停止服务
sudo systemctl stop blog

# 更新代码
git pull origin main

# 运行构建脚本
./scripts/build.sh

# 重启服务
sudo systemctl start blog
sudo systemctl reload nginx

echo "部署完成!"
```

### 4. 监控和健康检查

```python
# app/health.py
from flask import Blueprint, jsonify
from app import db
from app.models import User

health = Blueprint('health', __name__)

@health.route('/health')
def health_check():
    """健康检查端点"""
    try:
        # 检查数据库连接
        db.session.execute('SELECT 1')
        
        # 检查基本功能
        user_count = User.query.count()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'users': user_count
        })
    
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@health.route('/metrics')
def metrics():
    """应用指标"""
    from app.models import Post, Comment
    
    return jsonify({
        'posts': Post.query.count(),
        'published_posts': Post.query.filter_by(is_published=True).count(),
        'comments': Comment.query.count(),
        'approved_comments': Comment.query.filter_by(approved=True).count(),
        'users': User.query.count()
    })
```

## ❓ 常见问题

### 1. 数据库问题

**问题**: 数据库迁移失败
```bash
# 解决方案
# 1. 检查数据库连接
flask db current

# 2. 重置迁移
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 3. 手动修复迁移文件
# 编辑 migrations/versions/*.py 文件
```

**问题**: 外键约束错误
```python
# 解决方案：在删除时处理关联数据
@main.route('/post/<int:id>/delete', methods=['POST'])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    
    # 先删除关联的评论
    Comment.query.filter_by(post_id=id).delete()
    
    # 再删除文章
    db.session.delete(post)
    db.session.commit()
    
    return redirect(url_for('main.index'))
```

### 2. 性能问题

**问题**: 页面加载缓慢
```python
# 解决方案：使用查询优化
# 1. 添加数据库索引
# 2. 使用 joinedload 预加载关联数据
posts = Post.query.options(
    db.joinedload(Post.author),
    db.joinedload(Post.category)
).filter_by(is_published=True).all()

# 3. 实现分页
posts = Post.query.paginate(
    page=page, per_page=10, error_out=False
)
```

**问题**: 内存使用过高
```python
# 解决方案：使用生成器和批处理
def process_posts_batch():
    batch_size = 100
    offset = 0
    
    while True:
        posts = Post.query.offset(offset).limit(batch_size).all()
        if not posts:
            break
        
        for post in posts:
            # 处理文章
            yield post
        
        offset += batch_size
```

### 3. 安全问题

**问题**: XSS 攻击
```python
# 解决方案：使用模板自动转义和内容过滤
import bleach

def safe_content(content):
    allowed_tags = ['p', 'br', 'strong', 'em', 'a']
    allowed_attributes = {'a': ['href']}
    
    return bleach.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attributes
    )
```

**问题**: SQL 注入
```python
# 解决方案：使用参数化查询
# 错误的方式
query = f"SELECT * FROM post WHERE title = '{title}'"

# 正确的方式
posts = Post.query.filter(Post.title == title).all()
# 或者使用原生 SQL 时
result = db.session.execute(
    text("SELECT * FROM post WHERE title = :title"),
    {'title': title}
)
```

### 4. 部署问题

**问题**: 静态文件 404
```nginx
# Nginx 配置
location /static {
    alias /path/to/app/static;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

**问题**: 数据库连接超时
```python
# config.py
class ProductionConfig(Config):
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0
    }
```

---

## 📞 技术支持

如果在开发过程中遇到问题，可以通过以下方式获取帮助：

1. **查看文档**: 首先查看项目文档和 README
2. **搜索问题**: 在 GitHub Issues 中搜索类似问题
3. **创建 Issue**: 如果问题未解决，创建新的 Issue
4. **社区讨论**: 参与项目讨论区的交流

**联系方式**:
- GitHub: [项目地址](https://github.com/your-username/Trace_vlog)
- Email: your-email@example.com

---

*最后更新: 2024年12月*