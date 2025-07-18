from flask import Blueprint, make_response, url_for, request
from app.models import Post, Category
from datetime import datetime
import xml.etree.ElementTree as ET

sitemap = Blueprint('sitemap', __name__)

@sitemap.route('/sitemap.xml')
def generate_sitemap():
    """生成网站地图"""
    root = ET.Element('urlset')
    root.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    
    # 添加首页
    url = ET.SubElement(root, 'url')
    loc = ET.SubElement(url, 'loc')
    loc.text = url_for('main.index', _external=True)
    lastmod = ET.SubElement(url, 'lastmod')
    lastmod.text = datetime.now().strftime('%Y-%m-%d')
    changefreq = ET.SubElement(url, 'changefreq')
    changefreq.text = 'daily'
    priority = ET.SubElement(url, 'priority')
    priority.text = '1.0'
    
    # 添加关于我页面
    url = ET.SubElement(root, 'url')
    loc = ET.SubElement(url, 'loc')
    loc.text = url_for('main.about', _external=True)
    lastmod = ET.SubElement(url, 'lastmod')
    lastmod.text = datetime.now().strftime('%Y-%m-%d')
    changefreq = ET.SubElement(url, 'changefreq')
    changefreq.text = 'monthly'
    priority = ET.SubElement(url, 'priority')
    priority.text = '0.8'
    
    # 添加留言板页面
    url = ET.SubElement(root, 'url')
    loc = ET.SubElement(url, 'loc')
    loc.text = url_for('main.guestbook', _external=True)
    lastmod = ET.SubElement(url, 'lastmod')
    lastmod.text = datetime.now().strftime('%Y-%m-%d')
    changefreq = ET.SubElement(url, 'changefreq')
    changefreq.text = 'weekly'
    priority = ET.SubElement(url, 'priority')
    priority.text = '0.8'
    
    # 添加归档页面
    url = ET.SubElement(root, 'url')
    loc = ET.SubElement(url, 'loc')
    loc.text = url_for('main.archive', _external=True)
    lastmod = ET.SubElement(url, 'lastmod')
    lastmod.text = datetime.now().strftime('%Y-%m-%d')
    changefreq = ET.SubElement(url, 'changefreq')
    changefreq.text = 'weekly'
    priority = ET.SubElement(url, 'priority')
    priority.text = '0.7'
    
    # 添加所有文章页面
    posts = Post.query.filter_by(is_published=True).all()
    for post in posts:
        url = ET.SubElement(root, 'url')
        loc = ET.SubElement(url, 'loc')
        loc.text = url_for('main.post', id=post.id, _external=True)
        lastmod = ET.SubElement(url, 'lastmod')
        lastmod.text = post.updated_at.strftime('%Y-%m-%d') if post.updated_at else post.created_at.strftime('%Y-%m-%d')
        changefreq = ET.SubElement(url, 'changefreq')
        changefreq.text = 'monthly'
        priority = ET.SubElement(url, 'priority')
        priority.text = '0.6'
    
    # 添加所有分类页面
    categories = Category.query.all()
    for category in categories:
        url = ET.SubElement(root, 'url')
        loc = ET.SubElement(url, 'loc')
        loc.text = url_for('main.category', id=category.id, _external=True)
        lastmod = ET.SubElement(url, 'lastmod')
        lastmod.text = datetime.now().strftime('%Y-%m-%d')
        changefreq = ET.SubElement(url, 'changefreq')
        changefreq.text = 'weekly'
        priority = ET.SubElement(url, 'priority')
        priority.text = '0.5'
    
    # 生成XML
    tree = ET.ElementTree(root)
    xml_string = ET.tostring(root, encoding='utf-8', method='xml')
    
    response = make_response(xml_string)
    response.headers['Content-Type'] = 'application/xml'
    return response