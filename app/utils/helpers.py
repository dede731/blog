import re
import uuid
from datetime import datetime
from app.models import Post

def generate_slug(title):
    """
    从标题生成唯一的slug
    """
    # 移除特殊字符，只保留字母、数字、中文字符和空格
    slug = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', title)
    # 将空格替换为连字符
    slug = re.sub(r'\s+', '-', slug.strip())
    # 转换为小写
    slug = slug.lower()
    
    # 如果slug为空或太短，使用时间戳
    if not slug or len(slug) < 3:
        slug = f"post-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 确保slug唯一
    original_slug = slug
    counter = 1
    while Post.query.filter_by(slug=slug).first():
        slug = f"{original_slug}-{counter}"
        counter += 1
    
    return slug

def save_cover_image(file):
    """
    保存封面图片
    """
    if file and file.filename:
        import os
        import uuid
        from werkzeug.utils import secure_filename
        from flask import current_app
        
        # 生成唯一文件名
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # 确保uploads目录存在
        upload_dir = os.path.join(current_app.static_folder, 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # 保存文件
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        return unique_filename
    return None