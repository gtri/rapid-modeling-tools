import networkx as nx


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

    def __init__(self, incoming_graph_data=None,
                 root_attr_columns=None, ** attr):
        self.vertex_dict = {}
        self.vertex_set = set()
        self.edge_set = set()
        super().__init__(incoming_graph_data=None)
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

    @property
    def named_edge_set(self):
        edge_set_named = set()
        for edge in self.edge_set:
            edge_set_named.add(edge.named_edge_triple)

    def create_vertex_set(self, df=None, root_node_type=None):
        for node in self.nodes:
            mask = df == node
            mask_df = df[mask]
            # test_mask = ['component', 'Atomic Thing']
            # mask_test_df = mask_df[test_mask]
            # # print(mask_test_df)
            # print(mask_test_df.dropna(
            #     axis=1, how='all').dropna(axis=0, how='all').to_dict(
            #     'records'
            # ))
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
        """
        """
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
        """
        Produce a dictionary for the attributes. Primarily used to test that
        the object was created properly.
        """
        return {'name': self.name,
                'node types': self.node_types,
                'successors': self.successors,
                'predecessors': self.predecessors}

    def to_uml_json(self, translator=None):
        """
        Produce a dictionary emulating the JSON format required by the
        Java Plugin for MagicDraw.

        *Keyword arguments*:
            *translator -- A MDTranslator object that prvoides access to the
            JSON data file that translates the information from the Python
            meanigns here to MagicDraw terminology.
        """
        # TODO: if op == create then metatype should be a key value should not
        # TODO: if op == replace then value should be a key metatype should not
        node_uml_list = []

        for count, node_type in enumerate(self.node_types):
            if count == 0:
                node_uml_dict = {
                    'id': get_uml_id(name=self.name),
                    'ops': [
                        {
                            'op': 'create',  # evaluator replace with fn input.
                            'name': self.name,
                            'path': None,
                            'metatype': translator.get_uml_metatype(
                                node_key=node_type),
                            'stereotype': translator.get_uml_stereotype(
                                node_key=node_type),
                        }
                    ]
                }
            path_val, settings_val = translator.get_uml_settings(
                node_key=node_type)
            if settings_val and count != 0:
                decorations_dict = {
                    'op': 'replace',
                    'path': path_val,
                    'value': settings_val,
                }
                node_uml_dict['ops'].append(decorations_dict)
            elif settings_val and count == 0:
                node_uml_dict['ops'][0].update({'path': path_val,
                                                'value': settings_val})
            else:
                continue

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
    """
    A Directed Edge object that stores the source and target vertex objects
    along with the edge attribute connecting the two.
        * This Class was created to facilitate the graph difference exploration
        * The Directed Edges are returned as triples:
            * (source, target, edge_attribtue)

    *Keyword arguments*:
        * source: The Vertex at the tail of the directed edge
        * target: The Vertex at the tip fo the directed edge
        * edge_attribute: The string that describes the edge type
    """

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
