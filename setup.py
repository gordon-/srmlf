import setuptools
import re


def get_requirements(path):

    setuppy_pattern = \
        'https://github.com/{user}/{repo}/tarball/master#egg={egg}'

    dependency_links = []
    install_requires = []
    with open(path) as f:
        for line in f:

            if line.startswith('-e'):
                url_infos = re.search(
                    r'github.com/(?P<user>[^/.]+)/(?P<repo>[^.]+).git#egg='
                    '(?P<egg>.+)',
                    line).groupdict()
                dependency_links.append(setuppy_pattern.format(**url_infos))
                egg_name = '=='.join(url_infos['egg'].rsplit('-', 1))
                install_requires.append(egg_name)
            else:
                install_requires.append(line.strip())

    return install_requires, dependency_links


requirements, dependency_links = get_requirements('requirements.txt')
dev_requirements, dev_dependency_links = \
    get_requirements('dev-requirements.txt')

setuptools.setup(name='srmlf',
                 version='0.1.0',
                 description='Simple accountability within friends',
                 long_description=open('README').read().strip(),
                 author='Damien Nicolas',
                 author_email='pypi@gordon.re',
                 url='https://github.com/gordon-/srmlf/',
                 packages=setuptools.find_packages('src'),
                 package_dir={'': 'src'},
                 install_requires=requirements,
                 include_package_data=True,
                 scripts=['src/srmlf/srmlf'],
                 entry_points={'console_scripts': [
                     'srmlf = srmlf:main',
                 ]},
                 extras_require={
                     'dev': dev_requirements
                 },
                 setup_requires=['pytest-runner'],
                 tests_require=['pytest'],
                 license='GPLv3',
                 zip_safe=False,
                 keywords='cli reckoning tool',
                 classifiers=['Development Status :: 4 - Beta',
                              'Environment :: Console',
                              'Intended Audience :: Other Audience',
                              'License :: OSI Approved :: GNU General Public '
                              'License v3 or later (GPLv3+)',
                              'Natural Language :: English',
                              'Programming Language :: Python :: 3.3',
                              'Programming Language :: Python :: 3.4',
                              'Programming Language :: Python :: 3.5',
                              'Programming Language :: Python :: 3 :: Only',
                              'Topic :: Office/Business :: Financial :: '
                              'Accounting',
                              'Topic :: Utilities',
                              'Operating System :: OS Independent'],)
