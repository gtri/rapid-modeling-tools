import json
import networkx as nx

# TODO: implement DATA or the PATH to the DATA as a global.
# Better implemented with either the DIRECTORY and ROOT as globals or
# with the DATA itself as a global
with open('../data/CompositionGraphMaster.json') as f:
    data = json.load(f)


try:
    UML_METATYPE = data['Vertex MetaTypes']
except KeyError:
    UML_METATYPE = {
        'Composite Thing': 'Class',
        'Atomic Thing': 'Class',
        'composite owner': 'Property',
        'component': 'Property',
        'A_"composite owner"_component': 'Association'
    }


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


class PropertyDiGraph(nx.DiGraph):

    def __init__(self, incoming_graph_data=None, **attr):
        self.vertex_dict = {}
        self.vertex_set = set()
        self.edge_set = set()
        super().__init__(incoming_graph_data=None, **attr)
        # TODO: these two attribtues caused my Evaluator tests to fail
        # TODO: figure out a way to set these attrs without creating in init
        # self.create_vertex_set()
        # self.create_edge_set()

    @property
    def named_vertex_set(self):
        vert_set_named = set()
        for vert in self.vertex_set:
            vert_set_named.add(vert.name)

        return vert_set_named

    def create_vertex_set(self, df=None):
        for node in self.nodes:
            mask = df == node
            node_type_columns = df[mask].dropna(
                axis=1, how='all').columns
            node_types = {col for col in node_type_columns}
            vertex = Vertex(name=node, node_types=node_types,
                            successors=self.succ[node],
                            predecessors=self.pred[node])
            self.vertex_dict.update({node: vertex})
            self.vertex_set.add(vertex)

        return self.vertex_set

    def create_edge_set(self):
        edge_pair_attr_dict = nx.get_edge_attributes(self, 'edge_attribute')
        for edge_pair in edge_pair_attr_dict:
            source_vert = self.vertex_dict[edge_pair[0]]
            target_vert = self.vertex_dict[edge_pair[1]]
            edge = DiEdge(source=source_vert,
                          target=target_vert,
                          edge_attribute=edge_pair_attr_dict[edge_pair])
            self.edge_set.add(edge)


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
            temp_dict = {'source': self.name,
                         'target': node_name}
            temp_dict.update(self.successors[node_name])
            connections.append(temp_dict)
        for node_name in self.predecessors:
            temp_dict = {'source': node_name,
                         'target': self.name}
            temp_dict.update(self.predecessors[node_name])
            connections.append(temp_dict)
        return connections

    def to_dict(self):
        return {'name': self.name,
                'node types': self.node_types,
                'successors': self.successors,
                'predecessors': self.predecessors}

    def to_uml_json(self):
        # TODO: if op == create then metatype should be a key value should not
        # TODO: if op == replace then value should be a key metatype should not
        node_types_list = list(self.node_types)
        node_uml_list = []
        node_uml_dict = {
            'id': get_uml_id(name=self.name),
            'ops': [
                {
                    'op': 'create',
                    'name': self.name,
                    'path': None,
                    'metatype': UML_METATYPE[
                        node_types_list[0]],
                }
            ]
        }

        node_uml_list.append(node_uml_dict)

        # check the connections.
        edge_uml_list = []
        for connection in self.connections:
            edge_uml_dict = {
                'id': get_uml_id(name=connection['source']),
                'ops': [
                    {
                        'op': 'replace',
                        'path': '/' + connection['edge_attribute'],
                        'value': get_uml_id(name=connection['target']),
                    }
                ]
            }
            edge_uml_list.append(edge_uml_dict)

        return node_uml_list, edge_uml_list


class DiEdge(object):
    """Source and Target should be Vertex Objects.
    The DiEdge object's primary role is to return a triple describing
    the tail of the edge, tip of the edge and the type of the edge that
    connects two nodes"""

    def __init__(self, source=None, target=None, edge_attribute=None):
        # Source, Target and attr are actually strings not objects.
        self.source = source
        self.target = target
        self.edge_attribute = edge_attribute

    @property
    def named_edge_triple(self):
        return (self.source.name, self.target.name, self.edge_attribute)

    @property
    def edge_vert_type_triple(self):
        return (self.source.node_types,
                self.target.node_types,
                self.edge_attribute)

    @property
    def edge_triple(self):
        return (self.source, self.target, self.edge_attribute)
