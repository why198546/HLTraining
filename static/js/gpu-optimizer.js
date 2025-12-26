/**
 * GPU加速优化器
 * 动态管理will-change，避免内存浪费
 */

(function() {
    'use strict';

    // 配置
    const CONFIG = {
        scrollDebounce: 150,  // 滚动停止后多久移除will-change
        enableLogging: false   // 是否启用日志
    };

    /**
     * 滚动容器优化器
     * 在滚动时添加.scrolling类，停止后移除
     */
    class ScrollOptimizer {
        constructor() {
            this.scrollTimers = new WeakMap();
            this.init();
        }

        init() {
            // 监听所有可滚动容器
            const scrollableSelectors = [
                '.scroll-container',
                '.overflow-auto',
                '.overflow-y-auto',
                '.chat-messages',
                '.message-list',
                '.search-results'
            ];

            scrollableSelectors.forEach(selector => {
                document.querySelectorAll(selector).forEach(el => {
                    this.observeScroll(el);
                });
            });

            // 也监听window滚动
            this.observeScroll(window);

            if (CONFIG.enableLogging) {
                console.log('[GPU Optimizer] ScrollOptimizer initialized');
            }
        }

        observeScroll(element) {
            let scrollTimer;

            const handleScroll = () => {
                // 添加scrolling类
                if (element === window) {
                    document.body.classList.add('scrolling');
                } else {
                    element.classList.add('scrolling');
                }

                // 清除之前的定时器
                if (scrollTimer) {
                    clearTimeout(scrollTimer);
                }

                // 滚动停止后移除scrolling类
                scrollTimer = setTimeout(() => {
                    if (element === window) {
                        document.body.classList.remove('scrolling');
                    } else {
                        element.classList.remove('scrolling');
                    }
                }, CONFIG.scrollDebounce);
            };

            element.addEventListener('scroll', handleScroll, { passive: true });
        }
    }

    /**
     * 模态框优化器
     * 在模态框显示时添加.show类
     */
    class ModalOptimizer {
        constructor() {
            this.init();
        }

        init() {
            // 使用MutationObserver监听模态框的显示/隐藏
            const observer = new MutationObserver(mutations => {
                mutations.forEach(mutation => {
                    if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                        const target = mutation.target;
                        if (this.isModal(target)) {
                            const isVisible = window.getComputedStyle(target).display !== 'none';
                            
                            if (isVisible && !target.classList.contains('show')) {
                                target.classList.add('show');
                            } else if (!isVisible && target.classList.contains('show')) {
                                // 延迟移除，等动画完成
                                setTimeout(() => {
                                    target.classList.remove('show');
                                }, 300);
                            }
                        }
                    }
                });
            });

            // 监听所有可能的模态框
            document.querySelectorAll('.modal, .popup, .overlay, .dropdown-menu, .tooltip').forEach(el => {
                observer.observe(el, { attributes: true, attributeFilter: ['style', 'class'] });
            });

            if (CONFIG.enableLogging) {
                console.log('[GPU Optimizer] ModalOptimizer initialized');
            }
        }

        isModal(element) {
            return element.matches('.modal, .popup, .overlay, .dropdown-menu, .tooltip');
        }
    }

    /**
     * 图片懒加载优化器
     * 为懒加载图片添加临时will-change
     */
    class ImageOptimizer {
        constructor() {
            this.init();
        }

        init() {
            // 使用Intersection Observer监听图片加载
            if ('IntersectionObserver' in window) {
                const observer = new IntersectionObserver(entries => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            const img = entry.target;
                            
                            // 加载前添加will-change
                            img.style.willChange = 'opacity';
                            
                            // 加载完成后移除
                            img.addEventListener('load', () => {
                                setTimeout(() => {
                                    img.style.willChange = 'auto';
                                }, 1000);
                            }, { once: true });
                            
                            observer.unobserve(img);
                        }
                    });
                }, {
                    rootMargin: '50px'
                });

                // 监听所有懒加载图片
                document.querySelectorAll('img[loading="lazy"]').forEach(img => {
                    observer.observe(img);
                });

                if (CONFIG.enableLogging) {
                    console.log('[GPU Optimizer] ImageOptimizer initialized');
                }
            }
        }
    }

    /**
     * 性能监控器
     * 监控合成层数量和内存使用
     */
    class PerformanceMonitor {
        constructor() {
            this.enabled = CONFIG.enableLogging;
        }

        async getLayerCount() {
            // 这需要Chrome DevTools Protocol，实际使用中需要手动检查
            // 这里只是一个占位符
            if (this.enabled) {
                console.log('[GPU Optimizer] Use Chrome DevTools → More Tools → Rendering → Layer borders to check layer count');
            }
        }

        reportMemory() {
            if (this.enabled && performance.memory) {
                const used = Math.round(performance.memory.usedJSHeapSize / 1048576);
                const total = Math.round(performance.memory.totalJSHeapSize / 1048576);
                console.log(`[GPU Optimizer] Memory: ${used}MB / ${total}MB`);
            }
        }

        init() {
            if (this.enabled) {
                // 每30秒报告一次内存使用
                setInterval(() => {
                    this.reportMemory();
                }, 30000);

                console.log('[GPU Optimizer] PerformanceMonitor initialized');
            }
        }
    }

    /**
     * 主初始化函数
     */
    function init() {
        // 等待DOM加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        try {
            // 初始化各个优化器
            new ScrollOptimizer();
            new ModalOptimizer();
            new ImageOptimizer();
            
            const monitor = new PerformanceMonitor();
            monitor.init();

            if (CONFIG.enableLogging) {
                console.log('[GPU Optimizer] All optimizers initialized successfully');
            }

            // 暴露到全局，方便调试
            window.GPUOptimizer = {
                enableLogging: (enable) => {
                    CONFIG.enableLogging = enable;
                    console.log(`[GPU Optimizer] Logging ${enable ? 'enabled' : 'disabled'}`);
                },
                checkMemory: () => {
                    if (performance.memory) {
                        const used = Math.round(performance.memory.usedJSHeapSize / 1048576);
                        const total = Math.round(performance.memory.totalJSHeapSize / 1048576);
                        const percent = Math.round((used / total) * 100);
                        console.log(`Memory Usage: ${used}MB / ${total}MB (${percent}%)`);
                        return { used, total, percent };
                    } else {
                        console.log('Memory API not available');
                        return null;
                    }
                }
            };

        } catch (error) {
            hldebug.error('[GPU Optimizer] Initialization failed:', error);
        }
    }

    // 启动
    init();
})();
