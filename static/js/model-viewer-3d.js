/**
 * 通用3D模型查看器模块
 * 用于显示和交互3D模型，支持GLB/GLTF/OBJ格式
 */

class ModelViewer3D {
    constructor(containerOrId, options = {}) {
        // 支持传入元素ID或直接传入元素
        if (typeof containerOrId === 'string') {
            this.containerId = containerOrId;
            this.container = document.getElementById(containerOrId);
        } else {
            this.container = containerOrId;
            this.containerId = containerOrId.id || 'model-viewer';
        }
        
        // 默认配置
        this.config = {
            backgroundColor: options.backgroundColor || 0x2c3e50,
            cameraFov: options.cameraFov || 75,
            enableControls: options.enableControls !== false,
            enableAutoRotate: options.enableAutoRotate || false,
            enableAnimation: options.enableAnimation !== false,
            ...options
        };
        
        // Three.js 对象
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.currentModel = null;
        this.animationId = null;
        
        // 状态
        this.isAutoRotating = false;
        this.isWireframe = false;
        
        // 光源
        this.ambientLight = null;
        this.directionalLight = null;
        
        // 事件回调
        this.onModelLoaded = options.onModelLoaded || null;
        this.onLoadError = options.onLoadError || null;
        this.onLoadProgress = options.onLoadProgress || null;
        
        this.init();
    }
    
    /**
     * 初始化3D查看器
     */
    init() {
        if (!this.container) {
            console.error(`容器 ${this.containerId} 不存在`);
            return;
        }
        
        try {
            this.createScene();
            this.createCamera();
            this.createRenderer();
            this.createLights();
            
            if (this.config.enableControls) {
                this.createControls();
            }
            
            if (this.config.enableAnimation) {
                this.startAnimation();
            }
            
            console.log('3D查看器初始化完成');
        } catch (error) {
            console.error('3D查看器初始化失败:', error);
        }
    }
    
