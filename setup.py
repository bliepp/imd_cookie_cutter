import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="imd_cookie_cutter",
    version="1.0.0",
    author="bliepp",
    #author_email="author@example.com",
    description="A tool for removing atoms in IMD config files, just like a cookie cutter in higher dimensions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bliepp/imd_cookie_cutter",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
