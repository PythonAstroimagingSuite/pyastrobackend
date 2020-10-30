# setup.py for the pyastrobackend

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(

    name='pyastrobackend',  # Required

    use_scm_version=True,

    #version="0.1.0",

    #version=AlpacaDSCDriver_Version,  # Required

    description='Python support for astronomical hardware frameworks.',  # Optional

    long_description=long_description,  # Optional

    long_description_content_type='text/markdown',  # Optional (see note above)

    url='https://github.com/PythonAstroimagingSuite/pyastrobackend',  # Optional

    author='Michael Fulbright',  # Optional

    author_email='mike.fulbright@pobox.com',  # Optional

    license='GPLv3',

    classifiers=[  # Optional
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: End Users/Desktop',
        'Topic :: Scientific/Engineering :: Astronomy',

        'License :: OSI Approved :: GNU General Public License (GPL)',

        'Operating System :: OS Independent',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
    ],

    keywords='',  # Optional

    package_dir={},  # Optional

    packages=find_packages(include=['pyastrobackend']),  # Required

    python_requires='>=3.7, <3.8',

    install_requires=[
                      'astropy>=3.1.0',
                      'numpy>=1.11.0',
                      'pycurl >=7.40',
                      'pyindi-client>=0.2.3;platform_system=="Linux"',
                      'comtypes;platform_system=="Windows"',
                      'win32com;platform_system=="Windows"'
                     ],  # Optional

    extras_require={}, # Optional

    setup_requires=[],

    tests_require=[],

    package_data={}, #{'': 'docs/build/html/*'},# Optional

    include_package_data = True,

    data_files=[],  # Optional

    entry_points={},

    scripts=[],

    project_urls={  # Optional
#        'Bug Reports': 'https://github.com/pypa/sampleproject/issues',
#        'Funding': 'https://donate.pypi.org',
#        'Say Thanks!': 'http://saythanks.io/to/example',
#        'Source': 'https://github.com/pypa/sampleproject/',
    },
)

