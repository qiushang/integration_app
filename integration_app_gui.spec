# -*- mode: python -*-

block_cipher = None


a = Analysis(['integration_app_gui.py'],
             pathex=['C:\\Users\\zhouq\\Desktop\\app1', 'C:\\Windows\\SysWOW64', 'C:\\Windows\\System32\\downlevel'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='integration_app_gui',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
