import falcon
from endpoints.baserequest import BaseRequest
from common import ns_lada, ns_data, ns_cube, ns_lcd, ns_xsd, ns_qb4cc, ns_skos
from logs import main_logger, app_logger

from rdflib import Namespace, Literal, URIRef, BNode, Graph
from rdflib.namespace import RDF, FOAF, XSD, RDFS, OWL, SKOS

import json

class FilteredObservationsPreview(BaseRequest):

    def on_post(self, req, resp):
        main_logger.info('Preview')

        raw_json = req.stream.read()
        obj = json.loads(raw_json.decode('utf-8'))
        main_logger.info(obj)

        expressions = obj['expression']
        expFilters = []
        for f in expressions:
            if(f['type'] != 'group'):
                for fv in f['values']:
                    expFilters.append('<' + fv + '>')

        corpora = obj['corpus']
        corpusFilters = []
        for f in corpora:
            if(f['type'] != 'group'):
                for fv in f['values']:
                    corpusFilters.append('<' + fv + '>')

        genres = obj['genre']
        genreFilters = []
        for f in genres:
            if(f['type'] != 'group'):
                for fv in f['values']:
                    genreFilters.append('<' + fv + '>')

        functions = obj['function']
        funcFilters = []
        for f in functions:
            if(f['type'] != 'group'):
                for fv in f['values']:
                    funcFilters.append('<' + fv + '>')




        query = """
            select distinct ?title ?pub ?ds ?obs {
                ?obs a <http://purl.org/linked-data/cube#Observation> .
                ?obs <http://purl.org/linked-data/cube#dataSet> ?ds .
                ?ds <http://data.hulib.helsinki.fi/id/ontology/varieng/v1/file> ?file .
                ?pub <http://lada/file> ?file .
                ?pub <http://purl.org/dc/terms/title> ?title .
                ?obs <http://data.hulib.helsinki.fi/id/ontology/varieng/v1/data/frequency> ?freq .
                    ?obs <http://lada/timeperiod> ?period .
                    ?period <http://www.w3.org/2000/01/rdf-schema#label> ?periodName .
                #FILTER(?freq > 0) .
        """

        if obj['noexpression']:
            if obj['noexpression'] == 1:
                query = query + " FILTER NOT EXISTS { ?obs <http://lada/gen_expression> ?exp } . "
            if obj['noexpression'] == 3:
                query = query + " ?obs <http://lada/gen_expression> ?exp . "


        else:
            if(len(expFilters) > 0):
                joined = ", ".join(expFilters)
                query = query + "?obs <http://lada/gen_expression> ?exp . FILTER(?exp IN(" + joined + ")) . "


        if obj['nocorpus']:
            if obj['nocorpus'] == 1:  # no value
                query = query + " FILTER NOT EXISTS { ?obs <http://h224.it.helsinki.fi:8080/varieng/data/Corpus> ?corpus } . "
            if obj['nocorpus'] == 2:
                query = query + " OPTIONAL { ?obs <http://h224.it.helsinki.fi:8080/varieng/data/Corpus> ?corpus . ?corpus <http://www.w3.org/2000/01/rdf-schema#label> ?corpusName . } "
            if obj['nocorpus'] == 3:
                query = query + " ?obs <http://h224.it.helsinki.fi:8080/varieng/data/Corpus> ?corpus . "
        else:
            # some value
            query = query + """
                ?obs <http://h224.it.helsinki.fi:8080/varieng/data/Corpus> ?corpus .
                ?corpus <http://www.w3.org/2000/01/rdf-schema#label> ?corpusName .
                """
            if len(corpusFilters) > 0: # specific values
                joined = ", ".join(corpusFilters)
                query = query + " FILTER(?corpus IN(" + joined + ")) . "

