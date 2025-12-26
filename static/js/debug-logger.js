/**
 * 调试日志模块 - 集中控制所有console输出
 * 本地环境自动启用，生产环境关闭
 * 不显示任何启用提示，防止别人知道怎么启用调试
 */

// 根据环境自动设置DEBUG模式
// 本地开发环境（localhost）启用DEBUG，生产环境关闭
if (typeof window.hldebug === 'undefined') {
    window.hldebug = location.hostname === 'localhost' || location.hostname === '127.0.0.1';
}

window.DebugLogger = {
    // 普通日志（默认不显示）
    log: function(...args) {
        if (window.hldebug) {
            console.log(...args);
        }
    },

    // 警告日志（重要，建议保留）
    warn: function(...args) {
        if (window.hldebug) {
            console.warn(...args);
        }
    },

    // 错误日志（一定要显示，问题排查用）
    error: function(...args) {
        console.error(...args);  // 错误始终显示
    },

    // 强制显示日志（无视DEBUG开关）
    force: function(...args) {
        console.log(...args);
    },

    // 切换DEBUG状态（静默切换，不显示提示）
    toggle: function() {
        window.hldebug = !window.hldebug;
        return window.hldebug;
    },

    // 获取当前状态
    isEnabled: function() {
        return window.hldebug;
    }
};

// 快捷方式
window.hldebug = window.DebugLogger;
