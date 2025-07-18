# Trace_vlog - 个人博客系统

一个基于 Flask 的现代化个人博客系统，具有完整的文章管理、用户认证、评论系统、全文搜索和管理后台功能。

## ✨ 主要特性

- 📝 **文章管理**: 支持 Markdown 编辑、分类管理、标签系统、草稿保存
- 👥 **用户系统**: 用户注册、登录、个人资料管理、邮箱验证
- 💬 **评论系统**: 支持嵌套评论、评论审核、点赞功能、邮件通知
- 🛡️ **敏感词过滤**: 智能内容审核，支持自定义敏感词库、正则表达式、白名单
- 🔍 **全文搜索**: 强大的搜索功能，支持多关键词、分类、标签、排序，智能搜索建议
- 📱 **响应式设计**: 完美适配桌面和移动设备
- 🎨 **现代化UI**: 基于 Bootstrap 5 的美观界面，支持暗色模式
- ⚡ **高性能**: Redis 缓存、数据库优化、静态文件压缩
- 🔒 **安全防护**: XSS防护、CSRF保护、SQL注入防护、文件上传安全
- 📊 **数据统计**: 访问统计、热门内容分析、搜索统计
- 🛠️ **管理后台**: 完整的后台管理系统，支持用户管理、内容审核、系统监控
- 🌐 **API 支持**: RESTful API，支持第三方集成

## 🚀 快速开始

### 环境要求

- Python 3.8+
- SQLite/MySQL/PostgreSQL
- Redis (可选，用于缓存)
- Node.js 16+ (可选，用于前端资源构建)

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/Trace_vlog.git
cd Trace_vlog
```

2. **创建虚拟环境**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库和其他设置
```

5. **初始化数据库**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. **创建管理员账户**
```bash
python create_admin.py
```

7. **运行应用**
```bash
flask run
```

访问 http://localhost:5000 即可使用博客系统。

## 📖 文档

- 📋 **[开发指南](DEVELOPMENT_GUIDE.md)** - 开发环境搭建、代码规范、测试指南
- 🚀 **[部署指南](DEPLOYMENT.md)** - 详细的部署说明和生产环境配置
- 📚 **[项目文档](PROJECT_DOCS.md)** - 技术架构、功能模块和设计说明
- 🔍 **[搜索功能](SEARCH_FEATURES.md)** - 全文搜索功能详解和使用指南
- 🌐 **[API 文档](API_DOCS.md)** - RESTful API 接口说明和示例代码

## 🛠️ 技术栈

### 后端技术
- **Web 框架**: Flask 2.3+
- **数据库 ORM**: SQLAlchemy
- **认证系统**: Flask-Login
- **表单处理**: Flask-WTF
- **数据库迁移**: Flask-Migrate
- **邮件发送**: Flask-Mail
- **缓存系统**: Redis
- **任务队列**: Celery (可选)

### 前端技术
- **UI 框架**: Bootstrap 5
- **JavaScript 库**: jQuery 3.6+
- **图标库**: Font Awesome 6
- **代码高亮**: Highlight.js
- **Markdown 编辑器**: SimpleMDE
- **图表库**: Chart.js

### 数据库支持
- **开发环境**: SQLite
- **生产环境**: MySQL 8.0+ / PostgreSQL 12+

### 部署技术
- **Web 服务器**: Nginx
- **WSGI 服务器**: Gunicorn
- **容器化**: Docker + Docker Compose
- **进程管理**: Systemd
- **SSL 证书**: Let's Encrypt

## 📁 项目结构

```
Trace_vlog/
├── app/                    # 应用主目录
│   ├── __init__.py        # 应用工厂
│   ├── models.py          # 数据模型
│   ├── auth/              # 认证模块
│   │   ├── routes.py      # 认证路由
│   │   └── forms.py       # 认证表单
│   ├── main/              # 主要功能模块
│   │   ├── routes.py      # 主要路由
│   │   └── forms.py       # 主要表单
│   ├── admin/             # 管理后台模块
│   │   ├── routes.py      # 管理路由
│   │   └── forms.py       # 管理表单
│   ├── api/               # API 模块
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
│       ├── sensitive_word_filter.py  # 敏感词过滤
│       ├── email.py       # 邮件发送
│       └── helpers.py     # 辅助函数
├── migrations/            # 数据库迁移文件
├── tests/                 # 测试文件
│   ├── test_auth.py       # 认证测试
│   ├── test_main.py       # 主要功能测试
│   ├── test_models.py     # 模型测试
│   └── test_api.py        # API 测试
├── scripts/               # 脚本文件
│   ├── backup_db.py       # 数据库备份
│   ├── deploy.sh          # 部署脚本
│   └── monitor.py         # 监控脚本
├── config.py              # 配置文件
├── run.py                 # 应用入口
├── requirements.txt       # 生产依赖
├── requirements-dev.txt   # 开发依赖
├── Dockerfile             # Docker 配置
├── docker-compose.yml     # Docker Compose 配置
├── .env.example          # 环境变量示例
├── .gitignore            # Git 忽略文件
└── README.md             # 项目说明
```

## 🔧 配置说明

主要配置项在 `config.py` 中：

