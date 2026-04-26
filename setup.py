from setuptools import setup, find_packages

setup(
    name='nana-wiki',
    version='0.0.5',
    packages=find_packages(include=['nana', 'nana.*']),
    install_requires=[
        'openai>=1.0.0',
        'python-dotenv>=1.0.0',
        'rich>=13.0.0',
        'typer>=0.12.0',
        'pyyaml>=6.0',
        'questionary>=2.0.0',
        'prompt_toolkit>=3.0.0',
        'requests>=2.31.0',
        'pillow>=10.0.0',
        'rich-pixels>=3.0.0',
    ],
    entry_points={
        'console_scripts': [
            'nana=nana.cli:app',
        ],
    },
    package_data={
        'nana': ['locales/*.yaml', 'assets/*'],
    },
)
