// 教程页面JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeTutorial();
    addTutorialStyles();
});

function initializeTutorial() {
    // 设置标签页切换
    setupTabs();
    
    // 设置FAQ折叠功能
    setupFAQ();
    
    // 添加滚动动画
    setupScrollAnimations();
}

function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // 移除所有active类
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // 添加active类到当前按钮和对应内容
            this.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
            
            // 添加切换动画
            const activeContent = document.getElementById(targetTab);
            activeContent.style.opacity = '0';
            activeContent.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                activeContent.style.transition = 'all 0.3s ease';
                activeContent.style.opacity = '1';
                activeContent.style.transform = 'translateY(0)';
            }, 50);
        });
    });
}

function setupFAQ() {
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        const answer = item.querySelector('.faq-answer');
        const icon = question.querySelector('i');
        
        question.addEventListener('click', function() {
            const isOpen = item.classList.contains('open');
            
            // 关闭所有其他FAQ项目
            faqItems.forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.classList.remove('open');
                    const otherAnswer = otherItem.querySelector('.faq-answer');
                    const otherIcon = otherItem.querySelector('.faq-question i');
                    otherAnswer.style.maxHeight = '0';
                    otherIcon.style.transform = 'rotate(0deg)';
                }
            });
            
            // 切换当前FAQ项目
            if (isOpen) {
                item.classList.remove('open');
                answer.style.maxHeight = '0';
                icon.style.transform = 'rotate(0deg)';
            } else {
                item.classList.add('open');
                answer.style.maxHeight = answer.scrollHeight + 'px';
                icon.style.transform = 'rotate(180deg)';
            }
        });
    });
}

function setupScrollAnimations() {
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
    
    // 观察需要动画的元素
    const animateElements = document.querySelectorAll(
        '.quick-step, .tutorial-card, .process-step, .knowledge-card, .faq-item'
    );
    
    animateElements.forEach(el => {
        observer.observe(el);
    });
}

