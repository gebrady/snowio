from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="snowio",
    version="0.1.0",
    author="snowio",
    description="Find Landsat scenes and map snow extents with bounding polygon",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "folium>=0.14.0",
        "ipywidgets>=8.0.0",
        "ipykernel>=6.0.0",
        "jupyter>=1.0.0",
        "landsatxplore>=0.14.0",
        "requests>=2.28.0",
        "shapely>=2.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
