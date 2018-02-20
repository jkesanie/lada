import falcon
from endpoints.baserequest import BaseRequest
from common import ns_lada, ns_data, ns_cube, ns_lcd, ns_xsd, ns_qb4cc, ns_skos
from logs import main_logger, app_logger

from rdflib import Namespace, Literal, URIRef, BNode, Graph
from rdflib.namespace import RDF, FOAF, XSD, RDFS, OWL, SKOS

import json


class Groups(BaseRequest):
    def handle_type(self, type, data):
        ggroup = Graph()
        gmap = Graph()
        for obj in data:
            uri = obj['uri']
            label = obj['label']            
            uris = obj['values']
            id = URIRef(uri) #ns_lada[type + '/' + uri]

            stmt = (id , RDF.type, ns_lada[type.title()])
            ggroup.add(stmt)
            stmt = ( id, RDFS.label, Literal(label))
            ggroup.add(stmt)

            for refUri in uris:
                stmt = ( id, URIRef('http://www.w3.org/2002/07/owl#sameAs'), URIRef(refUri) )
                gmap.add(stmt)

        self.dm.add_graph(ggroup, 'ggroup')
        self.dm.add_graph(gmap, 'gmap')

    def on_get(self, req, resp):
        pass


    def on_post(self, req, resp):
        raw_json = req.stream.read()
        obj = json.loads(raw_json.decode('utf-8'))
        main_logger.info(obj)

        # delete old data
        self.dm.clear('ggroup')
        self.dm.clear('gmap')


        for key in obj:
            if not key.startswith('no'):
                self.handle_type(key, obj[key])

        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'
        resp.data = json.dumps({"status": "OK"}, indent=1, sort_keys=True)



class GroupThings(BaseRequest):
    def on_get(self, req, resp, type):

        main_logger.info('GET: Group' + type)
        queryStr = """select ?uri ?label (group_concat(distinct ?value;separator="||") as ?values) {
                ?uri a <http://lada/""" + type + """>  .
                ?uri <http://www.w3.org/2000/01/rdf-schema#label> ?label .
                OPTIONAL {
                    ?uri <http://www.w3.org/2002/07/owl#sameAs> ?link .
                    ?link <http://www.w3.org/2000/01/rdf-schema#label> ?value .
                }
            } group by ?uri ?label order by ?label
            """
        data = []
        qres = self.dm.query(queryStr, ['ggroup', 'gmap', 'ggen', 'glcd'])
        for row in qres:
            #main_logger.info(row)
            if(row['uri'] != None):
                data.append(
                    {
                        'uri': row['uri'],
                        'label': row['label'],
                        'values': row['values'].split('||')
                    }
                )
        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'
        resp.data = json.dumps({ type.lower(): data})

    def on_post(self, req, resp, type):
        main_logger.info('Post: Group' + type.title())
        raw_json = req.stream.read()
        obj = json.loads(raw_json.decode('utf-8'))
        main_logger.info(obj)

        uri = obj['uri']
        label = obj['name']
        uris = obj['values']
        id = ns_lada[type + '/' + str(uuid.uuid4())]
        if(uri != ''):
            id = URIRef(uri)
            # delete old values
            self.dm.remove((id, None, None), 'ggroup')
            self.dm.remove((id, None, None), 'gmap')

        ggroup = Graph()
        ggmap = Graph()

        stmt = (id , RDF.type, ns_lada[type.title()])
        ggroup.add(stmt)
        stmt = ( id, RDFS.label, Literal(label))
        ggroup.add(stmt)

        for refUri in uris:
            stmt = ( id, URIRef('http://www.w3.org/2002/07/owl#sameAs'), URIRef(refUri) )
            gmap.add(stmt)

        self.dm.add_graph(ggroup, 'ggroup')
        self.dm.add_graph(gmap, 'gmap')

        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'
        resp.data = json.dumps({"status": "OK"}, indent=1, sort_keys=True)

        #ggroup.serialize("ggroup.ttl", format="turtle")
        #gmap.serialize("gmap.ttl", format="turtle")

class GroupCorpora(GroupThings):
    def on_get(self, req, resp):
        super(GroupCorpora, self).on_get(req, resp, "Corpus")

    def on_post(self, req, resp):
        super(GroupCorpora, self).on_post(req, resp, "corpus")

class GroupExpressions(GroupThings):
    def on_get(self, req, resp):
        super(GroupExpressions, self).on_get(req, resp, "Expression")

    def on_post(self, req, resp):
        super(GroupExpressions, self).on_post(req, resp, "expression")

class GroupFunctions(GroupThings):
    def on_get(self, req, resp):
        super(GroupFunctions, self).on_get(req, resp, "Function")

    def on_post(self, req, resp):
        super(GroupFunctions, self).on_post(req, resp, "function")

class GroupGenres(GroupThings):
    def on_get(self, req, resp):
        super(GroupGenres, self).on_get(req, resp, "Genre")

    def on_post(self, req, resp):
        super(GroupGenres, self).on_post(req, resp, "genre")
