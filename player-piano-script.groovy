// Java libs
import java.util.ArrayList;
import javax.swing.*;
// Groovy libs
import groovy.json.*;
// NoMagic Open API
import com.nomagic.magicdraw.ui.dialogs.*;
import com.nomagic.magicdraw.ui.dialogs.selection.*;
import com.nomagic.magicdraw.openapi.uml.*;
import com.nomagic.uml2.ext.magicdraw.classes.mdkernel.*;
import com.nomagic.uml2.ext.jmi.helpers.*;
// Other third party libraries

// big outer try - checks on load of API's, key files, etc.
try {
	
	// Have a general log for steps along the way in the program.
	execution_status_log = new ArrayList<String>();
	execution_status_log.add('Started macro.');
	
	command_processing_log = new ArrayList<String>();
	
	// Have a log that goes through all of the model editing operations.
	
	create_log = new ArrayList<String>();
	replace_log = new ArrayList<String>();
	rename_log = new ArrayList<String>();
	
	// an extra detailed log to check that the script is working correctly
	
	verification_log = new ArrayList<String>();

	// get hooks into Cameo for use later
	live_app = com.nomagic.magicdraw.core.Application.getInstance();
	live_log = live_app.getGUILog();
	live_project = live_app.getProject();
	
	// dictionary to hold the ids discovered as we go
	temp_ids = {};
	temp_elements = {};
	homeless_elements = [];
	ends_to_nuke = [];
	c_ends_to_nuke = [];
	
	// try to make the element picker
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
		
		execution_status_log.add('Default home is now ' + default_home.getHumanName());
	}
	catch(Exception e){
		execution_status_log.add('Failed to create picker.');
		execution_status_log.add(e.getMessage());
	}
	finally {
	
	}
	
	// select file to pull data from
	
	stringBuilder = null;
	reader = null;
	
	try {
		dialogParent = MDDialogParentProvider.getProvider().getDialogParent();
		chooser = new JFileChooser();
		returnVal = chooser.showOpenDialog(dialogParent);
		if(returnVal == JFileChooser.APPROVE_OPTION) {
		   fc = chooser.getSelectedFile();
		}
	// It feels weird to use imported Java to load files - there must be a pure JavaScript way to do this
		fis = new FileReader(chooser.getSelectedFile());
		reader = new BufferedReader(fis);
		stringBuilder = new StringBuilder();
		
		execution_status_log.add('Opened file ' + fc.getAbsolutePath());
	}
	catch(Exception e){
		execution_status_log.add('Failed to open file.');
		execution_status_log.add(e.getMessage());
	}
	finally {
	}
	
	parsed_model = null;
	
	// create a new class and use reflection to create it
	
	try {
		// Load the file contents into a string buffer and then use JSON utilities to create
		// a data structure
		
		while((line = reader.readLine()) != null) {
			stringBuilder.append(line);
		}
		
		changes_to_make = null;
		
		try {
			// Groovy has a really nice JSON facility built-in it appears.
			
			jsonSlurper = new JsonSlurper();
			execution_status_log.add('JSON parser created.');
			changes_to_make = jsonSlurper.parseText(stringBuilder.toString());
			execution_status_log.add('JSON parser has parsed text.');
			target_size = changes_to_make['modification targets'].size();
			execution_status_log.add(target_size.toString() + ' modification targets found.');
		}
		catch(Exception e){
			execution_status_log.add('JSON parse failed.');
			execution_status_log.add(e.getMessage());
		}
		finally{
		
		}
		
		// change object can now be cycled to make changes on selected objects
		
		// start the editing session to make changes to the model
		
		SessionManager.getInstance().createSession('Modify Model from File');
		
		execution_status_log.add('Model session created.');
		
		ele_factory = live_project.getElementsFactory();
		
		execution_status_log.add('Element factory acquired.');
		
		model_mgr = ModelElementsManager.getInstance();
		
		execution_status_log.add('Model element manager acquired.');
		
		for (model_change in changes_to_make['modification targets']) {
			
			// start by looking at what model element to modify
			
			item_to_edit = model_change['id'];
			
			// read operations to apply to the selected model element
			
			for (op_to_execute in model_change['ops']) {
				
				op_type = op_to_execute['op'];
				
				if (op_type == 'replace'){
					item_to_edit_reported = '';
					item_edited_value_reported = '';
					
					try {
						// if item was created this session, you can't get it by ID.
						
						ele_to_mod = null;
						
						if (item_to_edit.split('_')[0] == 'new') {
							ele_to_mod = temp_elements[item_to_edit];
						}
						else {
							ele_to_mod = live_project.getElementByID(item_to_edit);
						}
						
						if (ele_to_mod == null) {
							command_processing_log.add('Don\'t have an element to mod for id = ' + item_to_edit);
						}
						
						// determine if the target is a standard language attribute or an attribute
						// due to a custom Stereotype
						
						// TODO: extend beyond one step in the path
						attribute_to_hit = null;
						
						if (op_to_execute['path'] != null) {
							attribute_to_hit = op_to_execute['path'].split('/m2/')[1];
						}
						
						// This is the cheat for loading M1 value properties directly from spreadsheet.
													
						value_shortcuts = op_to_execute['value'];
						if (value_shortcuts != null && attribute_to_hit == null){
							// iterate keys to find needed properties to load - note that we use name : type notation
							live_log.log('Found a value shortcut! This leg of code is a HACK!!!!!');
							for(index in value_shortcuts) {
								live_log.log(index + ' : ' + value_shortcuts[index]);
								split_point = index.split(' : ');
								new_name = '';
								type_to_get = null;
								if (split_point.size() > 1) {
									new_name = split_point[0];
									// hunt for the value type of interest
									
									live_log.log('Trying to find ' + split_point[1]);
									
									type_to_get = com.nomagic.magicdraw.uml.ClassifierFinder.findClassifierOrDataType(live_project, split_point[1], [], null);
									live_log.log('Property will have type ' + type_to_get.getName());
									
								}
								else {
									new_name = index;
									type_to_get = com.nomagic.magicdraw.uml.ClassifierFinder.findClassifierOrDataType(live_project, 'String', [], sysml_package);    
								}
								live_log.log('New value property name will be: ' + new_name + ' owner id should be ' + item_to_edit);
								
								new_val_prop = ele_factory.createPropertyInstance();
								
								live_log.log('New property created.');
								
								if (item_to_edit.split('_')[0] == 'new') {
									owning_element = owning_element = temp_elements[item_to_edit];
									new_val_prop.setOwner(owning_element);
								}
								new_val_prop.setName(new_name);
								
								if (type_to_get != null){
									new_val_prop.setType(type_to_get);            
								}
								
								live_log.log('Property should have value of ' + value_shortcuts[index]);
								
								if (type_to_get.getName() == 'String') {
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
								apply_stereo = StereotypesHelper.getStereotype(live_project, 'ValueProperty');
								
								live_log.log('Found stereotype to apply ' + apply_stereo.getHumanName());
								
								class_list.add(apply_stereo); 
							}
						}
						
						// Path constructed correctly with appropriate metamodel level identified.
						
						try {
							
							item_to_edit_reported = ele_to_mod.getID() + '(' + ele_to_mod.getHumanName() + ')';
						
							switch(attribute_to_hit) {
								case 'Documentation':
									replace_log.add('(' + attribute_to_hit + ') Element ' + item_to_edit_reported + ' has documentation ' +
										CoreHelper.getComment(ele_to_mod) + ' to become ' + op_to_execute['value']);
									CoreHelper.setComment(ele_to_mod, op_to_execute['value']);
									break;
								case 'association':
									end_element = null;
									if (op_to_execute['value'].split('_')[0] == 'new') {
										end_element = temp_elements[op_to_execute['value']];
									}
									else {
										end_element = live_project.getElementByID(op_to_execute['value']);
									}
									
									item_edited_value_reported = end_element.getID() + '(' + end_element.getHumanName() + ')';
									
									replace_log.add('(' + attribute_to_hit + ') New association of object: ' + item_to_edit_reported + ' is ' +
										item_edited_value_reported);
									
									ele_to_mod.setAssociation(end_element);
									
									break;   
								case 'defaultValue':
									
									replace_log.add('(' + attribute_to_hit + ') Applying default value of ' + op_to_execute['value'] + ' to ' + 	
										item_to_edit_reported);
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
								case "end":
									end_element = null;
									if (op_to_execute['value'].split('_')[0] == 'new') {
										end_element = temp_elements[op_to_execute['value']];
									}
									else {
										end_element = live_project.getElementByID(op_to_execute['value']);
									}
									
									item_edited_value_reported = end_element.getID() + '(' + end_element.getHumanName() + ')';
									
									replace_log.add('(' + attribute_to_hit + ') New connector end of object: ' + item_to_edit_reported + ' is '
										+ item_edited_value_reported);
									
									// API forces you to go the opposite direction
									
									end_element.setOwner(ele_to_mod);
									break;
								case 'isConjugated':
									replace_log.add('(' + attribute_to_hit + ') Setting isConjugated flag to ' + op_to_execute['value'] + ' on ' + 	
										item_to_edit_reported);
									conj = op_to_execute['value'];
									if (conj == 'true') {
									   ele_to_mod.setConjugated(true);
									}
									break;
								case 'memberEnd':
									end_element = null;
									if (op_to_execute['value'].split('_')[0] == 'new') {
										end_element = temp_elements[op_to_execute['value']];
									}
									else {
										end_element = live_project.getElementByID(op_to_execute['value']);
									}
									
									item_edited_value_reported = end_element.getID() + '(' + end_element.getHumanName() + ')';
									
									replace_log.add('(' + attribute_to_hit + ') New memberEnd of object: ' + item_to_edit_reported + ' is '
										+ item_edited_value_reported);
									
									// API forces you to go the opposite direction
									
									end_element.setAssociation(ele_to_mod);
									break;
								case 'nestedClassifier':
									owned_element = null;
									if (op_to_execute['value'].split('_')[0] == 'new') {
										owned_element = temp_elements[op_to_execute['value']];
									}
									else {
										owned_element = live_project.getElementByID(op_to_execute['value']);
									}
									
									item_edited_value_reported = owned_element.getID() + '(' + owned_element.getHumanName() + ')';
									
									replace_log.add('(' + attribute_to_hit + ') Element ' + item_to_edit_reported + ' is set to own ' +
										item_edited_value_reported);
									
									ele_to_mod.setOwner(owned_element);
									
									homeless_new = [];
									for (homeless in homeless_elements){
										if (homeless_elements[homeless] == ele_to_mod) {
										   // do nothing
										}
										else {
											homeless_new.add(homeless_elements[homeless]);
										}
									}
									
									homeless_elements = homeless_new;
									
								case 'owner':
									owning_element = null;
									if (op_to_execute['value'].split('_')[0] == 'new') {
										owning_element = temp_elements[op_to_execute['value']];
									}
									else {
										owning_element = live_project.getElementByID(op_to_execute['value']);
									}
									
									item_edited_value_reported = owning_element.getID() + '(' + owning_element.getHumanName() + ')';
									
									replace_log.add('(' + attribute_to_hit + ') Element ' + item_edited_value_reported + ' is set to own ' +
										item_to_edit_reported);
										
									ele_to_mod.setOwner(owning_element);
									
									if (homeless_elements.contains(ele_to_mod)) {
										homeless_elements.remove(ele_to_mod);
									}
									break;
								case 'propertyPath':
								   element_path_list = [];
								   element_value_list = [];
								   
								   item_edited_value_reported = '';
								   
								   verification_log.add('Deep verify property path for ' + item_to_edit_reported);
								   
								   for (path_place in op_to_execute['value']) {
									   ele_path = null;
									   
									   if (path_place.split('_')[0] == 'new') {
										   ele_path = temp_elements[path_place];
										   element_path_list.add(ele_path);
									   }
									   else {
										   ele_path = live_project.getElementByID(path_place);
										   element_path_list.add(ele_path);
									   }
									   
									   item_edited_value_reported = item_edited_value_reported + 
											ele_path.getID() + '(' + ele_path.getHumanName() + '), ';
								   }
								   
								   replace_log.add('(' + attribute_to_hit + ') Property path under ' + item_to_edit_reported + ' is replaced by ' +
										item_edited_value_reported);
								   
								   // apply the stereotype
								   
								   apply_stereo = StereotypesHelper.getStereotype(live_project, 'NestedConnectorEnd');
								   
								   // element to get the slot defining feature from
																								   
								   com.nomagic.uml2.ext.jmi.helpers.StereotypesHelper.addStereotype(ele_to_mod, apply_stereo);
								   
								   ele_asi = ele_to_mod.getAppliedStereotypeInstance();
								   
								   for (asi_class in ele_asi.getClassifier()) {
								       verification_log.add('Property Path owning stereotype classifier includes ' +
								   asi_class.getName() + ' for ' + item_to_edit_reported);
								   }
								   
								   //for (asi_slot in ele_asi.getSlot()) {
								   //   live_log.log('Property path ASI includes slot ' + ele_asi.getSlot()[asi_slot].getDefiningFeature().getName());
									  //live_log.log('PP Slot = ' + pp_slot.getDefiningFeature().getName());
								  //}
								   
								   for (prop_path_step in element_path_list){
									   ele_value = ele_factory.createElementValueInstance();
									   ele_value.setElement(prop_path_step);
									   element_value_list.add(ele_value);
									   verification_log.add("Element value points to " + ele_value.getElement().getHumanName());
								   }
								   
								   verification_log.add("element value list is of Java class " + element_value_list.toArray().getClass());
								   
								   StereotypesHelper.setStereotypePropertyValue(ele_to_mod,
										apply_stereo, 'propertyPath', element_value_list.toArray(), true);
								   
								   verification_log.add('Trying to apply value for ' +
										com.nomagic.magicdraw.sysml.util.SysMLProfile.ELEMENTPROPERTYPATH_PROPERTYPATH_PROPERTY + 
										' on stereotype ' + apply_stereo.getName() + ' on end with role ' + item_to_edit_reported);
										
								    for (asi_slot in ele_asi.getSlot()) {
									    verification_log.add('Property path ASI includes slot ' + asi_slot.
											getDefiningFeature().getName());
										counter = 0;
									    for (val in asi_slot.getValue()) {
											verification_log.add('Slot value includes ' +
												val.getID());
												
											// for some reason, the element values placed by the stereotypes helper don't actually point to their elements;
											// this is a patch
											val.setElement(element_path_list.get(counter));
											counter++;
											verification_log.add('Value includes element ' + val.getElement().getHumanName());
									    }
								    }
								   
								   break;
								case 'role':
									role_element = null;
									if (op_to_execute['value'].split('_')[0] == 'new') {
										role_element = temp_elements[op_to_execute['value']];
									}
									else {
										role_element = live_project.getElementByID(op_to_execute['value']);
									}
									
									item_edited_value_reported = role_element.getID() + '(' + role_element.getHumanName() + ')';
									
									replace_log.add('(' + attribute_to_hit + ') Setting role on ' + item_to_edit_reported + ' to ' +
										item_edited_value_reported);
									
									ele_to_mod.setRole(role_element);
									break;
								case 'type':
									typing_element = null;
									if (op_to_execute['value'].split('_')[0] == 'new') {
										typing_element = temp_elements[op_to_execute['value']];
									}
									else {
										typing_element = live_project.getElementByID(op_to_execute['value']);
									}
									
									item_edited_value_reported = typing_element.getID() + '(' +
										typing_element.getHumanName() + ')';
									
									replace_log.add('(' + attribute_to_hit + ') Setting type on ' + item_to_edit_reported + ' to ' +
										item_edited_value_reported);
									
									ele_to_mod.setType(typing_element);
									break;
								default:
									execution_status_log.add("Processing attribute " + attribute_to_hit);
									key_member = null;
									key_member_found = false;
									key_slot = null;
									key_slot_found = false;
									key_literal_found = false;
									// not a predefined location - look at applied Stereotypes
									try {
										ele_asi = ele_to_mod.getAppliedStereotypeInstance();
										execution_status_log.add('At ASI.');
										// look at classifier in case there is no slot
										for (class_to_check in ele_asi.getClassifier()) {
											for (mem_to_check in class_to_check.getMember()) {
												
												execution_status_log.add('Discovered member: ' + mem_to_check.getName());
												
												if (mem_to_check.getName() == attribute_to_hit) {
													switch (op_to_execute['op']){
														case 'replace':
															key_member = mem_to_check;
															key_member_found = true;
															break;    
													}    
												} 
											}    
										}
										
										replace_log.add('(' + attribute_to_hit + ') Setting tagged value ' + attribute_to_hit + ' on ' + item_to_edit_reported + ' to ' +
											op_to_execute['value']);
										
										// if a member has been matched to the path to replace, then see if there is a matching Slot
										
										if (key_member_found) {
										
											for (slot_to_check in ele_asi.getSlot()) {
				
												if (slot_to_check.getDefiningFeature().getName() == attribute_to_hit) {
													switch (op_to_execute['op']){
														case 'replace':
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
												val_found = false;
												raw_value = op_to_execute['value'];
												// check to see if the slot has a value
												for (slot_val in key_slot.getValue()) {
													// if the value is literal string, can simply overwrite string
													if (slot_val instanceof LiteralString) {
														val_found = true;
														
														slot_val.setValue(raw_value);
														live_log.log('Literal String found: ' + slot_val.getID());
														live_log.log('Literal String value: ' + slot_val.getValue());    
													}
													// if the target is an enumeration literal, then need to match valid literal
													else if (slot_val instanceof InstanceValue) {
														val_found = true;
														
														key_instance = slot_val.getInstance();
														
														if (key_instance instanceof EnumerationLiteral){
															live_log.log('Enumerator is ' + key_instance.getEnumeration().getHumanName());
															key_enum = key_instance.getEnumeration();
															for (literal in key_enum.getOwnedLiteral()){
																live_log.log('Enumerator includes ' + literal.getName());
																if (literal.getName() == raw_value) {
																	live_log.log('Matched enumeration literal ' + raw_value);
																	slot_val.setInstance(literal);
																}
															}
														}
														
														live_log.log('Instance Value found: ' + slot_val.getID());
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
									}
									catch(Exception e) {
										execution_status_log.add('Failed tagged value replace on ' + 
											item_to_edit_reported + ' for attribute ' + attribute_to_hit);
										execution_status_log.add(e.getMessage());
									}
									finally {
									
									}
									break;
								}
						}
						catch(Exception e) {
							execution_status_log.add('Failed meta-attribute replace for ' + item_to_edit_reported + 
								' on ' + attribute_to_hit);
							// need code line to make this easier.
							execution_status_log.add(e.getMessage());
						}
						finally {
						
						}
					}
					catch(err){
						execution_status_log.add('Failed get ele_mod for ' + item_to_edit);
						execution_status_log.add(e.getMessage());
					}
					finally {
					
					}
				
				}
				
				else if (op_type == 'create') {
					
					try {
					
						new_name = op_to_execute['name'];
						new_meta = op_to_execute['metatype'];
						new_stereo = "";
						
						if (op_to_execute['stereotype'] != null) {
							if (op_to_execute['stereotype'] instanceof ArrayList) {
								new_stereo = op_to_execute['stereotype'].get(0);
							}
							else {
								new_stereo = op_to_execute['stereotype'];
							}
						}
						
						//new_stereo = op_to_execute['stereotype'];
						
						new_element = null;
						
						create_log.add('Creating element id = ' + item_to_edit + '(' + 
							new_meta + ' ' + new_name + ' with stereotype ' + new_stereo + ')');
						
						try {
						
							switch(new_meta) {
						
								case 'Class':
									new_element = ele_factory.createClassInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);
									homeless_elements.add(new_element);
									break;
								case 'Property':
									new_element = ele_factory.createPropertyInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);
									break;
								case 'Port':
									new_element = ele_factory.createPortInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);
									break;
								case 'Association':
									new_element = ele_factory.createAssociationInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);
									homeless_elements.add(new_element);
									
									ends_to_nuke.add(new_element.getMemberEnd()[0]);
									ends_to_nuke.add(new_element.getMemberEnd()[1]);
									
									break;
								case 'Connector':
									new_element = ele_factory.createConnectorInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);
									
									c_ends_to_nuke.add(new_element.getEnd()[0]);
									c_ends_to_nuke.add(new_element.getEnd()[1]);
									
									break;
								case 'ConnectorEnd':
									new_element = ele_factory.createConnectorEndInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									// connector ends are not named elements
									break;
								case 'DataType':
									new_element = ele_factory.createDataTypeInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);
									homeless_elements.add(new_element);
									break;
								 
							}   
							
							if (new_stereo != null && new_stereo != "") {
								
								StereotypesHelper.createStereotypeInstance(new_element);
								
								//execution_status_log.add("Made stereotype instance for " + new_name);
								
								ele_asi = new_element.getAppliedStereotypeInstance();
								
								//execution_status_log.add("Retrieved stereotype instance for " + new_name +
								//	"(" + ele_asi.toString() + ")");
								
								class_list = ele_asi.getClassifier();
								apply_stereo = StereotypesHelper.getStereotype(live_project, new_stereo);
								
								//execution_status_log.add("Got stereotype " + new_stereo +  " from project");
								
								// apply values to slots
								
								stereo_path = op_to_execute['path'];
								stereo_value = op_to_execute['value'];
								
								class_list.add(apply_stereo);
								
								com.nomagic.uml2.ext.jmi.helpers.InstanceSpecificationHelper.setClassifierForInstanceSpecification(	
									class_list, ele_asi, true);
									
								//execution_status_log.add("Instance specification helper done for " + new_stereo);
							}
							
						}
						catch(Exception e) {
							execution_status_log.add('Failed to create new element.');
							execution_status_log.add(e.getMessage());
						}
						finally {
						
						}
					}
					catch(Exception e) {
						execution_status_log.add('Failed to find name or metatype on create.');
						execution_status_log.add(e.getMessage());
					}
					finally {
					
					}            
				}
				
				else if (op_type == 'rename') {
					if (item_to_edit.split('_')[0] == 'new') {
						ele_to_mod = temp_elements[item_to_edit];
					}
					else {
						ele_to_mod = live_project.getElementByID(item_to_edit);
					}
					
					rename_log.add('Renaming ' + item_to_edit_reported + ' to ' + op_to_execute['name']);
					
					ele_to_mod.setName(op_to_execute['name']);    
				}  
				
			}
			
		}
		
	}
	catch(Exception e){
		execution_status_log.add('Failed in file parsing stage.');
		execution_status_log.add(e.getMessage());
	}
	finally {
		// house the remaining homeless
		
		//execution_status_log.add('Have ' + ends_to_nuke.size().toString() + ' ends to nuke.');
		
		for (homeless_no_more in homeless_elements) {
			homeless_no_more.setOwner(default_home);
			execution_status_log.add('Housing homeless element ' + homeless_no_more.getHumanName());        
		}
		
		for (end_ready_to_nuke in ends_to_nuke) {
			//live_log.log('Should kill memberEnd of ' + end_ready_to_nuke.getOwner().getName());
			//model_mgr.removeElement(end_ready_to_nuke);
			//end_ready_to_nuke.setOwner(null);
			end_ready_to_nuke.setAssociation(null);    
		}
		
		for (c_end_ready_to_nuke in c_ends_to_nuke) {
			//live_log.log('Should kill memberEnd of ' + end_ready_to_nuke.getOwner().getName());
			//model_mgr.removeElement(end_ready_to_nuke);
			//end_ready_to_nuke.setOwner(null);
			c_end_ready_to_nuke.set_connectorOfEnd(null);    
		}
				   
		// close the open streams
		reader.close();
		
		// Close editing session so MD makes the model changes
		
		SessionManager.getInstance().closeSession();
		execution_status_log.add('Closed modeling session successfully.');
		
	}

}
catch(Exception e) {
	execution_status_log.add('Failed outermost try.');
    execution_status_log.add(e.getMessage());
}
finally {
	// uncomment below to expose detailed logs
	live_log.log('Execution steps:');
	for (entry in execution_status_log) {
		live_log.log(entry);
	}
	live_log.log('Elements processed:');
	for (entry in command_processing_log) {
		//live_log.log(entry);
	}
	live_log.log('Element creation commands:');
	for (entry in create_log) {
		//live_log.log(entry);
	}
	live_log.log('Relationship replace commands:');
	for (entry in replace_log) {
		//live_log.log(entry);
	}
	live_log.log('Element rename commands:');
	for (entry in rename_log) {
		//live_log.log(entry);
	}
	live_log.log('Verification Details:');
	for (entry in verification_log) {
		//live_log.log(entry);
	}
}