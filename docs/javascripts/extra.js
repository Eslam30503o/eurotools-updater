/* Euro Tools Code Manager - Documentation Custom JavaScript */
/* سكريبت مخصص لتوثيق نظام إدارة أكواد الأدوات الصناعية */

document.addEventListener('DOMContentLoaded', function() {
    
    // ===================================
    // 🎯 تحسينات التنقل والتفاعل
    // ===================================
    
    // إضافة تأثيرات التمرير السلس
    initSmoothScrolling();
    
    // إضافة مؤشرات التقدم للقراءة
    initReadingProgress();
    
    // تحسين البحث
    enhanceSearch();
    
    // إضافة اختصارات لوحة المفاتيح
    initKeyboardShortcuts();
    
    // تحسين الجداول
    enhanceTables();
    
    // إضافة أزرار النسخ المخصصة
    initCustomCopyButtons();
    
    // تحسين الصور
    enhanceImages();
    
    // إضافة إحصائيات القراءة
    initReadingStats();
    
    // ===================================
    // 🔄 دوال التحسين
    // ===================================
    
    /**
     * تهيئة التمرير السلس للروابط الداخلية
     */
    function initSmoothScrolling() {
        const links = document.querySelectorAll('a[href^="#"]');
        
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                const targetId = this.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                    
                    // تحديث URL بدون إعادة تحميل
                    history.pushState(null, null, `#${targetId}`);
                }
            });
        });
    }
    
    /**
     * إضافة مؤشر تقدم القراءة
     */
    function initReadingProgress() {
        // إنشاء شريط التقدم
        const progressBar = document.createElement('div');
        progressBar.className = 'reading-progress';
        progressBar.innerHTML = '<div class="reading-progress-bar"></div>';
        
        // إضافة الأنماط
        const style = document.createElement('style');
        style.textContent = `
            .reading-progress {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 3px;
                background: rgba(255,255,255,0.1);
                z-index: 1000;
                pointer-events: none;
            }
            
            .reading-progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #1976d2, #1565c0);
                width: 0%;
                transition: width 0.1s ease;
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(progressBar);
        
        // تحديث التقدم عند التمرير
        window.addEventListener('scroll', function() {
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            
            progressBar.querySelector('.reading-progress-bar').style.width = scrolled + '%';
        });
    }
    
    /**
     * تحسين وظيفة البحث
     */
    function enhanceSearch() {
        const searchInput = document.querySelector('.md-search__input');
        
        if (searchInput) {
            // إضافة اختصار البحث
            document.addEventListener('keydown', function(e) {
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                    e.preventDefault();
                    searchInput.focus();
                }
            });
            
            // إضافة نصائح البحث
            searchInput.setAttribute('placeholder', 'البحث... (Ctrl+K)');
            
            // تحسين نتائج البحث
            searchInput.addEventListener('input', function() {
                const query = this.value.toLowerCase();
                
                if (query.length > 2) {
                    highlightSearchResults(query);
                }
            });
        }
    }
    
    /**
     * إبراز نتائج البحث في الصفحة
     */
    function highlightSearchResults(query) {
        // إزالة الإبراز السابق
        removeHighlights();
        
        // البحث وإبراز النتائج
        const walker = document.createTreeWalker(
            document.querySelector('.md-content'),
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        const textNodes = [];
        let node;
        
        while (node = walker.nextNode()) {
            if (node.textContent.toLowerCase().includes(query)) {
                textNodes.push(node);
            }
        }
        
        textNodes.forEach(textNode => {
            const parent = textNode.parentNode;
            const text = textNode.textContent;
            const regex = new RegExp(`(${query})`, 'gi');
            const highlightedText = text.replace(regex, '<mark class="search-highlight">$1</mark>');
            
            const wrapper = document.createElement('span');
            wrapper.innerHTML = highlightedText;
            parent.replaceChild(wrapper, textNode);
        });
    }
    
    /**
     * إزالة إبراز البحث
     */
    function removeHighlights() {
        const highlights = document.querySelectorAll('.search-highlight');
        highlights.forEach(highlight => {
            const parent = highlight.parentNode;
            parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
            parent.normalize();
        });
    }
    
    /**
     * تهيئة اختصارات لوحة المفاتيح
     */
    function initKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // التنقل بين الصفحات
            if (e.altKey) {
                switch(e.key) {
                    case 'ArrowLeft':
                        e.preventDefault();
                        const prevLink = document.querySelector('.md-footer__link--prev');
                        if (prevLink) prevLink.click();
                        break;
                        
                    case 'ArrowRight':
                        e.preventDefault();
                        const nextLink = document.querySelector('.md-footer__link--next');
                        if (nextLink) nextLink.click();
                        break;
                }
            }
            
            // العودة للأعلى
            if (e.key === 'Home' && e.ctrlKey) {
                e.preventDefault();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
            
            // الذهاب للأسفل
            if (e.key === 'End' && e.ctrlKey) {
                e.preventDefault();
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            }
        });
        
        // إضافة مساعد الاختصارات
        addKeyboardShortcutsHelper();
    }
    
    /**
     * إضافة مساعد اختصارات لوحة المفاتيح
     */
    function addKeyboardShortcutsHelper() {
        const helper = document.createElement('div');
        helper.className = 'keyboard-shortcuts-helper';
        helper.innerHTML = `
            <div class="shortcuts-content">
                <h3>⌨️ اختصارات لوحة المفاتيح</h3>
                <div class="shortcut-item">
                    <kbd>Ctrl</kbd> + <kbd>K</kbd> - البحث
                </div>
                <div class="shortcut-item">
                    <kbd>Alt</kbd> + <kbd>←</kbd> - الصفحة السابقة
                </div>
                <div class="shortcut-item">
                    <kbd>Alt</kbd> + <kbd>→</kbd> - الصفحة التالية
                </div>
                <div class="shortcut-item">
                    <kbd>Ctrl</kbd> + <kbd>Home</kbd> - أعلى الصفحة
                </div>
                <div class="shortcut-item">
                    <kbd>Ctrl</kbd> + <kbd>End</kbd> - أسفل الصفحة
                </div>
                <div class="shortcut-item">
                    <kbd>?</kbd> - إظهار/إخفاء هذه المساعدة
                </div>
            </div>
        `;
        
        // إضافة الأنماط
        const style = document.createElement('style');
        style.textContent = `
            .keyboard-shortcuts-helper {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                padding: 20px;
                z-index: 10000;
                display: none;
                max-width: 400px;
                width: 90%;
            }
            
            [data-md-color-scheme="slate"] .keyboard-shortcuts-helper {
                background: #1e1e1e;
                color: white;
            }
            
            .shortcuts-content h3 {
                margin-top: 0;
                text-align: center;
                color: #1976d2;
            }
            
            .shortcut-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 0;
                border-bottom: 1px solid #eee;
            }
            
            .shortcut-item:last-child {
                border-bottom: none;
            }
            
            kbd {
                background: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 0.9em;
                font-family: monospace;
            }
            
            [data-md-color-scheme="slate"] kbd {
                background: #333;
                border-color: #555;
                color: white;
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(helper);
        
        // إظهار/إخفاء المساعدة بالضغط على ?
        document.addEventListener('keydown', function(e) {
            if (e.key === '?' && !e.ctrlKey && !e.altKey && !e.shiftKey) {
                e.preventDefault();
                helper.style.display = helper.style.display === 'block' ? 'none' : 'block';
            }
            
            if (e.key === 'Escape') {
                helper.style.display = 'none';
            }
        });
        
        // إخفاء عند النقر خارج المساعدة
        helper.addEventListener('click', function(e) {
            if (e.target === helper) {
                helper.style.display = 'none';
            }
        });
    }
    
    /**
     * تحسين عرض الجداول
     */
    function enhanceTables() {
        const tables = document.querySelectorAll('.md-typeset table');
        
        tables.forEach(table => {
            // إضافة wrapper للتمرير الأفقي
            const wrapper = document.createElement('div');
            wrapper.className = 'table-wrapper';
            wrapper.style.cssText = `
                overflow-x: auto;
                margin: 1em 0;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            `;
            
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
            
            // إضافة فرز للجداول
            addTableSorting(table);
        });
    }
    
    /**
     * إضافة إمكانية فرز الجداول
     */
    function addTableSorting(table) {
        const headers = table.querySelectorAll('th');
        
        headers.forEach((header, index) => {
            header.style.cursor = 'pointer';
            header.style.userSelect = 'none';
            header.title = 'اضغط للفرز';
            
            header.addEventListener('click', function() {
                sortTable(table, index);
            });
        });
    }
    
    /**
     * فرز الجدول حسب العمود
     */
    function sortTable(table, columnIndex) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        const isAscending = table.dataset.sortDirection !== 'asc';
        table.dataset.sortDirection = isAscending ? 'asc' : 'desc';
        
        rows.sort((a, b) => {
            const aText = a.cells[columnIndex].textContent.trim();
            const bText = b.cells[columnIndex].textContent.trim();
            
            // محاولة الفرز كأرقام أولاً
            const aNum = parseFloat(aText);
            const bNum = parseFloat(bText);
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return isAscending ? aNum - bNum : bNum - aNum;
            }
            
            // الفرز كنص
            return isAscending ? 
                aText.localeCompare(bText, 'ar') : 
                bText.localeCompare(aText, 'ar');
        });
        
        // إعادة ترتيب الصفوف
        rows.forEach(row => tbody.appendChild(row));
        
        // تحديث مؤشر الفرز
        updateSortIndicator(table, columnIndex, isAscending);
    }
    
    /**
     * تحديث مؤشر الفرز في رأس الجدول
     */
    function updateSortIndicator(table, columnIndex, isAscending) {
        // إزالة المؤشرات السابقة
        table.querySelectorAll('th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });
        
        // إضافة المؤشر الجديد
        const header = table.querySelectorAll('th')[columnIndex];
        header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
        
        // إضافة الأنماط إذا لم تكن موجودة
        if (!document.querySelector('#table-sort-styles')) {
            const style = document.createElement('style');
            style.id = 'table-sort-styles';
            style.textContent = `
                th.sort-asc::after { content: ' ↑'; }
                th.sort-desc::after { content: ' ↓'; }
            `;
            document.head.appendChild(style);
        }
    }
    
    /**
     * إضافة أزرار نسخ مخصصة للكود
     */
    function initCustomCopyButtons() {
        const codeBlocks = document.querySelectorAll('pre code');
        
        codeBlocks.forEach(codeBlock => {
            const pre = codeBlock.parentElement;
            
            // إنشاء زر النسخ
            const copyButton = document.createElement('button');
            copyButton.className = 'custom-copy-button';
            copyButton.innerHTML = '📋 نسخ';
            copyButton.title = 'نسخ الكود';
            
            // إضافة الأنماط
            copyButton.style.cssText = `
                position: absolute;
                top: 8px;
                right: 8px;
                background: rgba(255,255,255,0.9);
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
                cursor: pointer;
                transition: all 0.2s ease;
            `;
            
            // تحديد موضع relative للـ pre
            pre.style.position = 'relative';
            
            // إضافة الزر
            pre.appendChild(copyButton);
            
            // وظيفة النسخ
            copyButton.addEventListener('click', function() {
                navigator.clipboard.writeText(codeBlock.textContent).then(() => {
                    copyButton.innerHTML = '✅ تم النسخ';
                    copyButton.style.background = '#4caf50';
                    copyButton.style.color = 'white';
                    
                    setTimeout(() => {
                        copyButton.innerHTML = '📋 نسخ';
                        copyButton.style.background = 'rgba(255,255,255,0.9)';
                        copyButton.style.color = 'inherit';
                    }, 2000);
                });
            });
        });
    }
    
    /**
     * تحسين عرض الصور
     */
    function enhanceImages() {
        const images = document.querySelectorAll('.md-typeset img');
        
        images.forEach(img => {
            // إضافة تأثير التكبير عند النقر
            img.style.cursor = 'pointer';
            img.addEventListener('click', function() {
                openImageModal(this);
            });
            
            // إضافة lazy loading
            img.loading = 'lazy';
            
            // إضافة تأثير التحميل
            img.addEventListener('load', function() {
                this.style.opacity = '1';
                this.style.transform = 'scale(1)';
            });
            
            img.style.cssText += `
                opacity: 0;
                transform: scale(0.95);
                transition: all 0.3s ease;
            `;
        });
    }
    
    /**
     * فتح نافذة منبثقة للصورة
     */
    function openImageModal(img) {
        const modal = document.createElement('div');
        modal.className = 'image-modal';
        modal.innerHTML = `
            <div class="image-modal-content">
                <span class="image-modal-close">&times;</span>
                <img src="${img.src}" alt="${img.alt}">
                <div class="image-modal-caption">${img.alt || 'صورة'}</div>
            </div>
        `;
        
        // إضافة الأنماط
        const style = document.createElement('style');
        style.textContent = `
            .image-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.9);
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
                animation: fadeIn 0.3s ease;
            }
            
            .image-modal-content {
                position: relative;
                max-width: 90%;
                max-height: 90%;
                text-align: center;
            }
            
            .image-modal img {
                max-width: 100%;
                max-height: 80vh;
                border-radius: 8px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.5);
            }
            
            .image-modal-close {
                position: absolute;
                top: -40px;
                right: 0;
                color: white;
                font-size: 30px;
                cursor: pointer;
                z-index: 10001;
            }
            
            .image-modal-caption {
                color: white;
                margin-top: 16px;
                font-size: 16px;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(modal);
        
        // إغلاق النافذة
        modal.addEventListener('click', function(e) {
            if (e.target === modal || e.target.classList.contains('image-modal-close')) {
                document.body.removeChild(modal);
                document.head.removeChild(style);
            }
        });
        
        // إغلاق بالضغط على Escape
        document.addEventListener('keydown', function escapeHandler(e) {
            if (e.key === 'Escape') {
                document.body.removeChild(modal);
                document.head.removeChild(style);
                document.removeEventListener('keydown', escapeHandler);
            }
        });
    }
    
    /**
     * إضافة إحصائيات القراءة
     */
    function initReadingStats() {
        const content = document.querySelector('.md-content');
        if (!content) return;
        
        // حساب وقت القراءة المقدر
        const text = content.textContent;
        const wordsPerMinute = 200; // متوسط سرعة القراءة
        const words = text.trim().split(/\s+/).length;
        const readingTime = Math.ceil(words / wordsPerMinute);
        
        // إنشاء عنصر الإحصائيات
        const stats = document.createElement('div');
        stats.className = 'reading-stats';
        stats.innerHTML = `
            <div class="stats-item">
                <span class="stats-icon">📖</span>
                <span class="stats-text">وقت القراءة: ${readingTime} دقيقة</span>
            </div>
            <div class="stats-item">
                <span class="stats-icon">📝</span>
                <span class="stats-text">عدد الكلمات: ${words.toLocaleString('ar')}</span>
            </div>
        `;
        
        // إضافة الأنماط
        const style = document.createElement('style');
        style.textContent = `
            .reading-stats {
                background: rgba(25, 118, 210, 0.1);
                border: 1px solid rgba(25, 118, 210, 0.2);
                border-radius: 8px;
                padding: 12px;
                margin: 16px 0;
                display: flex;
                gap: 16px;
                flex-wrap: wrap;
            }
            
            .stats-item {
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 14px;
                color: #666;
            }
            
            [data-md-color-scheme="slate"] .stats-item {
                color: #ccc;
            }
            
            .stats-icon {
                font-size: 16px;
            }
        `;
        
        document.head.appendChild(style);
        
        // إدراج الإحصائيات في بداية المحتوى
        const firstHeading = content.querySelector('h1, h2');
        if (firstHeading && firstHeading.nextSibling) {
            firstHeading.parentNode.insertBefore(stats, firstHeading.nextSibling);
        }
    }
    
    // ===================================
    // 🎉 رسالة ترحيب في وحدة التحكم
    // ===================================
    
    console.log(`
    🛠️ Euro Tools Code Manager Documentation
    ═══════════════════════════════════════
    
    مرحباً بك في توثيق نظام إدارة أكواد الأدوات الصناعية!
    
    💡 نصائح سريعة:
    • اضغط ? لعرض اختصارات لوحة المفاتيح
    • استخدم Ctrl+K للبحث السريع
    • اضغط على الصور لتكبيرها
    • اضغط على رؤوس الجداول للفرز
    
    🔗 روابط مفيدة:
    • GitHub: https://github.com/your-username/euro-tools-code-manager
    • الدعم: support@eurotools.com
    
    📊 إحصائيات هذه الصفحة متاحة أعلى المحتوى
    `);
});

// ===================================
// 🌐 دوال مساعدة عامة
// ===================================

/**
 * تحديث عداد الزوار (إذا كان متاحاً)
 */
function updateVisitorCount() {
    // يمكن ربطه بخدمة إحصائيات خارجية
    const count = localStorage.getItem('euro-docs-visits') || 0;
    localStorage.setItem('euro-docs-visits', parseInt(count) + 1);
}

/**
 * إرسال تقييم للصفحة
 */
function submitPageFeedback(rating, comment) {
    // يمكن ربطه بنظام تقييم خارجي
    console.log('تقييم الصفحة:', { rating, comment, page: window.location.pathname });
}

/**
 * مشاركة الصفحة
 */
function sharePage() {
    if (navigator.share) {
        navigator.share({
            title: document.title,
            url: window.location.href
        });
    } else {
        // نسخ الرابط للحافظة
        navigator.clipboard.writeText(window.location.href).then(() => {
            alert('تم نسخ رابط الصفحة!');
        });
    }
}

// تحديث عداد الزوار عند تحميل الصفحة
updateVisitorCount();