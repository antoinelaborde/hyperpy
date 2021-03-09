import setuptools
from setuptools import setup

TEST_DEPS = [
    'pytest==6.1.1',
    'pytest-cov==2.10.1',
    'mock==4.0.2'
]

setup(
    name="hyperpy",
    author='Antoine Laborde',
    author_email="lab.antoine@gmail.com",
    descripton="Hyperspectral data management",
    packages=setuptools.find_packages('src'),
    zip_safe=True,
    package_dir={"": "src"},
    install_requires=[
        'scikit-learn==0.23.2',
        'pandas==1.1.3',
        'bokeh==2.2.1',
        'holoviews==1.14.1'
    ],
    tests_requires=TEST_DEPS,
    extras_require={
        'test': TEST_DEPS
    }
)
