# sherlock-python/sherlock.spec

# This is the configuration file for PyInstaller.

# Analysis block: Finds all the Python files and dependencies.
a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        # This is the most important part.
        # It tells PyInstaller to include our entire Django project.
        ('sherlock', 'sherlock'),
        ('inventory', 'inventory'),
        ('static', 'static'),
        ('templates', 'templates'),
    ],
    hiddenimports=[
    'inventory.apps.InventoryConfig',
    'whitenoise.middleware',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# PYC block: Handles the compiled Python files.
pyz = PYZ(a.pure)

# EXE block: Creates the final executable file.
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Sherlock', # This will be the name of your .exe file
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True, # Set to True to see server output, False for a "windowless" app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)