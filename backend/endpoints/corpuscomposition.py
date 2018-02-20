import falcon
from endpoints.baserequest import BaseRequest
from common import ns_lada, ns_data, ns_cube, ns_lcd, ns_xsd, ns_qb4cc, ns_skos
from logs import main_logger, app_logger

from rdflib import Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, FOAF, XSD, RDFS, OWL, SKOS

import json

class CCFiltered(BaseRequest):

    def on_post(self, req, resp):
        pubURI = req.get_param('pubURI')
        sheet = req.get_param('sheet')
        raw_json = req.stream.read()
        obj = json.loads(raw_json.decode('utf-8'))

        data = []

        for corpus in obj['corpora']:
            corpusURI = corpus['uri']
            corpusLabel = corpus['label']
            queryStr= """
                    select distinct ?cc ?label ?dim {
                    ?cc a <http://data.hulib.helsinki.fi/ns/qb4cc#CorpusComposition> .
                    ?cc <http://data.hulib.helsinki.fi/ns/qb4cc#corpus> <%s> .
                    ?cc <http://purl.org/dc/terms/title> ?label .
                    OPTIONAL {
                        ?cc <http://purl.org/linked-data/cube#structure> ?s .
                        ?s <http://data.hulib.helsinki.fi/ns/qb4cc#dimension> ?d .
                        ?d <http://purl.org/linked-data/cube#dimension> ?dim .
                        ?dim a <http://data.hulib.helsinki.fi/ns/qb4cc#Genre> .

                    }

                }
            """ % (corpusURI)
            pubData = []
            qres = self.dm.query_cc(queryStr)
            for row in qres:
                genres = []
                if(row['dim']):
                    #main_logger.info('has dim')
                    main_logger.info(row['dim'])
                    q2 = "select distinct ?uri ?label { <%s> <http://purl.org/linked-data/cube#codeList> ?list . ?uri <http://www.w3.org/2004/02/skos/core#inScheme> ?list . ?uri <http://www.w3.org/2004/02/skos/core#prefLabel> ?label } order by ?label" % (row['dim'])
                    main_logger.info(q2)
                    qres2 = gcc.query(q2)
                    for row2 in qres2:
                        genres.append({
                            'uri': row2['uri'],
                            'label': row2['label']
                        })
                pubData.append(
                    {
                        'uri': row['cc'],
                        'label': row['label'],
                        'genres': genres
                    }
                )
            data.append( {
                'uri': corpusURI,
                'label': corpusLabel,
                'options': pubData,
                'selected': ''
            })
        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'
        resp.data = json.dumps({pubURI + sheet: data})