#        if obj['nocorpus']:
#            if obj['nocorpus'] == 1:
#                query = query + " FILTER NOT EXISTS { ?obs <http://h224.it.helsinki.fi:8080/varieng/data/Corpus> ?corpus } . "
#            if obj['nocorpus'] == 3:
#                query = query + " ?obs <http://h224.it.helsinki.fi:8080/varieng/data/Corpus> ?corpus . "
#        else:
#            query = query + """
#                ?obs <http://lada/corpus> ?corpus .
#                # TODO: get rid of this filter!
#                #FILTER NOT EXISTS { ?obs <http://h224.it.helsinki.fi:8080/varieng/data/Corpus> ?corpus  }
#                """
#            joined = ", ".join(corpusFilters)
#            query = query + " FILTER(?corpus IN(" + joined + ")) . "

        if obj['nofunction']:
            if obj['nofunction'] == 1:
                query = query + " FILTER NOT EXISTS { ?obs <http://lada/gen_function> ?func } . "
            if obj['nofunction'] == 3:
                query = query + " ?obs <http://lada/gen_function> ?func . "
        else:
            if(len(funcFilters) > 0):
                joined = ", ".join(funcFilters)
                query = query + "?obs <http://lada/gen_function> ?func . FILTER(?func IN(" + joined + ")) . "

        if obj['nogenre']:
            if obj['nogenre'] == 1:
                query = query + " FILTER NOT EXISTS { ?obs <http://lada/gen_genre> ?genre } . "
            if obj['nogenre'] == 3:
                query = query + " ?obs <http://lada/gen_genre> ?genre . "

        else:
            if(len(genreFilters) > 0):
                joined = ", ".join(genreFilters)
                query = query + "?obs <http://lada/gen_genre> ?genre . FILTER(?genre IN(" + joined + ")) . "




        query = query + "} order by ?title ?ds ?obs"

        pubs = [];
        data = {}
        previousDs = None
        previousPub = None
        numOfDs = 0
        numOfObs = 0
        main_logger.info(query)
        qres = self.dm.query_all(query)
        for row in qres:
            #main_logger.info(row)
            pub = row['pub']
            ds = row['ds']
            obs = row['obs']
            if not pub in data:
                data[pub] = {'title': row['title'], 'uri': row['pub']}

            if previousDs == None and previousPub == None:
                main_logger.info('first row')
                data[pub]['obs'] = 1
                data[pub]['ds'] = 1
                previousDs = ds
                previousPub = pub
                continue


            if previousDs != ds:
                numOfDs = numOfDs + 1
                data[pub]['ds'] = numOfDs
                data[pub]['obs'] = numOfObs

            if previousPub != pub:
                data[previousPub]['ds'] = numOfDs

                data[previousPub]['obs'] = numOfObs + 1
                numOfObs = 0
                numOfDs = 0



            numOfObs = numOfObs + 1

            previousDs = ds
            previousPub = pub

        if previousPub != None:
            data[previousPub]['obs'] = numOfObs

        for key in data:
            pubs.append(data[key])


        main_logger.info(data)

        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'
        resp.data = json.dumps(pubs)



