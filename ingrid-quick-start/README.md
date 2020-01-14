# Quick Start Guide and FALQ (Frequently Asked Leading Questions)

## Why Was This Tool Made?

Ingrid Nerdman capitalizes on the wealth of system model information described in a small number of common modeling patterns, from a modeling structure perspective. After identifying a common modeling patter, the systems engineering task becomes that of a data entry problem resulting in many systems engineering products capturing data in spreadsheets. Spreadsheets alone lack the structure to mark differences in the kids of information captured (components vs. functions), readily apparent to computers or even non-subject matter experts. Meanwhile, subject matter experts endow the data with semantic annotations without understanding how to express those annotations through the data structures. Thus, Ingrid seeks to address these issues by combining the data collection, semantic annotation and model creation into one workflow. Inspired by the approach taken by the Maple MBSE tool and the Excel Import in Cameo Systems Modeler, Ingrid Nerdman collects data from subject matter experts and non-subject matter experts in the form of an Excel spreadsheet and creates a wholly formed Cameo Model.

Commonly on MBSE projects, modeling professionals find themselves overwhelmed by the volume of information to capture, spending inordinate amounts of time transcribing those data. Ultimately, hurting the productivity of the team and preventing them from taking full advantage of their models; preparing queries and reports to support the larger engineering team. Automating the most straightforward and voluminous parts of the data wrangling effort, collecting and structuring the data according to common modeling patterns, allows the modeling experts to focus on best uses of those dat.

### If Inspired by Commercial Tools, Why Make a New One?

Primarily because it involves filling in gaps left behind by existing tools.

For one - Maple MBSE does not do comparisons between baseline models and updates on its own. It relies upon the facilities of the Teamwork Cloud or other modeling tools. Having Ingrid perform the change calculations makes it independent of the modeling tool used. It should be compatible with Cameo, Integrity Modeler, Rhapsody, Papyrus, or any other modeling tool. This also allows for engineers that do not have access to any of these tools to act as configuration managers to check that the collected and updated data are ready to go into the model.

For another - Cameo importers work well with string or value fields but do not handle importing the connections between modeling elements gracefully. Thus to making complete model updates requires additional effort. Here we can point out that the existence of the Excel and CSV imports lead the Ingrid team to de-emphasize bulk loading of these values and focus on the development of importing model elements and their links to each other.

## How Do I Get the Tool?

You have already succeeded in step one, which is to make it to this site. The tool is set up to be installed within a controlled conda environment after it is cloned from this Git repository.

See the README.md file for step-by-step install instructions for the Ingrid component.

The Player Piano component is a Groovy script intended to be run in Cameo System Modeler through the macro facility.

The player piano takes the basic commands created by the ingrid code (e.g., create, replace, rename elements and attributes) and makes them compatible with the Cameo OpenAPI. A similar script could be written for any other modeling tool.

In Cameo, go to the Tools > Macros > Organize Macros menu as shown below. Then click the "Add" button to get to the Macro Information Dialog.

![](macros_organize_screen.png)

![](macro_config_screen.png)

In the Macro Information dialog, set the macro name to "Player Piano." Set the Macro Language to Groovy and then locate the player-piano-script.groovy file and set it as the file for the macro. Press OK and the macro should now be loaded into your Cameo installation.

Once the macro is loaded, it there will now be a Tools > Macros > Player Piano menu item. Use this to launch the macro.

# Quick Start

## The Example Model

The distribution of this tool includes a configured Excel file with the capability to calculate inputs to the modeling templates. The Excel file uses multiple formulas facilitating the entry of architectural entities and relationships in a modeling style compatible with SysML and requires no knowledge of SysML. The model captures the basic composition of a system, the major working components, connections and interfaces between them. As a fun and illustrative exercise, the file provided here outlines the open source description of a Tesla 3-style electric sedan. To incorporate the example Excel file into the Ingrid Nerdman workflow, the user must export individual, black tabbed, sheets; otherwise, the Excel file is configured for immediate use.

### Major Tabs

The first tab in the example model serves as a README to guide you through the use of the other sheets. Multiple sheets support the entry of useful information like the description of components, their composition into their assembly parent, full assembly paths for components, and connections between components. Using formulas within these sheets process the data to fill information into the SysML-oriented templates matching specific, pre-defined modeling patterns (living as JSON templates for the Ingrid tool).

## Processing Steps

### Creating the Input Files

