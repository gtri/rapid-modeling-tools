# Rapid Modeling Tools

## AKA "Ingrid Nerdman"

Developed at Georgia Tech Research Institute by Shane Connelly and Bjorn Cole. Government sponsorship (SOCOM TALOS) acknowledged.

This repository collects multiple tools to allow for rapid data entry into object modeling languages such as UML and SysML. The goal of this project is to allow for rapid entry of model data that shares common modeling patterns and approaches. While it was built to work with the UML metamodel, it could in principle support several others that have a defined metamodel and graph orientation.

The repository includes Rick's Cafe Americain, which examines spreadsheets with metadata and calculates how to either create a new model from scratch or make updates to a model to match the data in the spreadsheets.

The player-piano component works with MagicDraw to interpret model modification instructions in the MagicDraw API. It is very easy to change this over to work with other tools such as Rhapsody, Capella, or Papyrus if you know the API commands to add and modify modeling relationships. You could even build up REST messages!

The ingrid-quick-start provides a basic starting spreadsheet with an example to show how to calculate model modification commands.

Each of these projects has their own sub README with more details.