from logs import main_logger, app_logger
from rdflib import Namespace, Literal, URIRef, BNode
from rdflib.graph import Graph
from rdflib.namespace import RDF, FOAF, XSD, RDFS, OWL, SKOS

import os
import json

class DataManager(object):

    def __init__(self, graph_storage, cc_storage, file_storage, lcdURL, lcdPort):
        self.storage = graph_storage
        self.cc_storage = cc_storage
        self.file_storage = file_storage
        self.lcdURL = lcdURL
        self.lcdPort = lcdPort

        # TODO: get this from properties
        self.cc_inputFolder = 'data/corpus-composition/'
        inputFolder = self.cc_inputFolder
        # load corpus compositions
        for infile in os.listdir(inputFolder):
            main_logger.info('Adding ' + infile + ' to the corpus composition graph')
            self.cc_storage.add_file(inputFolder + infile, "turtle", None)

        # calculate gcc triples
        main_logger.info("Number of triples in GCC:" + str(self.cc_storage.count_triples()))

        # process corpus mapping - this should come from LCD
        with open('data/corpus-mapping.json') as data_file:
            data = json.load(data_file)
            g = Graph()
            for abbr in data:
                uri = data[abbr]
                corpusTypeURI = URIRef('http://h224.it.helsinki.fi:8080/varieng/types/Corpus')
                g.add( (URIRef(uri), RDF.type, corpusTypeURI) )
                g.add( (URIRef(uri), RDFS.label, Literal(abbr)))

            self.storage.add_graph(g, 'glcd')

        self.storage.export('glcd')

    def get_file_storage(self):
        return self.file_storage

    def query_cc(self, query_string):
        return self.cc_storage.query(query_string, None)


    def query_all(self, query_string):
        return self.storage.query(query_string, None)

    def query(self, query_string, target_graphs):
        return self.storage.query(query_string, target_graphs)

    def value(self, subject, predicate, target_graph):
        return self.storage.value(subject, predicate, target_graph)

    def remove(self, triple_pattern, target_graphs):
        self.storage.remove(triple_pattern, target_graphs)

    def remove_from_all(self, triple_pattern):
        self.storage.remove(triple_pattern, None)

    def add_triple(self, triple, target_graph):
        self.storage.add_triple(triple, target_graph)

    def add_graph(self, graph, target_graph):
        self.storage.add_graph(graph, target_graph)

    def add_file(self, file, format, target_graph):
        self.storage.add_file(file, format, target_graph)


    def clear(self, target_graph):
        self.storage.clear(target_graph)

    def export(self, context):
        self.storage.export(context)
