from setuptools import setup

setup(
    name='clitellum',
    version='1.0.1',
    packages=['clitellum', 'clitellum.core', 'clitellum.endpoints',
              'clitellum.endpoints.channels', 'clitellum.utils'],
    package_dir={'clitellum': 'clitellum'},
    url='',
    license='GPL',
    author='sergio',
    author_email='sbermudezlozano@gmail.com',
    description='Clitellum Communication Framework',
    extras_require={
    },
    requires=['config',]
)