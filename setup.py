# setup.py
from setuptools import find_packages, setup
from setuptools.extension import Extension

from Cython.Build import cythonize
from Cython.Distutils import build_ext

setup(
    name="Release Tool",
    version='0.100',
    packages = find_packages(),
    ext_modules = cythonize(
        [
            Extension("Data_Grapher", ["Data_Grapher.py"]),
        ],
        build_dir="build_cythonize",
        compiler_directives={
            'language_level' : "3",
            'always_allow_keywords': True,
        }
    ),
    cmdclass=dict(
        build_ext=build_ext
    ),
)