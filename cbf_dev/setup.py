from setuptools import find_packages, setup

package_name = 'cbf_dev'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'lar_msgs', 'lar_utils'],
    zip_safe=True,
    maintainer='giacomo',
    maintainer_email='buranig@stuent.ethz.ch',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # 'cbf = cbf_dev.CBF:main',
            # 'c3bf = cbf_dev.C3BF:main'
        ],
    },
)
