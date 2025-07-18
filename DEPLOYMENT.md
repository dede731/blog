# Trace_vlog 部署文档

## 📋 部署前准备

### 系统要求
- **操作系统**: Linux (推荐 Ubuntu 20.04+) / Windows Server / macOS
- **Python**: 3.8+ (推荐 3.9+)
- **数据库**: MySQL 5.7+ / MariaDB 10.3+
- **内存**: 最低 1GB，推荐 2GB+
- **存储**: 最低 5GB 可用空间

### 依赖软件
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv mysql-server nginx

# CentOS/RHEL
sudo yum install python3 python3-pip mysql-server nginx

# Windows
# 下载并安装 Python 3.9+, MySQL 8.0+
```

## 🚀 部署步骤

### 1. 获取源码
```bash
git clone https://github.com/your-username/trace_vlog.git
cd trace_vlog
```

### 2. 创建虚拟环境
```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 数据库配置

#### 4.1 创建数据库
```sql
-- 登录 MySQL
mysql -u root -p

-- 创建数据库
CREATE DATABASE trace_vlog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（可选）
CREATE USER 'trace_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON trace_vlog.* TO 'trace_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 4.2 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
nano .env
```

`.env` 文件配置示例：
```env
# 数据库配置
MYSQL_USER=trace_user
MYSQL_PASSWORD=your_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=trace_vlog

# 应用配置
SECRET_KEY=your-very-secret-key-here
FLASK_ENV=production

# 邮件配置（可选）
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 5. 初始化数据库
```bash
# 初始化数据库迁移
python manage.py db init

# 执行数据库迁移
python manage.py db migrate -m "Initial migration"
python manage.py db upgrade

# 初始化公告数据（可选）
python init_announcements.py
```

### 6. 创建管理员账户
```bash
python manage.py shell
```

在 Python shell 中执行：
```python
from app.models import User
from app import db

# 创建管理员用户
admin = User(
    username='admin',
    email='admin@example.com',
    is_admin=True
)
admin.set_password('your_admin_password')
db.session.add(admin)
db.session.commit()
exit()
```

## 🌐 生产环境部署

### 方式一：使用 Gunicorn + Nginx

#### 1. 安装 Gunicorn
```bash
pip install gunicorn
```

#### 2. 创建 Gunicorn 配置文件
```bash
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

#### 3. 创建 systemd 服务文件
```bash
sudo nano /etc/systemd/system/trace_vlog.service
```

```ini
[Unit]
Description=Trace_vlog Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/trace_vlog
Environment="PATH=/path/to/trace_vlog/venv/bin"
ExecStart=/path/to/trace_vlog/venv/bin/gunicorn -c gunicorn.conf.py manage:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 4. 启动服务
```bash
sudo systemctl daemon-reload
sudo systemctl enable trace_vlog
sudo systemctl start trace_vlog
sudo systemctl status trace_vlog
```

#### 5. 配置 Nginx
```bash
sudo nano /etc/nginx/sites-available/trace_vlog
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/trace_vlog/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    client_max_body_size 16M;
}
```

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/trace_vlog /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 方式二：使用 Docker

#### 1. 创建 Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-c", "gunicorn.conf.py", "manage:app"]
```

#### 2. 创建 docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - MYSQL_HOST=db
      - MYSQL_USER=trace_user
      - MYSQL_PASSWORD=your_password
      - MYSQL_DATABASE=trace_vlog
    depends_on:
      - db
    volumes:
      - ./app/static/uploads:/app/app/static/uploads

  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=root_password
      - MYSQL_DATABASE=trace_vlog
      - MYSQL_USER=trace_user
      - MYSQL_PASSWORD=your_password
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

volumes:
  mysql_data:
```

#### 3. 启动容器
```bash
docker-compose up -d
```

## 🔒 SSL/HTTPS 配置

### 使用 Let's Encrypt
```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取 SSL 证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 性能优化

### 1. 数据库优化
```sql
-- 添加索引
CREATE INDEX idx_posts_published ON posts(is_published, created_at);
CREATE INDEX idx_comments_approved ON comments(approved, created_at);
CREATE INDEX idx_posts_category ON posts(category_id);
```

