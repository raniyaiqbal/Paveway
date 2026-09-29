from setuptools import find_packages, setup

package_name = 'paveway_vision'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/vision.launch.py']),
        ('share/' + package_name + '/models', ['models/v8.pt']),
        ('share/' + package_name, ['angle-2.avi']),
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
            'yolov8 = paveway_vision.yolov8:main',
            'hsv = paveway_vision.red_object_detector:main',
            'video_publisher = paveway_vision.video_publisher:main',
            'object_mapper = paveway_vision.object_mapper:main'
        ],
    },
)
