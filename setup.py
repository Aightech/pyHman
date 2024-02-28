from setuptools import find_packages, setup
setup(
    name='pyhman',
    packages=find_packages(include=['pyhman']),
    version='0.1.0',
    description='Python library for the Hman robot',
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    url='https://github.com/Aightech/pyHman',
    author='Alexis Devillard',
    license='GPL-3.0',
    install_requires=[],
    setup_requires=['pytest-runner'],
    extras_require={"dev": ["twine>=4.0.2"]},
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)