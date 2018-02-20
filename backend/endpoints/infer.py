import falcon
from endpoints.baserequest import BaseRequest
from common import ns_lada, ns_data, ns_cube, ns_lcd, ns_xsd, ns_qb4cc, ns_skos
from logs import main_logger, app_logger

from rdflib import Namespace, Literal, URIRef, BNode
from rdflib.graph import Graph
from rdflib.namespace import RDF, FOAF, XSD, RDFS, OWL, SKOS

import json

class Infer(BaseRequest):

    def on_post(self, req, resp):
        main_logger.info("POST /infer")

        #self.dm.clear('ginf')

        queryStr = """
            CONSTRUCT { ?s1 ?p1 ?o1  }
            WHERE {
                ?o1 <http://www.w3.org/2002/07/owl#sameAs> ?o2 .
                ?s1 ?p1 ?o2 .
                ?o2 ?p2 ?o3 .
            }
            """

        self.dm.export('gmap')
        self.dm.export('ggroup')
        qres = self.dm.query(queryStr, ['gmap', 'ggen', 'ggroup'])
        ginf = Graph()
        for row in qres:
            #main_logger.info(row)
            pred = str(row[1])
            #main_logger.info(pred)
            parts = pred.split('gen_')
            if "gen_" in pred:
                ginf.add( ( row[0], URIRef(parts[0] + parts[1]), row[2] ) )
            else:
                ginf.add(row)

        ginf.serialize("ginf.ttl", format="turtle")
        self.dm.add_graph(ginf, 'ginf')

        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'
        resp.data = json.dumps({"status": "OK"})
