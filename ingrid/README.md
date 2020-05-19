[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
=======
# **Using Ingrid Nerdman**
Here we present two methods to install and work with Ingrid, either using [Anaconda](https://www.anaconda.com/distribution/ "Anaconda Download Page")/[Miniconda](https://docs.conda.io/en/latest/miniconda.html "Miniconda Download Page") and [anaconda-project](https://anaconda-project.readthedocs.io/en/latest/ "Anaconda Project Homepage") or without anaconda-project by running the commands described in `anaconda-project.yml` at the command line instead of through the `anaconda-project` interface. Although, we strongly encourage using miniconda and anaconda-project.

# **Installation**

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
    * Issue commands listed in `anaconda-project.yml` by typing `anaconda-project run <command name (and flags if applicable)>`
        * `anaconda-project run test`
        * `anaconda-project run cli --create --input "<path\to\file\filename>" --output "<path\to\output\directory>"`
        * `anaconda-project run cli --compare --original "<path\to\original\file\filename>" --update "<path\to\update\directory>" --output "<path\to\output\directory>"`
        * **Note:** `anaconda-project run cli` does **not** require the user to specify an `--output` directory.
            * If the user neglects to specify an output directory then `ingrid` places all generated files in the same directory as the input files.
        * **Help Messages**
            * `anaconda-project list-commands` prints all `anaconda-project run <command>` options
            * `anaconda-project run cli -h` prints the help information for the command line integration
            * `anaconda-project run <command> -h` prints the help information for any command, if that command has associated help information.

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
        * In the `ingrid` directory run `pytest` to run all the tests
        * `model_processing --create --input "<path/to/file/filename>" --output "<path\to\output\directory>"`
        * `model_processing --compare --original "<path\to\original\file\filename>" --update "<path\to\update\directory>" --output "<path\to\output\directory>"`
        * **Note:** `model_processing` does **not** require the user to specify a `--output` directory.
            * If the user neglects to specify an output directory then `ingrid` places all generated files in the same directory as the input files.
        * **Help Messages**
            * `model_processing -h` prints the help messages for the command line integration

### Structure of Command Line Integration (cli) Commands

**Dissecting a "compare" operation:**

* **Without Anaconda Project**
    * `model-processing --compare --original "<path\to\original\file\filename>" --update "<path\to\update\directory>" --output "<path\to\output\directory>"`
        * `model-processing` alerts the command line integration script that we wish to execute the `ingrid` functionality with the following arguments.
        * At a high level, that means that the `model_processing` program understands the flags `--compare`, `--original`, `--update`, and `--output`.
            * In reality, `model_processing` understands `--compare` and `--compare` expects inputs of `--original` and `--update` with an optional `--output`.
            * `--original` should be followed by a relative or absolute file path to the original Excel file.
                * Placing the file path in quotations `" "` allows for spaces, which would otherwise be interpreted as separate arguments.
            * `--update` should be a relative or absolute file path to the update Excel file(s).
                * Ingrid handles more than one compare by computing the differences of each update file relative to the original file. Ingrid does not check for difference between any two files given in the update list since user intention may not be confidently interpreted.
            * `--output` should be a path to a directory where the user wishes for Ingrid to place the results of the `--compare` command.
                * `--output` is optional and if not specified then Ingrid places all outputs in the same directory as the input file.
    * These explanations generalize to the `--create` command.


* **With Anaconda Project**
    * `anaconda-project run cli --compare --original "<path\to\original\file\filename>" --update "<path\to\update\directory>" --output "<path\to\output\directory>"`
        * `anaconda-project run cli`: tells the terminal to open the `anaconda-project` script. Then scan for the command titled `cli` and execute that command. This translates to the invocation of the `model_processing` program.
        * Now that we have invoked the `model_processing` program we supply it the rest of the arguments.
        * At this point, `anaconda-project` passes the rest of the arguments to the `model_processing` program.
            * Read above for a description of the `model_processing` program and how it parses commands.

### Generating Documentation

* To generate the Documentation that lives in the `./doc` directory you will
need to run two commands.
    * First make sure you have a `doc/` directory at the same level as the
    `anaconda-project.yml` file.
    * `anaconda-project run build-sphinx`
    * `anaconda-project run make html`
    * Documentation should be in `./doc/_build/html` and open
    `index.html` using your browser.

### Testing

* **Run all the Tests**
    * `anaconda-project run test`

* **Run a single Test File**
    * `anaconda-project run test <test file name.py>`

* **Run a single Test Case**
    * `anaconda-project run test -k "<test method name>"`
        * The double quotes are significant

* **Producing a Test Report**
    * `anaconda-project run test --cov=test`