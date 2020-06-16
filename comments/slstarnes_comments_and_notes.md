# Luke's Comments and Notes

Note: Each finding has a status flag (or will soon) at the start of the finding. These flags are defined below:
* **[INFO]** - information only, no action required
* **[HEADING]** - heading bullet, information only, no action required
* **[IN PROGRESS]** - Shane is working to address finding
* **[WAITING]** - this finding may be OBE, but we are waiting on something to know for sure. No action for now.
* **[IN PR]** - this finding is reflected in the changes within the PR, so does not need to be thought of as separate finding.
* **[OPEN]** - finding needs to be assessed by Shane
* **[CLOSED]** - finding has been addressed
* **[IGNORE]** - this finding is overcome by events or in error or no longer relevant. 
---
* **[INFO]** I am viewing the `README.md` file in the root as the README for the standard user (i.e. not a developer) and the `ingrid/README.md` file is intended for "advanced users" / devers. This is why I made the changes to the base README to include the install usage information.    
* **[HEADING]** Excel file (`/ingrid_quick_start/Example Data.xlsx`) comments
  * **[IN PROGRESS]** Shane and I discussed -- the spreadsheet has some issues and seems to have always had issues. Shane is going to talk to others in SER to see if the issues can be fixed or if we should change Quick Start to use a simpler spreadsheet. 
  * **[WAITING]** In general I think you need some more explanation on this spreadsheet. I don't see anything really. I do not think you expect for your users to all intuit the purpose of every tab / column.
    * I do not think it is unreasonable (I know it seems a bit pedantic, but i think it would be of value) to have a markdown file where you list each tab and column and provide a brief description....
       * Part Type Split
         * Component - the component of the automobile 
         * Role - the role of the component in the automobile          
  * **[WAITING]** on the README tab you list 4 colors. However, you have 2 tones of blue and 2 tones of green in addition to light orange and black. 
  * **[WAITING]** Tab `Component Report`, Column F - has `#REF!` errors. 
  * **[WAITING]** Tab `Component Report`, Column G - This is a direct pointer to column D on the `Component Tracking` tab. But, that column is empty. I would populate the source column. 
  * **[WAITING]** Tab `Component Report`, Columns C,D,E,G - These are all direct pointers (pointing to a specific cell). Why not a VLOOKUP or INDEX/MATCH? Doing something like that would allow the rows to be in different orders. If they are the same then why have the data on 3 separate sheets?
  * **[WAITING]** Tab `Part-Assembly Locators`, Columns B,C - What does the black column name mean? Does it mean "don't touch this"? If so, i didn't see that documented. Secondly, if this is what it means then why isn't column B black since it is also a formula? There needs to be clarity as to what the user modifies.  
  * **[WAITING]** Tab `Part Type Split`, Column F - I would use this formula `=COUNTIF($D$2:D2,"Basic")`. When you drag it down it will count occurrences of Basic between start and current row. You can do the same for Index and Spatial. 
  * **[WAITING]** Tab `Delegation Counters`, Column O - There is a note that doesn't seem to belong - "One more thing to know - is this last delegation for the row?"'
  * **[WAITING]** Tab `Delegation Counters`, Columns A-F - `#REF!` errors occur because you are pointing to rows on `Connections` that are empty.
  * **[WAITING]** Tab `Delegation Counters`, Columns K-N - `#N/A` errors occur because the vectors selected in the formulas are of different lengths. 
