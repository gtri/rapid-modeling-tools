# from graph_creation import UML_METATYPE

UML_METATYPE = {}
UML_ID = {
    'count': 0
}


def get_uml_id(name=None):
    if name in UML_ID.keys():
        return UML_ID[name]
    else:
        UML_ID.update({name: 'new_{0}'.format(UML_ID['count'])})
        UML_ID['count'] += 1
        return UML_ID[name]


class Vertex(object):

    def __init__(self, name=None, node_types=set(),
                 successors=None, predecessors=None):
        self.name = name
        self.node_types = node_types
        self.successors = successors
        self.predecessors = predecessors

    @property
    def connections(self):
        connections = []
        # {'<node name>' : {'edge_attribute': 'edge type'}}
        for node_name in self.successors:
            temp_dict = {'node_name': node_name}
            temp_dict.update(self.successors[node_name])
            connections.append(temp_dict)
        for node_name in self.predecessors:
            temp_dict = {'node_name': node_name}
            temp_dict.update(self.predecessors[node_name])
            connections.append(temp_dict)
        return connections

    def spanning_tree(self, pattern=None):
        pass

    def to_dict(self):
        return {'name': self.name,
                'node types': self.node_types,
                'successors': self.successors,
                'predecessors': self.predecessors}

    def to_uml_json(self):
        # TODO: if op == create then metatype should be a key value should not
        # TODO: if op == replace then value should be a key metatype should not
        node_uml_json_list = []
        node_uml_dict = {
            'id': get_uml_id(name=self.name),
            'ops': [
                {
                    'op': 'create',
                    'path': None,
                    'metatype': UML_METATYPE[
                        self.node_types[0]],
                }
            ]
        }

        node_uml.append(node_uml_json_list)

        # check the connections.
        edge_uml_json_list = []
        for connection in self.connections:
            edge_uml_dict = {
                'id': get_uml_id(name=connection['node_name']),
                'ops': [
                    {
                        'op': 'replace',
                        'path': get_uml_id(name=connection['edge_attribute']),
                        'value': get_uml_id(name=self.name),
                    }
                ]
            }
            edge_uml_json_list.append(edge_uml_dict)
            return node_uml_json_list, edge_uml_json_list
