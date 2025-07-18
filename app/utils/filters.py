# 敏感词过滤器
import time

class SensitiveWordFilter:
    """敏感词过滤器
    
    用于过滤评论和留言中的敏感词，支持添加、删除敏感词，以及对文本进行过滤。
    """
    
    def __init__(self, sensitive_words=None):
        """初始化敏感词过滤器
        
        Args:
            sensitive_words: 敏感词列表，默认为None
        """
        self.sensitive_words = sensitive_words or []
        self.replacement = '***'  # 敏感词替换字符
        self._last_load_time = 0  # 上次加载时间
        self._cache_duration = 300  # 缓存5分钟
    
    def load_from_database(self):
        """从数据库加载敏感词（带缓存）"""
        current_time = time.time()
        
        # 如果缓存还有效，直接返回
        if current_time - self._last_load_time < self._cache_duration and self.sensitive_words:
            return
        
        try:
            from flask import current_app
            from app.models import SensitiveWord
            
            # 检查是否在应用上下文中
            if current_app:
                words = SensitiveWord.query.all()
                self.sensitive_words = [word.word for word in words]
                self._last_load_time = current_time
                return
        except Exception as e:
            # 如果数据库不可用，使用默认敏感词
            pass
        
        # 默认敏感词列表
        if not self.sensitive_words:  # 只有在没有敏感词时才使用默认列表
            self.sensitive_words = [
                '赌博', '色情', '暴力', '政治', '诈骗', '违法', '犯罪',
                '黄赌毒', '传销', '邪教', '恐怖', '极端', '歧视'
            ]
            self._last_load_time = current_time
    
    def add_word(self, word):
        """添加敏感词
        
        Args:
            word: 要添加的敏感词
        """
        if word and word not in self.sensitive_words:
            self.sensitive_words.append(word)
            # 清除缓存，强制下次重新加载
            self._last_load_time = 0
    
    def add_words(self, words):
        """批量添加敏感词
        
        Args:
            words: 要添加的敏感词列表
        """
        for word in words:
            if word and word not in self.sensitive_words:
                self.sensitive_words.append(word)
        # 清除缓存，强制下次重新加载
        self._last_load_time = 0
    
    def remove_word(self, word):
        """删除敏感词
        
        Args:
            word: 要删除的敏感词
        """
        if word in self.sensitive_words:
            self.sensitive_words.remove(word)
            # 清除缓存，强制下次重新加载
            self._last_load_time = 0
    
    def filter_text(self, text):
        """过滤文本中的敏感词
        
        Args:
            text: 要过滤的文本
            
        Returns:
            过滤后的文本
        """
        if not text:
            return text
        
        # 确保敏感词列表是最新的（带缓存）
        self.load_from_database()
        
        if not self.sensitive_words:
            return text
        
        filtered_text = text
        for word in self.sensitive_words:
            if word in filtered_text:
                filtered_text = filtered_text.replace(word, self.replacement)
        
        return filtered_text
    
    def contains_sensitive_words(self, text):
        """检查文本是否包含敏感词
        
        Args:
            text: 要检查的文本
            
        Returns:
            如果包含敏感词，返回True；否则返回False
        """
        if not text:
            return False
        
        # 确保敏感词列表是最新的（带缓存）
        self.load_from_database()
        
        if not self.sensitive_words:
            return False
        
        for word in self.sensitive_words:
            if word in text:
                return True
        
        return False
    
    def get_contained_words(self, text):
        """获取文本中包含的敏感词列表
        
        Args:
            text: 要检查的文本
            
        Returns:
            文本中包含的敏感词列表
        """
        if not text:
            return []
        
        # 确保敏感词列表是最新的（带缓存）
        self.load_from_database()
        
        if not self.sensitive_words:
            return []
        
        contained_words = []
        for word in self.sensitive_words:
            if word in text:
                contained_words.append(word)
        
        return contained_words

# 创建默认的敏感词过滤器实例
default_filter = SensitiveWordFilter()
# 注意：不在这里加载数据库，而是在每次使用时动态加载