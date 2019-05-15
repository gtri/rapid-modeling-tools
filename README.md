[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

**Starting the Environment**
* Install `miniconda3` to a location on your computer separate from `Anaconda`
* Enter the top level directory containing the `anaconda-project.yml` file
* `activate <path to miniconda3>`
* The environment should boot up
* If the environment does not boot through this method:
    * `activate envs\default`

**First Things First**
* After booting the environment specified by the anaconda-project.yml file run the command:
    * `anaconda-project run setup`.
    * This command packages the code and facilitates the other functionality.

**Generating Documentation**
* To generate the Documentation that lives in the ./doc directory you will
need to run two commands.
    * First make sure you have a doc/ directory at the same level as the
    `anaconda-project.yml` file.
    * `anaconda-project run build-sphinx`
    * `anaconda-project run make html`
    * Documentation should be in `./doc/_build/html` and you should open
    `index.html` using your browser.

**Command Line Interaction with Ingrid Nerdman (Rick's Cafe American)**
* `anaconda-project run cli <specify commands and inputs/outputs>`

    * Help:
        * `anaconda-project run cli -h (or --help)`
        * Will produce help text that specifies the

    * Creating a new model:
        * Input File: `anaconda-project run cli --create --input "<path\to\file\filename>" --output "<path\to\output\directory>"`
            * If your filename has spaces then wrap your path in quotes:
                * `"path\to\file\filename"`
            * Omitting `-o <outdir>` will cause the program to place your creation instruction json next to your input file with the same name but a `.json` extension.
        * Input Directory: `anaconda-project run cli --create --input "<path\to\directory>"`
            * Option to add a `--output "<path\to\output\directory>"` but if none provided then the program will place the produced `.json` files into the input directory.

    * Compare one or more models to a common ancestor:
        * This program only compares one family of files at a time. Meaning that if the user desires to compare multiple families of files then the program must be run once for each of the desired comparisons.
            * A family of files is an Original File and the Updated Files that are to be compared against the Original.
        * `anaconda-project run cli --compare --original <path\to\original\file\filename> --update "<path\to\update\directory>"`
            * If your filename has spaces then wrap your path in quotes:
                * `"path\to\file\filename"`
            * Optionally the user can provide an output directory by specifying `--output "<path\to\output\directory>"`

**Using Jupyter Lab**
* create a ```notebooks``` directory in the top level
* run ```anaconda-project run setup```
    * This make it so you can import graph_analysis as a module
* run ```anaconda-project run jupyter lab```
    * This will launch a jupyter lab session in the notebooks directory

**Producing a `changes_uml.json`**
* In the `test_graph_analysis/test_graph_creation`
* If commented, uncomment the `class TestProduceJson` and all of its methods
* `anaconda-project run test -k "test_json_creation"`
* A `changes_uml.json` should be created and placed within the `data` directory

**Testing**

* **Running all of the Tests**
    * `anaconda-project run test`

* **Running a single Test File**
    * `anaconda-project run test <test file name.py>`

* **Running a single Test Case**
    * `anaconda-project run test -k "<test method name>"`
        * The double quotes are significant

* **Producing a Test Report**
    * `anaconda-project run test --cov=test_graph_analysis`
        * `test_graph_analysis` is only directory containing tests. Other test directories could be passed, if the exist, to create a coverage report for the test files in those directories.

Shane Connelly (shane.connelly@gtri.gatech.edu)
