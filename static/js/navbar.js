// 统一导航栏JavaScript功能
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 导航栏JS加载完成');
    console.log('📱 当前页面:', window.location.pathname);
    console.log('📐 窗口尺寸:', window.innerWidth, 'x', window.innerHeight);
    console.log('📱 是否竖屏:', window.innerHeight > window.innerWidth);
    
    // 支持多个 .navbar，逐个绑定以避免选择到错误实例
    const navbars = document.querySelectorAll('.navbar');
    console.log('🔍 找到', navbars.length, '个navbar实例');
    if (!navbars || navbars.length === 0) {
        console.error('❌ 未找到 .navbar 实例');
    }

    navbars.forEach(navbar => {
        const navToggleLocal = navbar.querySelector('.nav-toggle');
        const navMenuLocal = navbar.querySelector('.nav-menu');

        if (!navToggleLocal || !navMenuLocal) return;

        // Ensure high z-index so nav is above page content
        navMenuLocal.style.zIndex = '10001';
        navToggleLocal.style.zIndex = '10002';

        navToggleLocal.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            const wasActive = navMenuLocal.classList.contains('active');
            console.log('🎯 Toggle clicked, wasActive:', wasActive);
            navMenuLocal.classList.toggle('active');
            this.classList.toggle('active');
            
            // 只在移动端使用transform控制菜单显示/隐藏
            if (window.innerWidth <= 768) {
                if (navMenuLocal.classList.contains('active')) {
                    console.log('➕ 菜单打开 (移动端)');
                    navMenuLocal.style.transform = 'translateX(0)';
                } else {
                    console.log('➖ 菜单关闭 (移动端)');
                    navMenuLocal.style.transform = 'translateX(-100%)';
                }
            }
        });

        // 菜单内部链接点击关闭菜单
        const navLinksLocal = navMenuLocal.querySelectorAll('.nav-link:not(.nav-dropdown > .nav-link)');
        console.log(`🔗 找到 ${navLinksLocal.length} 个导航链接`);
        navLinksLocal.forEach(link => {
            if (!link.closest('.nav-dropdown')) {
                link.addEventListener('click', (e) => {
                    console.log('🖱️ nav-link 被点击:', link.href);
                    // 只在移动端关闭菜单
                    if (window.innerWidth <= 768) {
                        navMenuLocal.classList.remove('active');
                        navToggleLocal.classList.remove('active');
                        navMenuLocal.style.transform = 'translateX(-100%)';
                        console.log('✅ 菜单已关闭 (移动端)，允许默认导航');
                    }
                });
            }
        });

        // 下拉菜单本地处理
        const dropdownLocal = navMenuLocal.querySelector('.nav-dropdown');
        if (dropdownLocal) {
            const dropdownToggle = dropdownLocal.querySelector('.nav-link');
            const dropdownMenu = dropdownLocal.querySelector('.dropdown-menu');
            dropdownToggle.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                dropdownLocal.classList.toggle('active');
            });

            const dropdownLinks = dropdownMenu ? dropdownMenu.querySelectorAll('a') : [];
            dropdownLinks.forEach(link => {
                link.addEventListener('click', () => {
                    // 只在移动端关闭菜单
                    if (window.innerWidth <= 768) {
                        navMenuLocal.classList.remove('active');
                        navToggleLocal.classList.remove('active');
                        navMenuLocal.style.transform = 'translateX(-100%)';
                    }
                });
            });

            document.addEventListener('click', function (e) {
                if (!dropdownLocal.contains(e.target)) {
                    dropdownLocal.classList.remove('active');
                }
            });
        }

        // 页面加载时确保菜单处于关闭状态（仅在移动端）
        // 只在窗口宽度 <= 768px 时强制设置transform和移除active类
        if (window.innerWidth <= 768) {
            navMenuLocal.classList.remove('active');
            navToggleLocal.classList.remove('active');
            navMenuLocal.style.transform = 'translateX(-100%)';
            console.log('🔧 页面加载：强制关闭菜单 (移动端), transform设为translateX(-100%)');
        } else {
            // 桌面端：移除可能存在的transform样式
            navMenuLocal.style.transform = '';
            console.log('🖥️ 页面加载：桌面端，清除transform样式');
        }
    });
    
    // 导航栏滚动效果
    let lastScrollTop = 0;
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const header = document.querySelector('.header');
        
        if (header) {
            if (scrollTop > lastScrollTop && scrollTop > 100) {
                // 向下滚动，隐藏导航栏
                header.style.transform = 'translateY(-100%)';
            } else {
                // 向上滚动，显示导航栏
                header.style.transform = 'translateY(0)';
            }
            
            // 添加滚动阴影效果
            if (scrollTop > 0) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        }
        
        lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
    }, false);
    
    // 自动高亮当前页面的导航链接
    function setActiveNavLink() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            const linkPath = new URL(link.href).pathname;
            
            // 移除所有active类
            link.classList.remove('active');
            
            // 精确匹配或首页特殊处理
            if (linkPath === currentPath || 
                (currentPath === '/' && linkPath === '/') ||
                (currentPath.startsWith('/create') && linkPath.includes('create')) ||
                (currentPath.startsWith('/gallery') && linkPath.includes('gallery')) ||
                (currentPath.startsWith('/tutorial') && linkPath.includes('tutorial')) ||
                (currentPath.startsWith('/video') && linkPath.includes('video')) ||
                (currentPath.startsWith('/auth') && linkPath.includes('auth'))) {
                link.classList.add('active');
            }
        });
    }
    
    // 页面加载时设置激活状态
    setActiveNavLink();
});