class QueryFilteredObservations(BaseRequest):


    def on_post(self, req, resp):
        main_logger.info('POST query filtered')
        raw_json = req.stream.read()
        obj = json.loads(raw_json.decode('utf-8'))
        main_logger.info(obj)

        expressions = obj['expression']
        expFilters = []
        for f in expressions:
            if(f['type'] != 'group'):
                expFilters.append('<' + f['uri'] + '>')

        corpora = obj['corpus']
        corpusFilters = []
        for f in corpora:
            if(f['type'] != 'group'):
                corpusFilters.append('<' + f['uri'] + '>')

        genres = obj['genre']
        genreFilters = []
        for f in genres:
            if(f['type'] != 'group'):
                genreFilters.append('<' + f['uri'] + '>')

        functions = obj['function']
        funcFilters = []
        for f in functions:
            if(f['type'] != 'group'):
                funcFilters.append('<' + f['uri'] + '>')


        query = """
            select distinct ?obs ?pub ?title ?year ?authors ?pubExcluded ?ds ?excluded ?row ?col ?sheet ?comment ?freq ?per ?corpus ?corpus2 ?corpusName ?genre ?genreName ?exp ?expName ?func ?funcName ?period ?periodName {
                ?obs a <http://purl.org/linked-data/cube#Observation> .
                ?obs <http://lada/filtered> ?f .
                ?pub <http://lada/file> ?file .
                ?pub <http://purl.org/dc/terms/title> ?title .
                ?pub <http://purl.org/dc/terms/issued> ?year .
                ?pub <http://purl.org/dc/terms/creator> ?authors .
                #FILTER NOT EXISTS {
                OPTIONAL {
                    ?pub <http://lada/excluded> ?pubExcluded
                } .
                ?ds <http://data.hulib.helsinki.fi/id/ontology/varieng/v1/file> ?file .
                ?obs <http://lada/sheet> ?sheet .
                ?obs <http://lada/timeperiod> ?period .
                ?period <http://www.w3.org/2000/01/rdf-schema#label> ?periodName .
                ?obs <http://purl.org/linked-data/cube#dataSet> ?ds .
                OPTIONAL {
                    ?ds <http://www.w3.org/2000/01/rdf-schema#comment> ?comment .
                } .

                ?obs <http://lada/row> ?row .
                ?obs <http://lada/col> ?col .
                ?obs <http://lada/sheet> ?sheet .
                ?obs <http://lada/timeperiod> ?period .
                ?period <http://www.w3.org/2000/01/rdf-schema#label> ?periodName .
                #FILTER NOT EXISTS {
                OPTIONAL {
                    ?obs <http://lada/excluded> ?excluded .
                } .
                ?obs <http://data.hulib.helsinki.fi/id/ontology/varieng/v1/data/frequency> ?freq .
                ?obs <http://data.hulib.helsinki.fi/id/ontology/varieng/v1/data/per> ?per .
                #FILTER(?freq > 0) .
        """

