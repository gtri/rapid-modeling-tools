import gooey
import sys
sys.setrecursionlimit(5000)
gooey_root = os.path.dirname(gooey.__file__)
gooey_languages = Tree(os.path.join(gooey_root, 'languages'), prefix = 'gooey/languages')
gooey_images = Tree(os.path.join(gooey_root, 'images'), prefix = 'gooey/images')
added_files = [("src/model_processing/patterns/*.json", "model_processing/patterns")]
a = Analysis(['src/model_processing/gui.py'],
             pathex=['src/model_processing/'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None,
			 datas=added_files,
             )
a.scripts = a.scripts - [("src/model_processing/cli.py", None, None)]
pyz = PYZ(a.pure)

options = [('u', None, 'OPTION'), ('u', None, 'OPTION'), ('u', None, 'OPTION')]

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          options,
          gooey_languages, # Add them in to collected files
          gooey_images, # Same here.
          name='rapid-modeling-tools',
          debug=True,
          strip=None,
          upx=True,
          console=False,
          windowed=True,
          icon=os.path.join(gooey_root, 'images', 'program_icon.ico'))
