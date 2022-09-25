from setuptools import setup, find_packages

setup(
    name='gbooks-dl',
    version='0.0.1',
    packages=find_packages(),
    url='https://github.com/moosejaw/gbooks-dl',
    author='Josh Demir',
    author_email='josh@akinji.net',
    description='A command-line program for downloading online book previews to your local computer.',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Multimedia',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3 :: Only'
    ]
)
