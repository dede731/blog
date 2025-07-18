from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Comment, GuestbookMessage, GuestbookReply, SensitiveWord
from app import db
from urllib.parse import urlparse
import csv
import io
import os
from werkzeug.utils import secure_filename

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash('邮箱或密码错误')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册')
            return redirect(url_for('auth.register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功，请登录')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """个人资料页面"""
    if request.method == 'POST':
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        current_user.bio = request.form.get('bio')
        
        # 处理头像上传
        avatar = request.files.get('avatar')
        if avatar and avatar.filename:
            filename = secure_filename(avatar.filename)
            timestamp = str(int(time.time()))
            filename = f"avatar_{timestamp}_{filename}"
            avatar_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            avatar.save(avatar_path)
            current_user.avatar = filename
        
        db.session.commit()
        flash('个人资料更新成功')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html')


@auth.route('/comments', methods=['GET'])
@login_required
def comments():
    """评论管理页面"""
    # 获取过滤参数
    filter_type = request.args.get('filter', 'all')
    search = request.args.get('search', '')
    
    if current_user.is_admin:
        # 管理员可以查看所有评论
        query = Comment.query
    else:
        # 普通用户只能查看自己的评论
        query = Comment.query.filter_by(author_id=current_user.id)
    
    # 应用过滤条件
    if filter_type == 'pending':
        query = query.filter_by(approved=False)
    elif filter_type == 'approved':
        query = query.filter_by(approved=True)
    
    # 应用搜索条件
    if search:
        query = query.filter(Comment.content.contains(search))
    
    # 分页
    page = request.args.get('page', 1, type=int)
    comments = query.order_by(Comment.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    return render_template('auth/comments.html', comments=comments, 
                           filter=filter_type, search=search)


@auth.route('/comments/<int:id>/approve')
@login_required
def approve_comment(id):
    """批准评论"""
    comment = Comment.query.get_or_404(id)
    
    # 检查权限：管理员或文章作者可以批准评论
    if not current_user.is_admin and comment.post.author_id != current_user.id:
        abort(403)
    
    comment.approved = True
    db.session.commit()
    flash('评论已批准')
    return redirect(url_for('auth.comments', filter=request.args.get('filter', 'all')))


@auth.route('/comments/<int:id>/unapprove')
@login_required
def unapprove_comment(id):
    """取消批准评论"""
    comment = Comment.query.get_or_404(id)
    
    # 检查权限：管理员或文章作者可以取消批准评论
    if not current_user.is_admin and comment.post.author_id != current_user.id:
        abort(403)
    
    comment.approved = False
    db.session.commit()
    flash('评论已设为待审核')
    return redirect(url_for('auth.comments', filter=request.args.get('filter', 'all')))


@auth.route('/comments/<int:id>/reply', methods=['POST'])
@login_required
def reply_comment(id):
    """回复评论"""
    parent_comment = Comment.query.get_or_404(id)
    content = request.form.get('content')
    
    if not content:
        flash('回复内容不能为空')
        return redirect(url_for('main.post', id=parent_comment.post_id))
    
    # 敏感词过滤
    from app.utils.filters import default_filter
    
    # 检查是否包含敏感词
    if default_filter.contains_sensitive_words(content):
        sensitive_words = default_filter.get_contained_words(content)
        flash(f'回复包含敏感词：{", ".join(sensitive_words)}，请修改后重新提交')
        return redirect(url_for('main.post', id=parent_comment.post_id))
    
    # 创建回复评论
    reply = Comment(
        content=content,
        author=current_user,
        post=parent_comment.post,
        parent=parent_comment,
        approved=True  # 通过敏感词过滤的回复自动发布
    )
    
    db.session.add(reply)
    db.session.commit()
    flash('回复已发布')
    return redirect(url_for('main.post', id=parent_comment.post_id))


@auth.route('/comments/<int:id>/delete')
@login_required
def delete_comment(id):
    """删除评论"""
    comment = Comment.query.get_or_404(id)
    
    # 检查权限：管理员、文章作者或评论作者可以删除评论
    if not current_user.is_admin and comment.post.author_id != current_user.id and comment.author_id != current_user.id:
        abort(403)
    
    post_id = comment.post_id  # 保存文章ID用于重定向
    
    db.session.delete(comment)
    db.session.commit()
    flash('评论已删除')
    
    # 如果是从评论管理页面来的，返回评论管理页面；否则返回文章页面
    if request.referrer and 'comments' in request.referrer and 'auth' in request.referrer:
        return redirect(url_for('auth.comments', filter=request.args.get('filter', 'all')))
    else:
        return redirect(url_for('main.post', id=post_id))


@auth.route('/sensitive-words')
@login_required
def sensitive_words():
    """敏感词管理页面"""
    # 只有管理员可以管理敏感词
    if not current_user.is_admin:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    words = SensitiveWord.query.order_by(SensitiveWord.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    return render_template('auth/sensitive_words.html', words=words)


@auth.route('/sensitive-words/add', methods=['POST'])
@login_required
def add_sensitive_word():
    """添加敏感词"""
    # 只有管理员可以添加敏感词
    if not current_user.is_admin:
        abort(403)
    
    word = request.form.get('word')
    if not word:
        flash('敏感词不能为空')
        return redirect(url_for('auth.sensitive_words'))
    
    # 检查敏感词是否已存在
    if SensitiveWord.query.filter_by(word=word).first():
        flash('该敏感词已存在')
        return redirect(url_for('auth.sensitive_words'))
    
    # 创建敏感词
    sensitive_word = SensitiveWord(word=word, created_by=current_user.id)
    db.session.add(sensitive_word)
    db.session.commit()
    
    # 更新敏感词过滤器
    from app.utils.filters import default_filter
    default_filter.add_word(word)
    
    flash('敏感词添加成功')
    return redirect(url_for('auth.sensitive_words'))


@auth.route('/sensitive-words/import', methods=['POST'])
@login_required
def import_sensitive_words():
    """批量导入敏感词"""
    # 只有管理员可以导入敏感词
    if not current_user.is_admin:
        abort(403)
    
    word_list = request.form.get('word_list')
    if not word_list:
        flash('敏感词列表不能为空')
        return redirect(url_for('auth.sensitive_words'))
    
    # 解析敏感词列表
    words = [w.strip() for w in word_list.split('\n') if w.strip()]
    
    # 添加敏感词
    added_count = 0
    for word in words:
        # 检查敏感词是否已存在
        if not SensitiveWord.query.filter_by(word=word).first():
            sensitive_word = SensitiveWord(word=word, created_by=current_user.id)
            db.session.add(sensitive_word)
            added_count += 1
    
    if added_count > 0:
        db.session.commit()
        
        # 更新敏感词过滤器
        from app.utils.filters import default_filter
        default_filter.add_words(words)
        
        flash(f'成功导入{added_count}个敏感词')
    else:
        flash('没有新的敏感词被导入')
    
    return redirect(url_for('auth.sensitive_words'))


@auth.route('/sensitive-words/import-file', methods=['POST'])
@login_required
def import_sensitive_words_file():
    """从文件导入敏感词"""
    # 只有管理员可以导入敏感词
    if not current_user.is_admin:
        abort(403)
    
    file = request.files.get('word_file')
    encoding = request.form.get('encoding', 'utf-8')
    
    if not file or file.filename == '':
        flash('请选择要上传的文件')
        return redirect(url_for('auth.sensitive_words'))
    
    try:
        # 读取文件内容
        file_content = file.read().decode(encoding)
        words = []
        
        # 根据文件扩展名处理
        filename = secure_filename(file.filename)
        if filename.endswith('.csv'):
            # 处理CSV文件
            csv_reader = csv.reader(io.StringIO(file_content))
            for i, row in enumerate(csv_reader):
                if i == 0:  # 跳过表头
                    continue
                if row and row[0].strip():  # 取第一列作为敏感词
                    words.append(row[0].strip())
        else:
            # 处理TXT文件
            words = [w.strip() for w in file_content.split('\n') if w.strip()]
        
        # 添加敏感词到数据库
        added_count = 0
        for word in words:
            if word and not SensitiveWord.query.filter_by(word=word).first():
                sensitive_word = SensitiveWord(word=word, created_by=current_user.id)
                db.session.add(sensitive_word)
                added_count += 1
        
        if added_count > 0:
            db.session.commit()
            
            # 更新敏感词过滤器
            from app.utils.filters import default_filter
            default_filter.add_words(words)
            
            flash(f'成功从文件导入{added_count}个敏感词')
        else:
            flash('文件中没有新的敏感词被导入')
    
    except UnicodeDecodeError:
        flash(f'文件编码错误，请尝试其他编码格式')
    except Exception as e:
        flash(f'文件处理失败：{str(e)}')
    
    return redirect(url_for('auth.sensitive_words'))


@auth.route('/sensitive-words/import-preset', methods=['POST'])
@login_required
def import_preset_words():
    """导入预设敏感词库"""
    # 只有管理员可以导入敏感词
    if not current_user.is_admin:
        abort(403)
    
    categories = request.form.getlist('categories')
    if not categories:
        flash('请至少选择一个词库类别')
        return redirect(url_for('auth.sensitive_words'))
    
    # 预设敏感词库
    preset_words = {
        'basic': [
            '赌博', '博彩', '色情', '暴力', '恐怖', '血腥', '杀人', '自杀',
            '毒品', '吸毒', '贩毒', '海洛因', '冰毒', '摇头丸', '大麻',
            '诈骗', '传销', '洗钱', '非法集资', '高利贷', '套路贷',
            '反动', '颠覆', '分裂', '邪教', '法轮功', '达赖',
            '枪支', '炸弹', '爆炸', '武器', '军火', '弹药'
        ],
        'politics': [
            '政变', '革命', '推翻', '颠覆政权', '反政府', '分裂国家',
            '台独', '藏独', '疆独', '港独', '民运', '六四',
            '法轮功', '达赖', '热比娅', '东突', '世维会'
        ],
        'gambling': [
            '赌博', '博彩', '赌场', '老虎机', '轮盘', '百家乐', '21点',
            '德州扑克', '麻将赌博', '斗地主赌博', '网络赌博', '线上博彩',
            '体育博彩', '足球博彩', '篮球博彩', '赛马博彩', '彩票作弊',
            '私彩', '地下赌场', '赌资', '赌债', '洗码', '抽水'
        ],
        'drugs': [
            '毒品', '吸毒', '贩毒', '制毒', '海洛因', '冰毒', '摇头丸',
            '大麻', '可卡因', '鸦片', '吗啡', '杜冷丁', 'K粉', '麻古',
            '神仙水', '蓝精灵', '开心水', '忘情水', '迷魂药', '听话水',
            '安非他明', '甲基苯丙胺', '氯胺酮', '三唑仑'
        ],
        'fraud': [
            '诈骗', '电信诈骗', '网络诈骗', '金融诈骗', '传销', '非法集资',
            '庞氏骗局', '洗钱', '套路贷', '高利贷', '校园贷', '裸贷',
            '刷单', '刷信誉', '虚假广告', '假冒伪劣', '山寨产品',
            '钓鱼网站', '木马病毒', '恶意软件', '身份盗用'
        ],
        'violence': [
            '暴力', '恐怖', '血腥', '杀人', '谋杀', '自杀', '爆炸',
            '炸弹', '恐怖袭击', '恐怖主义', '极端主义', '武装分子',
            '绑架', '劫持', '人质', '枪击', '砍杀', '斩首',
            '酷刑', '虐待', '折磨', '残忍', '野蛮', '兽性'
        ]
    }
    
    # 收集要导入的敏感词
    words_to_import = []
    for category in categories:
        if category in preset_words:
            words_to_import.extend(preset_words[category])
    
    # 去重
    words_to_import = list(set(words_to_import))
    
    # 添加敏感词到数据库
    added_count = 0
    for word in words_to_import:
        if not SensitiveWord.query.filter_by(word=word).first():
            sensitive_word = SensitiveWord(word=word, created_by=current_user.id)
            db.session.add(sensitive_word)
            added_count += 1
    
    if added_count > 0:
        db.session.commit()
        
        # 更新敏感词过滤器
        from app.utils.filters import default_filter
        default_filter.add_words(words_to_import)
        
        flash(f'成功导入{added_count}个预设敏感词')
    else:
        flash('所选词库中的敏感词已全部存在')
    
    return redirect(url_for('auth.sensitive_words'))


@auth.route('/sensitive-words/<int:id>/delete')
@login_required
def delete_sensitive_word(id):
    """删除敏感词"""
    # 只有管理员可以删除敏感词
    if not current_user.is_admin:
        abort(403)
    
    sensitive_word = SensitiveWord.query.get_or_404(id)
    word = sensitive_word.word
    
    db.session.delete(sensitive_word)
    db.session.commit()
    
    # 更新敏感词过滤器
    from app.utils.filters import default_filter
    default_filter.remove_word(word)
    
    flash('敏感词已删除')
    return redirect(url_for('auth.sensitive_words'))


@auth.route('/guestbook-management')
@login_required
def guestbook_management():
    """留言板管理页面"""
    # 只有管理员可以管理留言板
    if not current_user.is_admin:
        abort(403)
    
    # 获取过滤参数
    filter_type = request.args.get('filter', 'all')
    search = request.args.get('search', '')
    
    # 构建查询
    query = GuestbookMessage.query
    
    # 应用过滤条件
    if filter_type == 'visible':
        query = query.filter_by(is_visible=True)
    elif filter_type == 'hidden':
        query = query.filter_by(is_visible=False)
    
    # 应用搜索条件
    if search:
        query = query.filter(GuestbookMessage.content.contains(search))
    
    # 分页
    page = request.args.get('page', 1, type=int)
    messages = query.order_by(GuestbookMessage.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    return render_template('auth/guestbook_management.html', messages=messages, 
                           filter=filter_type, search=search)


@auth.route('/guestbook-management/<int:id>/toggle-visibility')
@login_required
def toggle_message_visibility(id):
    """切换留言可见性"""
    # 只有管理员可以操作
    if not current_user.is_admin:
        abort(403)
    
    message = GuestbookMessage.query.get_or_404(id)
    message.is_visible = not message.is_visible
    db.session.commit()
    
    status = "显示" if message.is_visible else "隐藏"
    flash(f'留言已{status}')
    return redirect(url_for('auth.guestbook_management', filter=request.args.get('filter', 'all')))


@auth.route('/guestbook-management/<int:id>/delete')
@login_required
def delete_message(id):
    """删除留言"""
    # 只有管理员可以删除
    if not current_user.is_admin:
        abort(403)
    
    message = GuestbookMessage.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    
    flash('留言已删除')
    return redirect(url_for('auth.guestbook_management', filter=request.args.get('filter', 'all')))


@auth.route('/guestbook-management/reply/<int:id>/toggle-visibility')
@login_required
def toggle_reply_visibility(id):
    """切换回复可见性"""
    # 只有管理员可以操作
    if not current_user.is_admin:
        abort(403)
    
    reply = GuestbookReply.query.get_or_404(id)
    reply.is_visible = not reply.is_visible
    db.session.commit()
    
    status = "显示" if reply.is_visible else "隐藏"
    flash(f'回复已{status}')
    return redirect(url_for('auth.guestbook_management', filter=request.args.get('filter', 'all')))


@auth.route('/guestbook-management/reply/<int:id>/delete')
@login_required
def delete_reply(id):
    """删除回复"""
    # 只有管理员可以删除
    if not current_user.is_admin:
        abort(403)
    
    reply = GuestbookReply.query.get_or_404(id)
    db.session.delete(reply)
    db.session.commit()
    
    flash('回复已删除')
    return redirect(url_for('auth.guestbook_management', filter=request.args.get('filter', 'all')))