Directly export black-colored tabs for processing with Ingrid. To export the black-colored tabs, use Excel's built-in copy capability to create a new workbook containing only the desired sheet. This leaves the links inherent to the cells active. Removing this dependency, involves bulk selecting (such as holding Ctrl-Shift and using the arrow keys) the data followed by copy-paste special (values) to make cells containing the values.

![](excel_copy_screen.png)

Name the first sheet you export with the following convention "<PatternName> Starter.xlsx." The rest of the sheets should follow a similar convention "<PatternName> Update.xlsx." The Player Piano script takes further steps to set baselines and add references to the elements crated in MagicDraw. In this example, we use the "SystemParts" tab as the starter file and compute the others as updates.

### First Import Using "Create" Mode

Once exported, run the "System Parts Starter.xlsx" file through the Ingrid component in create mode by issuing the following command (assuming the files located in a directory parallel to the `ingrid` directory). This command will generate a new JSON file.

`anaconda-project run cli --create --input "..\Ingrid Quick Start\System Parts Starter.xlsx"`

In Cameo, open the "Import Example Base.mdzip" file. Then use the Tools > Macros > Player Piano menu item to launch the player piano script. Select a Package to be your default landing package ("Core Model"):

![](select_package_screen.png)

Then select your new `*.json` file to be the source of update instructions. If you did not specify the output directory then `ingrid` placed the output JSON in the same directory as the input file.

After the script runs, you should see a bunch of new modeling elements in the Package:

![](post_import_ct_screen.png)

In addition to the model update, there will be a new `*.csv` file with the same name as your `*.json` file.
The Player Piano generates this `*.csv` file to inform you of the newly created model elements as well as their associated MagicDraw IDs, required for further calculations.

### Adding Updates from Other Patterns Using "Compare" Mode

To add more information to the model, use the "System Spatial Parts Update.xlsx" as the update file. Open the file (it should just be the one SystemSpatialParts tab) and add a "Renames" tab. Name Cell A1 "new name" and cell B1 "old name." Now make a "SystemSpatialParts IDs" tab. Populate this sheet by copying all the data and the headers from the just-created `*.csv` file and paste it into the new IDs tab. Save this file. Similarly, include the IDs in the "System Spatial Parts Baseline.xlsx" and re-save this file. Now issue the command:

`anaconda-project run cli --compare --original "..\Ingrid Quick Start\System Spatial Parts Baseline.xlsx" --update "..\Ingrid Quick Start\System Spatial Parts Update.xlsx"`

This generates a new "graph_diff_changes 0-1(date-time).json" output file with new instructions. Rename this to "System Spatial Parts Update.json."

Run the Player Piano macro as before to find new model elements, and a new `*.csv` file recording the new elements with their IDs.

![](post_update_ct_screen.png)

You can continue to do the same with the "Interface Connection" tab and the "Interface Delegation" tab and you will have a new model!

### Rename Components and Updating Using "Compare" Mode

Part of Ingrid's change computations includes renames. To preform a simple rename, suppose you have an excel file titled "Composition Baseline.xlsx" which contains an entry "Car". Further suppose that you wish to rename all references to "Car" to "Tesla". For such an action, create a copy of the "Composition Baseline.xlsx", rename all instances of "Car" to "Tesla" in the pattern sheet, in the renames sheet under the "new name" column populate a cell with "Tesla" and the corresponding "old name" cell with "Car", and ensure that the IDs sheet contains the IDs for the model and save this changed sheet as "Composition Update.xlsx." Now issue the compare command as before:

`anaconda-project run cli --compare --original "..\Composition Baseline.xlsx" --update "..\Composition Update.xlsx"`

Once again, execute the Player Piano macro on the created JSON change file and you have now updated all instance of Car in your model to Tesla.

Ingrid supports computing model changes and renames simultaneously. This serves as a rudimentary example of the functionality.

Whenever computing changes, Ingrid generates a human readable Excel file, with the same name as the "graph_diff_changes..." JSON file, intended to alert the user to the changes the JSON file will make in the model and any instances where Ingrid could not determine the user's intention.

### Modifying Interface Type Using "Compare" Mode

Blah

### Possible Issues

If patterns are properly defined, there is a chance that the Player Piano will result in Cameo posting errors about model corruption or ill-formedness. This is likely due to a missing relationship or meta-attribute from the pattern. For example, if Properties do not have owners specified, this is considered an ill-formed model and it will trigger Cameo's model corruption detection.
