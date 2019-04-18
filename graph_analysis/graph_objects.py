import networkx as nx

from .utils import to_uml_json_decorations, to_uml_json_edge, to_uml_json_node


class PropertyDiGraph(nx.DiGraph):
    """
    Class for aggregating the Excel data from the Evaluator into a
    Directed Graph with node and edge properties.

    Parameters
    ----------
    incoming_graph_data : input graph
        Data to initialize the graph. If None is supplied than an empty
        graph is created. The data can be any format supported by
        `to_networkx_graph()`

    root_attr_columns : set
        Set of columns from the Excel file that do not appear under the
        'Columns to Navigation Map' and should be applied to the root node
        as additional attributes.

    Properties
    ----------
    named_vertex_set : set of strings
        Returns a vertex set populated by vertex.name

    vertex_set : set of Vertex objects
        Returns a vertex set containing `Vertex` objects.

    named_edge_set : set of strings
        Returns an edge set of the edges represented as a string.

    edge_set : set of DiEdge objects
        Returns an edge set contaning `DiEdge` objects.

    edge_dict : dict
        Returns a dictionary with string representation keys and a DiEdge
        as the value.

    Attributes
    ----------
    vertex_dict : dictionary
        dictionary with the keys as the Vertex name and the value as the
        vertex object.

    vertex_set : set
        set comprised of instances of the Vertex class.

    edge_set : set
        set comprised of instances of the DiEdge class.

    root_attr_columns : set
        set comprised of column names from the Excel file that are not found in
        the JSON file, could be empty.

    See Also
    --------
    networkx.DiGraph
    """

    def __init__(self, incoming_graph_data=None,
                 root_attr_columns=None, **attr):
        self.root_attr_columns = root_attr_columns
        super().__init__(incoming_graph_data=None)

    @property
    def vertex_set(self):
        """
        Returns a set of Vertex objects.
        """
        return set(self.nodes[node][node] for node in self.nodes)

    @property
    def named_vertex_set(self):
        """
        Returns a set of vertex names.
        """
        # TODO: Consider writing an ID_vertex_set for the ids because they
        # are more useful than the names.
        # vertex_set = self.vertex_set
        return set(vertex.name for vertex in self.vertex_set)

    @property
    def edge_set(self):
        """
        Returns a set of DiEdge objects.
        """
        return set(self.edges[edge]['diedge'] for edge in self.edges)

    @property
    def edge_dict(self):
        """
        Returns a dictionary with a tuple contaning the strings
        corresponding to the value.source, value.target
        value.edge_attribute, the value is a DiEdge object.
        """
        return {(k[0], k[1], v['edge_attribute']): v['diedge']
                for k, v in self.edges.items()}

    @property
    def named_edge_set(self):
        """
        Returns a set of named edge triples of the form (source name,
        target name, edge attribute) from the edge objects in the edge_set.
        """
        return set(edge.named_edge_triple for edge in self.edge_set)


