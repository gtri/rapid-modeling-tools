# Luke's Comments and Notes

* In `ingrid/environment.yml` the name of the conda env is "model-processing-dev". But, this is what you have user install to get started. IOW, this isn't really a dev repo. Long story short -- this is why I removed the "-dev". 
  * I mention somewhere else that perhaps the installation is handled fully through the `setup.py` and if this is the case then the `environment.yml` may be superfluous. 
* Excel file (`/ingrid_quick_start/Example Data.xlsx`) comments
  * In general I think you some more explanation on this spreadsheet. I don't see anything really. I do not think you expect for your users to all intuit the purpose of every tab / column.
    * I would not think it was unreasonable to have a markdown file where you list each tab and column....
       * Part Type Split
         * Component - the component of the automobile 
         * Role - the role of the component in the automobile
    * I know it seems a bit pedantic, but i think it would be of value            
  * on the README tab you list 4 colors. However, you have 2 tones of blue and 2 tones of green in addition to light orange and black. 
  * Tab `Component Report`, Column F - has `#REF!` errors. 
  * Tab `Component Report`, Column G - This is a direct pointer to column D on the `Component Tracking` tab. But, that column is empty. I would populate the source column. 
  * Tab `Component Report`, Columns C,D,E,G - These are all direct pointers (pointing to a specific cell). Why not a VLOOKUP or INDEX/MATCH? Doing something like that would allow the rows to be in different orders. If they are the same then why have the data on 3 separate sheets?
  * Tab `Part-Assembly Locators`, Columns B,C - What does the black column name mean? Does it mean "don't touch this"? If so, i didn't see that documented. Secondly, if this is what it means then why isn't column B black since it is also a formula? There needs to be clarity as to what the user modifies.  
  * Tab `Part Type Split`, Column F - I would use this formula `=COUNTIF($D$2:D2,"Basic")`. When you drag it down it will count occurrences of Basic between start and current row. You can do the same for Index and Spatial. 
  * Tab `Delegation Counters`, Column O - There is a note that doesn't seem to belong - "One more thing to know - is this last delegation for the row?"'
  * Tab `Delegation Counters`, Columns A-F - `#REF!` errors occur because you are pointing to rows on `Connections` that are empty.
  * Tab `Delegation Counters`, Columns K-N - `#N/A` errors occur because the vectors selected in the formulas are of different lengths. 
       
   
  

     