    /**
     * 创建3D场景
     */
    createScene() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(this.config.backgroundColor);
    }
    
    /**
     * 创建相机
     */
    createCamera() {
        const aspectRatio = this.container.clientWidth / this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(
            this.config.cameraFov, 
            aspectRatio, 
            0.1, 
            1000
        );
        this.camera.position.set(0, 2, 5);
    }
    
    /**
     * 创建渲染器
     */
    createRenderer() {
        // 检查是否传入了canvas元素
        if (this.container.tagName === 'CANVAS') {
            // 如果容器本身就是canvas，直接使用
            this.renderer = new THREE.WebGLRenderer({ 
                canvas: this.container,
                antialias: true 
            });
        } else {
            // 如果是普通容器，创建新的canvas
            this.renderer = new THREE.WebGLRenderer({ antialias: true });
            // 清空容器并添加canvas
            this.container.innerHTML = '';
            this.container.appendChild(this.renderer.domElement);
        }
        
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    }
    
    /**
     * 创建光源
     */
    createLights() {
        // 环境光
        this.ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(this.ambientLight);
        
        // 定向光
        this.directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        this.directionalLight.position.set(10, 10, 5);
        this.directionalLight.castShadow = true;
        this.scene.add(this.directionalLight);
    }
    
    /**
     * 创建控制器（需要OrbitControls）
     */
    createControls() {
        try {
            // 尝试多种方式访问OrbitControls
            let OrbitControls;
            
            if (typeof THREE !== 'undefined' && THREE.OrbitControls) {
                OrbitControls = THREE.OrbitControls;
            } else if (typeof window.THREE !== 'undefined' && window.THREE.OrbitControls) {
                OrbitControls = window.THREE.OrbitControls;
            } else if (typeof window.OrbitControls !== 'undefined') {
                OrbitControls = window.OrbitControls;
            }
            
            if (OrbitControls) {
                this.controls = new OrbitControls(this.camera, this.renderer.domElement);
                this.controls.enableDamping = true;
                this.controls.dampingFactor = 0.05;
                this.controls.autoRotate = this.config.enableAutoRotate;
                console.log('OrbitControls 创建成功');
            } else {
                console.warn('OrbitControls 不可用，使用简单鼠标控制');
                this.addMouseControls();
            }
        } catch (error) {
            console.warn('创建OrbitControls失败，使用简单鼠标控制:', error);
            this.addMouseControls();
        }
    }
    
    /**
     * 添加简单的鼠标控制
     */
    addMouseControls() {
        let isMouseDown = false;
        let mouseX = 0, mouseY = 0;
        
        const canvas = this.renderer.domElement;
        
        canvas.addEventListener('mousedown', (event) => {
            isMouseDown = true;
            mouseX = event.clientX;
            mouseY = event.clientY;
        });
        
        canvas.addEventListener('mouseup', () => {
            isMouseDown = false;
        });
        
        canvas.addEventListener('mousemove', (event) => {
            if (!isMouseDown || !this.currentModel) return;
            
            const deltaX = event.clientX - mouseX;
            const deltaY = event.clientY - mouseY;
            
            this.currentModel.rotation.y += deltaX * 0.01;
            this.currentModel.rotation.x += deltaY * 0.01;
            
            mouseX = event.clientX;
            mouseY = event.clientY;
        });
        
        // 滚轮缩放
        canvas.addEventListener('wheel', (event) => {
            event.preventDefault();
            this.camera.position.z += event.deltaY * 0.01;
            this.camera.position.z = Math.max(1, Math.min(10, this.camera.position.z));
        });
    }
    
    /**
     * 开始动画循环
     */
    startAnimation() {
        const animate = () => {
            this.animationId = requestAnimationFrame(animate);
            
            // 自动旋转
            if (this.isAutoRotating && this.currentModel) {
                this.currentModel.rotation.y += 0.01;
            }
            
            // 更新控制器
            if (this.controls) {
                this.controls.update();
            }
            
            // 渲染
            if (this.renderer && this.scene && this.camera) {
                this.renderer.render(this.scene, this.camera);
            }
        };
        animate();
    }
    
    /**
     * 加载3D模型
     * @param {string} modelUrl - 模型文件URL
     * @param {string} format - 模型格式 ('gltf', 'glb', 'obj')
     */
    loadModel(modelUrl, format = 'auto') {
        // 清除之前的模型
        this.clearModel();
        
        // 自动检测格式
        if (format === 'auto') {
            const ext = modelUrl.split('.').pop().toLowerCase();
            format = ext === 'glb' ? 'gltf' : ext;
        }
        
        console.log(`加载${format.toUpperCase()}模型:`, modelUrl);
        
        switch (format) {
            case 'gltf':
            case 'glb':
                this.loadGLTFModel(modelUrl);
                break;
            case 'obj':
                this.loadOBJModel(modelUrl);
                break;
            default:
                console.error('不支持的模型格式:', format);
                console.log('回退到占位符模型');
                this.createPlaceholderModel();
        }
    }
    
    /**
     * 加载GLTF/GLB模型
     */
    loadGLTFModel(modelUrl) {
        console.log('尝试加载真实GLB文件:', modelUrl);
        
        // 直接使用fetch加载GLB文件，绕过GLTFLoader的依赖问题
        this.loadGLBDirectly(modelUrl);
    }
    
    /**
     * 直接加载GLB文件
     */
    loadGLBDirectly(modelUrl) {
        console.log('直接加载GLB文件:', modelUrl);
        
        // 等待GLTFLoader模块加载完成
        const waitForGLTFLoader = () => {
            return new Promise((resolve, reject) => {
                const checkLoader = () => {
                    if (window.THREE && window.THREE.GLTFLoader) {
                        console.log('GLTFLoader 已加载完成');
                        resolve(window.THREE.GLTFLoader);
                    } else {
                        setTimeout(checkLoader, 100);  // 每100ms检查一次
                    }
                };
                checkLoader();
                
                // 5秒后超时
                setTimeout(() => {
                    reject(new Error('GLTFLoader 加载超时'));
                }, 5000);
            });
        };
        
        Promise.all([
            fetch(modelUrl).then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.arrayBuffer();
            }),
            waitForGLTFLoader()
        ])
        .then(([data, GLTFLoader]) => {
            console.log('GLB文件加载成功，大小:', data.byteLength, '字节');
            console.log('GLTFLoader 准备就绪，开始解析GLB');
            
            const loader = new GLTFLoader();
            
            // 直接解析GLB数据
            loader.parse(data, '', 
                (gltf) => {
                    console.log('GLB文件解析成功!');
                    this.currentModel = gltf.scene;
                    this.addModelToScene();
                    
                    if (this.onModelLoaded) {
                        this.onModelLoaded(this.currentModel);
                    }
                },
                (error) => {
                    console.error('GLB文件解析错误:', error);
                    this.createPlaceholderModel();
                }
            );
        })
        .catch(error => {
            console.error('GLB文件加载或GLTFLoader初始化错误:', error);
            this.createPlaceholderModel();
        });
    }    /**
     * 加载OBJ模型
     */
    loadOBJModel(modelUrl) {
        // 检查OBJLoader是否可用
        let OBJLoader;
        if (typeof THREE.OBJLoader !== 'undefined') {
            OBJLoader = THREE.OBJLoader;
        } else if (typeof window.OBJLoader !== 'undefined') {
            OBJLoader = window.OBJLoader;
        } else {
            console.error('OBJLoader 未加载');
            if (this.onLoadError) {
                this.onLoadError(new Error('OBJLoader 未加载'));
            }
            return;
        }
        
        const loader = new OBJLoader();
        
        loader.load(
            modelUrl,
            (object) => {
                this.currentModel = object;
                this.addModelToScene();
                
                if (this.onModelLoaded) {
                    this.onModelLoaded(this.currentModel);
                }
            },
            (progress) => {
                if (this.onLoadProgress) {
                    this.onLoadProgress(progress);
                }
            },
            (error) => {
                console.error('OBJ模型加载失败:', error);
                if (this.onLoadError) {
                    this.onLoadError(error);
                }
            }
        );
    }
    
    /**
     * 将模型添加到场景并调整位置
     */
    addModelToScene() {
        if (!this.currentModel) return;
        
        // 调整模型大小和位置
        const box = new THREE.Box3().setFromObject(this.currentModel);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        
        const maxDim = Math.max(size.x, size.y, size.z);
        const scale = maxDim > 0 ? 3 / maxDim : 1;
        this.currentModel.scale.setScalar(scale);
        
        this.currentModel.position.sub(center.multiplyScalar(scale));
        
        this.scene.add(this.currentModel);
        console.log('模型添加到场景成功');
    }
    
    /**
     * 创建占位符模型
     */
    createPlaceholderModel() {
        this.clearModel();
        
        // 创建自行车占位符模型
        const group = new THREE.Group();
        
        // 车身框架
        const frameGeometry = new THREE.BoxGeometry(2, 0.1, 0.1);
        const frameMaterial = new THREE.MeshLambertMaterial({ color: 0x0066cc });
        const frame = new THREE.Mesh(frameGeometry, frameMaterial);
        frame.position.set(0, 0.5, 0);
        group.add(frame);
        
        // 后轮
        const wheelGeometry = new THREE.TorusGeometry(0.5, 0.1, 8, 16);
        const wheelMaterial = new THREE.MeshLambertMaterial({ color: 0x333333 });
        const rearWheel = new THREE.Mesh(wheelGeometry, wheelMaterial);
        rearWheel.position.set(-1, 0, 0);
        rearWheel.rotation.y = Math.PI / 2;
        group.add(rearWheel);
        
        // 前轮
        const frontWheel = new THREE.Mesh(wheelGeometry, wheelMaterial);
        frontWheel.position.set(1, 0, 0);
        frontWheel.rotation.y = Math.PI / 2;
        group.add(frontWheel);
        
        // 座椅
        const seatGeometry = new THREE.BoxGeometry(0.3, 0.1, 0.4);
        const seatMaterial = new THREE.MeshLambertMaterial({ color: 0x8B4513 });
        const seat = new THREE.Mesh(seatGeometry, seatMaterial);
        seat.position.set(-0.3, 1, 0);
        group.add(seat);
        
        // 把手
        const handleGeometry = new THREE.CylinderGeometry(0.05, 0.05, 0.8);
        const handleMaterial = new THREE.MeshLambertMaterial({ color: 0x666666 });
        const handle = new THREE.Mesh(handleGeometry, handleMaterial);
        handle.position.set(0.8, 1.2, 0);
        handle.rotation.z = Math.PI / 2;
        group.add(handle);
        
        this.currentModel = group;
        this.scene.add(group);
        
        if (this.onModelLoaded) {
            this.onModelLoaded(this.currentModel);
        }
    }
    
    /**
     * 清除当前模型
     */
    clearModel() {
        if (this.currentModel) {
            this.scene.remove(this.currentModel);
            this.currentModel = null;
        }
    }
    
    /**
     * 获取当前模型
     */
    get model() {
        return this.currentModel;
    }
    
    /**
     * 控制函数
     */
    startAutoRotate() {
        this.isAutoRotating = true;
    }
    
    stopAutoRotate() {
        this.isAutoRotating = false;
    }
    
    toggleAutoRotate() {
        this.isAutoRotating = !this.isAutoRotating;
        return this.isAutoRotating;
    }
    
    /**
     * 旋转模型
     */
    rotateModel(duration = 1000) {
        if (!this.currentModel) return;
        
        const startRotation = this.currentModel.rotation.y;
        const endRotation = startRotation + Math.PI * 2; // 完整旋转一圈
        const startTime = Date.now();
        
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            this.currentModel.rotation.y = startRotation + (endRotation - startRotation) * progress;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        animate();
    }
    
    resetView() {
        if (this.camera) {
            this.camera.position.set(0, 2, 5);
            this.camera.lookAt(0, 0, 0);
            
            if (this.controls && this.controls.reset) {
                this.controls.reset();
            }
        }
    }
    
    toggleWireframe() {
        if (!this.currentModel) return;
        
        this.isWireframe = !this.isWireframe;
        
        this.currentModel.traverse((child) => {
            if (child.isMesh && child.material) {
                if (Array.isArray(child.material)) {
                    child.material.forEach(material => {
                        material.wireframe = this.isWireframe;
                    });
                } else {
                    child.material.wireframe = this.isWireframe;
                }
            }
        });
        
        return this.isWireframe;
    }
    
    /**
     * 背景控制
     */
    toggleBackground() {
        if (!this.scene) return false;
        
        const hasBackground = this.scene.background !== null;
        
        if (hasBackground) {
            this.scene.background = null;
        } else {
            this.scene.background = new THREE.Color(this.config.backgroundColor);
        }
        
        return !hasBackground; // 返回新的背景状态
    }
    
    setBackgroundColor(color) {
        if (this.scene) {
            this.config.backgroundColor = color;
            this.scene.background = new THREE.Color(color);
        }
    }
    
    /**
     * 光照控制
     */
    setAmbientLightIntensity(intensity) {
        if (this.ambientLight) {
            this.ambientLight.intensity = parseFloat(intensity);
        }
    }
    
    setDirectionalLightIntensity(intensity) {
        if (this.directionalLight) {
            this.directionalLight.intensity = parseFloat(intensity);
        }
    }
    
    /**
     * 获取当前模型引用
     */
    getCurrentModel() {
        return this.currentModel;
    }
    
    /**
     * 切换到点云模式
     */
    togglePointCloud() {
        if (!this.currentModel) return false;
        
        let hasPointCloud = false;
        
        this.currentModel.traverse((child) => {
            if (child.isMesh) {
                // 检查是否已经有点云对象
                const pointsName = child.name + '_points';
                const existingPoints = this.scene.getObjectByName(pointsName);
                
                if (existingPoints) {
                    // 移除点云，显示原mesh
                    this.scene.remove(existingPoints);
                    child.visible = true;
                } else {
                    // 创建点云，隐藏原mesh
                    const geometry = child.geometry;
                    if (geometry) {
                        const pointsGeometry = geometry.clone();
                        const pointsMaterial = new THREE.PointsMaterial({
                            color: 0x00ff00,
                            size: 0.05,
                            sizeAttenuation: true
                        });
                        
                        const points = new THREE.Points(pointsGeometry, pointsMaterial);
                        points.name = pointsName;
                        points.position.copy(child.position);
                        points.rotation.copy(child.rotation);
                        points.scale.copy(child.scale);
                        
                        this.scene.add(points);
                        child.visible = false;
                        hasPointCloud = true;
                    }
                }
            }
        });
        
        return hasPointCloud;
    }
    
    /**
     * 切换材质类型
     */
    switchMaterial(materialType) {
        if (!this.currentModel) return;
        
        this.currentModel.traverse((child) => {
            if (child.isMesh && child.material) {
                let newMaterial;
                const color = child.material.color ? child.material.color.getHex() : 0x888888;
                
                switch (materialType) {
                    case 'lambert':
                        newMaterial = new THREE.MeshLambertMaterial({ color: color });
                        break;
                    case 'phong':
                        newMaterial = new THREE.MeshPhongMaterial({ 
                            color: color,
                            shininess: 30
                        });
                        break;
                    case 'standard':
                        newMaterial = new THREE.MeshStandardMaterial({ 
                            color: color,
                            roughness: 0.5,
                            metalness: 0.2
                        });
                        break;
                    default: // 'original'
                        if (child.userData.originalMaterial) {
                            newMaterial = child.userData.originalMaterial;
                        } else {
                            newMaterial = new THREE.MeshLambertMaterial({ color: color });
                        }
                }
                
                // 保存原始材质
                if (!child.userData.originalMaterial) {
                    child.userData.originalMaterial = child.material.clone();
                }
                
                child.material = newMaterial;
            }
        });
    }
    
    /**
     * 调整大小
     */
    resize() {
        if (!this.camera || !this.renderer) return;
        
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }
    
    /**
     * 销毁查看器
     */
    dispose() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        if (this.controls && this.controls.dispose) {
            this.controls.dispose();
        }
        
        if (this.renderer) {
            this.renderer.dispose();
        }
        
        this.clearModel();
    }
}

// 导出到全局作用域
window.ModelViewer3D = ModelViewer3D;