class VertexReporterMixin:
    """
    Mixin that supplies the functions for a Vertex to package itself
    to JSON for consumption by MagicDraw. Contains a write method for
    change, deletion and creation instructions.
    """

    def change_node_to_uml(self, translator=None):
        """
        Package the Vertex information into a dictionary to be written out
        to JSON change instructions for the Player Piano.

        Returns a function call with the node attributes as a dictioanry
        keyword argument that builds a change dict for the passed node.

        Parameters
        ----------
        translator : MDTranslator

        Returns
        -------
        rename_uml_instructions : dict
            Contains the instructions MagicDraw needs to rename a node.

        See Also
        --------
        to_uml_json_node
        """
        my_id = str(self.id)
        if '_' == my_id[0]:
            id = my_id
        else:
            id = 'new_' + my_id
        for count, node_type in enumerate(self.node_types):
            if count == 0:
                node_dict = {
                    'id': id,
                    'op': 'rename',
                    'name': self.name,
                    'path': None,
                    'metatype': translator.get_uml_metatype(
                        node_key=node_type),
                    'stereotype': translator.get_uml_stereotype(
                        node_key=node_type),
                    'attributes': self.attributes,
                }
                return to_uml_json_node(**node_dict)

    def delete_node_to_uml(self, translator=None):
        """
        Packages the Vertex information into a dictionary to be written to
        JSON for consumption by the Player Piano into MagicDraw.

        Returns a function call with the node attributes as a dictioanry
        keyword argument that builds a change dict for the passed node.

        Parameters
        ----------
        translator : MDTranslator

        Returns
        -------
        delete_uml_instructions : dict
            Contains the instructions MagicDraw needs to delete a node.
        """
        my_id = str(self.id)
        if '_' == my_id[0]:
            id = my_id
        else:
            id = 'new_' + my_id
        node_dict = {
            'id': id,
            'op': 'delete',
            'name': self.name,
            'path': None,
            'metatype': translator.get_uml_metatype(
                node_key=self.node_types[0]),
            'stereotype': translator.get_uml_stereotype(
                node_key=self.node_types[0]),
            'attributes': self.attributes,
        }
        return to_uml_json_node(**node_dict)

    def create_node_to_uml(self, old_name='', translator=None):
        """Returns two lists of dictionaries formatted for JSON output to the
        MagicDraw interface layer. The first list returned contains the vertex
        and its values with additional subdictionaries if that particular
        Vertex had more than one node_type. The second list returned contains
        all of the connections of the Vertex.

        Parameters
        ----------
        translator : MDTranslator Object
            A MDTranslator object that prvoides access to the
            JSON data file that translates the information from the Python
            meanigns here to MagicDraw terminology.

        Notes
        -----
        First, the function loops over the node_types attribute. For the first
        node_type attribute encountered (regardless of its value), the metadata
        associated with that node_type is recorded. Subsequent loop iterations
        provide additional node_type information.
        While iterating the node_type information, the function checks
        for nodes with settings values under the vertex settings key in the
        JSON. If a node has a settings value then the ID of the associated
        settings node is retreived and associated to the node_decorations list.
        Next, the edge_uml_list is built using the connections property. From
        there, a source and target id are identified from the connections
        information and the get_uml_id function.
        With all of these lists populated, the function returns the
        node_uml_list, node_decorations, and the edge_uml_list to be packaged
        for the final JSON output. The JSON file contains all of the vertex
        data first followed by the edge data.
        """
        node_uml_list = []
        node_decorations = []
        # TODO: Remove this and test consequences.
        if old_name:
            name = old_name
        else:
            name = self.name

        for count, node_type in enumerate(self.node_types):
            if count == 0:
                my_id = str(self.id)
                if '_' == my_id[0]:
                    id = my_id
                else:
                    id = 'new_' + my_id
                node_dict = {
                    'id': id,
                    'op': 'create',  # evaluator replace with fn input.
                    'name': self.name,
                    'path': None,
                    'metatype': translator.get_uml_metatype(
                        node_key=node_type),
                    'stereotype': translator.get_uml_stereotype(
                        node_key=node_type),
                    'attributes': self.attributes,
                }
                node_uml_dict = to_uml_json_node(**node_dict)
                node_uml_list.append(node_uml_dict)

            if self.settings:
                for set_dict in self.settings:
                    item = list(set_dict.items())
                    path, value = item[0][0], item[0][1]
                    if isinstance(value, list) and any(
                            val in translator.uml_id.keys() for val in value):
                        values = filter(
                            lambda x: x in translator.uml_id.keys(), value)
                        value = []
                        for val in values:
                            id_val = str(translator.uml_id[val])
                            if '_' != id_val[0]:
                                id_val = 'new_' + id_val
                            value.append(id_val)
                    elif isinstance(
                            value, str) and value in translator.uml_id.keys():
                        value = str(translator.uml_id[value])
                        if '_' != value[0]:
                            value = 'new_' + value
                    node_dict.update({'op': 'replace',
                                      'path': path,
                                      'value': value})
                    decorations_dict = to_uml_json_decorations(**node_dict)
                    node_decorations.append(decorations_dict)
            else:
                continue

        # check the connections.
        edge_uml_list = []
        for connection in self.connections:
            # There will be some notion of a flag for the 'path' key to
            # change between m0, m1 and m2 type MD diagrams but that info is
            # TBD
            id_val = str(translator.get_uml_id(name=connection['source']))
            if '_' == id_val[0]:
                id = id_val
            else:
                id = 'new_' + id_val
            val_val = str(translator.get_uml_id(name=connection['target']))
            if '_' == val_val[0]:
                value = val_val
            else:
                value = 'new_' + val_val

            edge_dict = {
                'id': id,
                'op': 'replace',
                'path': connection['edge_attribute'],
                'value': value,
            }
            edge_uml_dict = to_uml_json_edge(**edge_dict)
            edge_uml_list.append(edge_uml_dict)

        return node_uml_list, node_decorations, edge_uml_list


