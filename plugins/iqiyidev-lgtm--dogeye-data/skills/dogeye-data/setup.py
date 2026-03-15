from setuptools import setup

setup(
    name="dogeye-skill",
    version="1.0.0",
    description="DogEye 实时加密数据查询 Skill",
    author="phpspy",
    py_modules=["dogeye"],
    entry_points={
        "console_scripts": [
            "dogeye=dogeye:main",
        ],
    },
    install_requires=[
        "requests>=2.28.0",
    ],
    python_requires=">=3.8",
)
