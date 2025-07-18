#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
初始化公告数据脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Announcement
from datetime import datetime

def init_announcements():
    """初始化公告数据"""
    app = create_app('development')  # 传递配置名称
    
    with app.app_context():
        # 检查是否已有公告数据
        if Announcement.query.first():
            print("公告数据已存在，跳过初始化")
            return
        
        # 创建示例公告
        announcements = [
            {
                'title': '网站全新改版上线',
                'content': '网站全新改版上线，新增多项功能，包括公告管理、友情链接管理等，欢迎体验！',
                'is_active': True,
                'order': 1
            },
            {
                'title': '新增文章封面图片功能',
                'content': '新增文章封面图片功能，让您的博客更加生动美观。',
                'is_active': True,
                'order': 2
            },
            {
                'title': '评论系统升级',
                'content': '评论系统升级，支持回复功能，提升用户交互体验。',
                'is_active': True,
                'order': 3
            },
            {
                'title': '网站维护通知',
                'content': '本网站将于每周日凌晨2:00-4:00进行例行维护，期间可能无法正常访问，敬请谅解。',
                'is_active': False,
                'order': 4
            }
        ]
        
        for announcement_data in announcements:
            announcement = Announcement(
                title=announcement_data['title'],
                content=announcement_data['content'],
                is_active=announcement_data['is_active'],
                order=announcement_data['order'],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(announcement)
        
        try:
            db.session.commit()
            print(f"成功创建 {len(announcements)} 条公告数据")
        except Exception as e:
            db.session.rollback()
            print(f"创建公告数据失败: {e}")

if __name__ == '__main__':
    init_announcements()