import setuptools


setup_args = dict(
    name="graph_analysis",
    version="0.1.0",
    author="Author Name",
    author_email="author@gmail.com",
    description="Description of my package",
    packages=setuptools.find_packages(),
    install_requires=["numpy", "pandas", "networkx", "xlrd"],
)

if __name__ == "__main__":
    setuptools.setup(**setup_args)
