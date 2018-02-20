import falcon
from endpoints.baserequest import BaseRequest
import json

class CubeThing(BaseRequest):
    def on_get(self, req, resp, property):
        query = """
            select distinct ?uri ?label {
                ?obs %s ?uri .
                ?uri rdfs:label ?label
            } order by ?label
            """ % (property)
        qres = self.dm.query_all(query)
        data = {}
        for row in qres:
            label = row.label
            uri = row.uri
            if not label in data:
                data[label] = []
            if not uri in data[label]:
                data[label].append(uri)


        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'
        resp.data = json.dumps(data, indent=1, sort_keys=True)

class CubeExpressions(CubeThing):
    def on_get(self, req, resp):
        super(CubeExpressions, self).on_get(req, resp, "lada:gen_expression")

class CubeGenres(CubeThing):
    def on_get(self, req, resp):
        super(CubeGenres, self).on_get(req, resp, "lada:gen_genre")

class CubeCorpora(CubeThing):
    def on_get(self, req, resp):
        query = """
            select distinct ?uri ?label {
                ?obs <http://h224.it.helsinki.fi:8080/varieng/data/Corpus> ?uri .
                ?uri rdfs:label ?label
            } order by ?label
            """
        qres = self.dm.query_all(query) #(g + glcd).query(query)
        data = {}
        for row in qres:
            label = row.label
            uri = row.uri
            if not label in data:
                data[label] = []
            if not uri in data[label]:
                data[label].append(uri)


        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'
        resp.data = json.dumps(data, indent=1, sort_keys=True)

class CubeFunctions(CubeThing):
    def on_get(self, req, resp):
        super(CubeFunctions, self).on_get(req, resp, "lada:gen_function")
