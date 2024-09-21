from setuptools import setup, find_packages

setup(
    name='ygclib',
    version='0.1.0',
    description='ygcグローバルチャットに簡単に参加できるようにするライブラリ',
    author='ysmreg',
    author_email='support@ysmserv.com',
    url='https://github.com/ysmservice/ygclib',
    packages=find_packages(),
    install_requires=[
        'discord.py>=2.0.0',
        'websockets>=10.0',
        'ujson>=5.0.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.8',
    keywords='discord chat global json websockets ujson',
)
