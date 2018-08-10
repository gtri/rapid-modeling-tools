**Starting the Environment**
* Install `miniconda3` to a location on your computer separate from `Anaconda`
* Enter the top level directory containing the `anaconda-project.yml` file
* `activate <path to miniconda3>`
* The environment should boot up

**Producing a `changes_uml.json`**
* In the `graph_analysis/test_graph_creation`
* If commented, uncomment the `class TestProduceJson` and all of its methods
* `anaconda-project run test -k "test_json_creation"`
* A `changes_uml.json` should be created and placed within the `data` directory

Shane Connelly (shane.connelly@gtri.gatech.edu)
