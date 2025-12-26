// 历史记录面板管理

class HistoryPanel {
    constructor(session, isTabMode = false) {
        this.session = session;
        this.isOpen = false;
        this.isTabMode = isTabMode; // 是否使用标签页模式
        this.init();
    }
    
    init() {
        if (!this.isTabMode) {
            // 旧模式：创建独立面板
            this.createPanelHTML();
            this.attachEvents();
        }
        // 标签页模式：不创建面板，直接使用现有的historyList
    }
    
    createPanelHTML() {
        const panel = document.createElement('div');
        panel.id = 'historyPanel';
        panel.className = 'history-panel';
        panel.innerHTML = `
            <div class="history-panel-header">
                <h3>📜 历史记录</h3>
                <button class="history-panel-close" title="关闭">✕</button>
            </div>
            <div class="history-panel-content">
                <div class="history-list" id="historyList">
                    <!-- 历史记录项将在这里动态生成 -->
                </div>
            </div>
            <div class="history-panel-footer">
                <div class="history-stats">
                    <span id="historyCurrentStep">0</span> / <span id="historyTotalSteps">0</span>
                </div>
                <button class="btn-clear-history" title="清空历史">🗑️ 清空</button>
            </div>
        `;
        document.body.appendChild(panel);
    }
    
    attachEvents() {
        // 关闭按钮
        document.querySelector('.history-panel-close').addEventListener('click', () => {
            this.close();
        });
        
        // 清空历史按钮
        document.querySelector('.btn-clear-history').addEventListener('click', () => {
            if (confirm('确定要清空所有历史记录吗？此操作无法撤销。')) {
                this.session.clear();
                // 保存初始状态
                this.saveInitialState();
                this.update();
            }
        });
    }
    
    saveInitialState() {
        const snapshot = {
            images: window.canvasState.images,
            translateX: window.canvasState.translateX,
            translateY: window.canvasState.translateY,
            scale: window.canvasState.scale
        };
        infiniteSession.saveState(snapshot);
    }
    
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
    
    open() {
        document.getElementById('historyPanel').classList.add('open');
        this.isOpen = true;
        this.update();
    }
    
    close() {
        document.getElementById('historyPanel').classList.remove('open');
        this.isOpen = false;
    }
    
    update() {
        const historyList = document.getElementById('historyList');
        const info = this.session.getInfo();
        
        // 更新统计信息
        const currentStepEl = document.getElementById('historyCurrentStep');
        const totalStepsEl = document.getElementById('historyTotalSteps');
        if (currentStepEl) currentStepEl.textContent = info.currentStep;
        if (totalStepsEl) totalStepsEl.textContent = info.totalSteps;
        
        // 清空列表
        if (!historyList) return;
        historyList.innerHTML = '';
        
        // 生成历史记录项
        this.session.history.forEach((historyItem, index) => {
            const item = document.createElement('div');
            item.className = 'history-item';
            if (index === this.session.currentStep) {
                item.classList.add('current');
            }
            
            const state = historyItem.state;
            const timestamp = new Date(historyItem.timestamp);
            const timeStr = timestamp.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            
            // 确定操作描述
            let description = '初始状态';
            let icon = '📍';
            
            if (index > 0) {
                const prevState = this.session.history[index - 1].state;
                const imageCountChange = state.images.length - prevState.images.length;
                
                if (imageCountChange > 0) {
                    description = `添加 ${imageCountChange} 张图片`;
                    icon = '➕';
                } else if (imageCountChange < 0) {
                    description = `删除 ${Math.abs(imageCountChange)} 张图片`;
                    icon = '➖';
                } else if (state.scale !== prevState.scale) {
                    description = '调整缩放';
                    icon = '🔍';
                } else if (state.translateX !== prevState.translateX || state.translateY !== prevState.translateY) {
                    description = '移动画布';
                    icon = '🔄';
                } else {
                    // 检查图片位置或尺寸变化
                    let hasChange = false;
                    for (let i = 0; i < state.images.length; i++) {
                        const curr = state.images[i];
                        const prev = prevState.images[i];
                        if (prev && (curr.x !== prev.x || curr.y !== prev.y)) {
                            description = '调整图片位置';
                            icon = '↔️';
                            hasChange = true;
                            break;
                        }
                        if (prev && (curr.width !== prev.width || curr.height !== prev.height)) {
                            description = '调整图片大小';
                            icon = '↕️';
                            hasChange = true;
                            break;
                        }
                    }
                    if (!hasChange) {
                        description = '修改';
                        icon = '✏️';
                    }
                }
            }
            
            item.innerHTML = `
                <div class="history-item-icon">${icon}</div>
                <div class="history-item-info">
                    <div class="history-item-desc">${description}</div>
                    <div class="history-item-meta">
                        <span class="history-item-time">${timeStr}</span>
                        <span class="history-item-images">🖼️ ${state.images.length}</span>
                    </div>
                </div>
                <div class="history-item-step">#${index + 1}</div>
            `;
            
            // 点击跳转到该历史点
            item.addEventListener('click', () => {
                this.jumpToStep(index);
            });
            
            historyList.appendChild(item);
        });
        
        // 滚动到当前项
        setTimeout(() => {
            const currentItem = historyList.querySelector('.history-item.current');
            if (currentItem) {
                currentItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }, 100);
    }
    
    jumpToStep(stepIndex) {
        if (stepIndex < 0 || stepIndex >= this.session.history.length) {
            return;
        }
        
        this.session.currentStep = stepIndex;
        const historyItem = this.session.getCurrentState();
        
        if (historyItem) {
            // 恢复状态
            const state = historyItem.state;
            window.canvasState.images = JSON.parse(JSON.stringify(state.images));
            window.canvasState.translateX = state.translateX;
            window.canvasState.translateY = state.translateY;
            window.canvasState.scale = state.scale;
            
            // 重新渲染画布
            window.reloadCanvas();
            
            // 更新面板
            this.update();
            
            // 显示提示
            const description = this.getStepDescription(stepIndex);
            window.showToast(`已跳转到: ${description}`, 'info');
        }
    }
    
    getStepDescription(index) {
        if (index === 0) return '初始状态';
        
        const state = this.session.history[index].state;
        const prevState = this.session.history[index - 1].state;
        const imageCountChange = state.images.length - prevState.images.length;
        
        if (imageCountChange > 0) return `添加 ${imageCountChange} 张图片`;
        if (imageCountChange < 0) return `删除 ${Math.abs(imageCountChange)} 张图片`;
        if (state.scale !== prevState.scale) return '调整缩放';
        if (state.translateX !== prevState.translateX || state.translateY !== prevState.translateY) return '移动画布';
        return '修改操作';
    }
}

// 导出到全局
window.HistoryPanel = HistoryPanel;
