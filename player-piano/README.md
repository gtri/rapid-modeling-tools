# Player Piano

The script `player-piano-script.groovy` supports the playback of MagicDraw instructions to the Open API to update models according the instructions generated by the `ingrid` tool.

## Unsupported Metatypes and Attributes
If you come across an unsupported metatype or attribute, please add the necessary definition to the switch cases in the `player-piano-script.groovy`.

```groovy
switch(new_meta) {

    case 'Class':
        new_element = ele_factory.createClassInstance();
        temp_ids[item_to_edit] = new_element.getID();
        temp_elements[item_to_edit] = new_element;
        new_element.setName(new_name);
        homeless_elements.add(new_element);
        break;
    .
    .
    .
    case "New Metatype":
        new_element = ele_factory.create__Metatype__Instance(); // This is a MagicDraw API call
        temp_ids[item_to_edit] = new_element.getID();
        temp_elements[item_to_edit] = new_element;
        new_element.setName(new_name);
        homeless_elements.add(new_element);
        ...
```

## Importing Player Piano as a MagicDraw Macro
The player piano takes the basic commands created by the ingrid code (e.g., create, replace, rename elements and attributes) and makes them compatible with the Cameo OpenAPI. A similar script could be written for any other modeling tool.

- With MagicDraw open locate the **Tools** menu
- Select `Tools > Macros > Organize Macros`
- For the `Name`, `Macro Language`, and `File` fields input "Player Piano", select "Groovy", and browse the file explorer (opened by clicking on the three dots button) to the `.../Rapid Modeling Tools/player-piano/player-piano-script.groovy` groovy script.
- Images included below

![](../ingrid-quick-start/images/macros_organize_screen.png)

![](../ingrid-quick-start/images/macro_config_screen.png)

Once the macro is loaded, there will be a `Tools > Macros > Player Piano` menu item. Use this to launch the macro.

The script is written in Groovy, and can be activated in MagicDraw through the Macro Engine. See [MagicDraw Online Documentation](https://docs.nomagic.com/display/MD190/Adding+a+Macro+and+editing+Macro+information) for instructions on how to do this.
