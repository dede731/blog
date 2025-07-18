# Trace_vlog API 文档

## 📋 目录

- [API 概述](#api-概述)
- [认证机制](#认证机制)
- [通用响应格式](#通用响应格式)
- [错误处理](#错误处理)
- [搜索 API](#搜索-api)
- [文章 API](#文章-api)
- [用户 API](#用户-api)
- [评论 API](#评论-api)
- [管理 API](#管理-api)
- [文件上传 API](#文件上传-api)
- [统计 API](#统计-api)
- [限流和配额](#限流和配额)

## 🌐 API 概述

Trace_vlog 提供 RESTful API，支持 JSON 格式的数据交换。所有 API 端点都以 `/api` 为前缀。

**基础信息**:
- **Base URL**: `https://your-domain.com/api`
- **版本**: v1
- **数据格式**: JSON
- **字符编码**: UTF-8
- **时间格式**: ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)

## 🔐 认证机制

### 1. Session 认证 (Web)

用于 Web 界面的认证，基于 Flask-Login 会话管理。

```javascript
// 登录
fetch('/auth/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
    },
    body: JSON.stringify({
        username: 'your_username',
        password: 'your_password'
    })
});

// 后续请求会自动携带会话信息
fetch('/api/posts', {
    credentials: 'include'
});
```

### 2. API Token 认证 (可选扩展)

```http
Authorization: Bearer your-api-token
```

### 3. 权限级别

- **Public**: 无需认证
- **User**: 需要用户登录
- **Admin**: 需要管理员权限

## 📄 通用响应格式

### 成功响应

```json
{
    "success": true,
    "data": {
        // 响应数据
    },
    "message": "操作成功",
    "timestamp": "2024-12-19T10:30:00Z"
}
```

### 分页响应

```json
{
    "success": true,
    "data": {
        "items": [...],
        "pagination": {
            "page": 1,
            "per_page": 10,
            "total": 100,
            "pages": 10,
            "has_prev": false,
            "has_next": true,
            "prev_num": null,
            "next_num": 2
        }
    }
}
```

### 错误响应

```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "请求参数无效",
        "details": {
            "field": "title",
            "message": "标题不能为空"
        }
    },
    "timestamp": "2024-12-19T10:30:00Z"
}
```

## ❌ 错误处理

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 422 | 数据验证失败 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

### 错误代码

| 错误代码 | 说明 |
|----------|------|
| VALIDATION_ERROR | 数据验证失败 |
| AUTHENTICATION_REQUIRED | 需要认证 |
| PERMISSION_DENIED | 权限不足 |
| RESOURCE_NOT_FOUND | 资源不存在 |
| RESOURCE_CONFLICT | 资源冲突 |
| RATE_LIMIT_EXCEEDED | 超出限流 |
| INTERNAL_ERROR | 内部错误 |

## 🔍 搜索 API

### 搜索文章

```http
GET /api/search
```

**参数**:
- `q` (string): 搜索关键词
- `category_id` (integer, optional): 分类ID
- `tag` (string, optional): 标签名
- `sort` (string, optional): 排序方式 (`relevance`, `date`, `popularity`)
- `page` (integer, optional): 页码，默认1
- `per_page` (integer, optional): 每页数量，默认10

**示例请求**:
```javascript
fetch('/api/search?q=Python&category_id=1&sort=date&page=1&per_page=10')
```

**响应**:
```json
{
    "success": true,
    "data": {
        "posts": [
            {
                "id": 1,
                "title": "Python 入门教程",
                "summary": "这是一篇 Python 入门教程...",
                "content": "详细内容...",
                "author": {
                    "id": 1,
                    "username": "admin",
                    "avatar": "/static/uploads/avatars/admin.jpg"
                },
                "category": {
                    "id": 1,
                    "name": "编程"
                },
                "tags": ["Python", "教程"],
                "created_at": "2024-12-19T10:30:00Z",
                "updated_at": "2024-12-19T10:30:00Z",
                "views": 100,
                "likes": 10,
                "comments_count": 5,
                "is_published": true
            }
        ],
        "pagination": {
            "page": 1,
            "per_page": 10,
            "total": 25,
            "pages": 3,
            "has_prev": false,
            "has_next": true
        },
        "search_info": {
            "query": "Python",
            "category": "编程",
            "tag": null,
            "sort": "date",
            "total_results": 25,
            "search_time": 0.05
        }
    }
}
```

### 搜索建议

```http
GET /api/search/suggestions
```

**参数**:
- `q` (string): 搜索关键词前缀

**示例请求**:
```javascript
fetch('/api/search/suggestions?q=Pyt')
```

**响应**:
```json
{
    "success": true,
    "data": {
        "suggestions": [
            {
                "text": "Python",
                "type": "keyword",
                "count": 15
            },
            {
                "text": "Python 教程",
                "type": "title",
                "count": 8
            },
            {
                "text": "Python 爬虫",
                "type": "tag",
                "count": 5
            }
        ]
    }
}
```

### 热门搜索

```http
GET /api/search/popular
```

**响应**:
```json
{
    "success": true,
    "data": {
        "popular_searches": [
            {
                "keyword": "Python",
                "count": 150,
                "trend": "up"
            },
            {
                "keyword": "JavaScript",
                "count": 120,
                "trend": "stable"
            }
        ]
    }
}
```

### 热门标签

```http
GET /api/search/tags
```

**响应**:
```json
{
    "success": true,
    "data": {
        "popular_tags": [
            {
                "name": "Python",
                "count": 25,
                "color": "#3776ab"
            },
            {
                "name": "JavaScript",
                "count": 20,
                "color": "#f7df1e"
            }
        ]
    }
}
```

## 📝 文章 API

### 获取文章列表

```http
GET /api/posts
```

**参数**:
- `page` (integer, optional): 页码
- `per_page` (integer, optional): 每页数量
- `category_id` (integer, optional): 分类ID
- `author_id` (integer, optional): 作者ID
- `published` (boolean, optional): 是否已发布

**权限**: Public

### 获取文章详情

```http
GET /api/posts/{id}
```

**权限**: Public

**响应**:
```json
{
    "success": true,
    "data": {
        "post": {
            "id": 1,
            "title": "文章标题",
            "content": "文章内容...",
            "summary": "文章摘要",
            "author": {
                "id": 1,
                "username": "admin",
                "avatar": "/static/uploads/avatars/admin.jpg"
            },
            "category": {
                "id": 1,
                "name": "编程"
            },
            "tags": ["Python", "教程"],
            "created_at": "2024-12-19T10:30:00Z",
            "updated_at": "2024-12-19T10:30:00Z",
            "views": 100,
            "likes": 10,
            "is_published": true,
            "meta": {
                "reading_time": 5,
                "word_count": 1200
            }
        },
        "related_posts": [
            {
                "id": 2,
                "title": "相关文章",
                "summary": "相关文章摘要"
            }
        ]
    }
}
```

### 创建文章

```http
POST /api/posts
```

**权限**: User

**请求体**:
```json
{
    "title": "文章标题",
    "content": "文章内容",
    "summary": "文章摘要",
    "category_id": 1,
    "tags": ["Python", "教程"],
    "is_published": true,
    "meta_description": "SEO 描述",
    "meta_keywords": "关键词1,关键词2"
}
```

### 更新文章

```http
PUT /api/posts/{id}
```

**权限**: User (作者) / Admin

### 删除文章

```http
DELETE /api/posts/{id}
```

**权限**: User (作者) / Admin

### 文章点赞

```http
POST /api/posts/{id}/like
```

**权限**: User

### 取消点赞

```http
DELETE /api/posts/{id}/like
```

**权限**: User

## 👤 用户 API

### 获取用户信息

```http
GET /api/users/{id}
```

**权限**: Public

**响应**:
```json
{
    "success": true,
    "data": {
        "user": {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "avatar": "/static/uploads/avatars/admin.jpg",
            "bio": "用户简介",
            "website": "https://example.com",
            "location": "北京",
            "joined_at": "2024-01-01T00:00:00Z",
            "stats": {
                "posts_count": 10,
                "comments_count": 50,
                "likes_received": 100
            }
        }
    }
}
```

### 更新用户信息

```http
PUT /api/users/{id}
```

**权限**: User (本人) / Admin

**请求体**:
```json
{
    "bio": "新的用户简介",
    "website": "https://newsite.com",
    "location": "上海"
}
```

### 修改密码

```http
POST /api/users/{id}/change-password
```

**权限**: User (本人)

**请求体**:
```json
{
    "current_password": "当前密码",
    "new_password": "新密码"
}
```

### 上传头像

```http
POST /api/users/{id}/avatar
```

**权限**: User (本人)

**请求**: multipart/form-data
- `avatar`: 图片文件

## 💬 评论 API

### 获取评论列表

```http
GET /api/posts/{post_id}/comments
```

**参数**:
- `page` (integer, optional): 页码
- `per_page` (integer, optional): 每页数量

**权限**: Public

### 创建评论

```http
POST /api/posts/{post_id}/comments
```

**权限**: User

**请求体**:
```json
{
    "content": "评论内容",
    "parent_id": null
}
```

### 更新评论

```http
PUT /api/comments/{id}
```

**权限**: User (作者) / Admin

### 删除评论

```http
DELETE /api/comments/{id}
```

**权限**: User (作者) / Admin

### 评论点赞

```http
POST /api/comments/{id}/like
```

**权限**: User

## 🛠️ 管理 API

### 获取系统统计

```http
GET /api/admin/stats
```

**权限**: Admin

**响应**:
```json
{
    "success": true,
    "data": {
        "stats": {
            "users": {
                "total": 100,
                "active": 80,
                "new_today": 5
            },
            "posts": {
                "total": 200,
                "published": 180,
                "drafts": 20,
                "new_today": 3
            },
            "comments": {
                "total": 500,
                "approved": 450,
                "pending": 50,
                "new_today": 10
            },
            "system": {
                "disk_usage": "2.5GB",
                "memory_usage": "512MB",
                "uptime": "7 days"
            }
        }
    }
}
```

### 管理用户

```http
GET /api/admin/users
POST /api/admin/users/{id}/ban
POST /api/admin/users/{id}/unban
DELETE /api/admin/users/{id}
```

**权限**: Admin

### 管理评论

```http
GET /api/admin/comments
POST /api/admin/comments/{id}/approve
POST /api/admin/comments/{id}/reject
```

**权限**: Admin

### 敏感词管理

```http
GET /api/admin/sensitive-words
POST /api/admin/sensitive-words
PUT /api/admin/sensitive-words/{id}
DELETE /api/admin/sensitive-words/{id}
```

**权限**: Admin

## 📁 文件上传 API

### 上传图片

```http
POST /api/upload/image
```

**权限**: User

**请求**: multipart/form-data
- `image`: 图片文件
- `type`: 上传类型 (`avatar`, `post`, `comment`)

**响应**:
```json
{
    "success": true,
    "data": {
        "url": "/static/uploads/images/2024/12/filename.jpg",
        "filename": "filename.jpg",
        "size": 102400,
        "type": "image/jpeg"
    }
}
```

### 上传文件

```http
POST /api/upload/file
```

**权限**: User

**限制**:
- 最大文件大小: 16MB
- 允许的文件类型: jpg, jpeg, png, gif, pdf, doc, docx, txt
- 图片会自动压缩和生成缩略图

## 📊 统计 API

### 文章统计

```http
GET /api/stats/posts
```

**权限**: Public

**响应**:
```json
{
    "success": true,
    "data": {
        "total_posts": 200,
        "total_views": 10000,
        "total_likes": 500,
        "categories": [
            {
                "name": "编程",
                "count": 50
            }
        ],
        "popular_posts": [
            {
                "id": 1,
                "title": "热门文章",
                "views": 1000
            }
        ]
    }
}
```

### 搜索统计

```http
GET /api/stats/search
```

**权限**: Admin

**响应**:
```json
{
    "success": true,
    "data": {
        "total_searches": 1000,
        "popular_keywords": [
            {
                "keyword": "Python",
                "count": 150
            }
        ],
        "search_trends": [
            {
                "date": "2024-12-19",
                "count": 50
            }
        ]
    }
}
```

## 🚦 限流和配额

### 限流规则

| 端点类型 | 限制 |
|----------|------|
| 搜索 API | 100 次/分钟 |
| 文章 API | 60 次/分钟 |
| 评论 API | 30 次/分钟 |
| 上传 API | 10 次/分钟 |
| 管理 API | 无限制 |

### 限流响应

当超出限流时，返回 429 状态码：

```json
{
    "success": false,
    "error": {
        "code": "RATE_LIMIT_EXCEEDED",
        "message": "请求过于频繁，请稍后再试",
        "retry_after": 60
    }
}
```

### 响应头

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

## 🔧 SDK 和示例

### JavaScript SDK 示例

```javascript
class TraceBlogAPI {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            credentials: 'include',
            ...options
        };
        
        const response = await fetch(url, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error?.message || '请求失败');
        }
        
        return data;
    }
    
    // 搜索文章
    async searchPosts(query, options = {}) {
        const params = new URLSearchParams({
            q: query,
            ...options
        });
        
        return this.request(`/search?${params}`);
    }
    
    // 获取文章详情
    async getPost(id) {
        return this.request(`/posts/${id}`);
    }
    
    // 创建文章
    async createPost(postData) {
        return this.request('/posts', {
            method: 'POST',
            body: JSON.stringify(postData)
        });
    }
    
    // 创建评论
    async createComment(postId, content, parentId = null) {
        return this.request(`/posts/${postId}/comments`, {
            method: 'POST',
            body: JSON.stringify({ content, parent_id: parentId })
        });
    }
}

// 使用示例
const api = new TraceBlogAPI();

// 搜索文章
try {
    const result = await api.searchPosts('Python', {
        category_id: 1,
        sort: 'date',
        page: 1
    });
    console.log(result.data.posts);
} catch (error) {
    console.error('搜索失败:', error.message);
}

// 获取文章详情
try {
    const result = await api.getPost(1);
    console.log(result.data.post);
} catch (error) {
    console.error('获取文章失败:', error.message);
}
```

### Python SDK 示例

```python
import requests
from typing import Optional, Dict, Any

class TraceBlogAPI:
    def __init__(self, base_url: str = 'http://localhost:5000/api'):
        self.base_url = base_url
        self.session = requests.Session()
    
    def request(self, endpoint: str, method: str = 'GET', **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        
        if not response.ok:
            raise Exception(f"API 请求失败: {response.status_code}")
        
        return response.json()
    
    def search_posts(self, query: str, **params) -> Dict[str, Any]:
        """搜索文章"""
        params['q'] = query
        return self.request('/search', params=params)
    
    def get_post(self, post_id: int) -> Dict[str, Any]:
        """获取文章详情"""
        return self.request(f'/posts/{post_id}')
    
    def create_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建文章"""
        return self.request('/posts', method='POST', json=post_data)

# 使用示例
api = TraceBlogAPI()

# 搜索文章
try:
    result = api.search_posts('Python', category_id=1, sort='date')
    posts = result['data']['posts']
    print(f"找到 {len(posts)} 篇文章")
except Exception as e:
    print(f"搜索失败: {e}")

# 获取文章详情
try:
    result = api.get_post(1)
    post = result['data']['post']
    print(f"文章标题: {post['title']}")
except Exception as e:
    print(f"获取文章失败: {e}")
```

## 📝 更新日志

### v1.0.0 (2024-12-19)
- 初始版本发布
- 实现基础的文章、用户、评论 API
- 添加全文搜索功能
- 实现文件上传和管理功能
- 添加限流和安全机制

---

## 📞 技术支持

如果在使用 API 过程中遇到问题，可以通过以下方式获取帮助：

1. **查看文档**: 首先查看本 API 文档
2. **错误排查**: 检查请求格式和参数
3. **联系支持**: 发送邮件到 support@example.com
4. **GitHub Issues**: 在项目仓库中创建 Issue

**注意事项**:
- 所有时间均为 UTC 时间
- API 可能会有版本更新，请关注更新日志
- 生产环境请使用 HTTPS
- 请合理使用 API，避免频繁请求

---

*最后更新: 2024年12月*