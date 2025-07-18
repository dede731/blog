from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, make_response, jsonify, send_from_directory, g
from flask_login import login_required, current_user
from app.models import Post, Category, Tag, Comment, Like, FriendLink, SiteConfig, Announcement
from app import db
from app.utils.helpers import generate_slug
from markdown import markdown
import feedgenerator
from datetime import datetime
import html
import os
import uuid
from werkzeug.utils import secure_filename
import time
from collections import Counter
from sqlalchemy import func, desc

main = Blueprint('main', __name__)

# 缓存配置
CACHE_DURATION = 300  # 5分钟缓存
_cache = {}

# 搜索历史缓存（内存中存储，生产环境建议使用Redis）
_search_history = []
MAX_SEARCH_HISTORY = 100

def _record_search_query(query):
    """记录搜索查询"""
    global _search_history
    if query and len(query.strip()) > 0:
        # 避免重复记录相同的查询
        if query not in _search_history:
            _search_history.append(query)
            # 保持历史记录数量在限制内
            if len(_search_history) > MAX_SEARCH_HISTORY:
                _search_history.pop(0)

def _get_search_suggestions(query):
    """获取搜索建议"""
    if not query or len(query.strip()) < 2:
        return []
    
    suggestions = []
    
    # 从标题中获取建议
    title_matches = db.session.query(Post.title).filter(
        Post.title.contains(query),
        Post.is_published == True
    ).limit(5).all()
    
    for match in title_matches:
        if match.title not in suggestions:
            suggestions.append(match.title)
    
    # 从标签中获取建议
    tag_matches = db.session.query(Tag.name).filter(
        Tag.name.contains(query)
    ).limit(3).all()
    
    for match in tag_matches:
        if match.name not in suggestions:
            suggestions.append(match.name)
    
    return suggestions[:8]  # 最多返回8个建议

def _get_popular_tags(limit=20):
    """获取热门标签"""
    cache_key = 'popular_tags'
    current_time = time.time()
    
    if cache_key in _cache:
        data, timestamp = _cache[cache_key]
        if current_time - timestamp < 600:  # 10分钟缓存
            return data
    
    # 查询使用次数最多的标签
    from app.models import post_tags
    popular_tags = db.session.query(
        Tag.name, 
        func.count(post_tags.c.post_id).label('post_count')
    ).join(
        post_tags, Tag.id == post_tags.c.tag_id
    ).join(
        Post, post_tags.c.post_id == Post.id
    ).filter(
        Post.is_published == True
    ).group_by(
        Tag.id, Tag.name
    ).order_by(
        desc('post_count')
    ).limit(limit).all()
    
    result = [{'name': tag.name, 'count': tag.post_count} for tag in popular_tags]
    _cache[cache_key] = (result, current_time)
    return result

def _get_search_stats():
    """获取搜索统计信息"""
    global _search_history
    if not _search_history:
        return []
    
    # 统计搜索频率
    search_counter = Counter(_search_history)
    # 返回最热门的10个搜索词
    return search_counter.most_common(10)

def get_cached_data(key, fetch_func, duration=CACHE_DURATION):
    """通用缓存函数"""
    current_time = time.time()
    
    if key in _cache:
        data, timestamp = _cache[key]
        if current_time - timestamp < duration:
            return data
    
    # 缓存过期或不存在，重新获取数据
    data = fetch_func()
    _cache[key] = (data, current_time)
    return data

def get_site_config():
    """获取网站配置的辅助函数（带缓存）"""
    def fetch_config():
        site_config = {}
        configs = SiteConfig.query.all()
        for config in configs:
            site_config[config.key] = config.value
        return site_config
    
    return get_cached_data('site_config', fetch_config)

def get_all_categories():
    """获取所有分类（带缓存）"""
    def fetch_categories():
        return Category.query.all()
    
    return get_cached_data('all_categories', fetch_categories)

def get_featured_posts():
    """获取推荐文章（带缓存）"""
    def fetch_featured():
        return Post.query.filter_by(is_published=True, featured=True).order_by(Post.created_at.desc()).limit(3).all()
    
    return get_cached_data('featured_posts', fetch_featured, 600)  # 10分钟缓存

def get_popular_posts():
    """获取热门文章（带缓存）"""
    def fetch_popular():
        return Post.query.filter_by(is_published=True).order_by(Post.views.desc()).limit(5).all()
    
    return get_cached_data('popular_posts', fetch_popular, 600)  # 10分钟缓存

