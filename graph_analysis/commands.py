import os
import warnings
from pathlib import Path

from graph_analysis.graph_creation import *

from . import DATA_DIRECTORY, OUTPUT_DIRECTORY, PATTERNS


def create_md_model(input_paths, output_path=''):
    json_patterns = {
        pattern_path.parts[-1].split('.')[0].lower(): pattern_path
        for pattern_path in PATTERNS.glob('*.json')
    }

    wkbk_paths = []
    here = Path(os.getcwd())

    for path in input_paths:
        p = Path(path)
        if not p.is_absolute():
            p = here / p
        if p.is_dir():
            p = list(p.glob('*.xlsx'))
        else:
            p = [p]

        wkbk_paths.extend(p)

    for wkbk in wkbk_paths:
        if wkbk.parts[-1].split('.')[-1] != 'xlsx':
            msg = ('\n'
                   + 'This program only supports Excel Files.'
                   + ' "{0}" was skipped, not an Excel File'
                   ).format(wkbk.parts[-1])
            warnings.warn(msg)
            continue
        xl = pd.ExcelFile(wkbk)
        not_found = 0
        pattern_sheet = ''
        for sheet in xl.sheet_names:
            if sheet.lower() not in json_patterns.keys():
                not_found += 1
                if not_found == len(xl.sheet_names):
                    warn_msg = ('The Excel File "{0}" requires an '
                                + 'unsupported pattern type.').format(
                                    wkbk.parts[-1])
                    patterns_msg = ('The currently supported '
                                    + 'patterns are: {0}'.format(
                                        [*json_patterns]))
                    warnings.warn('\n' + warn_msg + '\n' + patterns_msg)
                    break
                else:
                    continue
            else:
                pattern_sheet = sheet.lower()
                break
        if pattern_sheet:
            data = (json_patterns[pattern_sheet]).read_text()
            data = json.loads(data)
            translator = MDTranslator(json_data=data)
            evaluator = Evaluator(excel_file=wkbk, translator=translator)
            evaluator.rename_df_columns()
            evaluator.add_missing_columns()
            evaluator.to_property_di_graph()
            property_di_graph = evaluator.prop_di_graph
            property_di_graph.create_vertex_set(
                df=evaluator.df, translator=translator)
            vert_set = property_di_graph.vertex_set
            json_out = {'modification targets': []}
            decs_json = []
            edge_json = []
            for vertex in vert_set:
                vert_uml, decs_uml, edge_uml = vertex.create_node_to_uml(
                    translator=translator)
                json_out['modification targets'].extend(vert_uml)
                decs_json.extend(decs_uml)
                edge_json.extend(edge_uml)

            json_out['modification targets'].extend(decs_json)
            json_out['modification targets'].extend(edge_json)

            if not output_path:
                outfile = wkbk.parent.joinpath(
                    wkbk.parts[-1]).with_suffix('.json')
            else:
                outfile = Path(output_path).joinpath(
                    wkbk.parts[-1]).with_suffix('.json')

            (outfile).write_text(
                json.dumps(json_out, indent=4, sort_keys=True)
            )


def compare_md_model(original, updated, output_path=''):
    # TODO: Check for filename potential conflicts.
    # This may have to be done at file creation time. Maybe supply the
    # filename upstream at the get_pattern_graph_diff() stage and that can
    # pass the filename to the other functions that are burried inside.

    # Check if the file already exists in the output directory before
    # creating it. If it does add a (1) and increment by 1 until
    # a free name is found.

    provided_paths = [original]
    provided_paths.extend(updated)
    wkbk_paths = []
    here = Path(os.getcwd())

    for path in provided_paths:
        p = Path(path)
        if not p.is_absolute():
            p = here / p
        if p.is_dir():
            p = list(p.glob('*.xlsx'))
        else:
            p = [p]

        wkbk_paths.extend(p)

    outpath = Path(output_path)
    if outpath:
        if outpath.is_dir():
            # TODO Do something??? But what?
            # Check for potential filename conflicts
            pass
        elif outpath.is_file():
            raise RuntimeError('Please provide an output directory')
    else:
        outpath = wkbk_paths[0].parent

    for wkbk in wkbk_paths:
        if wkbk.parts[-1].split('.')[-1] != 'xlsx':
            msg = ('\n'
                   + 'This program only supports Excel Files.'
                   + ' "{0}" was skipped, not an Excel File'
                   ).format(wkbk.parts[-1])
            warnings.warn(msg)
            continue

    json_patterns = {
        pattern_path.parts[-1].split('.')[0].lower(): pattern_path
        for pattern_path in PATTERNS.glob('*.json')
    }

    xl = pd.ExcelFile(wkbk_paths[0])
    not_found = 0
    pattern_sheet = ''
    for sheet in xl.sheet_names:
        if sheet.lower() not in json_patterns.keys():
            not_found += 1
            if not_found == len(xl.sheet_names):
                warn_msg = ('The Excel File "{0}" requires an '
                            + 'unsupported pattern type.').format(
                                wkbk.parts[-1])
                patterns_msg = ('The currently supported '
                                + 'patterns are: {0}'.format(
                                    [*json_patterns]))
                warnings.warn('\n' + warn_msg + '\n' + patterns_msg)
                break
            else:
                continue
        else:
            pattern_sheet = sheet.lower()
            break

    if pattern_sheet:
        data = (json_patterns[pattern_sheet]).read_text()
        data = json.loads(data)
        manager = Manager(
            excel_path=provided_paths,
            json_path=data,
        )
        translator = manager.translator
        for evaluator in manager.evaluators:
            evaluator.rename_df_columns()
            evaulator.add_missing_columns()
            evaulator.to_property_di_graph()
            property_di_graph = evaulator.prop_di_graph
            property_di_graph.create_vertex_set(
                df=evaulator.df, translator=translator,
            )
            property_di_graph.create_edge_set()
            vertex_set = property_di_graph.vertex_set

        # TODO: This needs to depend on the type of outpath.
        manager.get_pattern_graph_diff()
        manager.chagnes_to_excel(out_directory=outpath)
