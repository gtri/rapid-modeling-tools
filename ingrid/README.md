[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
=======
# Rapid Modeling Tools - Ingrid

Ingrid is a component of the [Rapid Modeling Tools](https://github.com/gtri/rapid-modeling-tools). * Ingrid is a python application which translates spreadsheet data into a set of JSON instructions which are read by the other component of the Rapid Modeling Tools. 

## General Installation and Usage

For the general user, the installation documented in the [Rapid Modeling Tools README.md](../README.md) should be used. This README uses `anaconda-project` which is not necessary for the standard user, but provides additional capabilities for the advanced user / developer. Similarly, the usage outlined in the [Quick Start README.md](../ingrid-quick-start/README.md) is also sufficient for the standard user. 

## Advanced Installation and Usage

As discussed above, the typical user will not need to follow this README, but for developers and other advanced users additional information is provided below. 

### Installation

- Clone `Rapid Modeling Tools`
  ```bash
  git clone https://github.com/gtri/rapid-modeling-tools.git
  ```

- Install either [Anaconda](https://www.anaconda.com/distribution/ "Anaconda Download Page") or [Miniconda](https://docs.conda.io/en/latest/miniconda.html "Miniconda Download Page").
- Install `Anaconda Project`
  - Create / activate a conda environment containing the package `anaconda-project` installed
    * This may be the environment titled `base` or an environment you have created and installed `anaconda-project` into
    * Below is a straightforward way to do this.
    ```bash
    conda create -y -n anaconda-project python=3.6
    conda activate anaconda-project
    conda install anaconda-project
    ```
- Initialize the project
  - Navigate to the root of the Rapid Modeling Tools cloned directory and enter the `ingrid` directory containing `anaconda-project.yml`.
  - Run `prepare` and `run setup`
    ```bash
    cd ingrid
    anaconda-project prepare
    anaconda-project run setup
    ```   
    
- TODO: When i run `anaconda-project run setup` I get --- /bin/sh: 1: python: Exec format error. When i run the pip command directly it works (although installs into conda "base")
    
  - You can now import `model_processing` as a package and access all the methods
- Using Ingrid through Anaconda Project     
    - The available commands are listed in [`anaconda-project.yml`](anaconda-project.yml) are accessible via `anaconda-project run <command name (and flags if applicable)>`
    - Example commands:
        - `anaconda-project run test` - this will run all of the tests using `pytest`
        - `anaconda-project run cli --create --input "<path\to\file\filename>" --output "<path\to\output\directory>"` - this will run `model_processing` to create the json file.
        - `anaconda-project run cli --compare --original "<path\to\original\file\filename>" --update "<path\to\update\directory>" --output "<path\to\output\directory>"` - this will run `model_processing` to compare.... [[[[[TODO: expand on this....]]]]]
          - **Note:** `anaconda-project run cli` does **not** require the user to specify an `--output` directory (the default is to use the same directory as the input files).
        * **Help Messages**
            * `anaconda-project list-commands` prints all `anaconda-project run <command>` options
            * `anaconda-project run cli -h` prints the help information for the command line integration
            * `anaconda-project run <command> -h` prints the help information for any command, if that command has associated help information.

### `model_processing` API 

- _Note:_ The `anaconda-project run cli ...` command is equivalent to the `model_processing ...` command.
- `model_processing` is accessible via the command line interface (CLI)

#### Command Flags

##### Create

> --create, -C

The `create` command generates a JSON file for Player Piano to use to create a MagicDraw Diagram

Required additional flags: 
- `--input`

Optional additional flags:
- `--output` 

```bash
model_processing --create --input <file_path>
```

##### Compare

> --compare, -C
    
The `compare` command compares a baseline Excel File with a collection of Change Files.

Required additional flags: 
- `--original`
- `--updated`

Optional additional flags:
- `--output` 

```bash
model_processing --create --input <file_path> --updated <file_path>
```
    
#### Option Flags

##### Input

> --input, -i

The `input` flag is used to provide the relative or absolute path to the Excel Workbook(s). If the path has spaces, then it should be placed in quotes.

This flag should only be used with the `create` command.

* TODO: workbooks plural? Not sure this is main clear in other parts of doc.  

##### Original

> --original, -O

The `original` flag is used to provide the relative or absolute path for the baseline file used in the comparison. If the path has spaces, then it should be placed in quotes. 

This flag should only be used with the `compare` command. 

##### Updated

> --updated, -u

The `updated` flag is used to provide the relative or absolute path to the Change Files. If the path has spaces, then it should be placed in quotes.

This flag should only be used with the `compare` command.

- TODO: What does this mean?
  - TODO --- Ingrid handles more than one compare by computing the differences of each update file relative to the original file. Ingrid does not check for difference between any two files given in the update list since user intention may not be confidently interpreted.

- TODO: what are "change files"? Are these excel files? 


##### Output

> --output, -o

The `output` flag is used to provide the directory path for the JSON output file(s). If the path has spaces, then it should be placed in quotes.

This flag can be used with both the `create` and the `compare` commands. 

This is an optional flag. The default behavior will place the JSON in the input location.


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
