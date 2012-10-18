# -*- coding: utf-8 -*-
"""Python packaging."""
from os.path import abspath, dirname, join
from setuptools import setup, find_packages


def read_relative_file(filename):
    """Returns contents of the given file, which path is supposed relative
    to this module."""
    with open(join(dirname(abspath(__file__)), filename)) as f:
        return f.read()

name = 'insight_reloaded'
version = read_relative_file('VERSION').strip()
readme = read_relative_file('README')
requirements = ['setuptools', 'tornado', 'tornado-redis',
                'requests', 'redis']
entry_points = {
    'console_scripts': [
        'insight_api = insight_reloaded.api:main',
        'insight = insight_reloaded.worker:main',
        'fake_callback = insight_reloaded.fake_callback:main',
        ]
    }


if __name__ == '__main__':  # ``import setup`` doesn't trigger setup().
    setup(name=name,
          version=version,
          description="""A full async docsplit previewer server based on Tornado and Redis""",
          long_description=readme,
          classifiers=[
                       "Programming Language :: Python",
                       'License :: Other/Proprietary License',
                       ],
          keywords='',
          author='Novapost',
          author_email='rd@novapost.fr',
          url='https://github.com/novagile/%s' % name,
          license='closed source',
          packages=find_packages(),
          include_package_data=True,
          zip_safe=False,
          install_requires=requirements,
          entry_points=entry_points,
    )
