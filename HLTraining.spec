# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 定义要包含的数据文件
datas = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('models', 'models'),
    ('uploads', 'uploads'),
    ('api', 'api'),
    ('requirements.txt', '.'),
    ('README.md', '.'),
    ('.env.example', '.'),
]

# 定义要隐藏导入的模块
hiddenimports = [
    'PIL',
    'PIL.Image',
    'cv2',
    'numpy',
    'flask',
    'werkzeug',
    'requests',
    'google.generativeai',
    'tencentcloud',
]

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='HLTraining',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HLTraining',
)