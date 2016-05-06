from distutils.core import setup

setup(
    name='nameko-pyrq',
    version='1.1.0',
    url='https://github.com/Sparkycz/nameko-pyrq/tree/master',
    license='The MIT License',
    author='Sparkycz',
    author_email='email@vladimirkaspar.cz',
    py_modules=['nameko_pyrq'],
    install_requires=[
        "nameko>=2.0.0",
        "redis",
        "py-rq==1.0.0"
    ],
    packages=['nameko_pyrq'],
    dependency_links=[
        "git+ssh://git@github.com/heureka/py-rq.git@0.2.1#egg=py-rq-1.0.0"
    ],
    description='Redis dependency for Nameko services'
)
