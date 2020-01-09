# Rapid Modeling Tools

## "Ingrid Nerdman (Ingestion Grid Nerdman)"

Developed at Georgia Tech Research Institute by Shane Connelly and Bjorn Cole. Government sponsorship (SOCOM TALOS) acknowledged.

### Installation

**We suggest that you clone this repository.**

Cloning the repository provides you access to add meta model JSON descriptions and update the `player-piano` to create novel model elements.

**Both `ingrid` and `player-piano` have README files detailing further steps for setup.**

### About

Rapid Modeling Tools contains two constituent programs. The `ingrid` tool translates spreadsheet data into object modeling languages such as UML and SysML using a JSON subgraph description. Development of Ingrid focused on the UML metamodel but could in principle support other modeling languages that have a defined metamodel and graph orientation. The `player-piano` works with MagicDraw, as a macro, to interpret the JSON model modification instructions, output from the Ingrid program to, in the MagicDraw API. As long as the user knows the API commands for another modeling tool such as Rhapsody, Capella or Papayrus the instructions produced by Ingrid could build models in those programs. The functionality developed here leaves the door open for the user to build up REST messages in the future.

### Getting Started

The `ingrid-quick-start` provides a basic starting spreadsheet with an example (model included) to show how to calculate model modification commands, both create and compare.


Each of these projects has their own sub README with more details. Please contact `ingrid-nerdman@gtri.gatech.edu` with questions.