### 2. 缓存配置
```python
# 在 config.py 中启用 Redis 缓存
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://localhost:6379/0'
```

### 3. 静态文件优化
```bash
# 压缩静态文件
sudo apt install gzip
# 在 Nginx 中启用 gzip 压缩
```

## 🔧 维护和监控

### 日志管理
```bash
# 查看应用日志
sudo journalctl -u trace_vlog -f

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 备份策略
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u trace_user -p trace_vlog > backup_$DATE.sql
tar -czf uploads_backup_$DATE.tar.gz app/static/uploads/
```

### 更新部署
```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt

# 执行数据库迁移
python manage.py db upgrade

# 重启服务
sudo systemctl restart trace_vlog
```

## 🚨 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务状态
   - 验证连接参数
   - 检查防火墙设置

2. **静态文件无法访问**
   - 检查文件权限
   - 验证 Nginx 配置
   - 确认文件路径

3. **内存不足**
   - 减少 Gunicorn worker 数量
   - 启用 swap 分区
   - 优化数据库查询

4. **上传文件失败**
   - 检查上传目录权限
   - 验证文件大小限制
   - 确认磁盘空间

### 性能监控
```bash
# 安装监控工具
pip install flask-monitoring-dashboard

# 在应用中启用
from flask_monitoringdashboard import dashboard
dashboard.bind(app)
```

## 🔧 高级配置

### 环境变量详细说明

```env
# 数据库配置
MYSQL_USER=trace_user                    # 数据库用户名
MYSQL_PASSWORD=your_secure_password      # 数据库密码
MYSQL_HOST=localhost                     # 数据库主机
MYSQL_PORT=3306                         # 数据库端口
MYSQL_DATABASE=trace_vlog               # 数据库名称

# 应用配置
SECRET_KEY=your-very-long-secret-key-here-at-least-32-chars  # 应用密钥
FLASK_ENV=production                     # 运行环境 (development/production)
DEBUG=False                             # 调试模式
WTF_CSRF_ENABLED=True                   # CSRF 保护

# 文件上传配置
UPLOAD_FOLDER=app/static/uploads        # 上传文件目录
MAX_CONTENT_LENGTH=16777216             # 最大上传文件大小 (16MB)
ALLOWED_EXTENSIONS=png,jpg,jpeg,gif,webp # 允许的文件扩展名

# 邮件配置
MAIL_SERVER=smtp.gmail.com              # SMTP 服务器
MAIL_PORT=587                           # SMTP 端口
MAIL_USE_TLS=True                       # 启用 TLS
MAIL_USE_SSL=False                      # 启用 SSL
MAIL_USERNAME=your-email@gmail.com      # 邮箱用户名
MAIL_PASSWORD=your-app-password         # 邮箱密码或应用密码
MAIL_DEFAULT_SENDER=your-email@gmail.com # 默认发件人

# 缓存配置
CACHE_TYPE=simple                       # 缓存类型 (simple/redis/memcached)
CACHE_DEFAULT_TIMEOUT=300               # 默认缓存时间 (秒)
CACHE_REDIS_URL=redis://localhost:6379/0 # Redis URL (如果使用 Redis)

# 安全配置
SESSION_COOKIE_SECURE=True              # 仅 HTTPS 传输 Cookie
SESSION_COOKIE_HTTPONLY=True            # 防止 XSS 攻击
PERMANENT_SESSION_LIFETIME=3600         # 会话过期时间 (秒)

# 分页配置
POSTS_PER_PAGE=10                       # 每页文章数
COMMENTS_PER_PAGE=20                    # 每页评论数

# SEO 配置
SITE_NAME=Trace_vlog                    # 网站名称
SITE_DESCRIPTION=个人技术博客            # 网站描述
SITE_KEYWORDS=技术,博客,编程,开发        # 网站关键词
SITE_AUTHOR=Your Name                   # 网站作者
```

### Nginx 完整配置

