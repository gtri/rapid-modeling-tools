[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
=======
# **Using Ingrid Nerdman**
Here we present two methods to install and work with Ingrid, either using [Anaconda](https://www.anaconda.com/distribution/ "Anaconda Download Page")/[Miniconda](https://docs.conda.io/en/latest/miniconda.html "Miniconda Download Page") and [anaconda-project](https://anaconda-project.readthedocs.io/en/latest/ "Anaconda Project Homepage") or without anaconda-project by running the commands described in `anaconda-project.yml` at the command line instead of through the `anaconda-project` interface. Although, we strongly encourage using miniconda and anaconda-project.

### Cloning the Repo
* Ensure that your github or bitbucket account has an associated SSH key
* From gitbash or another shell issue the `git clone <ssh or https address>` command followed by the https or ssh address of the project, acquired by clicking the clone button on the project repository.

### With Anaconda/Miniconda and Anaconda Project

* On windows open **Anaconda Prompt** or **WSL** (unix open **terminal**)
* Navigate to Rapid Modeling Tools cloned directory and enter the `ingrid` directory containing `anaconda-project.yml`
* Boot a conda environment containing the package `anaconda-project
    * This may be the environment titled `base` or an environment you have created and installed `anaconda-project` into
    * Some network configurations disallow users other than `admin` from changing the base environment; while allowing those other users to create custom environments
* `anaconda-project prepare`
* `anaconda-project run setup`
* Restart your command window
* You can now interact with the `ingrid` directory and import `model_processing` as a package and access all the methods
* **Ingrid Interactions Through Anaconda Project**
    * Open the terminal program used to install Ingrid
    * Issue commands listed in `anaconda-project.yml` by typing `anaconda-project run <command name (and flags if applicable)`
        * E.g. `anaconda-project run test`
        * E.g. `anaconda-project run cli --create --input "<path\to\file\filename>" --output "<path\to\output\directory>"`

### Without using Anaconda Project

* On windows open **Command Prompt** or **WSL** (unix open **terminal**)
* Navigate to the Rapid Modeling Tools cloned repository and enter the `ingrid` directory containing the `environment.yml` file
* Create a Python virtual environment using the `environment.yml` file
    * The `environment.yml` file contains all the project dependencies required for a virtual environment to run the Ingrid tool
* Run `setup.py` by issuing
    * `python -m pip install -e . --no-deps --ignore-installed`
* Restart your command window
* Booting the environment created by the `environment.yml` file gives that virtual environment access to the model_processing library
* You may interact with the Ingrid tool for model creation, comparison, document generation, and code testing from the command line while within the environment containing the project
    * View these commands in the `anaconda-project.yml` file through a text editor
* **Ingrid Interactions Without Anaconda Project**
    * Open the terminal program used to install Ingrid
    * Issue commands on the command line from the appropriate directory, see `anaconda-project.yml`
        * E.g. in the `ingrid` directory run `pytest` to run all the tests
        * E.g. `model_processing --create --input "<path/to/file/filename>" --output "<path\to\output\directory>"`

**Generating Documentation**
* To generate the Documentation that lives in the `./doc` directory you will
need to run two commands.
    * First make sure you have a `doc/` directory at the same level as the
    `anaconda-project.yml` file.
    * `anaconda-project run build-sphinx`
    * `anaconda-project run make html`
    * Documentation should be in `./doc/_build/html` and open
    `index.html` using your browser.

**Testing**

* **Running all of the Tests**
    * `anaconda-project run test`

* **Running a single Test File**
    * `anaconda-project run test <test file name.py>`

* **Running a single Test Case**
    * `anaconda-project run test -k "<test method name>"`
        * The double quotes are significant

* **Producing a Test Report**
    * `anaconda-project run test --cov=test`
