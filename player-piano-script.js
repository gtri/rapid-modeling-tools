var CollectionsAndFiles = new JavaImporter(
    com.nomagic.magicdraw.automaton,
    com.nomagic.magicdraw.core,
    com.nomagic.magicdraw.openapi.uml,
    com.nomagic.uml2.ext.magicdraw.classes.mdkernel,
    com.nomagic.uml2.impl.ElementsFactory,
    com.nomagic.uml2.ext.jmi.helpers.CoreHelper,
    com.nomagic.uml2.ext.jmi.helpers,
    com.nomagic.magicdraw.ui.dialogs.selection,
    com.nomagic.magicdraw.ui.dialogs,
    java.io.FileReader,
    java.io.BufferedReader,
    java.lang.StringBuilder,
    javax.swing.JFileChooser,
    java.io.File);

with(CollectionsAndFiles)
{
    try
    {
        live_app = Application.getInstance();
        live_log = live_app.getGUILog();
        live_project = live_app.getProject();
        
        sysml_package = live_project.getElementByID("_17_0_2_136f03d9_1344498413266_378771_11852");
              
        // dictionary to hold the ids discovered as we go
        temp_ids = {};
        temp_elements = {};
        var homeless_elements = [];
        ends_to_nuke = [];
        c_ends_to_nuke = [];
        
        try {
            // totally butt-pull based on snippet of OpenMBEE code on GitHub - thanks Doris!
            sel = new SelectElementInfo(false, false, null, true);
            dialogParent = MDDialogParentProvider.getProvider().getDialogParent();
            ele_selection = ElementSelectionDlgFactory.create(dialogParent);
            
            selectableFilter = new TypeFilterImpl([com.nomagic.uml2.ext.magicdraw.classes.mdkernel.Package.class]);
            visibleFilter  = new TypeFilterImpl([com.nomagic.uml2.ext.magicdraw.classes.mdkernel.Package.class]);
            
            ElementSelectionDlgFactory.initSingle(ele_selection, sel, selectableFilter, visibleFilter, [], null);
            
            default_home = null;
            
            ele_selection.show();
            
            if (ele_selection.getResult() == com.nomagic.ui.DialogConstants.OK
                && ele_selection.getSelectedElement() != null) {
                default_home = ele_selection.getSelectedElement();
            }
            
            live_log.log('Default home is now ' + default_home.getHumanName());
        }
        catch(err){
            live_log.log('Failed to create picker.');
            live_log.log(err);
        }
        finally {
        
        }
        
        // select file to pull data from
        
        try {
            chooser = new JFileChooser();
            returnVal = chooser.showOpenDialog(parent);
            if(returnVal == JFileChooser.APPROVE_OPTION) {
               fc = chooser.getSelectedFile();
            }
        // It feels weird to use imported Java to load files - there must be a pure JavaScript way to do this
            fis = new FileReader(chooser.getSelectedFile());
            reader = new BufferedReader(fis);
            stringBuilder = new StringBuilder();
        }
		catch(err){
		    live_log.log('Failed to open file.');
		}
		finally {
		}
		
		try {
		    
            while((line = reader.readLine()) != null) {
                stringBuilder.append(line);
            }
            
            var changes_to_make = null;
            
            try {
                changes_to_make = JSON.parse(stringBuilder.toString());
            }
            catch(err){
                live_log.log('JSON parse failed.');
            }
            finally{
            
            }
            
            // change object can now be cycled to make changes on selected objects
            
            // start the editing session to make changes to the model
            
            com.nomagic.magicdraw.openapi.uml.SessionManager.getInstance().createSession("Modify Model from File");
            
            live_log.log('Model session created.');
            
            ele_factory = live_project.getElementsFactory();
            
            live_log.log('Element factory acquired.');
            
            model_mgr = ModelElementsManager.getInstance();
            
            live_log.log('Model element manager acquired.');
            
            for (change_no in changes_to_make['modification targets']) {
                live_log.log(changes_to_make['modification targets'][change_no]);
                
                // start by looking at what model element to modify
                
                item_to_edit = changes_to_make['modification targets'][change_no]['id'];
                
                // read operations to apply to the selected model element
                
                for (op_no in changes_to_make['modification targets'][change_no]['ops']) {
                    op_to_execute = changes_to_make['modification targets'][change_no]['ops'][op_no];
                    op_type = op_to_execute['op'];
                    live_log.log('Op type: ' + op_type);
                    live_log.log('Op value: ' + op_to_execute['value']);
                    
                    if (op_type == 'replace'){
                    
                        try {
                            // if item was created this session, you can't get it by ID.
                            
                            ele_to_mod = null;
                            
                            if (item_to_edit.split("_")[0] == 'new') {
                                ele_to_mod = temp_elements[item_to_edit];
                            }
                            else {
                                ele_to_mod = live_project.getElementByID(item_to_edit);
                            }
							
							if (ele_to_mod == null) {
								live_log.log("Don't have an element to mod!");
							}
                            
                            // determine if the target is a standard language attribute or an attribute
                            // due to a custom Stereotype
                            
                            // TODO: extend beyond one step in the path
                            attribute_to_hit = null;
                            
                            if (op_to_execute['path'] != null) {
                                attribute_to_hit = op_to_execute['path'].split("/m2/")[1];
                                live_log.log('Op target: ' + attribute_to_hit);
                            }
                            
                            // implement shortcut for value properties using the keyword "value" under the replace operation
                                                        
                            value_shortcuts = op_to_execute['value'];
                            if (value_shortcuts != null && attribute_to_hit == null){
                                // iterate keys to find needed properties to load - note that we use name : type notation
                                live_log.log("Found a value shortcut!");
                                for(var index in value_shortcuts) {
                                    live_log.log(index + " : " + value_shortcuts[index]);
                                    split_point = index.split(" : ");
                                    new_name = "";
                                    type_to_get = null;
                                    if (split_point.length > 1) {
                                        new_name = split_point[0];
                                        // hunt for the value type of interest
                                        
                                        live_log.log("Trying to find " + split_point[1]);
                                        
                                        type_to_get = com.nomagic.magicdraw.uml.ClassifierFinder.findClassifierOrDataType(live_project, split_point[1], [], null);
                                        live_log.log("Property will have type " + type_to_get.getName());
                                        
                                    }
                                    else {
                                        new_name = index;
                                        type_to_get = com.nomagic.magicdraw.uml.ClassifierFinder.findClassifierOrDataType(live_project, "String", [], sysml_package);    
                                    }
                                    live_log.log("New value property name will be: " + new_name + " owner id should be " + item_to_edit);
                                    
                                    new_val_prop = ele_factory.createPropertyInstance();
                                    
                                    live_log.log("New property created.");
                                    
                                    if (item_to_edit.split("_")[0] == 'new') {
                                        owning_element = owning_element = temp_elements[item_to_edit];
                                        new_val_prop.setOwner(owning_element);
                                    }
                                    new_val_prop.setName(new_name);
                                    
                                    if (type_to_get != null){
                                        new_val_prop.setType(type_to_get);            
                                    }
                                    
                                    live_log.log("Property should have value of " + value_shortcuts[index]);
                                    
                                    if (type_to_get.getName() == "String") {
                                        new_val_literal = ele_factory.createLiteralStringInstance();
                                        new_val_prop.setDefaultValue(new_val_literal);
                                        new_val_literal.setValue(value_shortcuts[index]);
                                    }
                                    else {
                                        new_val_literal = ele_factory.createLiteralRealInstance();
                                        new_val_prop.setDefaultValue(new_val_literal);
                                        new_val_literal.setValue(value_shortcuts[index]);
                                    }
                                    
                                    StereotypesHelper.createStereotypeInstance(new_val_prop);
                                                                        
                                    ele_asi = new_val_prop.getAppliedStereotypeInstance();
                                    
                                    class_list = ele_asi.getClassifier();
                                    apply_stereo = StereotypesHelper.getStereotype(live_project, "ValueProperty");
                                    
                                    live_log.log('Found stereotype to apply ' + apply_stereo.getHumanName());
                                    
                                    class_list.add(apply_stereo); 
                                }
                            }
                            
                            try {
                            
								switch(attribute_to_hit) {
									case "Documentation":
										live_log.log('ele_to_mod is ' + ele_to_mod.getID());
										live_log.log('Element has documentation ' + CoreHelper.getComment(ele_to_mod));
										CoreHelper.setComment(ele_to_mod, op_to_execute['value']);
										break;
									case "association":
									    end_element = null;
                                        if (op_to_execute['value'].split("_")[0] == 'new') {
                                            end_element = temp_elements[op_to_execute['value']];
                                        }
                                        else {
                                            end_element = live_project.getElementByID(op_to_execute['value']);
                                        }
                                        live_log.log('New association of object: ' + ele_to_mod.getHumanName() + ' is ' + end_element.getHumanName());
                                        
                                        // API forces you to go the opposite direction
                                        
                                        ele_to_mod.setAssociation(end_element);
                                        break;   
									case "defaultValue":
										live_log.log('Working property default value of ' + op_to_execute['value'] + ' on ' + ele_to_mod.getHumanName());
										// check to see if literal value is already owned by property
										test_val = ele_to_mod.getDefaultValue();
										if (test_val == null){
											new_real_val = ele_factory.createLiteralRealInstance();
											new_real_val.setValue(op_to_execute['value']);
										}
										else {
											test_val.setValue(op_to_execute['value']);
										}
										break;
									case "memberEnd":
										end_element = null;
										if (op_to_execute['value'].split("_")[0] == 'new') {
											end_element = temp_elements[op_to_execute['value']];
										}
										else {
											end_element = live_project.getElementByID(op_to_execute['value']);
										}
										live_log.log('New memberEnd of object: ' + ele_to_mod.getHumanName() + ' is ' + end_element.getHumanName());
										
										// API forces you to go the opposite direction
										
										end_element.setAssociation(ele_to_mod);
										break;
									case "nestedClassifier":
									    owned_element = null;
									    if (op_to_execute['value'].split("_")[0] == 'new') {
                                            owned_element = temp_elements[op_to_execute['value']];
                                        }
                                        else {
                                            owned_element = live_project.getElementByID(op_to_execute['value']);
                                        }
                                        
                                        live_log.log("Owned element is " + owned_element.getHumanName());
                                        
                                        ele_to_mod.setOwner(owned_element);
                                        
                                        homeless_new = [];
                                        for (homeless in homeless_elements){
                                            if (homeless_elements[homeless] == ele_to_mod) {
                                               // do nothing
                                            }
                                            else {
                                                homeless_new.push(homeless_elements[homeless]);
                                            }
                                        }
                                        
                                        homeless_elements = homeless_new;
                                        
									case "owner":
										owning_element = null;
										if (op_to_execute['value'].split("_")[0] == 'new') {
											owning_element = temp_elements[op_to_execute['value']];
										}
										else {
											owning_element = live_project.getElementByID(op_to_execute['value']);
										}
										
										live_log.log('New owner of object: ' + ele_to_mod.getHumanName() + ' is ' + owning_element.getHumanName());
										ele_to_mod.setOwner(owning_element);
										
										if (homeless_elements.includes(ele_to_mod)) {
											homeless_elements.remove(ele_to_mod);
										}
										break;
									case "propertyPath":
									   element_path_list = [];
									   element_value_list = [];
									   
									   live_log.log("Ele to mod for property path is " + item_to_edit);
									   
									   for (path_place in op_to_execute['value']) {
                                           if (op_to_execute['value'][path_place].split("_")[0] == 'new') {
                                               element_path_list.push(temp_elements[op_to_execute['value'][path_place]]);
                                           }
                                           else {
                                               element_path_list.push(live_project.getElementByID(op_to_execute['value'][path_place]));
                                           }
                                       }
									   
									   // apply the stereotype
									   
									   apply_stereo = StereotypesHelper.getStereotype(live_project, "NestedConnectorEnd");
									   
									   // element to get the slot defining feature from
									   
									   //pp_stereo = StereotypesHelper.getStereotype(live_project, "ElementPropertyPath");
									   pp_prop = null;									   
									   
									   for (pp_att in apply_stereo.getMember()) {
									       if (apply_stereo.getMember()[pp_att].getName() == "propertyPath") {
									           pp_prop = apply_stereo.getMember()[pp_att];
									       }
									   }
									   
									   //pp_slot = StereotypesHelper.getSlot(ele_to_mod, pp_prop, true);
									   
									   com.nomagic.uml2.ext.jmi.helpers.StereotypesHelper.addStereotype(ele_to_mod, apply_stereo);
									   
									   ele_asi = ele_to_mod.getAppliedStereotypeInstance();
									   
									   for (asi_class in ele_asi.getClassifier()) {
									       live_log.log("Property Path classifier includes " + ele_asi.getClassifier()[asi_class].getName());
									   }
									   
									   for (asi_slot in ele_asi.getSlot()) {
                                          live_log.log("Property path ASI includes slot " + ele_asi.getSlot()[asi_slot].getDefiningFeature().getName());
                                          //live_log.log("PP Slot = " + pp_slot.getDefiningFeature().getName());
                                      }
									   
									   for (prop_path_step in element_path_list){
									       ele_value = ele_factory.createElementValueInstance();
									       ele_value.setElement(element_path_list[prop_path_step]);
									       live_log.log("New element value " + ele_value.getID() + " has value " + ele_value.getElement().getName());
									       element_value_list.push(ele_value);
									   }
									   
									   for (ele_val in element_value_list) {
									       live_log.log("New element list has value " + element_value_list[ele_val].getID());
									       live_log.log("New element list has value with element " + element_value_list[ele_val].getElement());
									       live_log.log("New element list has value with element name " + element_value_list[ele_val].getElement().getName());
									   }
									   
									   StereotypesHelper.setStereotypePropertyValue
                                            (ele_to_mod, apply_stereo, "propertyPath", element_value_list, true);
                                       
                                       live_log.log("Trying to apply value for " + com.nomagic.magicdraw.sysml.util.SysMLProfile.ELEMENTPROPERTYPATH_PROPERTYPATH_PROPERTY + 
                                            " on stereotype " + apply_stereo.getName() + " on end with role " + ele_to_mod.getID());
                                            
                                       for (asi_slot in ele_asi.getSlot()) {
                                           live_log.log("Property path ASI includes slot " + ele_asi.getSlot()[asi_slot].getDefiningFeature().getName());
                                           for (val in ele_asi.getSlot()[asi_slot].getValue()) {
                                                live_log.log('Value includes ' + ele_asi.getSlot()[asi_slot].getValue()[val].getID());
                                                 ele_asi.getSlot()[asi_slot].getValue()[val].setElement(element_path_list[val]);
                                                live_log.log('Value includes element + ' + ele_asi.getSlot()[asi_slot].getValue()[val].getElement().getName());
                                           }
                                           //live_log.log("PP Slot = " + pp_slot.getDefiningFeature().getName());
                                       }
									   
									   break;
								    case "role":
                                        role_element = null;
                                        if (op_to_execute['value'].split("_")[0] == 'new') {
                                            role_element = temp_elements[op_to_execute['value']];
                                        }
                                        else {
                                            role_element = live_project.getElementByID(op_to_execute['value']);
                                        }
                                        live_log.log('New role of object: ' + ele_to_mod.getHumanName() +
                                            ' [' + ele_to_mod.getID() + ']' + ' is ' + role_element.getHumanName());
                                        
                                        // API forces you to go the opposite direction
                                        
                                        ele_to_mod.setRole(role_element);
                                        break;
									case "type":
										typing_element = null;
										if (op_to_execute['value'].split("_")[0] == 'new') {
											typing_element = temp_elements[op_to_execute['value']];
										}
										else {
											typing_element = live_project.getElementByID(op_to_execute['value']);
										}
										live_log.log('New type of object: ' + ele_to_mod.getHumanName() + ' is ' + typing_element.getHumanName());
										ele_to_mod.setType(typing_element);
										break;
									default:
										var key_member = null;
										var key_member_found = false;
										var key_slot = null;
										var key_slot_found = false;
										var key_literal_found = false;
										// not a predefined location - look at applied Stereotypes
										try {
											ele_asi = ele_to_mod.getAppliedStereotypeInstance();
											live_log.log('At ASI.');
											// look at classifier in case there is no slot
											for (asi_class_index in ele_asi.getClassifier()) {
												class_to_check = ele_asi.getClassifier()[asi_class_index];
												for (class_member_index in class_to_check.getMember()) {
													mem_to_check = class_to_check.getMember()[class_member_index];
													live_log.log('Discovered member: ' + mem_to_check.getName());
													if (mem_to_check.getName() == attribute_to_hit) {
														switch (op_to_execute['op']){
															case "replace":
																live_log.log('Found replace.');
																key_member = mem_to_check;
																key_member_found = true;
																break;    
														}    
													} 
												}    
											}
											
											// if a member has been matched to the path to replace, then see if there is a matching Slot
											
											if (key_member_found) {
											
												for (asi_slot_index in ele_asi.getSlot()) {
													slot_to_check = ele_asi.getSlot()[asi_slot_index];
					
													if (slot_to_check.getDefiningFeature().getName() == attribute_to_hit) {
														switch (op_to_execute['op']){
															case "replace":
																key_slot_found = true;
																key_slot = slot_to_check;
																break;
														}    
													}        
												}
												// Create the slot and value
												if (!key_slot_found) {
													new_slot = ele_factory.createSlotInstance();
													new_slot.owner = ele_asi;
													new_slot.definingFeature = key_member;
													
													// TODO: Decide whether to do literal Integer, Real, or String
													raw_value = op_to_execute['value'];
													new_lit_string = ele_factory.createLiteralStringInstance();
													new_lit_string.owner = new_slot;
													new_lit_string.value = raw_value;
													new_slot.value = new_lit_string;
												}
												else {
													var val_found = false;
													raw_value = op_to_execute['value'];
													// check to see if the slot has a value
													for (val_index in key_slot.getValue()) {
														// if the value is literal string, can simply overwrite string
														if (key_slot.getValue()[val_index] instanceof LiteralString) {
															val_found = true;
															
															key_slot.getValue()[val_index].setValue(raw_value);
															live_log.log('Literal String found: ' + key_slot.getValue()[val_index].getID());
															live_log.log('Literal String value: ' + key_slot.getValue()[val_index].getValue());    
														}
														// if the target is an enumeration literal, then need to match valid literal
														else if (key_slot.getValue()[val_index] instanceof InstanceValue) {
															val_found = true;
															
															key_instance = key_slot.getValue()[val_index].getInstance();
															
															if (key_instance instanceof EnumerationLiteral){
																live_log.log('Enumerator is ' + key_instance.getEnumeration().getHumanName());
																key_enum = key_instance.getEnumeration();
																for (literal in key_enum.getOwnedLiteral()){
																	live_log.log('Enumerator includes ' + key_enum.getOwnedLiteral()[literal].getName());
																	if (key_enum.getOwnedLiteral()[literal].getName() == raw_value) {
																		live_log.log('Matched enumeration literal ' + raw_value);
																		key_slot.getValue()[val_index].setInstance(key_enum.getOwnedLiteral()[literal]);
																	}
																}
															}
															
															live_log.log('Instance Value found: ' + key_slot.getValue()[val_index].getID());
															live_log.log('Instance Value instance: ' + key_instance.getHumanName());
														}        
													}
													if (!val_found) {
														new_lit_string = ele_factory.createLiteralStringInstance();
														new_lit_string.owner = key_slot;
														new_lit_string.value = raw_value;
														key_slot.value = new_lit_string;    
													}
												}
											}
											live_log.log('Applied stereotype instance: ' + ele_asi);
										}
										catch(err) {
											live_log.log('Failed tagged value replace.');
											live_log.log(err);
										}
										finally {
										
										}
										break;
									}
							}
							catch(err) {
								live_log.log('Failed meta-attribute replace.');
								live_log.log(err);
							}
							finally {
							
							}
                        }
                        catch(err){
                            live_log.log('Failed get ele_mod for ' + item_to_edit);
                            live_log.log(err);
                        }
                        finally {
                        
                        }
                    }
                    
                    else if (op_type == 'create') {
                        live_log.log('Found create operation.');
                        // temp landing spot - a default in case ownership is not already set
                        
                        //new_name = 'dummy';
                        //new_meta = 'dummy';
                        
                        try {
                        
                            new_name = op_to_execute['name'];
                            new_meta = op_to_execute['metatype'];
                            new_stereo = op_to_execute['stereotype'];
                            
                            try {
                            
                                switch(new_meta) {
                                
                                    case "Class":
                                        new_element = ele_factory.createClassInstance();
                                        temp_ids[item_to_edit] = new_element.getID();
                                        temp_elements[item_to_edit] = new_element;
                                        new_element.setName(new_name);
                                        homeless_elements.push(new_element);
                                        break;
                                    case "Property":
                                        new_element = ele_factory.createPropertyInstance();
                                        temp_ids[item_to_edit] = new_element.getID();
                                        temp_elements[item_to_edit] = new_element;
                                        new_element.setName(new_name);
                                        break;
                                    case "Port":
                                        new_element = ele_factory.createPortInstance();
                                        temp_ids[item_to_edit] = new_element.getID();
                                        temp_elements[item_to_edit] = new_element;
                                        new_element.setName(new_name);
                                        break;
                                    case "Association":
                                        new_element = ele_factory.createAssociationInstance();
                                        temp_ids[item_to_edit] = new_element.getID();
                                        temp_elements[item_to_edit] = new_element;
                                        new_element.setName(new_name);
                                        homeless_elements.push(new_element);
                                        
                                        ends_to_nuke.push(new_element.getMemberEnd()[0]);
                                        ends_to_nuke.push(new_element.getMemberEnd()[1]);
                                        
                                        live_log.log('New association memberEnds are ' + 
                                            new_element.getMemberEnd()[0].getID() +  ' and ' + 
                                            new_element.getMemberEnd()[1].getID());
                                        
                                        break;
                                    case "Connector":
                                        new_element = ele_factory.createConnectorInstance();
                                        temp_ids[item_to_edit] = new_element.getID();
                                        temp_elements[item_to_edit] = new_element;
                                        new_element.setName(new_name);
                                        
                                        c_ends_to_nuke.push(new_element.getEnd()[0]);
                                        c_ends_to_nuke.push(new_element.getEnd()[1]);
                                        
                                        live_log.log('New connector ends are ' + 
                                            new_element.getEnd()[0].getID() +  ' and ' + 
                                            new_element.getEnd()[1].getID());
                                        
                                        break;
                                    case "ConnectorEnd":
                                        new_element = ele_factory.createConnectorEndInstance();
                                        temp_ids[item_to_edit] = new_element.getID();
                                        temp_elements[item_to_edit] = new_element;
                                        // connector ends are not named elements
                                        break;
                                    case "DataType":
                                        new_element = ele_factory.createDataTypeInstance();
                                        temp_ids[item_to_edit] = new_element.getID();
                                        temp_elements[item_to_edit] = new_element;
                                        new_element.setName(new_name);
                                        homeless_elements.push(new_element);
                                        break; 
                                     
                                }   
                                
                                live_log.log('Will create a ' + new_meta + ' with name ' + new_name);
                                
                                if (new_stereo != null) {
                                    live_log.log('Applying stereotype ' + new_stereo + ' to ' + new_name);
                                    
                                    StereotypesHelper.createStereotypeInstance(new_element);
                                    
                                    ele_asi = new_element.getAppliedStereotypeInstance();
                                    
                                    live_log.log('New ASI for element = ' + ele_asi.getHumanName());
                                    
                                    class_list = ele_asi.getClassifier();
                                    apply_stereo = StereotypesHelper.getStereotype(live_project, new_stereo);
                                    
                                    live_log.log('Found stereotype to apply ' + apply_stereo.getHumanName());
                                    
                                    // apply values to slots
                                    
                                    stereo_path = op_to_execute['path'];
                                    stereo_value = op_to_execute['value'];
                                    
                                    if (stereo_path != null){
                                        live_log.log('Applying value ' + stereo_value + ' on stereotype ' + new_stereo + ' on ' + new_element.getHumanName());
                                    }
                                    
                                    class_list.add(apply_stereo);
                                    
                                    com.nomagic.uml2.ext.jmi.helpers.InstanceSpecificationHelper.setClassifierForInstanceSpecification(class_list, ele_asi, true);
                                    
                                    ele_asi = new_element.getAppliedStereotypeInstance();
                                    
                                    class_list = ele_asi.getClassifier();
                                    
                                    for (cls in class_list) {
                                        live_log.log('New ASI has classifier ' + class_list[cls].getHumanName());
                                    } 
                                }
                                
                            }
                            catch(err) {
                                live_log.log('Failed to create new element.');
                                live_log.log(err);
                            }
                            finally {
                            
                            }
                        }
                        catch(err){
                            live_log.log('Failed to find name or metatype on create.');
                        }
                        finally {
                        
                        }            
                    }
                    else if (op_type == 'rename') {
                        if (item_to_edit.split("_")[0] == 'new') {
                            ele_to_mod = temp_elements[item_to_edit];
                        }
                        else {
                            ele_to_mod = live_project.getElementByID(item_to_edit);
                        }
                        
                        ele_to_mod.setName(op_to_execute['name']);    
                    }  
                }
                
            }
            
            // close the editing session to implement the changes
            
            //SessionManager.getInstance().closeSession();
            
        }
        catch(err){
            live_log.log('Failed factory and targets list try.');
        }
        finally {
            // house the remaining homeless
            
            live_log.log('Have ' + ends_to_nuke.length + ' ends to nuke.');
            
            for (homeless_no in homeless_elements) {
                homeless_elements[homeless_no].setOwner(default_home);
                live_log.log('Housing homeless element ' + homeless_elements[homeless_no].getHumanName());        
            }
            
            for (end_to_nuke in ends_to_nuke) {
                end_ready_to_nuke = ends_to_nuke[end_to_nuke];
                //live_log.log('Should kill memberEnd of ' + end_ready_to_nuke.getOwner().getName());
                //model_mgr.removeElement(end_ready_to_nuke);
                //end_ready_to_nuke.setOwner(null);
                end_ready_to_nuke.setAssociation(null);    
            }
            
            for (c_end_to_nuke in c_ends_to_nuke) {
                c_end_ready_to_nuke = c_ends_to_nuke[c_end_to_nuke];
                //live_log.log('Should kill memberEnd of ' + end_ready_to_nuke.getOwner().getName());
                //model_mgr.removeElement(end_ready_to_nuke);
                //end_ready_to_nuke.setOwner(null);
                c_end_ready_to_nuke.set_connectorOfEnd(null);    
            }
            
            // close the open streams
            reader.close();
            SessionManager.getInstance().closeSession();
            
        }
    }
    catch(err) {
        live_log.log('Failed first try.');
        live_log.log(err);
    }
    finally{
		
    }
}