# noexpression: 1 = no value, 2 = any or no value 3 = some value, none = specific values

        if obj['noexpression']:
            if obj['noexpression'] == 1:
                query = query + " FILTER NOT EXISTS { ?obs <http://lada/gen_expression> ?exp } . "
            if obj['noexpression'] == 2:
                query = query + " OPTIONAL { ?obs <http://lada/gen_expression> ?exp . ?exp <http://www.w3.org/2000/01/rdf-schema#label> ?expName . }"
            if obj['noexpression'] == 3:
                query = query + " ?obs <http://lada/gen_expression> ?exp . ?exp <http://www.w3.org/2000/01/rdf-schema#label> ?expName ."
        else:
            if(len(expFilters) > 0):
                joined = ", ".join(expFilters)
                query = query + "?obs <http://lada/expression> ?exp . ?exp <http://www.w3.org/2000/01/rdf-schema#label> ?expName . FILTER(?exp IN(" + joined + ")) . "

        if obj['nocorpus']:
            if obj['nocorpus'] == 1:  # no value
                query = query + " FILTER NOT EXISTS { ?obs <http://h224.it.helsinki.fi:8080/varieng/data/Corpus> ?corpus } . "
            if obj['nocorpus'] == 2:
                query = query + " OPTIONAL { ?obs <http://lada/corpus> ?corpus . ?corpus <http://www.w3.org/2000/01/rdf-schema#label> ?corpusName . ?obs <http://h224.it.helsinki.fi:8080/varieng/data/Corpus> ?corpus2   } .  "
            if obj['nocorpus'] == 3:
                query = query + " ?obs <http://lada/corpus> ?corpus . ?corpus <http://www.w3.org/2000/01/rdf-schema#label> ?corpusName . ?obs <http://h224.it.helsinki.fi:8080/varieng/data/Corpus> ?corpus2 . "
        else:
            # some value
            query = query + """
                ?obs <http://lada/corpus> ?corpus .
                ?corpus <http://www.w3.org/2000/01/rdf-schema#label> ?corpusName .
                # TODO: get rid of this filter!
                ?obs <http://h224.it.helsinki.fi:8080/varieng/data/Corpus> ?corpus2
                """
            if len(corpusFilters) > 0: # specific values
                joined = ", ".join(corpusFilters)
                query = query + " FILTER(?corpus IN(" + joined + ")) . "

        if obj['nofunction']:
            if obj['nofunction'] == 1:
                query = query + " FILTER NOT EXISTS { ?obs <http://lada/gen_function> ?func } . "
            if obj['nofunction'] == 2:
                query = query + "OPTIONAL { ?obs <http://lada/gen_function> ?func . ?func <http://www.w3.org/2000/01/rdf-schema#label> ?funcName . } "
            if obj['nofunction'] == 3:
                query = query + " ?obs <http://lada/gen_function> ?func . ?func <http://www.w3.org/2000/01/rdf-schema#label> ?funcName . "
        else:
            query = query + "?obs <http://lada/function> ?func . ?func <http://www.w3.org/2000/01/rdf-schema#label>  ?funcName . "
            if(len(funcFilters) > 0):
                joined = ", ".join(funcFilters)
                query = query + "FILTER(?func IN(" + joined + ")) . "

        if obj['nogenre']:
            if obj['nogenre'] == 1:
                query = query + " FILTER NOT EXISTS { ?obs <http://lada/gen_genre> ?genre } . "
            if obj['nogenre'] == 2:
                query = query + "OPTIONAL { ?obs <http://lada/gen_genre> ?genre . ?genre <http://www.w3.org/2000/01/rdf-schema#label> ?genreName . } "
            if obj['nogenre'] == 3:
                query = query + " ?obs <http://lada/gen_genre> ?genre . ?genre <http://www.w3.org/2000/01/rdf-schema#label> ?genreName ."
        else:
            if(len(genreFilters) > 0):
                joined = ", ".join(genreFilters)
                query = query + "?obs <http://lada/genre> ?genre . ?genre <http://www.w3.org/2000/01/rdf-schema#label> ?genreName . FILTER(?genre IN(" + joined + ")) . "


        query = query + "} order by ?pub ?sheet ?row ?col "

        qres = self.dm.query_all(query)
        data = []
        pubs = {}
        sheets = {}

        # Group by publication -> sheet (ds)
        # pub
        # - sheets[]
        #   - obs[]

        # Group together observations that share common dimension values
        main_logger.info('GO')
        for row in qres:
            #main_logger.info(row)
            pub = row['pub']
            sheet = row['sheet']
            main_logger.info(sheet)
            if not pub in pubs:
                newPub = {
                    'pub': row['pub'],
                    'title': row['title'],
                    'year': row['year'],
                    'authors': row['authors'],
                    'excluded': row['pubExcluded'],
                    'sheets': []
                }
                data.append(newPub)
                pubs[pub] = newPub

            if (pub + sheet) not in sheets:
                newSheet = {
                    'name': row['sheet'],
                    'desc': row['comment'],
                    'obs': []
                }
                pubs[pub]['sheets'].append(newSheet)
                sheets[pub + sheet] = newSheet

            sheets[pub + sheet]['obs'].append( {
                'obs': row['obs'],
                'excluded': row['excluded'],
                'row': int(row['row']),
                'col': int(row['col']),
                'freq': row['freq'],
                'per': int(row['per']),
                #'corpus': row['corpus'],
                'corpus2': row['corpus2'],
                'corpusName': row['corpusName'],
                'genre': row['genre'],
                'genreName': row['genreName'],
                'exp': row['exp'],
                'expName': row['expName'],
                'func': row['func'],
                'funcName': row['funcName'],
                'period': row['period'],
                'periodName': row['periodName']
            })
        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'
        resp.data = json.dumps(data)