def get_active_announcements():
    """获取活跃公告（带缓存）"""
    def fetch_announcements():
        return Announcement.query.filter_by(is_active=True).order_by(Announcement.order.asc(), Announcement.created_at.desc()).limit(5).all()
    
    return get_cached_data('active_announcements', fetch_announcements, 300)  # 5分钟缓存

# 允许的图片扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_cover_image(file):
    if file and allowed_file(file.filename):
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        # 添加UUID前缀避免文件名冲突
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # 创建uploads目录的绝对路径
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # 保存文件
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        return unique_filename
    return None

@main.route('/')
@main.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    # 使用缓存的数据
    categories = get_all_categories()
    featured_posts = get_featured_posts()
    popular_posts = get_popular_posts()
    announcements = get_active_announcements()
    
    return render_template('main/index.html', posts=posts, categories=categories, 
                         featured_posts=featured_posts, popular_posts=popular_posts, 
                         announcements=announcements)

@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    post.views += 1
    db.session.commit()
    content = markdown(post.content)
    # 获取已审核的评论，按创建时间排序
    comments = Comment.query.filter_by(post=post, approved=True, parent_id=None).order_by(Comment.created_at.asc()).all()
    return render_template('main/post.html', post=post, content=content, comments=comments)

@main.route('/category/<int:id>')
def category(id):
    category = Category.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(category=category, is_published=True).order_by(
        Post.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    
    # 使用缓存的数据
    categories = get_all_categories()
    site_config = get_site_config()
    
    return render_template('main/category.html', category=category, posts=posts, 
                         categories=categories, site_config=site_config)

@main.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    """处理图片上传"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': '不支持的文件格式'})
        
        # 确保uploads目录存在
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # 生成唯一文件名
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # 保存文件
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # 返回图片URL
        image_url = url_for('static', filename=f'uploads/{unique_filename}')
        
        return jsonify({
            'success': True,
            'url': image_url,
            'filename': unique_filename
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'上传失败: {str(e)}'})

@main.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category_id = request.form.get('category_id')
        summary = request.form.get('summary')
        
        if not all([title, content, category_id]):
            flash('请填写所有必填字段')
            return redirect(url_for('main.create'))
        
        category = Category.query.get(category_id)
        if not category:
            flash('分类不存在')
            return redirect(url_for('main.create'))
        
        # 处理封面图片上传
        cover_image = None
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file.filename != '':
                cover_image = save_cover_image(file)
        
        # 生成slug
        slug = generate_slug(title)
        
        post = Post(title=title, content=content, summary=summary,
                    author=current_user, category=category, cover_image=cover_image, slug=slug)
        db.session.add(post)
        db.session.commit()
        
        # 清除相关缓存
        _cache.pop('featured_posts', None)
        _cache.pop('popular_posts', None)
        
        flash('文章发布成功')
        return redirect(url_for('main.post', id=post.id))
    
    # 使用缓存的分类数据
    categories = get_all_categories()
    return render_template('main/create.html', categories=categories)

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    
    # 检查权限：只有文章作者或管理员可以编辑
    if post.author_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category_id = request.form.get('category_id')
        summary = request.form.get('summary')
        
        if not all([title, content, category_id]):
            flash('请填写所有必填字段')
            return redirect(url_for('main.edit', id=id))
        
        category = Category.query.get(category_id)
        if not category:
            flash('分类不存在')
            return redirect(url_for('main.edit', id=id))
        
        # 处理封面图片上传
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file.filename != '':
                cover_image = save_cover_image(file)
                if cover_image:
                    post.cover_image = cover_image
        
        post.title = title
        post.content = content
        post.summary = summary
        post.category = category
        db.session.commit()
        
        # 清除相关缓存
        _cache.pop('featured_posts', None)
        _cache.pop('popular_posts', None)
        
        flash('文章更新成功')
        return redirect(url_for('main.post', id=post.id))
    
    # 使用缓存的分类数据
    categories = get_all_categories()
    return render_template('main/edit.html', post=post, categories=categories)

@main.route('/delete/<int:id>')
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    
    # 检查权限：只有文章作者或管理员可以删除
    if post.author_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    db.session.delete(post)
    db.session.commit()
    
    # 清除相关缓存
    _cache.pop('featured_posts', None)
    _cache.pop('popular_posts', None)
    
    flash('文章已删除')
    return redirect(url_for('main.index'))


@main.route('/categories')
@login_required
def categories():
    # 这里需要最新的分类数据，不使用缓存
    categories = Category.query.order_by(Category.id.desc()).all()
    site_config = get_site_config()
    return render_template('main/categories.html', categories=categories, site_config=site_config)

@main.route('/columns')
@login_required
def columns():
    """专栏管理页面"""
    # 这里需要最新的分类数据，不使用缓存
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order.asc(), Category.created_at.desc()).all()
    site_config = get_site_config()
    return render_template('main/columns.html', categories=categories, site_config=site_config)


@main.route('/categories/create', methods=['GET', 'POST'])
@login_required
def create_category():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        sort_order = request.form.get('sort_order', 0, type=int)
        
        if not name:
            flash('专栏名称不能为空')
            return redirect(url_for('main.create_category'))
        if Category.query.filter_by(name=name).first():
            flash('专栏名称已存在')
            return redirect(url_for('main.create_category'))
            
        category = Category(
            name=name, 
            description=description,
            sort_order=sort_order
        )
        db.session.add(category)
        db.session.commit()
        
        # 清除分类缓存
        _cache.pop('all_categories', None)
        
        flash('专栏创建成功')
        return redirect(url_for('main.columns'))
    site_config = get_site_config()
    return render_template('main/create_category.html', site_config=site_config)


@main.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        sort_order = request.form.get('sort_order', 0, type=int)
        is_active = request.form.get('is_active') == 'on'
        
        if not name:
            flash('专栏名称不能为空')
            return redirect(url_for('main.edit_category', id=id))
        if Category.query.filter_by(name=name).filter(Category.id != id).first():
            flash('专栏名称已存在')
            return redirect(url_for('main.edit_category', id=id))
            
        category.name = name
        category.description = description
        category.sort_order = sort_order
        category.is_active = is_active
        db.session.commit()
        
        # 清除分类缓存
        _cache.pop('all_categories', None)
        
        flash('专栏更新成功')
        return redirect(url_for('main.columns'))
    site_config = get_site_config()
    return render_template('main/edit_category.html', category=category, site_config=site_config)


@main.route('/categories/delete/<int:id>')
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    if category.posts.count() > 0:
        flash('该分类下还有文章，无法删除')
        return redirect(url_for('main.categories'))
    db.session.delete(category)
    db.session.commit()
    
    # 清除分类缓存
    _cache.pop('all_categories', None)
    
    flash('分类删除成功')
    return redirect(url_for('main.categories'))



@main.route('/post/<int:post_id>/comments', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get('content')
    parent_id = request.form.get('parent_id')
    if not content:
        flash('评论内容不能为空')
        return redirect(url_for('main.post', id=post_id))
    
    # 敏感词过滤
    from app.utils.filters import default_filter
    
    # 检查是否包含敏感词
    if default_filter.contains_sensitive_words(content):
        sensitive_words = default_filter.get_contained_words(content)
        flash(f'评论包含敏感词：{", ".join(sensitive_words)}，请修改后重新提交')
        return redirect(url_for('main.post', id=post_id))
    
    # 创建评论 - 所有注册用户都可以评论
    comment = Comment(content=content, author=current_user, post=post)
    
    # 所有评论都自动通过，无需审核（但必须通过敏感词过滤）
    comment.approved = True
    
    if parent_id:
        parent_comment = Comment.query.get(parent_id)
        if parent_comment and parent_comment.post_id == post.id:
            comment.parent = parent_comment
    
    db.session.add(comment)
    db.session.commit()
    
    flash('评论已发布')
    
    return redirect(url_for('main.post', id=post_id))


@main.route('/api/search/suggestions')
def search_suggestions_api():
    """搜索建议API"""
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])
    
    suggestions = _get_search_suggestions(query)
    return jsonify(suggestions)


@main.route('/api/search/popular')
def popular_searches_api():
    """热门搜索API"""
    stats = _get_search_stats()
    return jsonify([{'query': query, 'count': count} for query, count in stats])


@main.route('/api/tags/popular')
def popular_tags_api():
    """热门标签API"""
    tags = _get_popular_tags()
    return jsonify(tags)


@main.route('/search')
def search():
    query = request.args.get('q', '').strip()
    category_id = request.args.get('category', type=int)
    tag_name = request.args.get('tag', '').strip()
    sort_by = request.args.get('sort', 'relevance')  # relevance, date, views
    page = request.args.get('page', 1, type=int)
    
    if not query and not tag_name:
        flash('请输入搜索关键词或选择标签')
        return redirect(url_for('main.index'))
    
    # 记录搜索历史（简单实现，可以后续扩展到数据库）
    if query:
        _record_search_query(query)
    
    # 构建搜索结果
    posts_query = Post.query.filter_by(is_published=True)
    
    # 全文搜索逻辑
    if query:
        # 分词处理（简单按空格分割）
        keywords = [kw.strip() for kw in query.split() if kw.strip()]
        
        # 构建搜索条件
        search_conditions = []
        for keyword in keywords:
            # 标题搜索权重最高
            title_condition = Post.title.contains(keyword)
            # 摘要搜索权重中等
            summary_condition = Post.summary.contains(keyword)
            # 内容搜索权重较低
            content_condition = Post.content.contains(keyword)
            # 标签搜索
            tag_condition = Post.tags.any(Tag.name.contains(keyword))
            
            search_conditions.append(
                title_condition | summary_condition | content_condition | tag_condition
            )
        
        # 所有关键词都要匹配（AND逻辑）
        if search_conditions:
            from sqlalchemy import and_
            posts_query = posts_query.filter(and_(*search_conditions))
    
    # 分类过滤
    if category_id:
        posts_query = posts_query.filter_by(category_id=category_id)
    
    # 标签过滤
    if tag_name:
        posts_query = posts_query.filter(Post.tags.any(Tag.name.ilike(f'%{tag_name}%')))
    
    # 排序逻辑
    if sort_by == 'date':
        posts_query = posts_query.order_by(Post.created_at.desc())
    elif sort_by == 'views':
        posts_query = posts_query.order_by(Post.views.desc(), Post.created_at.desc())
    else:  # relevance
        # 相关性排序：优先显示标题匹配的文章
        if query:
            # 简单的相关性排序：标题匹配 > 摘要匹配 > 内容匹配
            posts_query = posts_query.order_by(
                Post.title.contains(query).desc(),
                Post.summary.contains(query).desc(),
                Post.created_at.desc()
            )
        else:
            posts_query = posts_query.order_by(Post.created_at.desc())
    
    # 分页
    posts = posts_query.paginate(page=page, per_page=10, error_out=False)
    
    # 获取搜索建议
    suggestions = _get_search_suggestions(query) if query else []
    
    # 获取热门标签
    popular_tags = _get_popular_tags()
    
    # 使用缓存的分类数据
    categories = get_all_categories()
    
    # 搜索统计
    total_results = posts.total
    
    return render_template('main/search_results.html', 
                         posts=posts, 
                         categories=categories, 
                         query=query,
                         category_id=category_id,
                         tag_name=tag_name,
                         sort_by=sort_by,
                         total_results=total_results,
                         suggestions=suggestions,
                         popular_tags=popular_tags)


@main.route('/archive')
def archive():
    posts = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).all()
    archive_dict = {}
    for post in posts:
        year_month = post.created_at.strftime('%Y-%m')
        archive_dict.setdefault(year_month, []).append(post)
    
    return render_template('main/archive.html', archive=archive_dict)


@main.route('/tag/<string:name>')
def tag(name):
    tag = Tag.query.filter_by(name=name).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = tag.posts.filter_by(is_published=True).order_by(Post.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    # 使用缓存的分类数据
    categories = get_all_categories()
    return render_template('main/tag.html', tag=tag, posts=posts, categories=categories)


@main.route('/rss')
def rss():
    """生成博客的RSS订阅源"""
    feed = feedgenerator.Rss201rev2Feed(
        title="Trace_vlog",
        link=request.url_root,
        description="分享技术见解，记录成长足迹",
        language="zh-cn",
        author_name="Trace_vlog",
        feed_url=url_for('main.rss', _external=True)
    )
    
    posts = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).limit(20).all()
    
    for post in posts:
        # 清理HTML标签，获取纯文本摘要
        summary = post.summary or html.escape(post.content[:200] + '...' if len(post.content) > 200 else post.content)
        
        feed.add_item(
            title=post.title,
            link=url_for('main.post', id=post.id, _external=True),
            description=summary,
            pubdate=post.created_at,
            author_name=post.author.username,
            categories=[post.category.name] if post.category else []
        )
    
    response = make_response(feed.writeString('utf-8'))
    response.headers['Content-Type'] = 'application/rss+xml; charset=utf-8'
    return response


@main.route('/category/<int:id>/rss')
def category_rss(id):
    """生成特定分类的RSS订阅源"""
    category = Category.query.get_or_404(id)
    
    feed = feedgenerator.Rss201rev2Feed(
        title=f"Trace_vlog - {category.name}",
        link=url_for('main.category', id=category.id, _external=True),
        description=f"Trace_vlog博客 - {category.name}分类文章",
        language="zh-cn",
        author_name="Trace_vlog",
        feed_url=url_for('main.category_rss', id=category.id, _external=True)
    )
    
    posts = Post.query.filter_by(category_id=id, is_published=True).order_by(Post.created_at.desc()).limit(20).all()
    
    for post in posts:
        summary = post.summary or html.escape(post.content[:200] + '...' if len(post.content) > 200 else post.content)
        
        feed.add_item(
            title=post.title,
            link=url_for('main.post', id=post.id, _external=True),
            description=summary,
            pubdate=post.created_at,
            author_name=post.author.username
        )
    
    response = make_response(feed.writeString('utf-8'))
    response.headers['Content-Type'] = 'application/rss+xml; charset=utf-8'
    return response


@main.route('/post/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    """点赞或取消点赞文章"""
    post = Post.query.get_or_404(post_id)
    
    # 获取客户端IP地址作为访客标识
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', ''))
    
    if current_user.is_authenticated:
        # 注册用户点赞
        like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
        
        if like:
            # 如果已点赞，则取消点赞
            db.session.delete(like)
            db.session.commit()
            return jsonify(status='success', action='unliked', count=post.get_like_count())
        else:
            # 如果未点赞，则添加点赞
            like = Like(user_id=current_user.id, post_id=post_id)
            db.session.add(like)
            db.session.commit()
            return jsonify(status='success', action='liked', count=post.get_like_count())
    else:
        # 访客点赞（基于IP地址）
        like = Like.query.filter_by(guest_ip=client_ip, post_id=post_id).first()
        
        if like:
            # 如果已点赞，则取消点赞
            db.session.delete(like)
            db.session.commit()
            return jsonify(status='success', action='unliked', count=post.get_like_count())
        else:
            # 如果未点赞，则添加点赞
            like = Like(guest_ip=client_ip, post_id=post_id)
            db.session.add(like)
            db.session.commit()
            return jsonify(status='success', action='liked', count=post.get_like_count())


@main.route('/post/<int:post_id>/like/status')
def post_like_status(post_id):
    """获取文章点赞状态"""
    post = Post.query.get_or_404(post_id)
    
    if current_user.is_authenticated:
        is_liked = post.is_liked_by(current_user)
    else:
        # 访客根据IP地址检查点赞状态
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', ''))
        is_liked = post.is_liked_by(None, guest_ip=client_ip)
    
    return jsonify(
        status='success',
        is_liked=is_liked,
        count=post.get_like_count()
    )


@main.route('/about')
def about():
    """关于我页面"""
    return render_template('main/about.html')


@main.route('/guestbook', methods=['GET', 'POST'])
def guestbook():
    """留言板页面"""
    from app.models import GuestbookMessage, GuestbookReply
    
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('请先登录')
            return redirect(url_for('auth.login'))
        
        content = request.form.get('content')
        parent_id = request.form.get('parent_id')
        
        if not content or len(content.strip()) == 0:
            flash('留言内容不能为空', 'danger')
            return redirect(url_for('main.guestbook'))
        
        # 敏感词过滤
        from app.utils.filters import default_filter
        
        # 检查是否包含敏感词
        if default_filter.contains_sensitive_words(content):
            sensitive_words = default_filter.get_contained_words(content)
            flash(f'留言包含敏感词：{", ".join(sensitive_words)}，请修改后重新提交', 'danger')
            return redirect(url_for('main.guestbook'))
        
        if parent_id:
            # 这是一个回复
            parent_message = GuestbookMessage.query.get(parent_id)
            if parent_message:
                reply = GuestbookReply(
                    content=content, 
                    author_id=current_user.id,
                    message_id=parent_id,
                    is_visible=True  # 所有回复都直接可见，无需审核
                )
                db.session.add(reply)
                db.session.commit()
                
                flash('回复发布成功', 'success')
        else:
            # 这是一个新留言
            message = GuestbookMessage(content=content, author_id=current_user.id)
            
            # 所有留言都直接可见，无需审核（但必须通过敏感词过滤）
            message.is_visible = True
            
            db.session.add(message)
            db.session.commit()
            
            flash('留言发布成功', 'success')
        
        return redirect(url_for('main.guestbook'))
    
    page = request.args.get('page', 1, type=int)
    messages = GuestbookMessage.query.filter_by(is_visible=True).order_by(
        GuestbookMessage.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    
    return render_template('main/guestbook.html', messages=messages)


@main.route('/guestbook/add', methods=['POST'])
@login_required
def add_message():
    """添加留言（保留兼容性）"""
    return redirect(url_for('main.guestbook'))


@main.route('/guestbook/reply/<int:reply_id>/delete', methods=['POST'])
@login_required
def delete_reply(reply_id):
    """删除回复"""
    from app.models import GuestbookReply
    
    reply = GuestbookReply.query.get_or_404(reply_id)
    
    # 检查权限：管理员、回复作者或留言作者可以删除
    if not (current_user.is_admin or 
            current_user.id == reply.author_id or 
            current_user.id == reply.message.author_id):
        flash('没有权限删除此回复', 'danger')
        return redirect(url_for('main.guestbook'))
    
    db.session.delete(reply)
    db.session.commit()
    flash('回复已删除', 'success')
    return redirect(url_for('main.guestbook'))


@main.route('/guestbook/message/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_message(message_id):
    """删除留言"""
    from app.models import GuestbookMessage
    
    message = GuestbookMessage.query.get_or_404(message_id)
    
    # 检查权限：管理员或留言作者可以删除
    if not (current_user.is_admin or current_user.id == message.author_id):
        flash('没有权限删除此留言', 'danger')
        return redirect(url_for('main.guestbook'))
    
    db.session.delete(message)
    db.session.commit()
    flash('留言已删除', 'success')
    return redirect(url_for('main.guestbook'))


@main.route('/guestbook/reply/<int:message_id>', methods=['POST'])
@login_required
def reply_guestbook(message_id):
    if not current_user.is_admin:
        abort(403)
    
    from app.models import GuestbookMessage, GuestbookReply
    from app.utils.filters import default_filter
    
    message = GuestbookMessage.query.get_or_404(message_id)
    content = request.form.get('content')
    
    if not content:
        flash('回复内容不能为空')
        return redirect(url_for('main.guestbook'))
    
    # 敏感词过滤
    if default_filter.contains_sensitive_words(content):
        contained_words = default_filter.get_contained_words(content)
        flash(f'回复包含敏感词：{", ".join(contained_words)}，请修改后重新提交')
        return redirect(url_for('main.guestbook'))
    
    reply = GuestbookReply(
        content=content,
        message_id=message_id,
        author_id=current_user.id,
        is_visible=True  # 管理员回复直接可见
    )
    
    db.session.add(reply)
    db.session.commit()
    flash('回复提交成功')
    return redirect(url_for('main.guestbook'))


@main.route('/robots.txt')
def robots():
    """提供robots.txt文件"""
    return send_from_directory(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'), 'robots.txt')


@main.route('/links')
def friend_links():
    """友情链接页面"""
    # 获取所有激活的友情链接，按排序字段排序
    links = FriendLink.query.filter_by(is_active=True).order_by(FriendLink.order.asc()).all()
    
    # 获取网站配置
    site_config = get_site_config()
    
    return render_template('main/links.html', links=links, site_config=site_config)


@main.route('/admin/links')
@login_required
def admin_links():
    """友情链接管理页面，仅管理员可访问"""
    if not current_user.is_admin:
        abort(403)
    
    links = FriendLink.query.order_by(FriendLink.order.asc()).all()
    site_config = get_site_config()
    return render_template('admin/links.html', links=links, site_config=site_config)


@main.route('/admin/links/add', methods=['GET', 'POST'])
@login_required
def add_link():
    """添加友情链接，仅管理员可访问"""
    if not current_user.is_admin:
        abort(403)
    
    if request.method == 'POST':
        name = request.form.get('name')
        url = request.form.get('url')
        description = request.form.get('description')
        logo = request.form.get('logo')
        order = request.form.get('order', 0)
        is_active = True if request.form.get('is_active') else False
        
        if not name or not url:
            flash('名称和URL不能为空', 'danger')
            return redirect(url_for('main.add_link'))
        
        link = FriendLink(name=name, url=url, description=description, 
                         logo=logo, order=order, is_active=is_active)
        db.session.add(link)
        db.session.commit()
        
        flash('友情链接添加成功', 'success')
        return redirect(url_for('main.admin_links'))
    
    site_config = get_site_config()
    return render_template('admin/link_form.html', link=None, site_config=site_config)


@main.route('/admin/links/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_link(id):
    """编辑友情链接，仅管理员可访问"""
    if not current_user.is_admin:
        abort(403)
    
    link = FriendLink.query.get_or_404(id)
    
    if request.method == 'POST':
        link.name = request.form.get('name')
        link.url = request.form.get('url')
        link.description = request.form.get('description')
        link.logo = request.form.get('logo')
        link.order = request.form.get('order', 0)
        link.is_active = True if request.form.get('is_active') else False
        
        if not link.name or not link.url:
            flash('名称和URL不能为空', 'danger')
            return redirect(url_for('main.edit_link', id=id))
        
        db.session.commit()
        
        flash('友情链接更新成功', 'success')
        return redirect(url_for('main.admin_links'))
    
    site_config = get_site_config()
    return render_template('admin/link_form.html', link=link, site_config=site_config)


@main.route('/admin/links/delete/<int:id>')
@login_required
def delete_link(id):
    """删除友情链接，仅管理员可访问"""
    if not current_user.is_admin:
        abort(403)
    
    link = FriendLink.query.get_or_404(id)
    db.session.delete(link)
    db.session.commit()
    
    flash('友情链接删除成功', 'success')
    return redirect(url_for('main.admin_links'))


# ==================== 网站公告管理 ====================

@main.route('/admin/announcements')
@login_required
def admin_announcements():
    """网站公告管理页面，仅管理员可访问"""
    if not current_user.is_admin:
        abort(403)
    
    announcements = Announcement.query.order_by(Announcement.order.asc(), Announcement.created_at.desc()).all()
    site_config = get_site_config()
    return render_template('admin/announcements.html', announcements=announcements, site_config=site_config)


@main.route('/admin/announcements/add', methods=['GET', 'POST'])
@login_required
def add_announcement():
    """添加网站公告，仅管理员可访问"""
    if not current_user.is_admin:
        abort(403)
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        order = request.form.get('order', 0)
        is_active = True if request.form.get('is_active') else False
        
        if not title or not content:
            flash('标题和内容不能为空', 'danger')
            return redirect(url_for('main.add_announcement'))
        
        announcement = Announcement(title=title, content=content, order=order, is_active=is_active)
        db.session.add(announcement)
        db.session.commit()
        
        flash('网站公告添加成功', 'success')
        return redirect(url_for('main.admin_announcements'))
    
    site_config = get_site_config()
    return render_template('admin/announcement_form.html', announcement=None, site_config=site_config)


@main.route('/admin/announcements/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_announcement(id):
    """编辑网站公告，仅管理员可访问"""
    if not current_user.is_admin:
        abort(403)
    
    announcement = Announcement.query.get_or_404(id)
    
    if request.method == 'POST':
        announcement.title = request.form.get('title')
        announcement.content = request.form.get('content')
        announcement.order = request.form.get('order', 0)
        announcement.is_active = True if request.form.get('is_active') else False
        
        if not announcement.title or not announcement.content:
            flash('标题和内容不能为空', 'danger')
            return redirect(url_for('main.edit_announcement', id=id))
        
        db.session.commit()
        
        flash('网站公告更新成功', 'success')
        return redirect(url_for('main.admin_announcements'))
    
    site_config = get_site_config()
    return render_template('admin/announcement_form.html', announcement=announcement, site_config=site_config)


@main.route('/admin/announcements/delete/<int:id>')
@login_required
def delete_announcement(id):
    """删除网站公告，仅管理员可访问"""
    if not current_user.is_admin:
        abort(403)
    
    announcement = Announcement.query.get_or_404(id)
    db.session.delete(announcement)
    db.session.commit()
    
    flash('网站公告删除成功', 'success')
    return redirect(url_for('main.admin_announcements'))