# Rapid Modeling Tools

## "Ingrid Nerdman (Ingestion Grid Nerdman)"

Developed at Georgia Tech Research Institute by Shane Connelly and Bjorn Cole. Government sponsorship (SOCOM TALOS) acknowledged.

### Installation

**We suggest that you clone this repository.**

Cloning the repository provides you access to add meta model JSON descriptions and update the `player-piano` to create novel model elements.

**Ingrid:**

- Clone `Rapid Modeling Tools`
- Create a Python environment from the `environment.yml`
- Run `setup.py`
- Detailed instructions found in the [README.md](ingrid/README.md) in the `ingrid` directory for usage with anaconda-project and without anaconda-project

**Player Piano**
- In MagicDraw Tools > Macros > Organice Macros
- Provide the name Player Piano, the language as Groovy and browse the file explorer to the location of this project `.../player-piano/player-piano-script.groovy` and click okay
- Detailed instructions with images found in the [Readme.md](player-piano/Readme.md) in the `player-piano` directory

### About

Rapid Modeling Tools contains two constituent programs. The `ingrid` tool translates spreadsheet data into object modeling languages such as UML and SysML using a JSON subgraph description. Development of Ingrid focused on the UML metamodel but could in principle support other modeling languages that have a defined metamodel and graph orientation. The `player-piano` works with MagicDraw, as a macro, to interpret the JSON model modification instructions, output from the Ingrid program to, in the MagicDraw API. As long as the user knows the API commands for another modeling tool such as Rhapsody, Capella or Papayrus the instructions produced by Ingrid could build models in those programs. The functionality developed here leaves the door open for the user to build up REST messages in the future.

### Getting Started

The [ingrid-quick-start](ingrid-quick-start/README.md) provides a basic starting spreadsheet with an example (model included) to show how to calculate model modification commands, both create and compare.


Each of these projects has their own sub README with more details. Please contact `ingrid-nerdman@gtri.gatech.edu` with questions.

### Goals to Bring Rapid Modeling Tools to a 1.0 Release:

Owing to the difficulty of automatic testing with the MagicDraw software the exact MagicDraw versions supported remains unknown. However, we have seen success with Cameo 19.0 and Python 3.6+.

- Establish Ingrid Nerdman as a MagicDraw plugin
- Include CI
- Expand coverage of the UML Metamodel in both JSON subgraph definition and Player Piano capability

This tool is intended for MBSE professionals and advanced technical users. Users of this tool set do so at their own risk.
Each of these projects has their own sub README with more details. Please contact ingrid-nerdman@gtri.gatech.edu with questions.

## Design

### Use Cases (purposes)
Rapid Modeling Tools (RMT) are designed to help domain experts and engineers express their efforts in a system model without having to know the intimate details of SysML.  The below use cases capture the essence of how domain expert engineers and modeling engineer interact with RMT to support system engineering and domain engineering processes.

![UseCases](diagrams/Rapid%20Modeling%20Tool%20-%20Use%20Cases.png)

### Components
The RMT is comprised of four major components: an ingestion grid that captures design patterns, a set of model patterns, a translator which matches design patterns to model patterns and creates lists of model transformations, and then the player piano which will execute the model transformations using the Cameo Systems Modeler API.  The component hierarchy, and the hiearchy within usage context are shown in the next two images below.

![ComponentHierarchy](diagrams/Rapid%20Modeling%20Tool%20-%20Component%20Hierarchy.png)

![ComponentHierarchyInContext](diagrams/Rapid%20Modeling%20Tool%20Context.png)


### Workflows
At a high level, the notional workflow is as captured below in a sequence diagram.  The domain expert / engineer will inform for the modeling expert the design patterns they wish to capture.  The modeling expert will create a way of capturing that in a spread sheet (ingestion grid) and a modeling pattern file (captured in JSON) that matches that design pattern.  The domain expert will then fill out the spread sheet and give it to the modeling expert.  The modeling expert will then use the rest of the rapid modeling tools suite to translate the design patterns captured in the spreadsheet(s) into model transformation lists, then execute those model transformations using the Cameo Systems Modeler built-in API.


![HighLevelSequencing](diagrams/Usage%20-%20High%20Level%20Sequence%20Diagram.png)

![LowLevelSequencing](diagrams/Usage%20-%20Low%20Level%20Sequence%20Diagram.png)

### Item Flows

The items flowing across the components are depicted below.  There are four major items that flow using three major formats:

 - Design Patterns <--> Excel Workbook / Worksheets
 - Modeling Patterns <--> JSON
 - Model Transformation Lists <--> JSON
 - Model Transformations <--> CSM (MagicDraw) API Calls

![ComponentHierarchyInContext](diagrams/Rapid%20Modeling%20Tool%20-%20Internal%20Flows.png)

![ComponentHierarchyInContext](diagrams/Rapid%20Modeling%20Tool%20Context%20-%20Internal%20Flows.png)
