from setuptools import find_packages, setup
import os
from glob import glob


package_name = 'bumper_cars'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'lib'), glob('lib/*.py')),
    ],
    install_requires=['setuptools', 'bumper_msgs', 'lar_utils'],
    zip_safe=True,
    maintainer='giacomo',
    maintainer_email='buranig@student.ethz.ch',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "collision_avoidance_ros2 = bumper_cars.collision_avoidance_ros2:main",
            "state_buffer = bumper_cars.state_buffer:main",
            "joy_safety = bumper_cars.joy_safety:main",
            "wheel_remap = bumper_cars.wheel_joystick_remap:main",
        ],
    },
)