```nginx
# /etc/nginx/sites-available/trace_vlog
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL 证书配置
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # 日志配置
    access_log /var/log/nginx/trace_vlog_access.log;
    error_log /var/log/nginx/trace_vlog_error.log;
    
    # 客户端配置
    client_max_body_size 16M;
    client_body_timeout 60s;
    client_header_timeout 60s;
    
    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # 静态文件缓存
    location /static {
        alias /path/to/trace_vlog/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
        
        # 字体文件 CORS
        location ~* \.(woff|woff2|ttf|eot)$ {
            add_header Access-Control-Allow-Origin *;
        }
    }
    
    # 上传文件缓存
    location /static/uploads {
        alias /path/to/trace_vlog/app/static/uploads;
        expires 30d;
        add_header Cache-Control "public";
    }
    
    # robots.txt
    location /robots.txt {
        alias /path/to/trace_vlog/app/static/robots.txt;
        expires 1d;
    }
    
    # 主应用代理
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓冲配置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### 系统服务配置优化

```ini
# /etc/systemd/system/trace_vlog.service
[Unit]
Description=Trace_vlog Flask Application
After=network.target mysql.service
Wants=mysql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/trace_vlog
Environment="PATH=/path/to/trace_vlog/venv/bin"
Environment="FLASK_ENV=production"
ExecStart=/path/to/trace_vlog/venv/bin/gunicorn -c gunicorn.conf.py manage:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

# 安全配置
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/path/to/trace_vlog/app/static/uploads
ReadWritePaths=/tmp

# 资源限制
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
```

### Gunicorn 生产配置

```python
# gunicorn.conf.py
import multiprocessing
import os

# 服务器配置
bind = "127.0.0.1:8000"
backlog = 2048

# Worker 配置
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2

# 应用配置
preload_app = True
reload = False

# 日志配置
accesslog = "/var/log/trace_vlog/access.log"
errorlog = "/var/log/trace_vlog/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程配置
pidfile = "/var/run/trace_vlog/gunicorn.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# 安全配置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# SSL 配置 (如果直接使用 HTTPS)
# keyfile = "/path/to/private.key"
# certfile = "/path/to/certificate.crt"

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker aborted (pid: %s)", worker.pid)
```

### 数据库优化配置

```sql
-- MySQL 配置优化 (/etc/mysql/mysql.conf.d/mysqld.cnf)
[mysqld]
# 基本配置
default-storage-engine = InnoDB
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# 连接配置
max_connections = 200
max_connect_errors = 10000
wait_timeout = 28800
interactive_timeout = 28800

# 缓冲池配置
innodb_buffer_pool_size = 1G
innodb_buffer_pool_instances = 4
innodb_log_file_size = 256M
innodb_log_buffer_size = 16M

# 查询缓存
query_cache_type = 1
query_cache_size = 128M
query_cache_limit = 2M

# 慢查询日志
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2

# 二进制日志
log_bin = /var/log/mysql/mysql-bin.log
binlog_format = ROW
expire_logs_days = 7

# 性能优化
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT
innodb_file_per_table = 1
```

### Redis 缓存配置

```bash
# 安装 Redis
sudo apt install redis-server

# 配置 Redis (/etc/redis/redis.conf)
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

```python
# Flask 应用中启用 Redis 缓存
from flask_caching import Cache

cache = Cache()

# 在 config.py 中
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://localhost:6379/0'
CACHE_DEFAULT_TIMEOUT = 300
```

## 🔍 监控和日志管理

### 日志轮转配置

```bash
# /etc/logrotate.d/trace_vlog
/var/log/trace_vlog/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload trace_vlog
    endscript
}

/var/log/nginx/trace_vlog_*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data adm
    postrotate
        systemctl reload nginx
    endscript
}
```

### 系统监控脚本

