// 统一导航栏JavaScript功能
document.addEventListener('DOMContentLoaded', function() {
    // 移动端导航切换
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            this.classList.toggle('active');
        });
        
        // 点击菜单项后关闭移动端菜单
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            });
        });
    }
    
    // 用户下拉菜单
    const dropdown = document.querySelector('.nav-dropdown');
    if (dropdown) {
        const dropdownToggle = dropdown.querySelector('.nav-link');
        const dropdownMenu = dropdown.querySelector('.dropdown-menu');
        
        dropdownToggle.addEventListener('click', function(e) {
            e.preventDefault();
            dropdown.classList.toggle('active');
        });
        
        // 点击外部关闭下拉菜单
        document.addEventListener('click', function(e) {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('active');
            }
        });
    }
    
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