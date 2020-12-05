from setuptools import find_packages, setup

setup(
    name='pikitlib',
    packages=find_packages(),
    version='0.0.4',
    description='WPILIb-equivilent for 1076 robot kits',
    author='1076',
    license='None',
    install_requires=['pynetworktables', 'pygame'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests'
)
