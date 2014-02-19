import sys
import os

from cx_Freeze import setup, Executable

if os.name == 'nt':
    cfscc_path = (os.path.join(sys.prefix, 'DLLs\cfscc.dll'), 'cfscc.dll')
else:
    cfscc_path = (os.path.join(sys.prefix, 'DLLs\libcfscc.so'), 'libcfscc.so')

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages=['fscc'], excludes=[], includes=['re'],
                    include_files=[cfscc_path], include_msvcr=True)


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
      options=dict(build_exe=buildOptions),
      executables=executables)
