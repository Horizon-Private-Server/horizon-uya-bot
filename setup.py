from setuptools import setup, find_packages

def load_requirements(filename):
    with open(filename, 'r') as f:
        return f.read().splitlines()

setup(
    name='uyalivetrackerbackend',
    version='0.0.1',
    packages=find_packages(),
    install_requires=load_requirements('requirements.txt'),
    description='UYA Live tracker backend',
    url='https://github.com/Horizon-Private-Server/horizon-uya-bot',  # GitHub repository URL
    author='John Janecek',
    author_email='janecektyler@gmail.com',
    license='MIT',  # Choose your license
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',  # Specify the minimum Python version
)