class Vertex(VertexReporterMixin):
    """
    Class for representing the node data from the PropertyDiGraph as an object.

    Vertex provides convenient access to the properties of the nodes in the
    PropertyDiGraph and critically provides the method for packaging itself
    for the MagicDraw interface layer.

    Properties
    ----------
    connections : list
        List of dictionaries with successors first and predecessors after. The
        dictionaries contain source, target key value pairs.

    Parameters
    ----------
    name : string
        Name attribute of the vertex object that is the same as the name in the
        Evaluator.df entires.

    node_types : set
        Set of strings that reflects the names of the columns under which
        the name of this vertex can be found in the Evaluator.df

    successors : set
        Set of successors saved off from the PropertyDiGraph

    predecessors : set
        Set of predecessors saved off from the PropertyDiGraph

    attribtues : dictionary
        Dictionary holding the data encapsulated in the root_node_attr_columns

    Notes
    -----
    This class encapsulates the node data from the PropertyDiGraph, providing
    user defined functions for accessing the information of a particular
    Vertex. Additionally, this class contains the to_uml_json() method which,
    is now deprecated in favor of the VertexReporterMixin which contains all
    of the JSON writing functionality.
    """

    def __init__(self, name=None, node_types=list(),
                 successors=None, predecessors=None, attributes=None,
                 settings=None, id=None, original_name=False,
                 original_id=None, **kwargs,):
        self.name = name
        if original_id:
            self.id = original_id
            self.original_id = original_id
        else:
            self.id = id
            self.original_id = original_id
        # self.id = id
        self.node_types = node_types
        self.successors = successors
        self.predecessors = predecessors
        self.attributes = attributes
        self.settings = settings
        self.original_name = original_name
        # self.original_id = original_id

    def __repr__(self):
        return 'Vertex Obj({0}, {1})'.format(
            self.name, self.id,)

    @property
    def has_rename(self):
        if self.original_name or self.original_id:
            return True
        else:
            return False

    @property
    def connections(self):
        """Returns a list of dictionaries with key value pairs for source and
        target node names.
        """
        connections = []
        if self.successors:
            connections.extend(self.successors)
        if self.predecessors:
            connections.extend(self.predecessors)
        return connections

    def to_dict(self):
        """Produces a dictionary for the attributes. Used to test that
        the object was created properly.
        """
        return {'name': self.name,
                'node types': self.node_types,
                'successors': self.successors,
                'predecessors': self.predecessors,
                'attributes': self.attributes}

    def to_uml_json(self, translator=None):
        """
        For details see the `VertexReporterMixin.create_node_to_uml()`.
        This functions is left in because of its use in testing.
        """
        # TODO: if op == create then metatype should be a key value should not
        # TODO: if op == replace then value should be a key metatype should not
        node_uml_list = []
        node_decorations = []

        for count, node_type in enumerate(self.node_types):
            if count == 0:
                node_uml_dict = {
                    'id': translator.get_uml_id(name=self.name),
                    'ops': [
                        {
                            'op': 'create',  # evaluator replace with fn input.
                            'name': self.name,
                            'path': None,
                            'metatype': translator.get_uml_metatype(
                                node_key=node_type),
                            'stereotype': translator.get_uml_stereotype(
                                node_key=node_type),
                            'attributes': self.attributes
                        }
                    ]
                }
            path_val, settings_val = translator.get_uml_settings(
                node_key=node_type)
            if settings_val:
                if self.settings:
                    settings_val = list(set(get_uml_id(name=node)
                                            for node in self.settings))
                decorations_dict = {
                    'id': get_uml_id(name=self.name),
                    'ops': [
                        {
                            'op': 'replace',
                            'path': '/' + path_val,
                            'value': settings_val,
                        }
                    ]
                }
                node_decorations.append(decorations_dict)
            else:
                continue

        node_uml_list.append(node_uml_dict)

        # check the connections.
        edge_uml_list = []
        for connection in self.connections:
            # There will be some notion of a flag for the 'path' key to
            # change between m0, m1 and m2 type MD diagrams but that info is
            # TBD
            edge_uml_dict = {
                'id': translator.get_uml_id(name=connection['source']),
                'ops': [
                    {
                        'op': 'replace',
                        'path': '/m2/' + connection['edge_attribute'],
                        'value': translator.get_uml_id(
                            name=connection['target']),
                    }
                ]
            }
            edge_uml_list.append(edge_uml_dict)

        return node_uml_list, node_decorations, edge_uml_list


