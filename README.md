**Starting the Environment**
* Install `miniconda3` to a location on your computer separate from `Anaconda`
* Enter the top level directory containing the `anaconda-project.yml` file
* `activate <path to miniconda3>`
* The environment should boot up

**Using Jupyter Lab**
* create a ```notebooks``` directory in the top level
* run ```anaconda-project run setup```
    * This make it so you can import graph_analysis as a module
* run ```anaconda-project run jupyter lab```
    * This will launch a jupyter lab session in the notebooks directory

**Producing a `changes_uml.json`**
* In the `graph_analysis/test_graph_creation`
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

Shane Connelly (shane.connelly@gtri.gatech.edu)
