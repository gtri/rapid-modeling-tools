# Rapid Modeling Tools

## AKA "Ingrid Nerdman"

Developed at Georgia Tech Research Institute by Shane Connelly and Bjorn Cole. Government sponsorship (SOCOM TALOS) acknowledged.

This repository collects multiple tools to allow for rapid data entry into object modeling languages such as UML and SysML. The goal of this project is to allow for rapid entry of model data that shares common modeling patterns and approaches. While it was built to work with the UML metamodel, it could in principle support several others that have a defined metamodel and graph orientation.

The repository includes a translator, formerly known as Rick's Cafe Americain, which examines spreadsheets with metadata and calculates how to either create a new model from scratch or make updates to a model to match the data in the spreadsheets.

The player-piano component works with MagicDraw to interpret model modification instructions in the MagicDraw API. It is very easy to change this over to work with other tools such as Rhapsody, Capella, or Papyrus if you know the API commands to add and modify modeling relationships. You could even build up REST messages!

The ingrid-quick-start provides a basic starting spreadsheet with an example to show how to calculate model modification commands.

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


