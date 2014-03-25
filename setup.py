import sys
import os

from cx_Freeze import setup, Executable

if os.name == 'nt':
    cfscc_path = (os.path.join(sys.prefix, 'DLLs\cfscc.dll'), 'cfscc.dll')
    settings_path = ('defaults.fscc', 'defaults.fscc')
else:
    cfscc_path = (os.path.join(sys.prefix, 'DLLs\libcfscc.so'), 'libcfscc.so')
    settings_path = ('defaults.fscc', 'defaults.fscc')

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages=['fscc'], excludes=[], includes=['re'],
                    include_files=[cfscc_path, settings_path], include_msvcr=True)


# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
    Executable('qfscc.py', base=base)
]

setup(name='qfscc',
      version='1.0.1',
      description='Fastcom FSCC GUI',
      author='Commtech, Inc.',
      options=dict(build_exe=buildOptions),
      executables=executables)
