import os
from pathlib import Path
from warnings import warn

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
        xl = pd.ExcelFile(wkbk)
        not_found = 0
        for sheet in xl.sheet_names:
            if not_found == len(xl.sheet_names):
                warn('The Excel File {0} requires an '.format(
                     wkbk.parts[-1])
                     + 'unsupported pattern type.')
            if sheet.lower() not in json_patterns.keys():
                not_found += 1
                continue
            data = (json_patterns[sheet.lower()]).read_text()
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

            outfile = wkbk.parts[-1].split('.')[0] + '.json'
            (OUTPUT_DIRECTORY / outfile).write_text(
                json.dumps(json_out, indent=4, sort_keys=True)
            )