class FilteredObservations(BaseRequest):
    def on_get(self, req, resp):
        main_logger.info('GET filtered')


        query = """
            select distinct ?obs ?pub ?title ?year ?authors ?pubExcluded ?ds ?excluded ?row ?col ?sheet ?comment ?freq ?per ?corpus2 ?corpusName ?genre ?genreName ?exp ?expName ?func ?funcName ?period ?periodName {
                #graph <http://lada/graph/filtered> {
                    ?obs a <http://purl.org/linked-data/cube#Observation> .
                    ?obs <http://lada/filtered> ?f .
                #}
                ?pub <http://lada/file> ?file .
                ?pub <http://purl.org/dc/terms/title> ?title .
                ?pub <http://purl.org/dc/terms/issued> ?year .
                ?pub <http://purl.org/dc/terms/creator> ?authors .
                OPTIONAL {
                    ?pub <http://lada/excluded> ?pubExcluded
                } .
                ?ds <http://data.hulib.helsinki.fi/id/ontology/varieng/v1/file> ?file .
                ?obs <http://purl.org/linked-data/cube#dataSet> ?ds .
                OPTIONAL {
                    ?ds <http://www.w3.org/2000/01/rdf-schema#comment> ?comment .
                } .
                ?obs <http://lada/row> ?row .
                ?obs <http://lada/col> ?col .
                ?obs <http://lada/sheet> ?sheet
                OPTIONAL {
                    ?obs <http://lada/gen_expression> ?exp .
                    ?exp <http://www.w3.org/2000/01/rdf-schema#label> ?expName .
                }
                OPTIONAL {
                    ?obs <http://lada/gen_function> ?func .
                    ?func <http://www.w3.org/2000/01/rdf-schema#label> ?funcName .
                }
                OPTIONAL {
                    ?obs <http://lada/gen_genre> ?genre .
                    ?genre <http://www.w3.org/2000/01/rdf-schema#label> ?genreName .
                }
#                OPTIONAL {
                    ?obs <http://lada/timeperiod> ?period .
                    ?period <http://www.w3.org/2000/01/rdf-schema#label> ?periodName .
#                }


                ?obs <http://h224.it.helsinki.fi:8080/varieng/data/Corpus> ?corpus2 .
                ?corpus2 <http://www.w3.org/2000/01/rdf-schema#label> ?corpusName .
                OPTIONAL {
                    ?obs <http://lada/excluded> ?excluded .
                } .
                ?obs <http://data.hulib.helsinki.fi/id/ontology/varieng/v1/data/frequency> ?freq .
                ?obs <http://data.hulib.helsinki.fi/id/ontology/varieng/v1/data/per> ?per .
                #FILTER(?freq > 0) .
            } order by ?pub ?sheet ?row ?col
        """
        main_logger.info(query)
        qres = self.dm.query_all(query)
        data = []
        pubs = {}
        sheets = {}

        # Group by publication -> sheet (ds)
        # pub
        # - sheets[]
        #   - obs[]

        # Group together observations that share common dimension values
        main_logger.info('GO')
        for row in qres:
            #main_logger.info(row)
            pub = row['pub']
            sheet = row['sheet']
            main_logger.info(sheet)
            if not pub in pubs:
                newPub = {
                    'pub': row['pub'],
                    'title': row['title'],
                    'year': row['year'],
                    'authors': row['authors'],
                    'excluded': row['pubExcluded'],
                    'sheets': []
                }
                data.append(newPub)
                pubs[pub] = newPub

            if (pub + sheet) not in sheets:
                newSheet = {
                    'name': row['sheet'],
                    'desc': row['comment'],
                    'obs': []
                }
                pubs[pub]['sheets'].append(newSheet)
                sheets[pub + sheet] = newSheet

            sheets[pub + sheet]['obs'].append( {
                'obs': row['obs'],
                'excluded': row['excluded'],
                'row': int(row['row']),
                'col': int(row['col']),
                'freq': row['freq'],
                'per': int(row['per']),
                #'corpus': row['corpus'],
                'corpus2': row['corpus2'],
                'corpusName': row['corpusName'],
                'genre': row['genre'],
                'genreName': row['genreName'],
                'exp': row['exp'],
                'expName': row['expName'],
                'func': row['func'],
                'funcName': row['funcName'],
                'period': row['period'],
                'periodName': row['periodName']
            })
        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'
        resp.data = json.dumps(data)

    def on_delete(self, req, resp):
        main_logger.info('DELETE filtered')
        self.dm.clear('gfiltered')

        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'
        resp.data = json.dumps({"status": "OK"})

    def on_post(self, req, resp):
        main_logger.info('POST filtered')
        raw_json = req.stream.read()
        obj = json.loads(raw_json.decode('utf-8'))
        main_logger.info(obj)

        expressions = obj['expression']
        expFilters = []
        for f in expressions:
            if(f['type'] != 'group'):
                expFilters.append('<' + f['uri'] + '>')

        corpora = obj['corpus']
        corpusFilters = []
        for f in corpora:
            if(f['type'] != 'group'):
                corpusFilters.append('<' + f['uri'] + '>')

        genres = obj['genre']
        genreFilters = []
        for f in genres:
            if(f['type'] != 'group'):
                genreFilters.append('<' + f['uri'] + '>')

        functions = obj['function']
        funcFilters = []
        for f in functions:
            if(f['type'] != 'group'):
                funcFilters.append('<' + f['uri'] + '>')

        query = """
            construct {
                #?obs a <http://purl.org/linked-data/cube#Observation>
                ?obs <http://lada/filtered> 1
            }
            where {
        """


