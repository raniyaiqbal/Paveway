from setuptools import find_packages, setup

package_name = 'paveway_web'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/web.launch.py']),
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
            'battery_publisher = paveway_web.battery_publisher:main',
            'distance_publisher = paveway_web.distance_publisher:main',
            'time_publisher = paveway_web.time_publisher:main',
        ],
    },
)
