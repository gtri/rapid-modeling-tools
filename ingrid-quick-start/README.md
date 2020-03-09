# Quick Start

## The Example Model

The distribution of this tool includes a configured Excel file with the capability to calculate inputs to the modeling templates. The Excel file uses multiple formulas facilitating the entry of architectural entities and relationships in a modeling style compatible with SysML and requires no knowledge of SysML. The model captures the basic composition of a system, the major working components, connections and interfaces between them. As a fun and illustrative exercise, the file provided here outlines the open source description of a Tesla 3-style electric sedan. To incorporate the example Excel file into the Ingrid Nerdman workflow, the user must export individual, black tabbed, sheets; otherwise, the Excel file is configured for immediate use.

### Major Tabs

The first tab in the example model serves as a README to guide you through the use of the other sheets. Multiple sheets support the entry of useful information like the description of components, their composition into their assembly parent, full assembly paths for components, and connections between components. Using formulas within these sheets process the data to fill information into the SysML-oriented templates matching specific, pre-defined modeling patterns (living as JSON templates for the Ingrid tool).

## Processing Steps

### Creating the Input Files

Directly export black-colored tabs for processing with Ingrid. To export the black-colored tabs, use Excel's built-in copy capability to create a new workbook containing only the desired sheet. This leaves the links inherent to the cells active. Removing this dependency, involves bulk selecting (such as holding Ctrl-Shift and using the arrow keys) the data followed by copy-paste special (values) to make cells containing the values.

**It is imperative that you name the sheet containing this data after the modeling pattern you choose to use. Be sure that this pattern has an accompanying JSON file in the patterns directory.** In effect if you wish to create a composition model then the sheet containing the data mentioned above should be named "Composition" to mirror the `composition.json` file in the [patterns](../ingrid/src/model_processing/patterns) directory. See the guide to creating a JSON pattern template to learn how to define your own modeling pattern.

![](excel_copy_screen.png)

Name the first sheet you export with the following convention "_PatternName_ Starter.xlsx." The rest of the sheets should follow a similar convention "_PatternName_ Update.xlsx." The Player Piano script takes further steps to set baselines and add references to the elements crated in MagicDraw. In this example, we use the "SystemParts" tab as the starter file and compute the others as updates.

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

To add more information to the model, use the "System Spatial Parts Update.xlsx" as the update file. Open the file (it should contain the singular SystemSpatialParts tab) and add a "Renames" tab. Name Cell A1 "new name" and cell B1 "old name." Now make a "SystemSpatialParts IDs" tab. Populate this sheet by copying all the data and the headers from the newly-created `*.csv` file and paste it into the new IDs tab. Save this file. Similarly, include the IDs in the "System Spatial Parts Baseline.xlsx" and re-save this file. Now issue the command:

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

### Possible Issues

If patterns are properly defined, there is a chance that the Player Piano will result in Cameo posting errors about model corruption or ill-formedness. This is likely due to a missing relationship or meta-attribute from the pattern. For example, if Properties do not have owners specified, this is considered an ill-formed model and it will trigger Cameo's model corruption detection.
