// AI画布页面交互逻辑
document.addEventListener('DOMContentLoaded', function() {
    // DOM元素
    const chatForm = document.getElementById('chatForm');
    const promptInput = document.getElementById('promptInput');
    const charCount = document.getElementById('charCount');
    const sendBtn = document.getElementById('sendBtn');
    const chatMessages = document.getElementById('chatMessages');
    const canvasGrid = document.getElementById('canvasGrid');
    const clearChatBtn = document.getElementById('clearChat');
    const clearCanvasBtn = document.getElementById('clearCanvas');
    const downloadAllBtn = document.getElementById('downloadAll');
    const imageModal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalClose = document.querySelector('.modal-close');
    const downloadImageBtn = document.getElementById('downloadImage');
    const deleteImageBtn = document.getElementById('deleteImage');
    const commandMenu = document.getElementById('commandMenu');
    const commandItems = document.querySelectorAll('.command-item');
    
    // 项目管理
    let currentProjectId = null;
    let autoSaveTimer = null;
    
    // 初始化：尝试从URL加载项目或创建新项目
    async function initializeProject() {
        const urlParams = new URLSearchParams(window.location.search);
        const projectId = urlParams.get('project_id');
        
        if (projectId) {
            // 加载已有项目
            await loadProject(projectId);
        } else {
            // 创建新项目
            await createNewProject();
        }
    }
    
    // 创建新项目
    async function createNewProject() {
        try {
            const response = await fetch('/api/canvas/projects/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: `画布项目 ${new Date().toLocaleString('zh-CN')}`
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                currentProjectId = result.project.project_id;
                console.log('✅ 创建新项目:', currentProjectId);
                
                // 更新URL但不刷新页面
                const newUrl = `/canvas?project_id=${currentProjectId}`;
                window.history.pushState({projectId: currentProjectId}, '', newUrl);
                
                // 启动自动保存
                startAutoSave();
            } else {
                console.error('❌ 创建项目失败:', result.error);
            }
        } catch (error) {
            console.error('❌ 创建项目错误:', error);
        }
    }
    
    // 加载项目
    async function loadProject(projectId) {
        try {
            const response = await fetch(`/api/canvas/projects/${projectId}`);
            const result = await response.json();
            
            if (result.success) {
                currentProjectId = projectId;
                const project = result.project;
                
                console.log('✅ 加载项目:', projectId);
                
                // 恢复画布数据
                if (project.canvas_data && project.canvas_data.images) {
                    canvasImages = project.canvas_data.images;
                    project.canvas_data.images.forEach(imageData => {
                        restoreImageToCanvas(imageData);
                    });
                }
                
                // 恢复对话历史
                if (project.chat_history && project.chat_history.length > 0) {
                    // 清空欢迎消息（除了第一条）
                    const messages = chatMessages.querySelectorAll('.message');
                    messages.forEach((msg, index) => {
                        if (index > 0) {
                            msg.remove();
                        }
                    });
                    
                    // 恢复对话
                    project.chat_history.forEach(msg => {
                        addMessage(msg.role === 'user' ? 'user' : 'assistant', msg.content, false);
                    });
                }
                
                // 启动自动保存
                startAutoSave();
            } else {
                console.error('❌ 加载项目失败:', result.error);
                // 如果加载失败，创建新项目
                await createNewProject();
            }
        } catch (error) {
            console.error('❌ 加载项目错误:', error);
            await createNewProject();
        }
    }
    
    // 保存项目
    async function saveProject() {
        if (!currentProjectId) return;
        
        try {
            // 收集画布数据
            const canvasData = {
                images: canvasImages.map((img, index) => {
                    const element = canvasGrid.querySelector(`[data-index="${index}"]`);
                    if (element) {
                        return {
                            ...img,
                            position: {
                                left: element.style.left,
                                top: element.style.top
                            },
                            size: {
                                width: element.style.width,
                                height: element.style.height
                            }
                        };
                    }
                    return img;
                })
            };
            
            const response = await fetch(`/api/canvas/projects/${currentProjectId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    canvas_data: canvasData
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                console.log('💾 项目已保存');
            } else {
                console.error('❌ 保存项目失败:', result.error);
            }
        } catch (error) {
            console.error('❌ 保存项目错误:', error);
        }
    }
    
    // 保存对话消息
    async function saveChatMessage(role, content, metadata = {}) {
        if (!currentProjectId) return;
        
        try {
            await fetch(`/api/canvas/projects/${currentProjectId}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    role: role,
                    content: content,
                    metadata: metadata
                })
            });
        } catch (error) {
            console.error('❌ 保存对话错误:', error);
        }
    }
    
    // 启动自动保存
    function startAutoSave() {
        // 清除之前的定时器
        if (autoSaveTimer) {
            clearInterval(autoSaveTimer);
        }
        
        // 每30秒自动保存一次
        autoSaveTimer = setInterval(() => {
            saveProject();
        }, 30000);
    }
    
    // 恢复图片到画布
    function restoreImageToCanvas(imageData) {
        const emptyCanvas = canvasGrid.querySelector('.empty-canvas');
        if (emptyCanvas) {
            emptyCanvas.remove();
        }
        
        const itemDiv = document.createElement('div');
        itemDiv.className = 'canvas-item';
        itemDiv.dataset.index = canvasImages.indexOf(imageData);
        
        // 恢复位置和大小
        if (imageData.position) {
            itemDiv.style.left = imageData.position.left;
            itemDiv.style.top = imageData.position.top;
        }
        if (imageData.size) {
            itemDiv.style.width = imageData.size.width;
            itemDiv.style.height = imageData.size.height;
        }
        
        // 创建临时图片获取原始尺寸
        const tempImg = new Image();
        tempImg.onload = function() {
            const imageWidth = this.width;
            const imageHeight = this.height;
            
            itemDiv.dataset.originalWidth = imageWidth;
            itemDiv.dataset.originalHeight = imageHeight;
            
            itemDiv.innerHTML = `
                <div class="canvas-item-image-wrapper">
                    <img src="${imageData.url}" alt="${imageData.prompt}" class="canvas-item-image">
                    <div class="canvas-item-overlay">
                        <div class="canvas-item-name">${imageData.prompt.substring(0, 30)}...</div>
                        <div class="canvas-item-resolution">${imageWidth} × ${imageHeight}</div>
                    </div>
                </div>
                <div class="selected-badge">已选中</div>
                <div class="resize-handle nw"></div>
                <div class="resize-handle ne"></div>
                <div class="resize-handle sw"></div>
                <div class="resize-handle se"></div>
                <div class="canvas-item-toolbar">
                    <button class="edit-btn" title="编辑"><i class="fas fa-edit"></i></button>
                    <button class="copy-btn" title="复制"><i class="fas fa-copy"></i></button>
                    <button class="delete" title="删除"><i class="fas fa-trash"></i></button>
                </div>
            `;
            
            setupImageInteractions(itemDiv);
            canvasGrid.appendChild(itemDiv);
        };
        tempImg.src = imageData.url;
    }
    
    // 初始化项目
    initializeProject();
    
    console.log('=== Canvas.js 已加载 ===');
    
    // 状态
    let isGenerating = false;
    let canvasImages = [];
    let currentImageIndex = null;
    let selectedImageIndex = null; // 当前选中的图片索引
    let currentCommand = null; // 当前选中的命令
    let commandMode = false; // 是否在命令模式
    let selectedCommandIndex = 0; // 命令菜单中选中的索引
    
    // 命令配置
    const commands = [
        { name: '生成', icon: '🎨', desc: '生成新图片', mode: 'generate' },
        { name: '对话', icon: '💬', desc: '与AI交流', mode: 'chat' },
        { name: '修改', icon: '✨', desc: '修改选中图片', mode: 'modify' }
    ];
    
    // 监听输入框，检测命令
    promptInput.addEventListener('input', function(e) {
        const value = this.value;
        const count = value.length;
        charCount.textContent = count;
        
        if (count > 900) {
            charCount.style.color = '#ff6b6b';
        } else {
            charCount.style.color = '#999';
        }
        
        // 检测是否输入了 "/"
        if (value === '/' || value.startsWith('/ ')) {
            console.log('检测到 / 输入，显示命令菜单');
            showCommandMenu();
        } else if (value.startsWith('/')) {
            // 如果以 / 开头但后面有内容，过滤命令
            const query = value.substring(1).toLowerCase();
            console.log('过滤命令:', query);
            filterCommands(query);
        } else {
            // 输入普通文本时，只隐藏菜单，保持currentCommand状态
            if (commandMode) {
                hideCommandMenu();
            }
        }
    });
    
    // 键盘导航命令菜单
    promptInput.addEventListener('keydown', function(e) {
        if (!commandMode) {
            // Ctrl+Enter发送消息
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && !isGenerating) {
                e.preventDefault();
                chatForm.dispatchEvent(new Event('submit'));
            }
            return;
        }
        
        const visibleItems = Array.from(commandItems).filter(item => item.style.display !== 'none');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedCommandIndex = (selectedCommandIndex + 1) % visibleItems.length;
            updateCommandSelection(visibleItems);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedCommandIndex = (selectedCommandIndex - 1 + visibleItems.length) % visibleItems.length;
            updateCommandSelection(visibleItems);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (visibleItems[selectedCommandIndex]) {
                selectCommand(visibleItems[selectedCommandIndex].dataset.command);
            }
        } else if (e.key === 'Escape') {
            e.preventDefault();
            cancelCommand();
        }
    });
    
    // 显示命令菜单
    function showCommandMenu() {
        console.log('showCommandMenu 被调用');
        commandMode = true;
        commandMenu.classList.add('active');
        console.log('菜单class:', commandMenu.className);
        selectedCommandIndex = 0;
        commandItems.forEach(item => item.style.display = 'flex');
        updateCommandSelection(Array.from(commandItems));
    }
    
    // 隐藏命令菜单（不清除已选择的命令）
    function hideCommandMenu() {
        commandMode = false;
        commandMenu.classList.remove('active');
    }
    
    // 取消命令选择（清除命令状态）
    function cancelCommand() {
        hideCommandMenu();
        currentCommand = null;
        promptInput.placeholder = '输入 / 查看命令，或直接描述你的需求...';
    }
    
    // 过滤命令
    function filterCommands(query) {
        commandMode = true;
        commandMenu.classList.add('active');
        let visibleCount = 0;
        
        commandItems.forEach(item => {
            const commandName = item.dataset.command.toLowerCase();
            if (commandName.includes(query)) {
                item.style.display = 'flex';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });
        
        if (visibleCount === 0) {
            hideCommandMenu();
        } else {
            selectedCommandIndex = 0;
            const visibleItems = Array.from(commandItems).filter(item => item.style.display !== 'none');
            updateCommandSelection(visibleItems);
        }
    }
    
    // 更新命令选中状态
    function updateCommandSelection(visibleItems) {
        commandItems.forEach(item => item.classList.remove('selected'));
        if (visibleItems[selectedCommandIndex]) {
            visibleItems[selectedCommandIndex].classList.add('selected');
            // 滚动到可见区域
            visibleItems[selectedCommandIndex].scrollIntoView({ block: 'nearest' });
        }
    }
    
    // 选择命令
    function selectCommand(commandName) {
        const command = commands.find(c => c.name === commandName);
        if (!command) return;
        
        currentCommand = command.mode;
        
        // 清空输入框并填入命令提示
        if (command.mode === 'generate') {
            promptInput.value = '';
            promptInput.placeholder = '🎨 生成模式：描述你想要的图片...';
            addMessage('assistant', '已切换到生成模式。告诉我你想生成什么图片吧！');
        } else if (command.mode === 'chat') {
            promptInput.value = '';
            promptInput.placeholder = '💬 对话模式：问我任何问题...';
            addMessage('assistant', '已切换到对话模式。有什么想了解的吗？');
        } else if (command.mode === 'modify') {
            if (selectedImageIndex === null) {
                promptInput.value = '';
                promptInput.placeholder = '✨ 修改模式：请先选择左侧的图片';
                addMessage('assistant', '修改模式需要先选中一张图片。请单击左侧画布中的图片。');
            } else {
                promptInput.value = '';
                promptInput.placeholder = '✨ 修改模式：告诉我如何修改选中的图片...';
                addMessage('assistant', '已切换到修改模式。告诉我要如何修改选中的图片！');
            }
        }
        
        hideCommandMenu();
        promptInput.focus();
    }
    
    // 点击命令项
    commandItems.forEach(item => {
        item.addEventListener('click', function() {
            selectCommand(this.dataset.command);
        });
    });
    
    // 点击输入框外部取消命令选择
    document.addEventListener('click', function(e) {
        if (!commandMenu.contains(e.target) && e.target !== promptInput) {
            // 只在命令菜单显示时才取消命令
            if (commandMode) {
                cancelCommand();
            }
        }
    });
    
    // 表单提交
    chatForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (isGenerating) return;
        
        const prompt = promptInput.value.trim();
        if (!prompt) return;
        
        // 如果有当前命令模式，根据模式强制意图
        let forcedIntent = null;
        if (currentCommand === 'generate') {
            forcedIntent = 'generate';
            console.log('🎯 强制意图: generate');
        } else if (currentCommand === 'chat') {
            forcedIntent = 'chat';
            console.log('🎯 强制意图: chat');
        } else if (currentCommand === 'modify') {
            if (selectedImageIndex !== null) {
                forcedIntent = 'modify';
                console.log('🎯 强制意图: modify');
            } else {
                addMessage('assistant', '❌ 修改模式需要先选中一张图片。');
                return;
            }
        }
        
        console.log('📝 用户输入:', prompt);
        console.log('🔧 当前命令:', currentCommand);
        console.log('💪 强制意图:', forcedIntent);
        
        // 添加用户消息
        addMessage('user', prompt);
        promptInput.value = '';
        charCount.textContent = '0';
        
        // 重置命令模式和占位符
        currentCommand = null;
        promptInput.placeholder = '输入 / 查看命令，或直接描述你的需求...';
        
        // 开始生成
        isGenerating = true;
        sendBtn.disabled = true;
        
        // 添加加载消息
        const loadingMsg = addMessage('assistant', '', true);
        
        try {
            // 先调用对话API判断意图
            const chatResponse = await fetch('/api/canvas/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    prompt: prompt,
                    selectedImageIndex: selectedImageIndex,
                    hasImages: canvasImages.length > 0,
                    forcedIntent: forcedIntent  // 传递强制意图
                })
            });
            
            const chatData = await chatResponse.json();
            
            console.log('🔍 收到后端响应:', chatData);
            console.log('📌 意图:', chatData.intent);
            console.log('💬 响应:', chatData.response);
            
            // 移除加载消息
            loadingMsg.remove();
            
            if (!chatData.success) {
                addMessage('assistant', `❌ 错误：${chatData.error || '未知错误'}`);
                return;
            }
            
            // 根据AI判断的意图执行不同操作
            if (chatData.intent === 'generate') {
                console.log('✅ 执行生成图片逻辑');
                // 需要生成图片
                await generateImage(chatData.refined_prompt || prompt);
            } else if (chatData.intent === 'modify' && selectedImageIndex !== null) {
                console.log('✅ 执行修改图片逻辑');
                // 需要修改已选中的图片
                await modifyImage(selectedImageIndex, chatData.refined_prompt || prompt);
            } else if (chatData.intent === 'chat') {
                console.log('✅ 执行对话逻辑');
                // 纯对话
                addMessage('assistant', chatData.response);
            } else if (chatData.intent === 'select_hint') {
                console.log('✅ 显示提示信息');
                // 提示用户选择图片
                addMessage('assistant', chatData.response);
            } else {
                console.log('⚠️ 未匹配到意图，使用默认响应');
                // 默认返回对话响应
                addMessage('assistant', chatData.response || '我理解了，请告诉我更多细节。');
            }
        } catch (error) {
            loadingMsg.remove();
            addMessage('assistant', `❌ 网络错误：${error.message}`);
        } finally {
            isGenerating = false;
            sendBtn.disabled = false;
        }
    });
    
    // 生成新图片
    async function generateImage(prompt) {
        const loadingMsg = addMessage('assistant', '', true);
        
        try {
            // 调用生成API
            const response = await fetch('/api/canvas/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: prompt })
            });
            
            const data = await response.json();
            loadingMsg.remove();
            
            if (data.success) {
                addMessage('assistant', '✨ 图片生成成功！已添加到画布中。');
                addToCanvas({
                    url: data.image_url,
                    prompt: prompt,
                    timestamp: new Date().toISOString()
                });
            } else {
                addMessage('assistant', `❌ 生成失败：${data.error || '未知错误'}`);
            }
        } catch (error) {
            loadingMsg.remove();
            addMessage('assistant', `❌ 生成错误：${error.message}`);
        }
    }
    
    // 修改已有图片
    async function modifyImage(imageIndex, instruction) {
        const loadingMsg = addMessage('assistant', '', true);
        
        try {
            const imageData = canvasImages[imageIndex];
            const response = await fetch('/api/canvas/modify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    image_url: imageData.url,
                    original_prompt: imageData.prompt,
                    instruction: instruction
                })
            });
            
            const data = await response.json();
            loadingMsg.remove();
            
            if (data.success) {
                addMessage('assistant', '✨ 图片修改成功！已添加到画布中。');
                addToCanvas({
                    url: data.image_url,
                    prompt: data.new_prompt,
                    timestamp: new Date().toISOString()
                });
            } else {
                addMessage('assistant', `❌ 修改失败：${data.error || '未知错误'}`);
            }
        } catch (error) {
            loadingMsg.remove();
            addMessage('assistant', `❌ 修改错误：${error.message}`);
        }
    }
    
    // 旧的表单提交逻辑（保留但不使用）
    async function oldGenerateLogic() {
        try {
            // 调用API生成图片
            const response = await fetch('/api/canvas/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: prompt })
            });
            
            const data = await response.json();
            
            // 移除加载消息
            loadingMsg.remove();
            
            if (data.success) {
                // 添加成功消息
                addMessage('assistant', '✨ 图片生成成功！已添加到画布中。');
                
                // 添加到画布
                addToCanvas({
                    url: data.image_url,
                    prompt: prompt,
                    timestamp: new Date().toISOString()
                });
            } else {
                addMessage('assistant', `❌ 生成失败：${data.error || '未知错误'}`);
            }
        } catch (error) {
            loadingMsg.remove();
            addMessage('assistant', `❌ 网络错误：${error.message}`);
        } finally {
            isGenerating = false;
            sendBtn.disabled = false;
        }
    }
    
    // 添加消息到聊天区
    function addMessage(type, content, isLoading = false, saveToProject = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        if (isLoading) {
            messageDiv.classList.add('loading');
            messageDiv.innerHTML = `
                <div class="message-content">
                    <div class="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="message-content">
                    <p>${content}</p>
                </div>
            `;
            
            // 保存到项目（不保存加载消息）
            if (saveToProject) {
                saveChatMessage(type === 'user' ? 'user' : 'assistant', content);
            }
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageDiv;
    }
    
    // 添加图片到画布
    function addToCanvas(imageData) {
        // 移除空状态提示
        const emptyCanvas = canvasGrid.querySelector('.empty-canvas');
        if (emptyCanvas) {
            emptyCanvas.remove();
        }
        
        // 创建图片元素
        const itemDiv = document.createElement('div');
        itemDiv.className = 'canvas-item';
        itemDiv.dataset.index = canvasImages.length;
        
        // 创建一个临时图片来获取原始尺寸
        const tempImg = new Image();
        tempImg.onload = function() {
            const imageWidth = this.width;
            const imageHeight = this.height;
            
            // 计算合适的显示尺寸（最大300px宽度，保持宽高比）
            let displayWidth = Math.min(imageWidth, 300);
            let displayHeight = (displayWidth / imageWidth) * imageHeight;
            
            // 随机位置
            const maxX = canvasGrid.clientWidth - displayWidth - 50;
            const maxY = canvasGrid.clientHeight - displayHeight - 50;
            const randomX = Math.max(20, Math.random() * maxX);
            const randomY = Math.max(20, Math.random() * maxY);
            
            // 设置位置和大小
            itemDiv.style.left = randomX + 'px';
            itemDiv.style.top = randomY + 'px';
            itemDiv.style.width = displayWidth + 'px';
            itemDiv.style.height = displayHeight + 'px';
            
            const time = new Date(imageData.timestamp);
            const timeStr = time.toLocaleTimeString('zh-CN', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            
            itemDiv.innerHTML = `
                <div class="canvas-item-image-wrapper">
                    <img src="${imageData.url}" alt="${imageData.prompt}" class="canvas-item-image">
                    <div class="canvas-item-overlay">
                        <div class="canvas-item-name">${imageData.prompt.substring(0, 30)}...</div>
                        <div class="canvas-item-resolution">${imageWidth} × ${imageHeight}</div>
                    </div>
                </div>
                <div class="selected-badge">已选中</div>
                <div class="resize-handle nw"></div>
                <div class="resize-handle ne"></div>
                <div class="resize-handle sw"></div>
                <div class="resize-handle se"></div>
                <div class="canvas-item-toolbar">
                    <button class="edit-btn" title="编辑"><i class="fas fa-edit"></i></button>
                    <button class="copy-btn" title="复制"><i class="fas fa-copy"></i></button>
                    <button class="delete" title="删除"><i class="fas fa-trash"></i></button>
                </div>
            `;
            
            // 存储原始尺寸
            itemDiv.dataset.originalWidth = imageWidth;
            itemDiv.dataset.originalHeight = imageHeight;
            
            setupImageInteractions(itemDiv);
            
            canvasGrid.appendChild(itemDiv);
        };
        tempImg.src = imageData.url;
        
        canvasImages.unshift(imageData);
        
        // 添加图片后自动保存项目
        setTimeout(() => {
            saveProject();
        }, 1000);
    }
    
    // 设置图片交互事件
    function setupImageInteractions(itemDiv) {
        // 点击选中/取消选中
        itemDiv.addEventListener('mousedown', function(e) {
            // 如果点击的是工具栏按钮或调整大小控制点，不处理
            if (e.target.closest('.canvas-item-toolbar') || e.target.classList.contains('resize-handle')) {
                return;
            }
            
            const index = parseInt(this.dataset.index);
            
            // 取消之前的选中
            const prevSelected = canvasGrid.querySelector('.canvas-item.selected');
            if (prevSelected && prevSelected !== this) {
                prevSelected.classList.remove('selected');
            }
            
            // 选中当前图片
            selectedImageIndex = index;
            this.classList.add('selected');
            
            // 开始拖拽
            startDrag(e, this);
        });
        
        // 工具栏按钮事件
        const editBtn = itemDiv.querySelector('.edit-btn');
        const copyBtn = itemDiv.querySelector('.copy-btn');
        const deleteBtn = itemDiv.querySelector('.delete');
        
        editBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const index = parseInt(itemDiv.dataset.index);
            selectedImageIndex = index;
            addMessage('assistant', `已选中图片。你可以告诉我如何修改它，比如"换个背景"、"改成晚上"等。`);
        });
        
        copyBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const index = parseInt(itemDiv.dataset.index);
            duplicateImage(index);
        });
        
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const index = parseInt(itemDiv.dataset.index);
            deleteImage(index);
        });
        
        // 调整大小控制点
        const resizeHandles = itemDiv.querySelectorAll('.resize-handle');
        resizeHandles.forEach(handle => {
            handle.addEventListener('mousedown', (e) => {
                e.stopPropagation();
                startResize(e, itemDiv, handle.classList[1]); // nw, ne, sw, se
            });
        });
    }
    
    // 打开图片预览
    function openImageModal(index) {
        if (index < 0 || index >= canvasImages.length) return;
        
        currentImageIndex = index;
        const imageData = canvasImages[index];
        
        modalImage.src = imageData.url;
        modalImage.alt = imageData.prompt;
        imageModal.classList.add('active');
        
        // 禁止背景滚动
        document.body.style.overflow = 'hidden';
    }
    
    // 关闭模态框
    function closeImageModal() {
        imageModal.classList.remove('active');
        currentImageIndex = null;
        document.body.style.overflow = '';
    }
    
    modalClose.addEventListener('click', closeImageModal);
    
    imageModal.addEventListener('click', function(e) {
        if (e.target === imageModal) {
            closeImageModal();
        }
    });
    
    // 下载图片
    downloadImageBtn.addEventListener('click', async function() {
        if (currentImageIndex === null) return;
        
        const imageData = canvasImages[currentImageIndex];
        try {
            const response = await fetch(imageData.url);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `canvas-${Date.now()}.png`;
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            alert('下载失败：' + error.message);
        }
    });
    
    // 删除图片
    deleteImageBtn.addEventListener('click', function() {
        if (currentImageIndex === null) return;
        
        if (confirm('确定要删除这张图片吗？')) {
            // 从数组中移除
            canvasImages.splice(currentImageIndex, 1);
            
            // 从DOM中移除
            const items = canvasGrid.querySelectorAll('.canvas-item');
            if (items[currentImageIndex]) {
                items[currentImageIndex].remove();
            }
            
            // 重新索引
            canvasGrid.querySelectorAll('.canvas-item').forEach((item, index) => {
                item.dataset.index = index;
            });
            
            // 如果画布为空，显示提示
            if (canvasImages.length === 0) {
                showEmptyCanvas();
            }
            
            closeImageModal();
        }
    });
    
    // 显示空画布提示
    function showEmptyCanvas() {
        canvasGrid.innerHTML = `
            <div class="empty-canvas">
                <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                    <line x1="9" y1="9" x2="15" y2="15"/>
                    <line x1="15" y1="9" x2="9" y2="15"/>
                </svg>
                <p>画布为空</p>
                <p class="hint">在右侧对话框中描述你想要的图片</p>
            </div>
        `;
    }
    
    // 清空对话
    clearChatBtn.addEventListener('click', function() {
        if (confirm('确定要清空所有对话记录吗？')) {
            // 保留欢迎消息
            const messages = chatMessages.querySelectorAll('.message');
            messages.forEach((msg, index) => {
                if (index > 0) {
                    msg.remove();
                }
            });
        }
    });
    
    // 清空画布
    clearCanvasBtn.addEventListener('click', function() {
        if (canvasImages.length === 0) return;
        
        if (confirm(`确定要清空画布中的所有 ${canvasImages.length} 张图片吗？`)) {
            canvasImages = [];
            showEmptyCanvas();
            addMessage('assistant', '画布已清空。');
        }
    });
    
    // 下载全部
    downloadAllBtn.addEventListener('click', async function() {
        if (canvasImages.length === 0) {
            alert('画布中没有图片');
            return;
        }
        
        if (!confirm(`确定要下载画布中的所有 ${canvasImages.length} 张图片吗？`)) {
            return;
        }
        
        for (let i = 0; i < canvasImages.length; i++) {
            const imageData = canvasImages[i];
            try {
                const response = await fetch(imageData.url);
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `canvas-${i + 1}-${Date.now()}.png`;
                a.click();
                window.URL.revokeObjectURL(url);
                
                // 避免浏览器阻止多个下载
                await new Promise(resolve => setTimeout(resolve, 500));
            } catch (error) {
                console.error('下载失败:', error);
            }
        }
    });
    
    // 键盘快捷键
    document.addEventListener('keydown', function(e) {
        // ESC关闭模态框或命令菜单
        if (e.key === 'Escape') {
            if (imageModal.classList.contains('active')) {
                closeImageModal();
            } else if (commandMode) {
                hideCommandMenu();
                promptInput.value = '';
                promptInput.focus();
            }
        }
        
        // Delete键删除选中的图片
        if (e.key === 'Delete' && selectedImageIndex !== null) {
            deleteImage(selectedImageIndex);
        }
    });
    
    // ========== 拖拽功能 ==========
    let isDragging = false;
    let dragStartX = 0;
    let dragStartY = 0;
    let dragElement = null;
    let elementStartX = 0;
    let elementStartY = 0;
    
    function startDrag(e, element) {
        isDragging = true;
        dragElement = element;
        dragStartX = e.clientX;
        dragStartY = e.clientY;
        elementStartX = parseInt(element.style.left) || 0;
        elementStartY = parseInt(element.style.top) || 0;
        
        element.style.cursor = 'grabbing';
        e.preventDefault();
    }
    
    document.addEventListener('mousemove', function(e) {
        if (isDragging && dragElement) {
            const deltaX = e.clientX - dragStartX;
            const deltaY = e.clientY - dragStartY;
            
            dragElement.style.left = (elementStartX + deltaX) + 'px';
            dragElement.style.top = (elementStartY + deltaY) + 'px';
        } else if (isResizing && resizeElement) {
            handleResize(e);
        }
    });
    
    document.addEventListener('mouseup', function() {
        if (isDragging && dragElement) {
            dragElement.style.cursor = 'move';
            isDragging = false;
            dragElement = null;
        }
        if (isResizing) {
            isResizing = false;
            resizeElement = null;
            resizeHandle = null;
        }
    });
    
    // ========== 调整大小功能 ==========
    let isResizing = false;
    let resizeElement = null;
    let resizeHandle = null;
    let resizeStartX = 0;
    let resizeStartY = 0;
    let resizeStartWidth = 0;
    let resizeStartHeight = 0;
    let resizeStartLeft = 0;
    let resizeStartTop = 0;
    
    function startResize(e, element, handleType) {
        isResizing = true;
        resizeElement = element;
        resizeHandle = handleType;
        resizeStartX = e.clientX;
        resizeStartY = e.clientY;
        resizeStartWidth = element.offsetWidth;
        resizeStartHeight = element.offsetHeight;
        resizeStartLeft = parseInt(element.style.left) || 0;
        resizeStartTop = parseInt(element.style.top) || 0;
        
        e.preventDefault();
        e.stopPropagation();
    }
    
    function handleResize(e) {
        const deltaX = e.clientX - resizeStartX;
        const deltaY = e.clientY - resizeStartY;
        
        const originalWidth = parseInt(resizeElement.dataset.originalWidth);
        const originalHeight = parseInt(resizeElement.dataset.originalHeight);
        const aspectRatio = originalWidth / originalHeight;
        
        let newWidth = resizeStartWidth;
        let newHeight = resizeStartHeight;
        let newLeft = resizeStartLeft;
        let newTop = resizeStartTop;
        
        switch(resizeHandle) {
            case 'se': // 右下角
                newWidth = Math.max(100, resizeStartWidth + deltaX);
                newHeight = newWidth / aspectRatio;
                break;
            case 'sw': // 左下角
                newWidth = Math.max(100, resizeStartWidth - deltaX);
                newHeight = newWidth / aspectRatio;
                newLeft = resizeStartLeft + (resizeStartWidth - newWidth);
                break;
            case 'ne': // 右上角
                newWidth = Math.max(100, resizeStartWidth + deltaX);
                newHeight = newWidth / aspectRatio;
                newTop = resizeStartTop + (resizeStartHeight - newHeight);
                break;
            case 'nw': // 左上角
                newWidth = Math.max(100, resizeStartWidth - deltaX);
                newHeight = newWidth / aspectRatio;
                newLeft = resizeStartLeft + (resizeStartWidth - newWidth);
                newTop = resizeStartTop + (resizeStartHeight - newHeight);
                break;
        }
        
        resizeElement.style.width = newWidth + 'px';
        resizeElement.style.height = newHeight + 'px';
        resizeElement.style.left = newLeft + 'px';
        resizeElement.style.top = newTop + 'px';
        
        // 更新分辨率显示
        const resolutionEl = resizeElement.querySelector('.canvas-item-resolution');
        if (resolutionEl) {
            resolutionEl.textContent = `${Math.round(newWidth)} × ${Math.round(newHeight)}`;
        }
    }
    
    // ========== 辅助功能 ==========
    function duplicateImage(index) {
        if (index < 0 || index >= canvasImages.length) return;
        
        const imageData = { ...canvasImages[index] };
        imageData.timestamp = Date.now();
        addToCanvas(imageData);
        addMessage('assistant', '已复制图片。');
    }
    
    function deleteImage(index) {
        if (index < 0 || index >= canvasImages.length) return;
        
        if (confirm('确定要删除这张图片吗？')) {
            // 从数组中移除
            canvasImages.splice(index, 1);
            
            // 从DOM中移除
            const items = canvasGrid.querySelectorAll('.canvas-item');
            items.forEach((item, idx) => {
                if (parseInt(item.dataset.index) === index) {
                    item.remove();
                }
            });
            
            // 重新索引
            canvasGrid.querySelectorAll('.canvas-item').forEach((item, idx) => {
                item.dataset.index = idx;
            });
            
            // 如果画布为空，显示提示
            if (canvasImages.length === 0) {
                showEmptyCanvas();
            }
            
            selectedImageIndex = null;
            addMessage('assistant', '已删除图片。');
            
            // 删除后自动保存
            saveProject();
        }
    }
    
    // 页面关闭前保存
    window.addEventListener('beforeunload', function() {
        if (currentProjectId) {
            saveProject();
        }
    });
});