```bash
#!/bin/bash
# /usr/local/bin/trace_vlog_monitor.sh

# 检查应用状态
check_app() {
    if ! systemctl is-active --quiet trace_vlog; then
        echo "$(date): Trace_vlog service is down, restarting..." >> /var/log/trace_vlog/monitor.log
        systemctl restart trace_vlog
    fi
}

# 检查数据库连接
check_database() {
    if ! mysqladmin ping -h localhost --silent; then
        echo "$(date): MySQL is not responding" >> /var/log/trace_vlog/monitor.log
        # 发送告警邮件
        echo "MySQL is down on $(hostname)" | mail -s "Database Alert" admin@example.com
    fi
}

# 检查磁盘空间
check_disk_space() {
    USAGE=$(df /var/log | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $USAGE -gt 80 ]; then
        echo "$(date): Disk usage is ${USAGE}%" >> /var/log/trace_vlog/monitor.log
        # 清理旧日志
        find /var/log/trace_vlog -name "*.log.*" -mtime +30 -delete
    fi
}

# 检查内存使用
check_memory() {
    MEMORY_USAGE=$(free | awk 'NR==2{printf "%.2f", $3*100/$2}')
    if (( $(echo "$MEMORY_USAGE > 90" | bc -l) )); then
        echo "$(date): High memory usage: ${MEMORY_USAGE}%" >> /var/log/trace_vlog/monitor.log
    fi
}

# 执行检查
check_app
check_database
check_disk_space
check_memory
```

```bash
# 添加到 crontab
# crontab -e
*/5 * * * * /usr/local/bin/trace_vlog_monitor.sh
```

### 性能监控

```python
# 在应用中添加性能监控
import time
import psutil
from flask import g, request

@app.before_request
def before_request():
    g.start_time = time.time()
    g.start_cpu = psutil.cpu_percent()
    g.start_memory = psutil.virtual_memory().percent

@app.after_request
def after_request(response):
    duration = time.time() - g.start_time
    cpu_usage = psutil.cpu_percent() - g.start_cpu
    memory_usage = psutil.virtual_memory().percent - g.start_memory
    
    # 记录慢请求
    if duration > 1.0:
        app.logger.warning(
            f'Slow request: {request.method} {request.path} '
            f'took {duration:.2f}s, CPU: {cpu_usage:.1f}%, Memory: {memory_usage:.1f}%'
        )
    
    # 添加性能头
    response.headers['X-Response-Time'] = f'{duration:.3f}s'
    return response
```

## 🔐 安全加固

### 防火墙配置

```bash
# UFW 防火墙配置
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 允许必要端口
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 限制 SSH 连接
sudo ufw limit ssh

# 查看状态
sudo ufw status verbose
```

### Fail2ban 配置

```bash
# 安装 Fail2ban
sudo apt install fail2ban

# 配置 (/etc/fail2ban/jail.local)
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
ignoreip = 127.0.0.1/8 ::1

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
```

### SSL 安全配置

```bash
# 生成强 DH 参数
sudo openssl dhparam -out /etc/nginx/dhparam.pem 2048

# 在 Nginx 配置中添加
ssl_dhparam /etc/nginx/dhparam.pem;
```

## 📊 备份和恢复

### 自动备份脚本

```bash
#!/bin/bash
# /usr/local/bin/backup_trace_vlog.sh

BACKUP_DIR="/backup/trace_vlog"
DATE=$(date +%Y%m%d_%H%M%S)
MYSQL_USER="backup_user"
MYSQL_PASSWORD="backup_password"
MYSQL_DATABASE="trace_vlog"

# 创建备份目录
mkdir -p $BACKUP_DIR/$DATE

# 数据库备份
mysqldump -u $MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE > $BACKUP_DIR/$DATE/database.sql

# 上传文件备份
tar -czf $BACKUP_DIR/$DATE/uploads.tar.gz -C /path/to/trace_vlog/app/static uploads/

# 配置文件备份
cp /path/to/trace_vlog/.env $BACKUP_DIR/$DATE/
cp /etc/nginx/sites-available/trace_vlog $BACKUP_DIR/$DATE/nginx.conf

# 删除 30 天前的备份
find $BACKUP_DIR -type d -mtime +30 -exec rm -rf {} +

# 备份到远程服务器 (可选)
# rsync -az $BACKUP_DIR/$DATE/ user@backup-server:/backup/trace_vlog/

echo "Backup completed: $BACKUP_DIR/$DATE"
```

### 恢复脚本