# noexpression: 1 = no value, 2 = any or no value 3 = some value, none = specific values

        if obj['noexpression']:
            if obj['noexpression'] == 1:
                query = query + " FILTER NOT EXISTS { ?obs <http://lada/gen_expression> ?exp } . "
            if obj['noexpression'] == 2:
                query = query + " ?obs a <http://purl.org/linked-data/cube#Observation> . "
            if obj['noexpression'] == 3:
                query = query + " ?obs <http://lada/gen_expression> ?exp . "
        else:
            if len(expFilters) > 0:
                joined = ", ".join(expFilters)
                query = query + "?obs <http://lada/expression> ?exp . FILTER(?exp IN(" + joined + ")) . "

        if obj['nocorpus']:
            if obj['nocorpus'] == 1:  # no value
                query = query + " FILTER NOT EXISTS { ?obs <http://h224.it.helsinki.fi:8080/varieng/data/Corpus> ?corpus } . "
            if obj['nocorpus'] == 2:
                query = query + " ?obs a <http://purl.org/linked-data/cube#Observation> . "

        else:
            # some value
            query = query + """
                ?obs <http://lada/corpus> ?corpus .
                # TODO: get rid of this filter!
                FILTER NOT EXISTS { ?obs <http://h224.it.helsinki.fi:8080/varieng/data/Corpus> ?corpus  }
                """
            if len(corpusFilters) > 0: # specific values
                joined = ", ".join(corpusFilters)
                query = query + " FILTER(?corpus IN(" + joined + ")) . "

        if obj['nofunction']:
            if obj['nofunction'] == 1:
                query = query + " FILTER NOT EXISTS { ?obs <http://lada/gen_function> ?func } . "
            if obj['nofunction'] == 2:
                query = query + " ?obs a <http://purl.org/linked-data/cube#Observation> . "
            if obj['nofunction'] == 3:
                query = query + " ?obs <http://lada/gen_function> ?func . "
        else:
            if len(funcFilters) > 0:
                joined = ", ".join(funcFilters)
                query = query + "?obs <http://lada/function> ?func . FILTER(?func IN(" + joined + ")) . "

        if obj['nogenre']:
            if obj['nogenre'] == 1:
                query = query + " FILTER NOT EXISTS { ?obs <http://lada/gen_genre> ?genre } . "
            if obj['nogenre'] == 2:
                query = query + " ?obs a <http://purl.org/linked-data/cube#Observation> . "

            if obj['nogenre'] == 3:
                query = query + " ?obs <http://lada/gen_genre> ?genre . "
        else:
            if len(genreFilters) > 0:
                joined = ", ".join(genreFilters)
                query = query + "?obs <http://lada/genre> ?genre . FILTER(?genre IN(" + joined + ")) . "





        #if not obj['nocorpus'] and not obj['noexpression'] and not obj['nogenre'] and not obj['nofunction']:
    #        query = query + "  ?obs a <http://purl.org/linked-data/cube#Observation> . "

        query = query + "}"

        main_logger.info(query)
        #qres = (gpubs + ggen + ggroup + gmap + ginf + glcd).query(query)
        qres = self.dm.query_all(query)
        gfiltered = Graph()
        for triple in qres:
            gfiltered.add(triple);

        gfiltered.serialize("gfiltered.ttl", format="turtle")
        self.dm.add_graph(gfiltered, 'gfiltered')
        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'
        resp.data = json.dumps({'status': 'OK'})