function addTutorialStyles() {
    const style = document.createElement('style');
    style.textContent = `
        /* 教程页面特定样式 */
        .tutorial-hero {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 6rem 0 4rem;
            text-align: center;
        }
        
        .tutorial-title {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .tutorial-subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .tutorial-content {
            background: white;
            padding: 4rem 0;
        }
        
        .tutorial-section {
            margin-bottom: 4rem;
        }
        
        .tutorial-section-title {
            display: flex;
            align-items: center;
            font-size: 2rem;
            color: #333;
            margin-bottom: 2rem;
        }
        
        .tutorial-section-title i {
            margin-right: 1rem;
            color: #667eea;
        }
        
        /* 快速开始步骤 */
        .quick-steps {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
        }
        
        .quick-step {
            display: flex;
            align-items: flex-start;
            background: #f8f9ff;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
            opacity: 0;
            transform: translateY(30px);
        }
        
        .quick-step.animate-in {
            opacity: 1;
            transform: translateY(0);
        }
        
        .quick-step:hover {
            transform: translateY(-5px);
        }
        
        .step-number {
            background: #667eea;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 1rem;
            flex-shrink: 0;
        }
        
        .step-content h3 {
            margin-bottom: 0.5rem;
            color: #333;
        }
        
        .step-content p {
            color: #666;
            line-height: 1.6;
        }
        
        /* 标签页样式 */
        .tutorial-tabs {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            border-bottom: 2px solid #e0e0e0;
            flex-wrap: wrap;
        }
        
        .tab-button {
            background: none;
            border: none;
            padding: 1rem 2rem;
            cursor: pointer;
            font-size: 1.1rem;
            color: #666;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
        }
        
        .tab-button:hover {
            color: #667eea;
        }
        
        .tab-button.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        
        .tab-content {
            display: none;
            padding: 2rem 0;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .tab-content h3 {
            font-size: 1.5rem;
            margin-bottom: 2rem;
            color: #333;
        }
        
        /* 教程卡片 */
        .tutorial-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }
        
        .tutorial-card {
            background: #f8f9ff;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
            opacity: 0;
            transform: translateY(30px);
        }
        
        .tutorial-card.animate-in {
            opacity: 1;
            transform: translateY(0);
        }
        
        .tutorial-card:hover {
            transform: translateY(-5px);
        }
        
        .card-icon {
            background: #667eea;
            color: white;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .tutorial-card h4 {
            margin-bottom: 1rem;
            color: #333;
            font-size: 1.2rem;
        }
        
        .tutorial-card p {
            color: #666;
            line-height: 1.6;
            margin-bottom: 1rem;
        }
        
        .tip-box {
            background: #e8f4fd;
            border-left: 4px solid #667eea;
            padding: 1rem;
            border-radius: 5px;
            font-size: 0.9rem;
        }
        
        .do-dont {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .do, .dont {
            padding: 0.5rem;
            border-radius: 5px;
            font-size: 0.9rem;
        }
        
        .do {
            background: #e8f5e8;
            color: #2e7d32;
        }
        
        .dont {
            background: #ffebee;
            color: #d32f2f;
        }
        
        .format-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
        }
        
        .format-list span {
            background: #667eea;
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.8rem;
        }
        
        .upload-methods {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .method {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: #f0f0f0;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
        }
        
        /* 流程步骤 */
        .process-flow {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1rem;
        }
        
        .process-step {
            background: #f8f9ff;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            max-width: 400px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.6s ease;
        }
        
        .process-step.animate-in {
            opacity: 1;
            transform: translateY(0);
        }
        
        .process-icon {
            background: #667eea;
            color: white;
            width: 80px;
            height: 80px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            margin: 0 auto 1rem;
        }
        
        .process-step h4 {
            margin-bottom: 1rem;
            color: #333;
            font-size: 1.3rem;
        }
        
        .process-arrow {
            color: #667eea;
            font-size: 1.5rem;
        }
        
        .feature-list {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            margin-top: 1rem;
        }
        
        .feature {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #4CAF50;
        }
        
        .controls-guide {
            margin-top: 1rem;
        }
        
        .control {
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
        }
        
        .download-formats {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            margin-top: 1rem;
            font-size: 0.9rem;
        }
        
        /* FAQ样式 */
        .faq-list {
            max-width: 800px;
        }
        
        .faq-item {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            margin-bottom: 1rem;
            overflow: hidden;
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s ease;
        }
        
        .faq-item.animate-in {
            opacity: 1;
            transform: translateY(0);
        }
        
        .faq-question {
            padding: 1.5rem;
            background: #f8f9ff;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background 0.3s ease;
        }
        
        .faq-question:hover {
            background: #f0f2ff;
        }
        
        .faq-question h4 {
            margin: 0;
            color: #333;
            font-size: 1.1rem;
        }
        
        .faq-question i {
            color: #667eea;
            transition: transform 0.3s ease;
        }
        
        .faq-answer {
            padding: 0 1.5rem;
            max-height: 0;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .faq-answer p {
            padding: 1rem 0;
            margin: 0;
            color: #666;
        }
        
        .faq-answer ul {
            padding-left: 2rem;
            color: #666;
        }
        
        .faq-answer li {
            margin-bottom: 0.5rem;
        }
        
        /* AI知识卡片 */
        .ai-knowledge {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2rem;
        }
        
        .knowledge-card {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
            transition: transform 0.3s ease;
            opacity: 0;
            transform: translateY(30px);
        }
        
        .knowledge-card.animate-in {
            opacity: 1;
            transform: translateY(0);
        }
        
        .knowledge-card:hover {
            transform: translateY(-10px);
        }
        
        .knowledge-icon {
            background: rgba(255, 255, 255, 0.2);
            width: 80px;
            height: 80px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            margin: 0 auto 1rem;
        }
        
        .knowledge-card h3 {
            margin-bottom: 1rem;
            font-size: 1.3rem;
        }
        
        .knowledge-card p {
            line-height: 1.6;
            opacity: 0.9;
        }
        
        /* 响应式设计 */
        @media (max-width: 768px) {
            .tutorial-title {
                font-size: 2rem;
            }
            
            .quick-steps {
                grid-template-columns: 1fr;
            }
            
            .tutorial-grid {
                grid-template-columns: 1fr;
            }
            
            .tutorial-tabs {
                flex-direction: column;
            }
            
            .tab-button {
                padding: 0.8rem 1rem;
            }
            
            .process-flow {
                padding: 0 1rem;
            }
            
            .ai-knowledge {
                grid-template-columns: 1fr;
            }
            
            .do-dont {
                flex-direction: column;
            }
            
            .upload-methods {
                flex-direction: column;
            }
        }
        
        /* 动画延迟 */
        .quick-step:nth-child(1) { transition-delay: 0.1s; }
        .quick-step:nth-child(2) { transition-delay: 0.2s; }
        .quick-step:nth-child(3) { transition-delay: 0.3s; }
        .quick-step:nth-child(4) { transition-delay: 0.4s; }
        
        .tutorial-card:nth-child(1) { transition-delay: 0.1s; }
        .tutorial-card:nth-child(2) { transition-delay: 0.2s; }
        .tutorial-card:nth-child(3) { transition-delay: 0.3s; }
        
        .knowledge-card:nth-child(1) { transition-delay: 0.1s; }
        .knowledge-card:nth-child(2) { transition-delay: 0.2s; }
        .knowledge-card:nth-child(3) { transition-delay: 0.3s; }
        .knowledge-card:nth-child(4) { transition-delay: 0.4s; }
        
        .faq-item:nth-child(1) { transition-delay: 0.1s; }
        .faq-item:nth-child(2) { transition-delay: 0.2s; }
        .faq-item:nth-child(3) { transition-delay: 0.3s; }
        .faq-item:nth-child(4) { transition-delay: 0.4s; }
    `;
    
    document.head.appendChild(style);
}