* **[HEADING]** Quick Start Readme (`ingrid-quick-start/README.md`)
  * **[IN PR]** This file tells the user to use `anaconda-project`, but this should not be a requirement to run the app.
  * **[HEADING]** There is quite a few questions I have from the _Creating the Input Files_.   
    * **[IN PR]** Is the user to export all of the black-colored tabs? This seems to be implied, but is not clear. I reworded things assuming this was the case, but I am not sure.
    * **[IN PR]** What is meant by the sentence that begins "Removing this dependency..." Are you telling the user why the did the copy or is this (the bulk selecting) a task they are supposed to execute?
    * **[OPEN]** There should be a better introduction to the concept of "you need a modeling pattern" than the statement about file naming. It sounds like I need to pick a modeling pattern. Is it safe to assume your users know what this will mean? If not, then you should provide a bit more info, but even if they do then it should be broached before talking about file naming.One option is to link to the `../ingrid/src/model_processing/patterns/README.md` file.
    * **[OPEN]** This sentence is confusing -- `In effect if you wish to create a composition model...`.  First, what data is mentioned above?
    * **[IN PR]** Looking at the code in `commands.py`, it looks like you cycle through the sheets in the workbook. This is confusing with this quick start writeup which sounds like I am to make 1 workbook for each black tab. NOTE: as part of the PR I changed the quickstart to say "...export any of the black-colored tabs that you would like to import...". I think this makes it clearer.   
* **[HEADING]** Ingrid Readme (`ingrid/README.md`)
  * **[INFO]** I ran the setup as documented in this PR's Ingrid/readme.md. I create a basic python 3.6 env and install anaconda-project. I then run prepare and run setup. All of that is successful. this is the setup for the following findings.
  * **[OPEN]** When I run `anaconda-project run make-html` I get a make error --- `make: *** No rule to make target html.  Stop.`. Note I am on a Mac.   
    * **[INFO]** The issue is that the make (or make.bat) are not present. I am pretty sure the `sphinx-quickstart` script is what creates the Makefile and a make.bat. Since I haven't run that I don't have the make file. 
    * **[INFO]** I did also try `sphinx-build -b html src/model_processing doc` but got an error saying `config directory doesn't contain a conf.py file`. 
  * **[OPEN]** When I ran `anaconda-project run test` it found 7 failures. 3 of these were in `test_commands.py`, 2 were in `test_graph_creation.py`, 2 were in `test_utils.py`.
  * **[OPEN]** Under Example Commands where you show the --compare example, the description needs to be expanded. I added this but didnt know how to complete the sentence. Right now it says `this will run model_processing to compare...`
  * **[OPEN]** The API section needs to be reviewed for accuracy. Specifically the description for the input, original, and updated flags need to be checked.    
* **[HEADING]** Patterns (`../ingrid/src/model_processing/patterns/README.md`)
  * **[OPEN]** Looking at these JSON files they seem specific to your spreadsheet. If I am doing a new project would I need to create new json files? I have not seen any discussion about updating / creating pattern files. The quick start makes it sound like if I want to make new patterns I can rather than -- unless you are using this dummy show-and-tell spreadsheet you have to create your own patterns. 
  * **[OPEN]** If the user creates a new pattern then they should go somewhere other than deep in this `src` folder like maybe `~/patterns` or `./patterns`.
  * **[IGNORE]** (Once i changed the install method this went away) These files do not come over as part of the install which means that the `PATTERNS` variable is pointing to a non-existent path. This means that the `json_patterns` variable under commands.create_md_model is always an empty list (`[]`).  When I say it doesn't come over, what I mean is that when i go look in the install directory (~/miniconda3/envs/model_processing/lib/python3.6/site-packages/model_processing-0.1.0-py3.6.egg/model_processing/) there is not a patterns folder.  
* **[HEADING]** General model_processing comments
  * **[OPEN]** I ran a simple create command and pointed to a single Excel file. The file had two sheets named `SystemSpatialParts` and `Sheet2`. I got this error -- `RuntimeError: Unrecognized sheet names for: SystemSpatialParts.xlsx`.  Does this mean that there can only be one sheet in the workbook? If so this should provide a more helpful error / graceful exit. 
  * **[OPEN]** I ran a simple create command and pointed to a single Excel file. The file had two sheets named `SystemSpatialParts` and `interfacedelegation`. I got this error -- `IndexError: single positional indexer is out-of-bounds`.  This is caused by graph_creation.py line 982 in add_missing_columns: `first_node_data = self.df.iloc[:, 0]`


Luke's Remaining Taskers:
* Finish going through quick start. I am at the point to import into Cameo. (I finally got a Cameo VM.)


     