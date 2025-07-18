// 搜索自动完成功能
class SearchAutoComplete {
    constructor(inputSelector, suggestionsSelector) {
        this.input = document.querySelector(inputSelector);
        this.suggestionsContainer = document.querySelector(suggestionsSelector);
        this.currentFocus = -1;
        this.suggestions = [];
        this.debounceTimer = null;
        
        if (this.input) {
            this.init();
        }
    }
    
    init() {
        // 创建建议容器
        if (!this.suggestionsContainer) {
            this.suggestionsContainer = document.createElement('div');
            this.suggestionsContainer.className = 'search-suggestions';
            this.input.parentNode.appendChild(this.suggestionsContainer);
        }
        
        // 绑定事件
        this.input.addEventListener('input', (e) => this.handleInput(e));
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        this.input.addEventListener('focus', (e) => this.handleFocus(e));
        
        // 点击外部关闭建议
        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.suggestionsContainer.contains(e.target)) {
                this.hideSuggestions();
            }
        });
    }
    
    handleInput(e) {
        const query = e.target.value.trim();
        
        // 清除之前的定时器
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        
        // 防抖处理
        this.debounceTimer = setTimeout(() => {
            if (query.length >= 2) {
                this.fetchSuggestions(query);
            } else {
                this.hideSuggestions();
            }
        }, 300);
    }
    
    handleKeydown(e) {
        const suggestions = this.suggestionsContainer.querySelectorAll('.suggestion-item');
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.currentFocus = Math.min(this.currentFocus + 1, suggestions.length - 1);
                this.updateFocus(suggestions);
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                this.currentFocus = Math.max(this.currentFocus - 1, -1);
                this.updateFocus(suggestions);
                break;
                
            case 'Enter':
                e.preventDefault();
                if (this.currentFocus >= 0 && suggestions[this.currentFocus]) {
                    this.selectSuggestion(suggestions[this.currentFocus].textContent);
                } else {
                    this.performSearch();
                }
                break;
                
            case 'Escape':
                this.hideSuggestions();
                this.input.blur();
                break;
        }
    }
    
    handleFocus(e) {
        const query = e.target.value.trim();
        if (query.length >= 2) {
            this.fetchSuggestions(query);
        }
    }
    
    async fetchSuggestions(query) {
        try {
            const response = await fetch(`/api/search/suggestions?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.success) {
                this.suggestions = data.suggestions;
                this.showSuggestions();
            }
        } catch (error) {
            console.error('获取搜索建议失败:', error);
        }
    }
    
    showSuggestions() {
        if (this.suggestions.length === 0) {
            this.hideSuggestions();
            return;
        }
        
        const html = this.suggestions.map((suggestion, index) => 
            `<div class="suggestion-item" data-index="${index}">${this.highlightMatch(suggestion)}</div>`
        ).join('');
        
        this.suggestionsContainer.innerHTML = html;
        this.suggestionsContainer.style.display = 'block';
        this.currentFocus = -1;
        
        // 绑定点击事件
        this.suggestionsContainer.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                this.selectSuggestion(item.textContent);
            });
        });
    }
    
    hideSuggestions() {
        this.suggestionsContainer.style.display = 'none';
        this.currentFocus = -1;
    }
    
    updateFocus(suggestions) {
        suggestions.forEach((item, index) => {
            item.classList.toggle('active', index === this.currentFocus);
        });
    }
    
    selectSuggestion(suggestion) {
        this.input.value = suggestion;
        this.hideSuggestions();
        this.performSearch();
    }
    
    highlightMatch(text) {
        const query = this.input.value.trim();
        if (!query) return text;
        
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<strong>$1</strong>');
    }
    
    performSearch() {
        const query = this.input.value.trim();
        if (query) {
            window.location.href = `/search?q=${encodeURIComponent(query)}`;
        }
    }
}

// 热门搜索功能
class PopularSearches {
    constructor(containerSelector) {
        this.container = document.querySelector(containerSelector);
        if (this.container) {
            this.loadPopularSearches();
        }
    }
    
    async loadPopularSearches() {
        try {
            const response = await fetch('/api/search/popular');
            const data = await response.json();
            
            if (data.success && data.popular_searches.length > 0) {
                this.renderPopularSearches(data.popular_searches);
            }
        } catch (error) {
            console.error('获取热门搜索失败:', error);
        }
    }
    
    renderPopularSearches(searches) {
        const html = searches.map(search => 
            `<a href="/search?q=${encodeURIComponent(search.query)}" class="badge bg-light text-dark text-decoration-none me-2 mb-2">
                ${search.query} <span class="badge bg-primary">${search.count}</span>
            </a>`
        ).join('');
        
        this.container.innerHTML = html;
    }
}

// 热门标签功能
class PopularTags {
    constructor(containerSelector) {
        this.container = document.querySelector(containerSelector);
        if (this.container) {
            this.loadPopularTags();
        }
    }
    
    async loadPopularTags() {
        try {
            const response = await fetch('/api/tags/popular');
            const data = await response.json();
            
            if (data.success && data.popular_tags.length > 0) {
                this.renderPopularTags(data.popular_tags);
            }
        } catch (error) {
            console.error('获取热门标签失败:', error);
        }
    }
    
    renderPopularTags(tags) {
        const html = tags.map(tag => 
            `<a href="/search?tag=${encodeURIComponent(tag.name)}" class="badge bg-primary text-decoration-none me-2 mb-2" title="${tag.count} 篇文章">
                ${tag.name} <span class="badge bg-light text-dark">${tag.count}</span>
            </a>`
        ).join('');
        
        this.container.innerHTML = html;
    }
}

// 搜索历史功能
class SearchHistory {
    constructor() {
        this.maxHistory = 10;
        this.storageKey = 'search_history';
    }
    
    addSearch(query) {
        if (!query || query.trim().length < 2) return;
        
        let history = this.getHistory();
        
        // 移除重复项
        history = history.filter(item => item !== query);
        
        // 添加到开头
        history.unshift(query);
        
        // 限制数量
        history = history.slice(0, this.maxHistory);
        
        // 保存
        localStorage.setItem(this.storageKey, JSON.stringify(history));
    }
    
    getHistory() {
        try {
            const history = localStorage.getItem(this.storageKey);
            return history ? JSON.parse(history) : [];
        } catch (error) {
            return [];
        }
    }
    
    clearHistory() {
        localStorage.removeItem(this.storageKey);
    }
    
    renderHistory(containerSelector) {
        const container = document.querySelector(containerSelector);
        if (!container) return;
        
        const history = this.getHistory();
        if (history.length === 0) {
            container.style.display = 'none';
            return;
        }
        
        const html = history.map(query => 
            `<a href="/search?q=${encodeURIComponent(query)}" class="list-group-item list-group-item-action">
                <i class="fas fa-history me-2"></i>${query}
            </a>`
        ).join('');
        
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h6 class="mb-0">搜索历史</h6>
                <button class="btn btn-sm btn-outline-secondary" onclick="searchHistory.clearHistory(); this.parentElement.parentElement.style.display='none';">
                    清除
                </button>
            </div>
            <div class="list-group">
                ${html}
            </div>
        `;
        
        container.style.display = 'block';
    }
}

// 初始化搜索功能
document.addEventListener('DOMContentLoaded', function() {
    // 初始化搜索自动完成
    const searchAutoComplete = new SearchAutoComplete('#searchQuery', '.search-suggestions');
    
    // 初始化热门搜索
    const popularSearches = new PopularSearches('#popular-searches');
    
    // 初始化热门标签
    const popularTags = new PopularTags('#popular-tags');
    
    // 初始化搜索历史
    window.searchHistory = new SearchHistory();
    
    // 记录当前搜索
    const urlParams = new URLSearchParams(window.location.search);
    const currentQuery = urlParams.get('q');
    if (currentQuery) {
        searchHistory.addSearch(currentQuery);
    }
    
    // 渲染搜索历史
    searchHistory.renderHistory('#search-history');
});

// CSS样式
const style = document.createElement('style');
style.textContent = `
.search-suggestions {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 1px solid #ddd;
    border-top: none;
    border-radius: 0 0 4px 4px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    z-index: 1000;
    max-height: 300px;
    overflow-y: auto;
    display: none;
}

.suggestion-item {
    padding: 8px 12px;
    cursor: pointer;
    border-bottom: 1px solid #eee;
    transition: background-color 0.2s;
}

.suggestion-item:hover,
.suggestion-item.active {
    background-color: #f8f9fa;
}

.suggestion-item:last-child {
    border-bottom: none;
}

.suggestion-item strong {
    color: #007bff;
}

.search-input-container {
    position: relative;
}

#search-history {
    display: none;
    margin-top: 1rem;
}
`;
document.head.appendChild(style);