```python
class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///blog.db'
    
    # 邮件配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Redis 配置
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # 文件上传配置
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'app/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 分页配置
    POSTS_PER_PAGE = 10
    COMMENTS_PER_PAGE = 20
    SEARCH_RESULTS_PER_PAGE = 10
```

## 🚀 部署

### 使用 Docker (推荐)

```bash
# 克隆项目
git clone https://github.com/your-username/Trace_vlog.git
cd Trace_vlog

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 使用 Docker Compose 部署
docker-compose up -d
```

### 传统部署

```bash
# 安装系统依赖
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx redis-server

# 部署应用
git clone https://github.com/your-username/Trace_vlog.git
cd Trace_vlog
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 配置数据库
flask db upgrade

# 配置 Nginx 和 Systemd
sudo cp configs/nginx.conf /etc/nginx/sites-available/trace-vlog
sudo cp configs/trace-vlog.service /etc/systemd/system/

# 启动服务
sudo systemctl enable trace-vlog
sudo systemctl start trace-vlog
sudo systemctl reload nginx
```

详细部署说明请参考 **[部署指南](DEPLOYMENT.md)**。

## 🧪 测试

```bash
# 安装测试依赖
pip install -r requirements-dev.txt

# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_auth.py

# 生成覆盖率报告
pytest --cov=app --cov-report=html

# 运行性能测试
pytest tests/test_performance.py

# 运行安全测试
bandit -r app/
```

## 🔍 功能特色

### 全文搜索系统
- **多关键词搜索**: 支持空格分隔的多个关键词
- **智能排序**: 基于相关性、时间、热度的排序算法
- **搜索建议**: 实时搜索建议和自动完成
- **搜索统计**: 热门搜索词和搜索趋势分析
- **高级搜索**: 支持分类、标签、作者等条件筛选

### 内容管理系统
- **Markdown 编辑器**: 支持实时预览和语法高亮
- **草稿系统**: 自动保存草稿，支持定时发布
- **标签系统**: 灵活的标签管理和标签云展示
- **分类管理**: 层级分类结构，支持分类统计
- **SEO 优化**: 自定义 meta 标签和 URL 结构

### 用户交互系统
- **评论系统**: 支持嵌套回复、表情符号、@提及
- **点赞系统**: 文章和评论点赞，用户互动统计
- **关注系统**: 用户关注和粉丝功能
- **通知系统**: 邮件通知和站内消息
- **个人中心**: 完整的用户资料和活动记录

## 🛡️ 安全特性

- **输入验证**: 严格的表单验证和数据清理
- **XSS 防护**: 自动 HTML 转义和内容过滤
- **CSRF 保护**: 表单令牌验证
- **SQL 注入防护**: 参数化查询和 ORM 保护
- **文件上传安全**: 文件类型检查和路径验证
- **敏感词过滤**: 智能内容审核系统
- **访问控制**: 基于角色的权限管理
- **安全头部**: 完整的 HTTP 安全头部配置

## 📊 性能优化

- **数据库优化**: 索引优化和查询缓存
- **Redis 缓存**: 页面缓存和数据缓存
- **静态文件优化**: Gzip 压缩和 CDN 支持
- **图片优化**: 自动压缩和多尺寸生成
- **懒加载**: 图片和内容的懒加载
- **分页优化**: 高效的分页查询
- **异步处理**: 邮件发送和文件处理异步化

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. **Fork 项目** - 点击右上角的 Fork 按钮
2. **创建功能分支** - `git checkout -b feature/AmazingFeature`
3. **提交更改** - `git commit -m 'Add some AmazingFeature'`
4. **推送到分支** - `git push origin feature/AmazingFeature`
5. **创建 Pull Request** - 在 GitHub 上创建 PR

### 贡献指南

- 遵循项目的代码规范 (PEP 8)
- 添加适当的测试用例
- 更新相关文档
- 确保所有测试通过
- 提供清晰的提交信息

详细贡献指南请参考 **[开发指南](DEVELOPMENT_GUIDE.md)**。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢以下开源项目和贡献者：

- **[Flask](https://flask.palletsprojects.com/)** - 轻量级 Web 框架
- **[Bootstrap](https://getbootstrap.com/)** - 响应式 UI 框架
- **[Font Awesome](https://fontawesome.com/)** - 图标库
- **[Highlight.js](https://highlightjs.org/)** - 代码高亮
- **[SimpleMDE](https://simplemde.com/)** - Markdown 编辑器
- **[Chart.js](https://www.chartjs.org/)** - 图表库

特别感谢所有为项目贡献代码、报告问题和提供建议的开发者们！

## 📞 联系方式

- **作者**: Your Name
- **邮箱**: your.email@example.com
- **项目主页**: https://github.com/your-username/Trace_vlog
- **在线演示**: https://demo.trace-vlog.com
- **文档站点**: https://docs.trace-vlog.com

## 🌟 支持项目

如果这个项目对你有帮助，请考虑：

- ⭐ **给项目点个 Star**
- 🐛 **报告 Bug 或提出建议**
- 💡 **贡献代码或文档**
- 📢 **分享给其他开发者**

---

**让我们一起构建更好的博客系统！** 🚀