from endpoints.baserequest import BaseRequest
import falcon
from common import ns_lada, ns_data, ns_cube, ns_lcd, ns_xsd, ns_qb4cc, ns_skos
from logs import main_logger, app_logger

import json

class CheckForLCDConnection(BaseRequest):
    def on_get(self, req, resp):
        status = "offline"
        if self.checkForConnection():
            status = "online"

        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'
        resp.data = json.dumps({"status": status})

class GetPublications(BaseRequest):


    def on_get(self, req, resp):
        queryStr = """select ?uri ?title ?year ?authors ?filePath ?rdfPath ?fileURI {
                ?uri a <http://h224.it.helsinki.fi:8080/varieng/Publication>  .
                ?uri <http://purl.org/dc/terms/title> ?title .
                ?uri <http://purl.org/dc/terms/issued> ?year .
                ?uri <http://purl.org/dc/terms/creator> ?authors .
                ?uri <http://lada/filePath> ?filePath .
                ?uri <http://lada/rdfPath> ?rdfPath .
                ?uri <http://lada/file> ?fileURI .
            } order by ?year ?authors
            """
        data = []
        qres = self.dm.query(queryStr, None)
        for row in qres:
            data.append(
                {
                    'uri': row['uri'],
                    'title': row['title'],
                    'year': row['year'],
                    'authors': row['authors'],
                    'filePath': row['filePath'],
                    'rdfPath': row['rdfPath'],
                    'fileURI': row['fileURI']
                }
            )
        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'
        resp.data = json.dumps(data)
