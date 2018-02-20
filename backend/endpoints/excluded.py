import falcon
from endpoints.baserequest import BaseRequest
from common import ns_lada, ns_data, ns_cube, ns_lcd, ns_xsd, ns_qb4cc, ns_skos
from logs import main_logger, app_logger

from rdflib import Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, FOAF, XSD, RDFS, OWL, SKOS

import json

class ExcludedPublications(BaseRequest):

    def on_get(self, req, resp):
        pass

    def on_delete(self, req, resp):
        main_logger.info('ExcludedPublications DELETE' + (req.get_param('pub') or 'empty'))
        self.dm.remove( (URIRef(req.get_param('pub')), ns_lada['excluded'], None), ['gexc'])
        #gexc.serialize("gexc-pub.ttl", format="turtle")
        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'
        resp.data = json.dumps({"status": "OK"}, indent=1, sort_keys=True)

    def on_post(self, req, resp):
        main_logger.info("ExcludedPublications POST with " + (req.get_param('pub') or 'empty' ))
        self.dm.add_triple( (URIRef(req.get_param('pub')), ns_lada['excluded'], Literal(1) ), 'gexc')

class ExcludedObservations(BaseRequest):

    def on_get(self, req, resp):
        pass

    def on_delete(self, req, resp):
        main_logger.info('ExcludedObservations DELETE' + (req.get_param('obs') or 'empty'))
        self.dm.remove( (URIRef(req.get_param('obs')), ns_lada['excluded'], None), ['gexc'] )
        #gexc.serialize("gexc.ttl", format="turtle")
        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'
        resp.data = json.dumps({"status": "OK"}, indent=1, sort_keys=True)

    def on_post(self, req, resp):
        main_logger.info("ExcludedObservations POST with " + (req.get_param('obs') or 'empty' ))

        self.dm.add_triple( (URIRef(req.get_param('obs')), ns_lada['excluded'], Literal(1) ), 'gexc' )
        #gexc.serialize("gexc.ttl", format="turtle")
