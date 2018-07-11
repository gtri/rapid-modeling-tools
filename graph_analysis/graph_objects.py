UML_ID = {}
UML_METACLASS = {}


class Vertex(object):

    def __init__(self, name=None, node_types=set(),
                 successors=None, predecessors=None):
        self.name = name
        self.node_types = node_types
        self.successors = successors
        self.predecessors = predecessors

    @property
    def connections(self):
        pass

    def spanning_tree(self, pattern=None):
        pass

    def to_dict(self):
        return {'name': self.name,
                'node types': self.node_types,
                'successors': self.successors,
                'predecessors': self.predecessors}
