from setuptools import setup, find_packages

VERSION = open("VERSION").read().strip()
README = open("README.md").read()

setup(
    name="better-gsc",
    version=VERSION,
    packages=find_packages(exclude=["tests.*", "tests"]),
    include_package_data=True,
    long_description=README,
    long_description_content_type="text/markdown",
    zip_safe=True,
    python_requires=">=3.7",
    install_requires=["matplotlib", "pandas", "click", "flask"],
    project_urls={
    },
    url="https://github.com/calpaterson/better-gsc",
    author="Cal Paterson",
    author_email="cal@calpaterson.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    entry_points={
        "console_scripts": [
            "better-gsc=better_gsc:main",
        ]
    }
)
