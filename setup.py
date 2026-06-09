#!/usr/bin/env python

import sys
import os
import os.path
import warnings

from setuptools import setup, Extension
import numpy

# --- 优化点：在此处定义你的绝对路径 ---
# 如果你想强制优先使用某个路径，直接在这里修改，或者通过环境变量设置
USER_INCLUDE_PATH = os.environ.get('MY_TA_INCLUDE', '/usr/local/include') 
USER_LIBRARY_PATH = os.environ.get('MY_TA_LIBRARY', '/usr/local/lib')

platform_supported = False
lib_talib_name = 'ta-lib'

# 构造路径列表：将用户自定义路径放在最前面
if any(s in sys.platform for s in ['darwin', 'linux', 'bsd', 'sunos']):
    platform_supported = True
    include_dirs = [USER_INCLUDE_PATH] + [
        '/usr/include', '/usr/local/include', '/opt/include', 
        '/opt/homebrew/include', '/opt/homebrew/opt/ta-lib/include',
    ]
    library_dirs = [USER_LIBRARY_PATH] + [
        '/usr/lib', '/usr/local/lib', '/usr/lib64', 
        '/opt/homebrew/lib', '/opt/homebrew/opt/ta-lib/lib',
    ]

elif sys.platform == "win32":
    platform_supported = True
    lib_talib_name = 'ta-lib-static'
    include_dirs = [USER_INCLUDE_PATH] + [
        r"c:\ta-lib\c\include", r"c:\Program Files\TA-Lib\include",
    ]
    library_dirs = [USER_LIBRARY_PATH] + [
        r"c:\ta-lib\c\lib", r"c:\Program Files\TA-Lib\lib",
    ]

# 环境变量依然保留最高优先级
if 'TA_INCLUDE_PATH' in os.environ:
    include_dirs = os.environ['TA_INCLUDE_PATH'].split(os.pathsep) + include_dirs

if 'TA_LIBRARY_PATH' in os.environ:
    library_dirs = os.environ['TA_LIBRARY_PATH'].split(os.pathsep) + library_dirs

if not platform_supported:
    raise NotImplementedError(sys.platform)

# 验证库是否存在
for path in library_dirs:
    try:
        if any(lib_talib_name in f for f in os.listdir(path)):
            print(f"Found {lib_talib_name} in {path}")
            break
    except OSError:
        continue
else:
    warnings.warn('Cannot find ta-lib library, installation may fail.')

try:
    from Cython.Distutils import build_ext
    has_cython = True
except ImportError:
    from setuptools.command.build_ext import build_ext
    has_cython = False

class NumpyBuildExt(build_ext):
    def build_extensions(self):
        numpy_incl = numpy.get_include()
        for ext in self.extensions:
            ext.include_dirs.append(numpy_incl)
        super().build_extensions()

cmdclass = {'build_ext': NumpyBuildExt}

ext_modules = [
    Extension(
        'talib._ta_lib',
        ['talib/_ta_lib.pyx' if has_cython else 'talib/_ta_lib.c'],
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=[lib_talib_name],
        runtime_library_dirs=[] if sys.platform == 'win32' else library_dirs)
]

setup(
    ext_modules=ext_modules,
    cmdclass=cmdclass,
)