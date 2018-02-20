from rdflib import Namespace, Literal, URIRef, BNode
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib.plugins.memory import IOMemory
from rdflib.namespace import RDF, FOAF, XSD, RDFS, OWL, SKOS
from common import graph_dict, ns_lada, ns_data, ns_cube, ns_lcd, ns_xsd, ns_qb4cc, ns_skos
from logs import main_logger

class InMemoryStorage(object):

    def __init__(self):

        store = IOMemory()

        self.g = ConjunctiveGraph(store=store)

        self.g.bind("lada",ns_lada)
        self.g.bind('data', ns_data)
        self.g.bind('cube', ns_cube)
        self.g.bind('qb', ns_cube)
        self.g.bind('lcd', ns_lcd)
        self.g.bind('xsd', ns_xsd)
        self.g.bind('qb4cc', ns_qb4cc)
        self.g.bind('skos', ns_skos)

        self.initNs = {
            'lada': ns_lada,
            'data': ns_data,
            'qb': ns_cube,
            'lcd': ns_lcd,
            'xsd': ns_xsd,
            'qb4cc': ns_qb4cc,
            'skos': ns_skos
        }


    def _concatenate_graphs(self, graphs):
        source = Graph()
        for g in graphs:
            if g in graph_dict:
                source += self.g.get_context(graph_dict[g])
            elif type(g) is URIRef:
                source += self.g.get_context(g)
        return source

    def add_triple(self, triple, context):
        if context:
            if type(context) is str:
                self.g.get_context(graph_dict[context]).add(triple)
            else:
                self.g.get_context(context).add(triple)
        else:
            self.g.add(triple)

    def add_graph(self, graph, context):
        if context:
            g = None
            if type(context) is str:
                g = self.g.get_context(graph_dict[context])
            else:
                g = self.g.get_context(context)
            g += graph
        else:
            self.g += graph

    def add_file(self, file, format, context):
        if context:
            if type(context) is str:
                self.g.get_context(graph_dict[context]).parse(file, format=format)
            else:
                self.g.get_context(context).parse(file, format=format)
        else:
            self.g.parse(file, format=format)


    def query(self, queryString, contexts):

        if contexts:
            if type(contexts) is list:
                return self._concatenate_graphs(contexts).query(queryString, initNs=self.initNs)
            elif type(contexts) is str:
                return self.g.get_context(graph_dict[contexts]).query(queryString, initNs=self.initNs)
            else:
                return self.g.get_context(contexts).query(queryString, initNs=self.initNs)
        else:
            return self.g.query(queryString, initNs=self.initNs)

    def value(self, subject, predicate, context):
        if context:
            if type(context) is str:
                return self.g.get_context(graph_dict[context]).value(subject, predicate)
            else:
                return self.g.get_context(context).value(subject, predicate)
        else:
            return self.g.value(subject, predicate)

    def remove(self, triple_pattern, contexts):
        if contexts:
            if type(contexts) is list:
                self._concatenate_graphs(contexts).remove(triple_pattern)
            else:
                self.g.get_context(graph_dict[contexts]).remove(triple_pattern)
        else:
            self.g.remove(triple_pattern)

    def clear(self, context):
        if context:
            if type(context) is str:
                self.g.remove_context(self.g.get_context(graph_dict[context]))
            else:
                self.g.remove_context(self.g.get_context(context))
        else:
            self.g.remove( (None, None, None) )

    def count_triples(self):
        c = 0;
        for s, p, o in self.g:
            c = c +1;
        return c

    def export(self, context):
        if type(context) is str:
            self.g.get_context(graph_dict[context]).serialize(context + ".ttl", format="turtle")
