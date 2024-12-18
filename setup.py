from setuptools import setup, find_packages

setup(
    name='ygclib',
    version='0.1.17',
    description='ygcグローバルチャットに簡単に参加できるようにするライブラリ',
    author='ysmreg',
    author_email='support@ysmserv.com',
    url='https://github.com/ysmservice/ygclib',
    packages=find_packages(),
    install_requires=[
        'discord.py>=2.0.0',    # discordライブラリ
        'websockets>=10.0',     # WebSocketサポート
        'ujson>=5.0.0',         # 高速なJSON処理
        'aiohttp>=3.7.4',       # 非同期HTTPクライアント
        'typing-extensions>=4.0.0'  # TYPE_CHECKINGのサポート
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
    keywords='discord chat global json websockets ujson aiohttp',
)