```bash
#!/bin/bash
# /usr/local/bin/restore_trace_vlog.sh

if [ $# -ne 1 ]; then
    echo "Usage: $0 <backup_date>"
    echo "Example: $0 20241201_120000"
    exit 1
fi

BACKUP_DATE=$1
BACKUP_DIR="/backup/trace_vlog/$BACKUP_DATE"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "Backup directory not found: $BACKUP_DIR"
    exit 1
fi

echo "Restoring from backup: $BACKUP_DATE"

# 停止服务
systemctl stop trace_vlog

# 恢复数据库
mysql -u root -p trace_vlog < $BACKUP_DIR/database.sql

# 恢复上传文件
tar -xzf $BACKUP_DIR/uploads.tar.gz -C /path/to/trace_vlog/app/static/

# 恢复配置文件
cp $BACKUP_DIR/.env /path/to/trace_vlog/
cp $BACKUP_DIR/nginx.conf /etc/nginx/sites-available/trace_vlog

# 重新加载配置
nginx -t && systemctl reload nginx

# 启动服务
systemctl start trace_vlog

echo "Restore completed"
```

## 📞 技术支持

### 故障排除检查清单

#### 应用无法启动
1. **检查日志**: `journalctl -u trace_vlog -f`
2. **检查配置**: 验证 `.env` 文件配置
3. **检查权限**: 确认文件和目录权限
4. **检查依赖**: `pip check` 验证依赖完整性
5. **检查端口**: `netstat -tlnp | grep 8000`

#### 数据库连接问题
1. **检查服务**: `systemctl status mysql`
2. **测试连接**: `mysql -u trace_user -p -h localhost trace_vlog`
3. **检查防火墙**: `ufw status`
4. **查看错误日志**: `/var/log/mysql/error.log`

#### 静态文件无法访问
1. **检查 Nginx 配置**: `nginx -t`
2. **检查文件权限**: `ls -la /path/to/static/files`
3. **查看 Nginx 日志**: `/var/log/nginx/error.log`
4. **检查磁盘空间**: `df -h`

#### 性能问题
1. **检查系统资源**: `htop`, `iotop`
2. **分析慢查询**: MySQL slow query log
3. **检查应用日志**: 查找慢请求记录
4. **监控网络**: `iftop`, `nethogs`

### 常用命令

```bash
# 服务管理
systemctl status trace_vlog
systemctl restart trace_vlog
systemctl reload trace_vlog

# 日志查看
journalctl -u trace_vlog -f
tail -f /var/log/trace_vlog/error.log
tail -f /var/log/nginx/trace_vlog_error.log

# 数据库操作
mysql -u trace_user -p trace_vlog
mysqldump -u trace_user -p trace_vlog > backup.sql

# 文件权限修复
chown -R www-data:www-data /path/to/trace_vlog
chmod -R 755 /path/to/trace_vlog
chmod -R 775 /path/to/trace_vlog/app/static/uploads

# 清理缓存
rm -rf /path/to/trace_vlog/app/__pycache__/*
systemctl restart trace_vlog

# 更新应用
cd /path/to/trace_vlog
git pull origin main
pip install -r requirements.txt
python manage.py db upgrade
systemctl restart trace_vlog
```

### 联系支持

如遇到部署问题，请：
1. **查看日志文件** - 收集错误信息
2. **检查配置文件** - 验证所有配置正确
3. **参考故障排除章节** - 按步骤排查问题
4. **提交 Issue** - 到项目仓库报告问题
5. **联系维护者** - 发送邮件或私信

**问题报告模板**:
```
环境信息:
- 操作系统: 
- Python 版本: 
- 数据库版本: 
- 部署方式: 

问题描述:
- 具体现象: 
- 错误信息: 
- 复现步骤: 

已尝试的解决方案:
- 

相关日志:
- 
```

---

**注意**: 生产环境部署前请务必：
- ✅ 更改所有默认密码
- ✅ 配置防火墙规则
- ✅ 启用 HTTPS 加密
- ✅ 设置定期备份
- ✅ 配置监控告警
- ✅ 进行安全加固
- ✅ 测试恢复流程