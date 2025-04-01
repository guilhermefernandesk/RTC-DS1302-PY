from setuptools import setup, find_packages

setup(
    name="ds1302",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["RPi.GPIO"],
    description="Biblioteca para comunicação com RTC DS1302 na Raspberry Pi",
    author="Guilherme Fernandes de Oliveira",
    author_email="guilhermeferoliv@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/guilhermefernandesk/RTC-DS1302-PY",
)
