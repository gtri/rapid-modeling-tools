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
