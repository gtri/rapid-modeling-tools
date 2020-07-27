[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)


# Rapid Modeling Tools - Ingrid

[Rapid Modeling Tools](https://github.com/gtri/rapid-modeling-tools) consists of two components, the Player Piano and Ingrid. Ingrid uses Python to translate spreadsheet data with an accompanying modeling pattern into a set of JSON instructions that the Player Piano interprets as API calls to Cameo to build and maintain models.

## General Installation and Usage

General users, should consult the Rapid Modeling Tools [installation documentation](../README.md). This Ingrid-specific README focuses on using `anaconda-project`. `anaconda-project` provides capabilities for the advanced user/developer that standard usage of RMT does not require. While geared towards everyone planning to use RMT, the [Quick Start README.md](../ingrid-quick-start/README.md) provides information for the standard user.

## Advanced Installation and Usage

Advanced users and developers should follow this README. Typical users do not need to follow this README to interact with RMT.

### Installation

- Clone `Rapid Modeling Tools`
  ```bash
  git clone https://github.com/gtri/rapid-modeling-tools.git
  cd rapid-modeling-tools
  ```


- Install either [Anaconda](https://www.anaconda.com/distribution/ "Anaconda Download Page") or [Miniconda](https://docs.conda.io/en/latest/miniconda.html "Miniconda Download Page").
- Install `Anaconda Project`
  - Create / activate a conda environment containing the package `anaconda-project` installed
    * This may be the environment titled `base` or an environment you have created and installed `anaconda-project` into
    * Below is a straightforward way to do this.
    ```bash
    conda create -y -n anaconda-project python=3.6 anaconda-project
    conda activate anaconda-project
    ```
- Initialize the project
  - Navigate to the root of the Rapid Modeling Tools cloned directory and enter the `ingrid` directory containing `anaconda-project.yml`.
  - Run `prepare` and `run setup`
    ```bash
    cd ingrid
    anaconda-project prepare
    anaconda-project run setup
		```
  - You can now import `model_processing` as a package and access all the methods
- Using Ingrid through Anaconda Project     
    - Find the available commands listed in [`anaconda-project.yml`](anaconda-project.yml). `anaconda-project run <command name (and flags if applicable)>` invokes the desired command with specified options in a conda managed environment.
    - Example commands:
        - `anaconda-project run test` - this will run all the tests using `pytest`
        - `anaconda-project run cli --create --input "<path\to\file\filename>" --pattern "<path\to\user\defined\pattern(file or directory)>" --output "<path\to\output\directory>"` - this will run `model_processing` to create the JSON file.
        - `anaconda-project run cli --compare --original "<path\to\original\file\filename>" --update "<path\to\update\directory>" --pattern "<path\to\user\defined\pattern(file or directory)>" --output "<path\to\output\directory>"` - this will run `model_processing` to compare the each update Excel file to the original and generates JOSN files with MagicDraw commands to update the original to match each file. Also, Ingrid produces an Excel file detailing the changes detected, added and deleted elements and changes that Ingrid could not determine and did not include in the update JSON.
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
    - Provide the absolute or relative path to the input Excel file(s).
        - Ingrid understands: a single path, a list of paths or a path to a directory containing Excel files. If Ingrid receives multiple Excel files then it runs a `--create` command for each of them.

Optional additional flags:
- `--pattern`
    - Provide the absolute or relative path to a user-defined pattern file or directory of files
        - Ingrid combines any pattern file(s) provided through this argument with the existing patterns when scanning input Excel sheets for their accompanying pattern.
- `--output`
    - Provide the absolute or relative path to an existing output directory.

```bash
model_processing --create --input <file_path>
```

##### Compare

> --compare, -C

The `compare` command compares a baseline Excel File with a collection of updated Excel Files.

Required additional flags:
- `--original`
    - Absolute or relative path to a single Excel file to be considered as the original version of the model. Typically, the file provided here reflects the current state of the model within Cameo.
- `--updated`
    - May be any of: a single Excel file, a list of Excel files or a directory containing Excel files considered as changed instances of the model.
    - Absolute or relative path to input Excel files or directory.

Optional additional flags:
- `--pattern`
    - Provide the absolute or relative path to a user-defined pattern file or directory of files
        - Ingrid combines any pattern file(s) provided through this argument with the existing patterns when scanning input Excel sheets for their accompanying pattern.
- `--output`
    - Provide the absolute or relative path to an existing output directory.


```bash
model_processing --create --input <file_path> --updated <file_path>
```

#### Option Flags

Note: For paths containing spaces, escape the spaces or place the entire path within quotes.

##### Input

> --input, -i

The `input` flag provides the relative or absolute path to the Excel Workbook(s). Ingrid accepts both a path to a single Excel file or as a path to a directory of Excel files. Ingrid will iterate over each worksheet in each workbook provided and find any worksheets that match a defined pattern.
    - Only the `--create` command accepts the `--input` flag.

##### Original

> --original, -O

The `original` flag provides the relative or absolute path to the singular baseline (original) Excel file used in the comparison. Only `--compare` understands this flag.

##### Updated

> --updated, -u

The `updated` flag provides the relative or absolute path to the updated Excel files used in the comparison. `--updated` understands a path to a single Excel file or a path to a directory of Excel files. If providing multiple files, Ingrid compares each file to the original but does not compare change files to one another. This flag works with `--compare`.

##### Output

> --output, -o

The `output` flag provides the path to the output directory for the JSON output file(s). Both `--create` and `--compare` understand the `--output` flag.

Ingrid does not require an output flag. If none provided, then Ingrid deposits any generated files into the same directory as the input files.

### Generating Documentation

* To generate the Documentation that lives in the `./doc` directory you will
need to run two commands.
    * First make sure you have a `doc/` directory at the same level as the
      `anaconda-project.yml` file
    * `anaconda-project run build-docs`
    * Documentation should be in `./docs/_build/html`
    * Open `index.html` using your browser

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
