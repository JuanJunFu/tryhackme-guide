// 網路攻擊鏈教學網站 - 主要JavaScript文件

document.addEventListener('DOMContentLoaded', function() {
    console.log('網路攻擊鏈教學網站已載入');
    
    // 初始化所有功能
    initializeNavigation();
    initializeStageNavigation();
    initializeSmoothScrolling();
    initializeAnimations();
});

// 導航功能
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const offsetTop = targetElement.offsetTop - 80; // 考慮固定導航欄高度
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// 階段導航功能
function initializeStageNavigation() {
    const stageButtons = document.querySelectorAll('.stage-nav-btn');
    const stageCards = document.querySelectorAll('.stage-card');
    
    stageButtons.forEach(button => {
        button.addEventListener('click', function() {
            const stageNumber = this.getAttribute('data-stage');
            
            // 移除所有按鈕的active狀態
            stageButtons.forEach(btn => btn.classList.remove('active'));
            // 添加當前按鈕的active狀態
            this.classList.add('active');
            
            // 隱藏所有階段卡片，並重設動畫屬性
            stageCards.forEach(card => {
                card.classList.remove('active');
                card.style.transition = '';
                card.style.opacity = '';
                card.style.transform = '';
            });
            // 顯示選中的階段卡片
            const targetStage = document.getElementById(`stage-${stageNumber}`);
            if (targetStage) {
                targetStage.classList.add('active');
                // 添加淡入動畫
                targetStage.style.opacity = '0';
                targetStage.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    targetStage.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                    targetStage.style.opacity = '1';
                    targetStage.style.transform = 'translateY(0)';
                }, 50);
            }
        });
    });
}

// 平滑滾動功能
function initializeSmoothScrolling() {
    // 全局滾動到指定區塊的函數
    window.scrollToSection = function(sectionId) {
        const targetElement = document.getElementById(sectionId);
        if (targetElement) {
            const offsetTop = targetElement.offsetTop - 80;
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }
    };
}

// 動畫效果
function initializeAnimations() {
    // 觀察者API用於元素進入視窗時的動畫
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // 觀察需要動畫的元素
    const animateElements = document.querySelectorAll('.condition-card, .defense-category, .stage-card');
    animateElements.forEach(el => {
        observer.observe(el);
    });
    
    // 工具項目懸停效果
    const toolItems = document.querySelectorAll('.tool-item');
    toolItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });
    
    // 條件卡片懸停效果增強
    const conditionCards = document.querySelectorAll('.condition-card');
    conditionCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(-5px) scale(1)';
        });
    });
}

// 導航欄滾動效果
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 100) {
        navbar.style.background = 'linear-gradient(135deg, rgba(44, 62, 80, 0.95), rgba(52, 152, 219, 0.95))';
        navbar.style.backdropFilter = 'blur(10px)';
    } else {
        navbar.style.background = 'linear-gradient(135deg, #2c3e50, #3498db)';
        navbar.style.backdropFilter = 'none';
    }
});

// 鍵盤快捷鍵
document.addEventListener('keydown', function(e) {
    // 數字鍵1-7切換階段
    if (e.key >= '1' && e.key <= '7') {
        const stageButton = document.querySelector(`[data-stage="${e.key}"]`);
        if (stageButton) {
            stageButton.click();
        }
    }
    
    // ESC鍵回到首頁
    if (e.key === 'Escape') {
        scrollToSection('home');
    }
});

