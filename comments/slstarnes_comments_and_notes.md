# Luke's Comments and Notes

Note: Each finding has a status flag (or will soon) at the start of the finding. These flags are defined below:
* **[NO ACTION RQD]** - information only, no action required
* **[HEADING]** - heading bullet, information only, no action required
* **[IN PROGRESS]** - Shane is working to address finding
* **[WAITING]** - this finding may be OBE, but we are waiting on something to know for sure. No action for now.
* **[IN PR]** - this finding is reflected in the changes within the PR, so does not need to be thought of as separate finding.
* **[OPEN]** - finding needs to be assessed by Shane
* **[CLOSED]** - finding has been addressed 
---
    * I do not think it is unreasonable to have a markdown file where you list each tab and column and provide a brief description....
       * Part Type Split
         * Component - the component of the automobile 
         * Role - the role of the component in the automobile
    * I know it seems a bit pedantic, but i think it would be of value            
  * _[WAITING]_ on the README tab you list 4 colors. However, you have 2 tones of blue and 2 tones of green in addition to light orange and black. 
  * _[WAITING]_ Tab `Component Report`, Column F - has `#REF!` errors. 
  * _[WAITING]_ Tab `Component Report`, Column G - This is a direct pointer to column D on the `Component Tracking` tab. But, that column is empty. I would populate the source column. 
  * _[WAITING]_ Tab `Component Report`, Columns C,D,E,G - These are all direct pointers (pointing to a specific cell). Why not a VLOOKUP or INDEX/MATCH? Doing something like that would allow the rows to be in different orders. If they are the same then why have the data on 3 separate sheets?
  * _[WAITING]_ Tab `Part-Assembly Locators`, Columns B,C - What does the black column name mean? Does it mean "don't touch this"? If so, i didn't see that documented. Secondly, if this is what it means then why isn't column B black since it is also a formula? There needs to be clarity as to what the user modifies.  
  * _[WAITING]_ Tab `Part Type Split`, Column F - I would use this formula `=COUNTIF($D$2:D2,"Basic")`. When you drag it down it will count occurrences of Basic between start and current row. You can do the same for Index and Spatial. 
  * _[WAITING]_ Tab `Delegation Counters`, Column O - There is a note that doesn't seem to belong - "One more thing to know - is this last delegation for the row?"'
  * _[WAITING]_ Tab `Delegation Counters`, Columns A-F - `#REF!` errors occur because you are pointing to rows on `Connections` that are empty.
  * _[WAITING]_ Tab `Delegation Counters`, Columns K-N - `#N/A` errors occur because the vectors selected in the formulas are of different lengths. 
* _[HEADING]_ Quick Start Readme (`ingrid-quick-start/README.md`)
  * This file tells the user to use `anaconda-project`, but this should not be a requirement to run the app.
  * There is quite a few questions I have from the _Creating the Input Files_.   
    * Is the the user to export all of the black-colored tabs? This seems to be implied, but is not clear. I reworded things assuming this was the case, but I am not sure.
    * What is meant by the sentence that begins "Removing this dependency..." Are you telling the user why the did the copy or is this (the bulk selecting) a task they are supposed to execute?
    * There should be a better introduction to the concept of "you need a modeling pattern" than the statement about file naming. It sounds like I need to pick a modeling pattern. Is it safe to assume your users know what this will mean? If not, then you should provide a bit more info, but even if they do then it should be broached before talking about file naming.One option is to link to the `../ingrid/src/model_processing/patterns/README.md` file.
    * This sentence is confusing -- `In effect if you wish to create a composition model...`.  First, what data is mentioned above?
    * Looking at the code in `commands.py`, it looks like you cycle through the sheets in the workbook. This is confusing with this quick start writeup which sounds like I am to make 1 workbook for each black tab. 
* Ingrid Readme (`ingrid/README.md`)
  * When I run `anaconda-project run make-html` I get a make error --- `make: *** No rule to make target html.  Stop.`. Note I am on a Mac.   
    * The issue is that the make (or make.bat) are not present. I am pretty sure the `sphinx-quickstart` script is what creates the Makefile and a make.bat. Since I haven't run that I don't have the make file. 
    * I did also try `sphinx-build -b html src/model_processing doc` but got an error saying `config directory doesn't contain a conf.py file`. 
* Patterns (`../ingrid/src/model_processing/patterns/README.md`)
  * Looking at these JSON files they seem specific to your spreadsheet. If I am doing a new project would I need to create new json files? I have not seen any discussion about updating / creating pattern files. The quick start makes it sound like if I want to make new patterns I can rather than -- unless you are using this dummy show-and-tell spreadsheet you have to create your own patterns. 
    * If the user does create patterns then they should go somewhere other than deep in this `src` folder like maybe `~/patterns` or `./patterns`.
  * These files do not come over as part of the install which means that the `PATTERNS` variable is pointing to a non-existent path. This means that the `json_patterns` variable under commands.create_md_model is always an empty list (`[]`).  When I say it doesn't come over, what I mean is that when i go look in the install directory (~/miniconda3/envs/model_processing/lib/python3.6/site-packages/model_processing-0.1.0-py3.6.egg/model_processing/) there is not a patterns folder.  
  
      

     