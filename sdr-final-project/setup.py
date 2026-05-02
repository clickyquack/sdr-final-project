from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'sdr-final-project'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.world')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Blackwellized Group',
    maintainer_email='ksteel6@kent.edu',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'joy_teleop = sdr_final_project.joy_teleop:main',
            'camera_viewer = sdr_final_project.camera_viewer:main',
            'save_named_locations = sdr_final_project.save_named_locations:main',
            'open_manipulator_joy_teleop = sdr_final_project.open_manipulator_joy_teleop:main',
        ],
    },
)