class FilteredResultObservations(BaseRequest):

    def on_post(self, req, resp):
        main_logger.info('GET filtered result')
        raw_json = req.stream.read()
        obj = json.loads(raw_json.decode('utf-8'))
        main_logger.info(obj)


        #corpus = req.get_param('corpus', None)
        #exp = req.get_param('exp', None)
        #func = req.get_param('func', None)
        #genre = req.get_param('genre', None)

        expressions = obj['expression']
        expFilters = []
        for f in expressions:
            if(f['type'] != 'group'):
                expFilters.append('<' + f['uri'] + '>')

        corpora = obj['corpus']
        corpusFilters = []
        for f in corpora:
            if(f['type'] != 'group'):
                corpusFilters.append('<' + f['uri'] + '>')

        genres = obj['genre']
        genreFilters = []
        for f in genres:
            if(f['type'] != 'group'):
                genreFilters.append('<' + f['uri'] + '>')

        functions = obj['function']
        funcFilters = []
        for f in functions:
            if(f['type'] != 'group'):
                funcFilters.append('<' + f['uri'] + '>')


        query = """
            select distinct ?obs ?freq ?per ?corpus ?corpusName ?genre ?genreName ?exp ?expName ?func ?funcName ?period ?periodName {
                ?obs a <http://purl.org/linked-data/cube#Observation> .
                ?obs <http://lada/filtered> ?f .
                ?pub <http://lada/file> ?file .
                ?pub <http://purl.org/dc/terms/title> ?title .
                ?pub <http://purl.org/dc/terms/issued> ?year .
                ?pub <http://purl.org/dc/terms/creator> ?authors .
                FILTER NOT EXISTS {
                    ?pub <http://lada/excluded> ?pubExcluded
                } .
                ?ds <http://data.hulib.helsinki.fi/id/ontology/varieng/v1/file> ?file .
                ?obs <http://purl.org/linked-data/cube#dataSet> ?ds .
                ?obs <http://lada/sheet> ?sheet .
#                OPTIONAL {
#                    ?obs <http://lada/function> ?func .
#                    ?func <http://www.w3.org/2000/01/rdf-schema#label> ?funcName .
#                }
#                OPTIONAL {
#                    ?obs <http://lada/genre> ?genre .
#                    ?genre <http://www.w3.org/2000/01/rdf-schema#label> ?genreName .
#                }
#                OPTIONAL {
                    ?obs <http://lada/timeperiod> ?period .
                    ?period <http://www.w3.org/2000/01/rdf-schema#label> ?periodName .
#                }
                FILTER NOT EXISTS {
                    ?obs <http://lada/excluded> ?excluded .
                } .
                ?obs <http://data.hulib.helsinki.fi/id/ontology/varieng/v1/data/frequency> ?freq .
                ?obs <http://data.hulib.helsinki.fi/id/ontology/varieng/v1/data/per> ?per .
                #FILTER(?freq > 0) .
        """

