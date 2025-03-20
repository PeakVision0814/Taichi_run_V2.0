# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_app.py'],
    pathex=['D:\\Lenovo\\Desktop\\Taichi_run_V2.0'],
    binaries=[],
    datas=[
        ('data/app_settings.json', 'data'),
        ('data/heart_rate_log_20250316-211736.csv', 'data'),
        ('icon/app_icon.ico', 'icon'),
        ('icon/gear_icon.ico', 'icon'),
        ('icon/gear_icon.png', 'icon'),
        ('icon/heart_rate.ico', 'icon'),
        ('icon/history_record.ico', 'icon'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='run_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,  # 使用 windowed 模式
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='run_app',
)
