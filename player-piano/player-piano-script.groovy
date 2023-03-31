/**
* Copyright (C) 2020 by the Georgia Tech Research Institute (GTRI)
* This software may be modified and distributed under the terms of
* the BSD 3-Clause license. See the LICENSE file for details.
**/

// Java libs
import org.apache.commons.lang.SystemUtils

import java.nio.file.Path
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
import com.nomagic.uml2.ext.magicdraw.compositestructures.mdinternalstructures.*;
// Other third party libraries

// big outer try for exception handling and reporting
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

	// get hooks into MagicDraw for use later
	live_app = com.nomagic.magicdraw.core.Application.getInstance();
	live_log = live_app.getGUILog();
	live_project = live_app.getProject();

	//grab all profiles in the project to help with identifying stereotypes
	all_profiles = StereotypesHelper.getAllProfiles(live_project)

	// dictionary to hold the ids discovered as we go
	temp_ids = {};
	temp_elements = {};
	homeless_elements = [];

	// these are all hacks to fight MagicDraw's built-in auto-production of elements.
	ends_to_nuke = [];
	c_ends_to_nuke = [];
	pps_to_save = [];
	assocs_to_clean = [];

	create_list = [];


	// try to make the element picker
	try {
		// Let the user pick a default location for elements without explicitly defined owners
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

	read_path = "";
	read_name = "";

	try {
		dialogParent = MDDialogParentProvider.getProvider().getDialogParent();
		chooser = new JFileChooser();
		returnVal = chooser.showOpenDialog(dialogParent);
		if(returnVal == JFileChooser.APPROVE_OPTION) {
		   fc = chooser.getSelectedFile();
		}

		fis = new FileReader(chooser.getSelectedFile());
		reader = new BufferedReader(fis);
		stringBuilder = new StringBuilder();

		execution_status_log.add('Opened file ' + fc.getAbsolutePath());

		found_path = fc.toPath();
		read_path = found_path.getParent().toString();
		read_name = found_path.getFileName();
	}
	catch(Exception e){
		execution_status_log.add('Failed to open file.');
		execution_status_log.add(e.getMessage());
	}
	finally {
	}

	parsed_model = null;

	// big try to interpret the list of modification instructions

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
						// if item was created this session, you can't get it by ID. This is the workaround

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

						// This is the cheat for loading M1 value properties directly from spreadsheet. Will eventually be fixed.

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

						// apply meta-attribute changes

						try {

							item_to_edit_reported = ele_to_mod.getID() + '(' + ele_to_mod.getHumanName() + ')';
							// ================================================
							// Add a switch case to cover a new meta-attribute

							switch(attribute_to_hit) {
								case 'aggregation' :
									replace_log.add('(' + attribute_to_hit + ') Setting aggregation for property ' + item_to_edit_reported + 
										' to ' + op_to_execute['value'])
									//the aggregation value in the JSON is a string so need to match it against the correct
									//aggregation kind enumeration literal
									AggregationKind aggregation_kind

									switch(op_to_execute['value']) {
										case 'composite' : 
											aggregation_kind = AggregationKindEnum.COMPOSITE
											break
										case 'shared' :
											aggregation_kind = AggregationKindEnum.SHARED
											break
										default : 
											aggregation_kind = AggregationKindEnum.NONE
											break
									}
									//set the aggregation of the element to mod (property) equal to the found aggregation enum literal
									ele_to_mod.setAggregation(aggregation_kind)
									break
								case 'documentation':
									replace_log.add('(' + attribute_to_hit + ') Element ' + item_to_edit_reported + ' has documentation ' +
										CoreHelper.getComment(ele_to_mod) + ' to become ' + op_to_execute['value']);
									CoreHelper.setCommentElement(ele_to_mod, ele_to_mod.getOwnedComment()[0]);
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
								case 'classifierBehavior':
									behavior_element = null;
									if (op_to_execute['value'].split('_')[0] == 'new') {
										behavior_element = temp_elements[op_to_execute['value']];
									}
									else {
										behavior_element = live_project.getElementByID(op_to_execute['value']);
									}

									item_edited_value_reported = behavior_element.getID() + '(' +
										behavior_element.getHumanName() + ')';

									replace_log.add('(' + attribute_to_hit + ') Setting method on ' + item_to_edit_reported + ' to ' +
										item_edited_value_reported);

									ele_to_mod.setClassifierBehavior(behavior_element);

									behavior_element.setOwner(ele_to_mod);

									if (homeless_elements.contains(behavior_element)) {
										homeless_elements.remove(behavior_element);
									}

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
								case 'defaultValueSpec':
									value_element = null;

									if (op_to_execute['value'].split('_')[0] == 'new') {
										value_element = temp_elements[op_to_execute['value']];
									}
									else {
										value_element = live_project.getElementByID(op_to_execute['value']);
									}

									item_edited_value_reported = value_element.getID() + '(' + value_element.getHumanName() + ')';

									replace_log.add('(' + attribute_to_hit + ') Default Value for ' + item_to_edit_reported + ' is '
										+ item_edited_value_reported);

									value_element.setOwner(ele_to_mod);

									ele_to_mod.setDefaultValue(value_element);

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
								case 'general':
									general_element = null;

									if (op_to_execute['value'].split('_')[0] == 'new') {
										general_element = temp_elements[op_to_execute['value']];
									}
									else {
										general_element = live_project.getElementByID(op_to_execute['value']);
									}

									item_edited_value_reported = general_element.getID() + '(' + general_element.getHumanName() + ')';

									replace_log.add('(' + attribute_to_hit + ') General classifier for ' + item_to_edit_reported + ' is '
										+ item_edited_value_reported);

									// TODO: need to check for existing generalization

									if (ele_to_mod.getGeneral().contains(general_element)) {

									}
									else {
										new_element = ele_factory.createGeneralizationInstance();

										new_element.setGeneral(general_element);
										new_element.setSpecific(ele_to_mod);

										new_element.setOwner(ele_to_mod);
									}

									break;

								case 'isConjugated':
									replace_log.add('(' + attribute_to_hit + ') Setting isConjugated flag to ' + op_to_execute['value'] + ' on ' +
										item_to_edit_reported);
									conj = op_to_execute['value'];
									if (conj == 'true') {
									   ele_to_mod.setConjugated(true);
									}
									break;
								case 'lower':
									lower_element = null;

									if (op_to_execute['value'].split('_')[0] == 'new') {
										lower_element = temp_elements[op_to_execute['value']];
									}
									else {
										lower_element = live_project.getElementByID(op_to_execute['value']);
									}

									item_edited_value_reported = lower_element.getID() + '(' + lower_element.getHumanName() + ')';

									replace_log.add('(' + attribute_to_hit + ') Default Value for ' + item_to_edit_reported + ' is '
										+ item_edited_value_reported);

									lower_element.setOwner(ele_to_mod);

									ele_to_mod.setLowerValue(lower_element);

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
								case 'method':
									behavior_element = null;
									if (op_to_execute['value'].split('_')[0] == 'new') {
										behavior_element = temp_elements[op_to_execute['value']];
									}
									else {
										behavior_element = live_project.getElementByID(op_to_execute['value']);
									}

									item_edited_value_reported = behavior_element.getID() + '(' +
										behavior_element.getHumanName() + ')';

									replace_log.add('(' + attribute_to_hit + ') Setting method on ' + item_to_edit_reported + ' to ' +
										item_edited_value_reported);

									// This is how to set properties that are collections in Groovy

									ele_to_mod.getMethod().add(behavior_element);

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
								case 'pp_end':
									// fake meta-attribute - participant property because of name collision

									pp_element = null;

									if (op_to_execute['value'].split('_')[0] == 'new') {
										pp_element = temp_elements[op_to_execute['value']];
									}
									else {
										pp_element = live_project.getElementByID(op_to_execute['value']);
									}

									item_edited_value_reported = '';

									// apply the stereotype

									apply_stereo = StereotypesHelper.getStereotype(live_project, 'ParticipantProperty');

									// element to get the slot defining feature from

									com.nomagic.uml2.ext.jmi.helpers.StereotypesHelper.addStereotype(ele_to_mod, apply_stereo);

									ele_asi = ele_to_mod.getAppliedStereotypeInstance();

									for (asi_class in ele_asi.getClassifier()) {
										verification_log.add('Participant property stereotype classifier includes ' +
											asi_class.getName() + ' for ' + item_to_edit_reported);
									}

									StereotypesHelper.setStereotypePropertyValue(ele_to_mod,
										apply_stereo, 'end', pp_element, true);

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
								case 'redefines':
									redefined_element = null;
									if (op_to_execute['value'].split('_')[0] == 'new') {
										redefined_element = temp_elements[op_to_execute['value']];
									}
									else {
										redefined_element = live_project.getElementByID(op_to_execute['value']);
									}

									item_edited_value_reported = redefined_element.getID() + '(' +
										redefined_element.getHumanName() + ')';

									replace_log.add('(' + attribute_to_hit + ') Setting method on ' + item_to_edit_reported + ' to ' +
										item_edited_value_reported);

									// This is how to set properties that are collections in Groovy

									ele_to_mod.getRedefinedElement().add(redefined_element);

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
								case 'opposite':
									opposite_element = null;
									if (op_to_execute['value'].split('_')[0] == 'new') {
										opposite_element = temp_elements[op_to_execute['value']];
									}
									else {
										opposite_element = live_project.getElementByID(op_to_execute['value']);
									}

									item_edited_value_reported = opposite_element.getID() + '(' + opposite_element.getHumanName() + ')';

									replace_log.add('(' + attribute_to_hit + ') Setting opposite on ' + item_to_edit_reported + ' to ' +
										item_edited_value_reported);

									ele_to_mod.setRole(opposite_element);
									break;
								case 'subject':
									subject_element = null;
									if (op_to_execute['value'].split('_')[0] == 'new') {
										subject_element = temp_elements[op_to_execute['value']];
									}
									else {
										subject_element = live_project.getElementByID(op_to_execute['value']);
									}

									item_edited_value_reported = subject_element.getID() + '(' +
										subject_element.getHumanName() + ')';

									replace_log.add('(' + attribute_to_hit + ') Setting method on ' + item_to_edit_reported + ' to ' +
										item_edited_value_reported);

									// This is how to set properties that are collections in Groovy

									ele_to_mod.getSubject().add(subject_element);

									break;
								case 'client':
									element = null;
									if (op_to_execute['value'].split('_')[0] == 'new') {
										element = temp_elements[op_to_execute['value']];
									}
									else {
										element = live_project.getElementByID(op_to_execute['value']);
									}

									item_edited_value_reported = element.getID() + '(' +
										element.getHumanName() + ')';

									replace_log.add('(' + attribute_to_hit + ') Setting method on ' + item_to_edit_reported + ' to ' +
										item_edited_value_reported);

									CoreHelper.setClientElement(ele_to_mod, element);

									break;
								case 'supplier':
									element = null;
									if (op_to_execute['value'].split('_')[0] == 'new') {
										element = temp_elements[op_to_execute['value']];
									}
									else {
										element = live_project.getElementByID(op_to_execute['value']);
									}

									item_edited_value_reported = element.getID() + '(' +
										element.getHumanName() + ')';

									replace_log.add('(' + attribute_to_hit + ') Setting method on ' + item_to_edit_reported + ' to ' +
										item_edited_value_reported);

									CoreHelper.setSupplierElement(ele_to_mod, element);

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
								case 'upper':
									upper_element = null;

									if (op_to_execute['value'].split('_')[0] == 'new') {
										upper_element = temp_elements[op_to_execute['value']];
									}
									else {
										upper_element = live_project.getElementByID(op_to_execute['value']);
									}

									item_edited_value_reported = upper_element.getID() + '(' + upper_element.getHumanName() + ')';

									replace_log.add('(' + attribute_to_hit + ') Default Value for ' + item_to_edit_reported + ' is '
										+ item_edited_value_reported);

									upper_element.setOwner(ele_to_mod);

									ele_to_mod.setUpperValue(upper_element);

									break;

									// End of new stereotype definition
									// =======================================
								default:
									execution_status_log.add("Processing attribute: " + attribute_to_hit);
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
										execution_status_log.add("UNSUPPORTED ATTRIBUTE " + attribute_to_hit);
										execution_status_log.add("Update switch case for new attribute.");
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

					// create new elements using the appropriate calls on the ElementsFactory

					try {
						String new_name = op_to_execute['name']
						old_name = new_name
						ArrayList<String> split_name = new_name.split("::")
						if (split_name.size() > 1) {
							new_name = split_name.last()
						}

						new_meta = op_to_execute['metatype'];
						new_stereo = "";

						if (op_to_execute['stereotype'] != null) {
							/*
							This will return a list of dictionaries, e.g. 
							"stereotype" : [{"stereotype" : "Block", "profile" : "_15_001...."}]
							*/
							new_stereo = op_to_execute['stereotype']
						}

						new_element = null;

						create_log.add('Creating element id = ' + item_to_edit + '(' +
							new_meta + ' ' + old_name + ' with stereotype ' + new_stereo + ')');

						try {

							new_assoc = false;
							new_prop = false;

							// ================================================
							// Create new switch cases for new Metatypes here.

							switch(new_meta) {

								case 'Class':
									new_element = ele_factory.createClassInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);
									homeless_elements.add(new_element);
									break;
								case 'Abstraction':
									new_element = ele_factory.createAbstractionInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);
									homeless_elements.add(new_element);
									break;
								case 'Activity':
									new_element = ele_factory.createActivityInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);
									homeless_elements.add(new_element);
									break;
								case 'Trigger':
									new_element = ele_factory.createSendSignalActionInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);
									homeless_elements.add(new_element);
									break;
								case 'Action':
									new_element = ele_factory.createCallBehaviorActionInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);
									homeless_elements.add(new_element);
									break;
								case 'InputPin':
									new_element = ele_factory.createInputPinInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);
									homeless_elements.add(new_element);
									break;
								case 'OutputPin':
									new_element = ele_factory.createOutputPinInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);
									homeless_elements.add(new_element);
									break;
								case 'Actor':
									new_element = ele_factory.createActorInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);
									homeless_elements.add(new_element);
									break;
								case 'Requirement':
									new_element = ele_factory.createRequirementInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);
									homeless_elements.add(new_element);
									break;
								case 'UseCase':
									new_element = ele_factory.createUseCaseInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);
									homeless_elements.add(new_element);
									break;
								case 'Comment':
									new_element = ele_factory.createCommentInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setBody(new_name);
									homeless_elements.add(new_element);
									break;
								case 'Property':
									new_element = ele_factory.createPropertyInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);

									new_prop = true;

									break;
								case 'Operation':
									new_element = ele_factory.createOperationInstance();
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
								case 'AssociationClass':
									new_element = ele_factory.createAssociationClassInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);
									homeless_elements.add(new_element);

									ends_to_nuke.add(new_element.getMemberEnd()[0]);
									ends_to_nuke.add(new_element.getMemberEnd()[1]);

									new_assoc = true;

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
								case 'LiteralString':
									new_element = ele_factory.createLiteralStringInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);
									break;
								case 'LiteralInteger':
									new_element = ele_factory.createLiteralIntegerInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);
									break;
								case 'LiteralReal':
									new_element = ele_factory.createLiteralRealInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);
									break;
								case 'LiteralUnlimitedNatural':
									new_element = ele_factory.createLiteralUnlimitedNaturalInstance();
									temp_ids[item_to_edit] = new_element.getID();
									temp_elements[item_to_edit] = new_element;
									new_element.setName(new_name);
									break;
								default:
									execution_status_log.add("UNSUPPORTED METATYPE " + new_meta);
									execution_status_log.add("Update the switch statement found in the create case " +
										"of the Player Piano Groovy script. Double check " +
										"edge paths supported by a switch case as well.");
									break;
							}

							// End of new metatype addition.
							// ================================================

							create_list.add([old_name, new_element]);

							if (new_stereo != null && new_stereo != "") {

								StereotypesHelper.createStereotypeInstance(new_element);

								//execution_status_log.add("Made stereotype instance for " + new_name);

								ele_asi = new_element.getAppliedStereotypeInstance();

								//execution_status_log.add("Retrieved stereotype instance for " + new_name +
								//	"(" + ele_asi.toString() + ")");

								class_list = ele_asi.getClassifier();

								//need to iterate over each stereotype dictionary to get stereotype name and profile id
								
								new_stereo.each { stereo_dict ->
									//get stereotype
									stereo_name = stereo_dict['stereotype']
									//lookup profile from the given name
									profile_name = stereo_dict['profile']
									profile = null
									all_profiles.each { prof ->
										if(prof.getName() == profile_name) {
											profile = prof
										} else if(prof.getQualifiedName() == profile_name) {
											profile = prof
										}
									}
									// add in logging info as well to help catch if stereotypes/profiles are not found successfully
									if(profile == null) {
										execution_status_log.add('Profile: "' + profile_name + 
											'" not found while attempting to apply stereotype: "' + stereo_name)
										execution_status_log.add('Verify that the correct profile name or qualified name is populated '+
											' for the stereotype in the input file. Profiles with non-unique names' +
											' should be idenfied by their qualified name.')
									}
									//get the stereotype object to apply
									apply_stereo = StereotypesHelper.getStereotype(live_project, stereo_name, profile) 

									//add the stereotype to the list of classifiers for the applied stereotype instance
									class_list.add(apply_stereo)

									// if stereotype is a particular SysML stereotype, see if it is generating additional elements

									if (stereo_name.equals("Block") && new_assoc) {
										execution_status_log.add("Making AssociationBlock");
										for (attr in new_element.getOwnedAttribute()) {
											execution_status_log.add("Have an owned attribute called " + attr.getName());
										}
										assocs_to_clean.add(new_element);
									}

									if (stereo_name.equals("ParticipantProperty") && new_prop) {
										execution_status_log.add("Making ParticipantProperty");
										pps_to_save.add(new_element);
									}

								}

								//execution_status_log.add("Got stereotype " + new_stereo +  " from project");

								// apply values to slots

								stereo_path = op_to_execute['path'];
								stereo_value = op_to_execute['value'];

								execution_status_log.add('These are the stereotypes to apply: ' + class_list)

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
						item_to_edit_reported = op_to_execute['name'];
					}
					else {
						ele_to_mod = live_project.getElementByID(item_to_edit);
						item_to_edit_reported = ele_to_mod.getHumanName();
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

		if (assocs_to_clean.size() > 0) {
			SessionManager.getInstance().createSession('Override MagicDraw automatic element creation');
		}

		for (assoc in assocs_to_clean) {
			execution_status_log.add("Checking " + assoc.getHumanName());
			all_remove = [];
			for (attr in assoc.getOwnedAttribute()) {
				execution_status_log.add("Found " + attr.getHumanName() + " under " + assoc.getHumanName());
				if (!pps_to_save.contains(attr) && StereotypesHelper.hasStereotype(attr, "ParticipantProperty")) {
					execution_status_log.add("Should remove " + attr.getHumanName() + " under " + assoc.getHumanName());
					all_remove.add(attr);
				}
			}
			for (remove in all_remove) {
				remove.setOwner(null);
			}
		}

		if (assocs_to_clean.size() > 0) {
			SessionManager.getInstance().closeSession();
		}

	}

}
catch(Exception e) {
	execution_status_log.add('Failed outermost try.');
	execution_status_log.add(e.getMessage());
}
finally {

	String filePathSeparator = System.getProperty('file.separator')

	String csvPath = read_path + filePathSeparator + read_name.toString().split("\\.")[0] + ".csv"

	execution_status_log.add("Writing ID's to " + csvPath)

	def csvFile = new File(csvPath)

	def fileWriter = new FileWriter(csvFile)

	fileWriter.write("Element Name, ID" + "\n")

	create_list.each { created ->
		/*if (created instanceof NamedElement) {
			file_writer.write(created.getName() + "," + created.getID() + "\n");
		}
		else if (created instanceof ConnectorEnd) {
			file_writer.write(created.getOwner().getName() + "-end," + created.getID() + "\n");
		}
		else {
			file_writer.write(created.getHumanName() + "," + created.getID() + "\n");
		}*/
		fileWriter.write(created[0] + "," + created[1].getID() + "\n")
	}

	fileWriter.close()

	// uncomment below to expose detailed logs
	live_log.log('Execution steps:');
	for (entry in execution_status_log) {
		 live_log.log(entry);
	}
	live_log.log('Elements processed:');
	for (entry in command_processing_log) {
		 live_log.log(entry);
	}
	live_log.log('Element creation commands:');
	for (entry in create_log) {
		 live_log.log(entry);
	}
	live_log.log('Relationship replace commands:');
	for (entry in replace_log) {
		 live_log.log(entry);
	}
	live_log.log('Element rename commands:');
	for (entry in rename_log) {
		 live_log.log(entry);
	}
	live_log.log('Verification Details:');
	for (entry in verification_log) {
		live_log.log(entry);
	}

	// render created names and id's into a file for slotting into other files



}
