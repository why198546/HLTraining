// model-viewer.js - 独立的3D模型查看模块
(function (global) {
    const state = {
        metadata: {
            url: null,
            name: null,
            size: null,
            meshCount: null,
            triCount: null
        },
        dom: {},
        viewer: null,
        animId: null
    };

    function init(config) {
        state.dom.container = document.getElementById(config.containerId);
        state.dom.shell = document.getElementById(config.shellId);
        state.dom.fullscreenShell = document.getElementById(config.fullscreenShellId);
        state.dom.fullscreenWrapper = document.getElementById(config.fullscreenWrapperId);
        state.dom.metaIds = config.metaIds || {};

        window.addEventListener('resize', handleResize);

        return {
            loadModel,
            enterFullscreen,
            exitFullscreen
        };
    }

    function loadModel(modelUrl) {
        if (!state.dom.container || !state.dom.shell) return;

        state.metadata.url = modelUrl;
        state.metadata.name = modelUrl ? modelUrl.split('/').pop() : null;
        updateMetaUI();
        fetchModelSize(modelUrl);

        state.dom.container.innerHTML = '';
        if (state.animId) cancelAnimationFrame(state.animId);

        const targetShell = getActiveShell();
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, targetShell.clientWidth / targetShell.clientHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setPixelRatio(window.devicePixelRatio || 1);
        renderer.setSize(targetShell.clientWidth, targetShell.clientHeight);
        state.dom.container.appendChild(renderer.domElement);

        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.9);
        directionalLight.position.set(2, 3, 4);
        scene.add(directionalLight);

        const loader = new THREE.GLTFLoader();
        loader.load(modelUrl, (gltf) => {
            scene.add(gltf.scene);

            const box = new THREE.Box3().setFromObject(gltf.scene);
            const size = box.getSize(new THREE.Vector3());
            const center = box.getCenter(new THREE.Vector3());
            gltf.scene.position.sub(center);
            const maxDim = Math.max(size.x, size.y, size.z);
            const fitHeight = maxDim / (2 * Math.tan((Math.PI * camera.fov) / 360));
            const fitWidth = fitHeight / camera.aspect;
            const distance = Math.max(fitHeight, fitWidth);
            camera.position.set(0, 0, distance * 1.6);
            camera.lookAt(0, 0, 0);
            camera.near = distance / 100;
            camera.far = distance * 100;
            camera.updateProjectionMatrix();

            const stats = computeModelStats(gltf.scene);
            state.metadata.meshCount = stats.meshes;
            state.metadata.triCount = stats.tris;
            updateMetaUI();

            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.enablePan = true;
            controls.minDistance = distance / 10;
            controls.maxDistance = distance * 5;
            controls.target.set(0, 0, 0);
            controls.update();

            const animate = () => {
                state.animId = requestAnimationFrame(animate);
                controls.update();
                renderer.render(scene, camera);
            };
            animate();

            state.viewer = { scene, camera, renderer, controls };
            handleResize();
        }, undefined, (error) => {
            console.error('模型加载失败:', error);
            if (global.toast && global.toast.show) {
                global.toast.show('模型加载失败', 'error');
            }
        });
    }

    function computeModelStats(root) {
        let meshes = 0;
        let tris = 0;
        root.traverse(node => {
            if (node.isMesh && node.geometry) {
                meshes += 1;
                const geom = node.geometry;
                if (geom.index) {
                    tris += geom.index.count / 3;
                } else if (geom.attributes.position) {
                    tris += geom.attributes.position.count / 3;
                }
            }
        });
        return {
            meshes,
            tris: Math.round(tris)
        };
    }

    function formatBytes(bytes) {
        if (!bytes || Number.isNaN(bytes)) return '--';
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), sizes.length - 1);
        return `${(bytes / Math.pow(1024, i)).toFixed(i === 0 ? 0 : 2)} ${sizes[i]}`;
    }

    async function fetchModelSize(url) {
        if (!url) return;
        try {
            const res = await fetch(url, { method: 'HEAD' });
            const length = res.headers.get('content-length');
            if (length) {
                state.metadata.size = parseInt(length, 10);
                updateMetaUI();
            }
        } catch (e) {
            console.warn('无法获取模型大小', e);
        }
    }

    function updateMetaUI() {
        const ids = state.dom.metaIds || {};
        const nameEl = ids.name ? document.getElementById(ids.name) : null;
        const sizeEl = ids.size ? document.getElementById(ids.size) : null;
        const meshEl = ids.meshes ? document.getElementById(ids.meshes) : null;
        const triEl = ids.tris ? document.getElementById(ids.tris) : null;
        const fsNameEl = ids.fullscreenName ? document.getElementById(ids.fullscreenName) : null;

        if (nameEl) nameEl.textContent = state.metadata.name || '--';
        if (fsNameEl) fsNameEl.textContent = state.metadata.name || '--';
        if (sizeEl) sizeEl.textContent = state.metadata.size ? formatBytes(state.metadata.size) : '--';
        if (meshEl) meshEl.textContent = state.metadata.meshCount ?? '--';
        if (triEl) triEl.textContent = state.metadata.triCount ?? '--';
    }

    function handleResize() {
        if (!state.viewer) return;
        const target = getActiveShell();
        if (!target || !target.clientWidth || !target.clientHeight) return;
        state.viewer.camera.aspect = target.clientWidth / target.clientHeight;
        state.viewer.camera.updateProjectionMatrix();
        state.viewer.renderer.setSize(target.clientWidth, target.clientHeight);
    }

    function getActiveShell() {
        const fs = state.dom.fullscreenWrapper;
        if (fs && fs.style.display !== 'none') {
            return state.dom.fullscreenShell || state.dom.shell;
        }
        return state.dom.shell;
    }

    function enterFullscreen() {
        if (!state.viewer || !state.dom.fullscreenWrapper || !state.dom.fullscreenShell) return;
        state.dom.fullscreenWrapper.style.display = 'flex';
        state.dom.fullscreenShell.innerHTML = '';
        if (state.viewer.renderer && state.viewer.renderer.domElement) {
            state.dom.fullscreenShell.appendChild(state.viewer.renderer.domElement);
        }
        handleResize();
    }

    function exitFullscreen() {
        if (!state.viewer || !state.dom.fullscreenWrapper || !state.dom.container) return;
        state.dom.fullscreenWrapper.style.display = 'none';
        state.dom.container.innerHTML = '';
        if (state.viewer.renderer && state.viewer.renderer.domElement) {
            state.dom.container.appendChild(state.viewer.renderer.domElement);
        }
        handleResize();
    }

    global.ModelViewer = { init };
})(window);