// 工具提示功能
function createTooltip(element, text) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
        position: absolute;
        background: #2c3e50;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 0.8rem;
        white-space: nowrap;
        z-index: 1000;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.3s ease;
        transform: translateX(-50%);
    `;
    
    element.addEventListener('mouseenter', function(e) {
        document.body.appendChild(tooltip);
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + rect.width / 2 + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
        tooltip.style.opacity = '1';
    });
    
    element.addEventListener('mouseleave', function() {
        if (tooltip.parentNode) {
            tooltip.parentNode.removeChild(tooltip);
        }
    });
}

// 為階段按鈕添加工具提示
document.querySelectorAll('.stage-nav-btn').forEach(btn => {
    const stageNumber = btn.getAttribute('data-stage');
    const stageNames = {
        '1': '目標情資偵蒐階段',
        '2': '準備武器階段',
        '3': '交付武器階段',
        '4': '利用漏洞階段（核心條件應用）',
        '5': '安裝惡意程式階段',
        '6': '命令與控制階段',
        '7': '達成目標階段'
    };
    
    if (stageNames[stageNumber]) {
        createTooltip(btn, stageNames[stageNumber]);
    }
});

// 搜索功能
function initializeSearch() {
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = '搜索工具或內容...';
    searchInput.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 5px;
        background: white;
        z-index: 999;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.3s ease;
        width: 250px;
    `;
    
    document.body.appendChild(searchInput);
    
    // Ctrl+F 顯示搜索框
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'f') {
            e.preventDefault();
            searchInput.style.opacity = '1';
            searchInput.style.pointerEvents = 'auto';
            searchInput.focus();
        }
        
        if (e.key === 'Escape') {
            searchInput.style.opacity = '0';
            searchInput.style.pointerEvents = 'none';
            searchInput.value = '';
            clearHighlights();
        }
    });
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        clearHighlights();
        
        if (searchTerm.length > 2) {
            highlightText(searchTerm);
        }
    });
}

// 文字高亮功能
function highlightText(searchTerm) {
    const textElements = document.querySelectorAll('p, li, h3, h4, h5, code, span');
    
    textElements.forEach(element => {
        if (element.children.length === 0) { // 只處理葉子節點
            const text = element.textContent;
            if (text.toLowerCase().includes(searchTerm)) {
                const regex = new RegExp(`(${searchTerm})`, 'gi');
                const highlightedText = text.replace(regex, '<mark style="background-color: #f39c12; color: white; padding: 2px 4px; border-radius: 2px;">$1</mark>');
                element.innerHTML = highlightedText;
            }
        }
    });
}

function clearHighlights() {
    const marks = document.querySelectorAll('mark');
    marks.forEach(mark => {
        const parent = mark.parentNode;
        parent.replaceChild(document.createTextNode(mark.textContent), mark);
        parent.normalize();
    });
}

// 初始化搜索功能
setTimeout(initializeSearch, 1000);

// 打印功能
function initializePrint() {
    const printButton = document.createElement('button');
    printButton.innerHTML = '<i class="fas fa-print"></i> 列印';
    printButton.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #3498db;
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 50px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
        z-index: 999;
        transition: all 0.3s ease;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 8px;
    `;
    
    printButton.addEventListener('click', function() {
        window.print();
    });
    
    printButton.addEventListener('mouseenter', function() {
        this.style.transform = 'scale(1.05)';
        this.style.boxShadow = '0 6px 16px rgba(52, 152, 219, 0.4)';
    });
    
    printButton.addEventListener('mouseleave', function() {
        this.style.transform = 'scale(1)';
        this.style.boxShadow = '0 4px 12px rgba(52, 152, 219, 0.3)';
    });
    
    document.body.appendChild(printButton);
}

// 初始化打印功能
setTimeout(initializePrint, 1000);

// 回到頂部按鈕
function initializeBackToTop() {
    const backToTopButton = document.createElement('button');
    backToTopButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTopButton.style.cssText = `
        position: fixed;
        bottom: 80px;
        right: 20px;
        background: #2c3e50;
        color: white;
        border: none;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(44, 62, 80, 0.3);
        z-index: 999;
        transition: all 0.3s ease;
        opacity: 0;
        pointer-events: none;
        font-size: 1.2rem;
    `;
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 500) {
            backToTopButton.style.opacity = '1';
            backToTopButton.style.pointerEvents = 'auto';
        } else {
            backToTopButton.style.opacity = '0';
            backToTopButton.style.pointerEvents = 'none';
        }
    });
    
    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    document.body.appendChild(backToTopButton);
}

// 初始化回到頂部功能
setTimeout(initializeBackToTop, 1000);

console.log('網路攻擊鏈教學網站JavaScript功能已全部載入完成');