# noexpression: 1 = no value, 2 = any or no value 3 = some value, none = specific values

        if obj['noexpression']:
            if obj['noexpression'] == 1:
                query = query + " FILTER NOT EXISTS { ?obs <http://lada/gen_expression> ?exp } . "
            if obj['noexpression'] == 2:
                query = query + " OPTIONAL { ?obs <http://lada/gen_expression> ?exp . ?exp <http://www.w3.org/2000/01/rdf-schema#label> ?expName . }"
            if obj['noexpression'] == 3:
                query = query + " ?obs <http://lada/gen_expression> ?exp . ?exp <http://www.w3.org/2000/01/rdf-schema#label> ?expName ."
        else:
            if(len(expFilters) > 0):
                joined = ", ".join(expFilters)
                query = query + "?obs <http://lada/expression> ?exp . ?exp <http://www.w3.org/2000/01/rdf-schema#label> ?expName . FILTER(?exp IN(" + joined + ")) . "

        if obj['nocorpus']:
            if obj['nocorpus'] == 1:  # no value
                query = query + " FILTER NOT EXISTS { ?obs <http://h224.it.helsinki.fi:8080/varieng/data/Corpus> ?corpus } . "
            if obj['nocorpus'] == 2:
                query = query + " OPTIONAL { ?obs <http://lada/corpus> ?corpus . ?corpus <http://www.w3.org/2000/01/rdf-schema#label> ?corpusName . FILTER NOT EXISTS { ?obs <http://h224.it.helsinki.fi:8080/varieng/data/Corpus> ?corpus  } } .  "
            if obj['nocorpus'] == 3:
                query = query + " ?obs <http://lada/corpus> ?corpus . ?corpus <http://www.w3.org/2000/01/rdf-schema#label> ?corpusName .  "
        else:
            # some value
            query = query + """
                ?obs <http://lada/corpus> ?corpus .
                ?corpus <http://www.w3.org/2000/01/rdf-schema#label> ?corpusName .
                # TODO: get rid of this filter!
                FILTER NOT EXISTS { ?obs <http://h224.it.helsinki.fi:8080/varieng/data/Corpus> ?corpus  }
                """
            if len(corpusFilters) > 0: # specific values
                joined = ", ".join(corpusFilters)
                query = query + " FILTER(?corpus IN(" + joined + ")) . "

        if obj['nofunction']:
            if obj['nofunction'] == 1:
                query = query + " FILTER NOT EXISTS { ?obs <http://lada/gen_function> ?func } . "
            if obj['nofunction'] == 2:
                query = query + "OPTIONAL { ?obs <http://lada/gen_function> ?func . ?func <http://www.w3.org/2000/01/rdf-schema#label> ?funcName . } "
            if obj['nofunction'] == 3:
                query = query + " ?obs <http://lada/gen_function> ?func . ?func <http://www.w3.org/2000/01/rdf-schema#label> ?funcName . "
        else:
            if(len(funcFilters) > 0):
                joined = ", ".join(funcFilters)
                query = query + "?obs <http://lada/function> ?func . ?func <http://www.w3.org/2000/01/rdf-schema#label> ?funcName . FILTER(?func IN(" + joined + ")) . "

        if obj['nogenre']:
            if obj['nogenre'] == 1:
                query = query + " FILTER NOT EXISTS { ?obs <http://lada/gen_genre> ?genre } . "
            if obj['nogenre'] == 2:
                query = query + "OPTIONAL { ?obs <http://lada/gen_genre> ?genre . ?genre <http://www.w3.org/2000/01/rdf-schema#label> ?genreName . } "
            if obj['nogenre'] == 3:
                query = query + " ?obs <http://lada/gen_genre> ?genre . ?genre <http://www.w3.org/2000/01/rdf-schema#label> ?genreName ."
        else:
            if(len(genreFilters) > 0):
                joined = ", ".join(genreFilters)
                query = query + "?obs <http://lada/genre> ?genre . ?genre <http://www.w3.org/2000/01/rdf-schema#label> ?genreName . FILTER(?genre IN(" + joined + ")) . "


        query = query + "} order by ?corpusName ?periodName ?expName ?genreName ?funcName "

        main_logger.info(query)
        qres = self.dm.query_all(query)
        data = []

        for row in qres:
            data.append( {
                'obs': row['obs'],
                'freq': row['freq'],
                'per': int(row['per']),
                'corpus': row['corpus'],
                'corpusName': row['corpusName'],
                'genre': row['genre'],
                'genreName': row['genreName'],
                'exp': row['exp'],
                'expName': row['expName'],
                'func': row['func'],
                'funcName': row['funcName'],
                'period': row['period'],
                'periodName': row['periodName']
            })
        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'
        resp.data = json.dumps(data)
