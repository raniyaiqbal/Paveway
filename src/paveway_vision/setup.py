from setuptools import find_packages, setup
from glob import glob

package_name = 'paveway_vision'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='hynwar',
    maintainer_email='hiba2anwar@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'potholes_hsv = paveway_vision.potholes_hsv:main',
            'potholes_map = paveway_vision.potholes_map:main'
        ],
    },
)