class DiEedgeReporterMixin:
    """
    Mixin that supplies the functions for a Directed Edge to package itself
    to JSON for consumption by MagicDraw. It contains a write method for
    changed edges.
    """

    def edge_to_uml(self, op='', translator=None):
        """
        Packages the DiEdge information into a dictionary to be written to
        JSON for consumption by the Player Piano into MagicDraw.

        Returns a function call with the edge attributes as a dictionary of
        keyword argument that builds a change dict for the passed edge.

        Parameters
        ----------
        op : string
            Specifies the desired operation for MagicDraw to preform when
            it reads the instructions for this edge

        translator : MDTranslator
        """
        id_val = str(self.source.id)
        if '_' == id_val[0]:
            id = id_val
        else:
            id = 'new_' + id_val
        val_val = str(self.target.id)
        if '_' == val_val[0]:
            value = val_val
        else:
            value = 'new_' + val_val
        edge_dict = {
            'id': id,
            'op': op,
            'path': self.edge_attribute,
            'value': value,
        }
        return to_uml_json_edge(**edge_dict)


class DiEdge(DiEedgeReporterMixin):
    """A Directed Edge object stores the source and target vertex objects
    along with the edge attribute connecting the two.

    This Class was created to facilitate the graph difference exploration
    The Directed Edges are returned as triples (source, target, edge_attribtue)

    Properties
    ----------
    named_edge_triple : tuple
        Triple with the source.name and target.name attributes and the
        edge_attribute string.

    edge_vert_type_triple : tuple
        The triple with the source.node_types and target.node_types attributes
        and the edge_attribute string. Should this property be updated to
        return multiple triples if there are multiple node_types?

    edge_triple : tuple
        The triple with the source and target Vertex objects and the
        edge_attribute string.

    Attributes
    ----------
    source : Vertex
        The Vertex at the tail of the directed edge

    target : Vertex
        The Vertex at the tip fo the directed edge

    edge_attribute : string
        The string that describes the edge type

    __len__ : Reference
        This is intended to mean that a DiEdge object only represents a single
        edge. If there are length issues later relating to a DiEdge then
        setting the __len__ reference in this was is incorrect.
    """

    def __init__(self, source=None, target=None, edge_attribute=None):
        # Source, Target and attr are actually objects and attr is str.
        self.source = source
        self.target = target
        self.edge_attribute = edge_attribute

    def __len__(self):  # TODO: Is this a snake in the grass???
        return 1

    def __repr__(self):
        return 'DiEdge Obj({0}, {1}, {2})'.format(
            self.source.name, self.target.name, self.edge_attribute)

    @property
    def has_rename(self):
        return self.source.has_rename or self.target.has_rename

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
