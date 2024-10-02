from setuptools import setup, find_packages

def load_requirements(filename):
    with open(filename, 'r') as f:
        return f.read().splitlines()

setup(
    name='livetrackerbackend',
    version='0.0.1',
    py_modules=['livetrackerbackend'],
    packages=find_packages(),  # Automatically finds all packages (folders with __init__.py)
    install_requires=load_requirements('requirements.txt'),
    description='UYA Live tracker backend',
    url='https://github.com/Horizon-Private-Server/horizon-uya-bot',  # GitHub repository URL
    author='John Janecek',
    author_email='janecektyler@gmail.com',
    license='MIT',  # Choose your license
    package_data={
        '': ['*.json'],  # Include all JSON files in all directories
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',  # Specify the minimum Python version
)
