import falcon
from endpoints.baserequest import BaseRequest
from common import ns_lada, ns_data, ns_cube, ns_lcd, ns_xsd, ns_qb4cc, ns_skos
from logs import main_logger, app_logger

from rdflib import Namespace, Literal, URIRef, BNode, Graph
from rdflib.namespace import RDF, FOAF, XSD, RDFS, OWL, SKOS

import json

class Normalize(BaseRequest):

    query_template = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX lcd-data: <http://data.hulib.helsinki.fi/id/ontology/varieng/v1/data/>
            PREFIX lcd: <http://data.hulib.helsinki.fi/ns/lcd#>
            PREFIX qb: <http://purl.org/linked-data/cube#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX qb4cc: <http://data.hulib.helsinki.fi/ns/qb4cc#>
            SELECT (((?absValue / ?w) * ?normalizationBase) as ?normalizedValue ) {{
            	BIND({0} as ?normalizationBase) .
                BIND({1} as ?absValue) .
              {{
                  SELECT (SUM(?words) as ?w) {{
        	        BIND(URI("{2}") as ?cc)
                    ?part qb4cc:isPartOfComposition ?cc .
                    ?part qb4cc:wordCount ?words .
                    ?part qb4cc:timePeriod ?tp .
                    ?tp lcd:startYear ?sy .
                    ?tp lcd:endYear ?ey .
                    {5}
                    #FILTER (ABS(?sy - {3}) <= 2  || ABS(?ey - {4}) <= 2)
                    FILTER ( (ABS(?sy - {3}) <= 2  || ABS(?ey - {4}) <= 2) || (?sy - {3} > 0 && ?ey - {4} < 0) )
                  }} group by ?cc
              }}
            }}
            """

    def on_get(self, req, resp):
        normalizationBase = req.get_param_as_int('base', 0)
        ccURI = req.get_param('ccURI', None)
        startYear = req.get_param('startYear', None)
        endYear = req.get_param('endYear', None)
        absValue = req.get_param_as_int('absValue', 0);
        obs = req.get_param('obs', None)
        pub = req.get_param('pub', None)
        sheet = req.get_param('sheet', None)
        ckey = req.get_param('ckey', None)
        ccGenre = req.get_param('ccgenre', None)
        ccGenres = req.get_param_as_list('ccgenres', None)

        genrePart = ''
        if ccGenres:
            gfilters = [];
            for f in ccGenres:
                gfilters.append('<' + f + '>')
            genrePart = '?part qb4cc:genre ?genre . FILTER (?genre IN(' + ','.join(gfilters) + ')) .'

        query = self.query_template.format(
                    normalizationBase,
                    absValue,
                    ccURI,
                    startYear,
                    endYear,
                    genrePart
                    )

        main_logger.info(query)
        qres = self.dm.query_cc(query)
        normValue = -1
        for row in qres:
            main_logger.info(row)
            normValue = row['normalizedValue']

        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'
        key = pub + sheet
        #if(genre):
        #    resp.data = json.dumps({ key: { ckey: { genre: normValue }}})
        #else:
        resp.data = json.dumps({ key: { ckey: normValue }})



class CreateNormalizedCube(BaseRequest):

    def on_post(self, req, resp):
        main_logger.info('POST norm2')
        raw_json = req.stream.read()
        obj = json.loads(raw_json.decode('utf-8'))
        main_logger.info(obj)



        s = ns_lada['cube']
        dsd = ns_lada['structure']

        gresult = Graph()

        gresult.add( (s, RDF.type, ns_cube['DataSet']) )
        gresult.add( (s, ns_cube['structure'], dsd) )

        for key in obj:
            main_logger.info(key)
            clusters = obj[key]
            for o in clusters:
                if o['selected']:
                    uri = URIRef(o['selected'])
                    obs = o['values'][o['selected']]

                    # find the one with the per = 1

                    for vkey in o['values']:
                        value = o['values'][vkey]
                        if value['per'] == 1:
                            uri = URIRef(value['obs'])

                    gresult.add( (uri, RDF.type, ns_cube['Observation']) )
                    gresult.add( (uri, ns_lada['frequency'], Literal(float(obs['freq'])) ) )
                    #if o['period']:
                    #    gresult.add( (uri, ns_lada['timeperiod'], URIRef(o['period'])) )
                    #if o['corpus2']:
                #        gresult.add( (uri, ns_lcd['corpus'], URIRef(o['corpus2']) ))
                #    if o['genre']:
                #        gresult.add( (uri, ns_lada['genre'], URIRef(o['genre']) ))
                    #if not filters['noexpression'] and o['exp']: # and !noexpression
                        #gresult.add( (uri, ns_lada['expression'], URIRef(o['exp']) ))
                #    if o['func']:
                #        gresult.add( (uri, ns_lada['function'], URIRef(o['func']) ))

        gresult.serialize("gresult3.ttl", format="turtle")
        self.dm.add_graph(gresult, 'gresult')

class NormalizedCubeDefinitions(BaseRequest):

    def on_post(self, req, resp):
        main_logger.info('POST cube definitions')
        raw_json = req.stream.read()
        obj = json.loads(raw_json.decode('utf-8'))
        main_logger.info(obj)

        self.dm.clear('gresult')

        gresult = Graph()

        s = ns_lada['structure']
        gresult.add( (s, RDF.type, ns_cube['DataStructureDefinition']) )
        # only measure is frequency
        mnode = BNode()
        gresult.add( (s, ns_cube['component'], mnode) )
        gresult.add( (mnode, RDFS.label, Literal('normalized frequency') ))

        measure = ns_lada['measure#frequency']
        gresult.add( (measure, RDF.type, ns_cube['Measure'] ))
        gresult.add( (measure, RDFS.range, ns_xsd['decimal'] ))
        gresult.add( (mnode, ns_cube['measure'], measure) )
        # TODO: add normalization base to the measure




        if not obj['nocorpus'] or len(obj['corpus']) > 0:
            anode = BNode()
            #corpusDim = ns_lcd['Corpus']
            corpusDim = ns_lada['corpus']
            gresult.add( (s, ns_cube['component'], anode ) )
            gresult.add( (anode, RDFS.label, Literal('Corpus')) )
            gresult.add( (anode, ns_cube['dimension'], corpusDim) )
            gresult.add( (corpusDim, RDF.type, ns_qb4cc['corpus']) )
            gresult.add( (corpusDim, RDFS.range, ns_lcd['Corpus']) )

        if len(obj['corpus']) > 0:
#            for c in obj['corpus']:
#                gresult.add( (URIRef(c['uri']), RDFS.label, Literal(c['label'])) )
            cList = ns_lada['codelist/corpus']
            gresult.add( (ns_lada['corpus'], ns_cube['codeList'], cList ))
            for c in obj['corpus']:
                gresult.add( (URIRef(c['uri']), RDFS.label, Literal(c['label'])) )
                gresult.add( (URIRef(c['uri']), SKOS.prefLabel, Literal(c['label'])) )
                gresult.add( (URIRef(c['uri']), SKOS.inScheme, cList) )


        if not obj['noexpression'] or len(obj['expression']) > 0:
            anode = BNode()
            dim = ns_lada['expression']
            gresult.add( (s, ns_cube['component'], anode ) )
            gresult.add( (anode, RDFS.label, Literal('Expression')) )
            gresult.add( (anode, ns_cube['dimension'], dim) )
            gresult.add( (dim, RDF.type, ns_qb4cc['expression']) )
            #gresult.add( (dim, RDFS.range, ns_lcd['Expression']) )
            gresult.add( (dim, RDFS.range, ns_skos['Concept']) )

        if len(obj['expression']) > 0:
            expList = ns_lada['codelist/exp']
            gresult.add( (ns_lada['expression'], ns_cube['codeList'], expList ))
            for c in obj['expression']:
                gresult.add( (URIRef(c['uri']), RDFS.label, Literal(c['label'])) )
                gresult.add( (URIRef(c['uri']), SKOS.prefLabel, Literal(c['label'])) )
                gresult.add( (URIRef(c['uri']), SKOS.inScheme, expList) )

        if not obj['nofunction'] or len(obj['function']) > 0:
            anode = BNode()
            dim = ns_lada['function']
            gresult.add( (s, ns_cube['component'], anode ) )
            gresult.add( (anode, RDFS.label, Literal('Function')) )
            gresult.add( (anode, ns_cube['dimension'], dim) )
            gresult.add( (dim, RDF.type, ns_qb4cc['function']) )
            #gresult.add( (dim, RDFS.range, ns_lcd['Expression']) )
            gresult.add( (dim, RDFS.range, ns_skos['Concept']) )

        if len(obj['function']) > 0:
            expList = ns_lada['codelist/func']
            gresult.add( (ns_lada['function'], ns_cube['codeList'], expList ))
            for c in obj['function']:
                gresult.add( (URIRef(c['uri']), RDFS.label, Literal(c['label'])) )
                gresult.add( (URIRef(c['uri']), SKOS.prefLabel, Literal(c['label'])) )
                gresult.add( (URIRef(c['uri']), SKOS.inScheme, expList) )

        if not obj['nogenre'] or len(obj['genre']) > 0 or obj['nogenre'] != 1:
            anode = BNode()
            dim = ns_lada['genre']
            gresult.add( (s, ns_cube['component'], anode ) )
            gresult.add( (anode, RDFS.label, Literal('Genre')) )
            gresult.add( (anode, ns_cube['dimension'], dim) )
            gresult.add( (dim, RDF.type, ns_qb4cc['genre']) )
            #gresult.add( (dim, RDFS.range, ns_lcd['Expression']) )
            gresult.add( (dim, RDFS.range, ns_skos['Concept']) )

        if len(obj['genre']) > 0:
            expList = ns_lada['codelist/genre']
            gresult.add( (ns_lada['genre'], ns_cube['codeList'], expList ))
            for c in obj['genre']:
                gresult.add( (URIRef(c['uri']), RDFS.label, Literal(c['label'])) )
                gresult.add( (URIRef(c['uri']), SKOS.prefLabel, Literal(c['label'])) )
                gresult.add( (URIRef(c['uri']), SKOS.inScheme, expList) )


        #TODO: add other dimensiton types hre

#            corpusList = ns_lada['codelist/corpus']
#            gresult.add( (corpusDim, ns_cube['codeList'], corpusList ))

        if len(obj['timeperiod']) > 0:
            periodnode = BNode()
            periodDim = ns_lada['timeperiod']
            gresult.add( (s, ns_cube['component'], periodnode ) )
            gresult.add( (periodnode, RDFS.label, Literal('Time period')) )
            gresult.add( (periodnode, ns_cube['dimension'], periodDim) )
            gresult.add( (periodDim, RDF.type, ns_qb4cc['timePeriod']) )
            gresult.add( (periodDim, RDFS.range, ns_qb4cc['TimePeriod']) )
            periodList = ns_lada['codelist/period']
            gresult.add( (ns_lada['timeperiod'], ns_cube['codeList'], periodList ))
            for c in obj['timeperiod']:
                gresult.add( (URIRef(c['uri']), RDFS.label, Literal(c['label'])) )
                gresult.add( (URIRef(c['uri']), SKOS.prefLabel, Literal(c['label'])) )
                gresult.add( (URIRef(c['uri']), SKOS.inScheme, periodList) )



        gresult.serialize("gresult.ttl", format="turtle")

        self.dm.add_graph(gresult, 'gresult')

        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'
#        resp.data = json.dumps({'status': 'OK'})
        resp.data = json.dumps(obj)


    def on_get(self, req, resp):
        main_logger.info('GET cube definitions')
        graphURI = req.get_param('graphuri', default=None)

        measures = []
        dimensions = []
        attributes = []


        # query for measures
        measure_query = """
            select ?measure ?label ?range {
                ?s a <http://purl.org/linked-data/cube#DataStructureDefinition> .
                ?s <http://purl.org/linked-data/cube#component> ?c .
                ?c <http://purl.org/linked-data/cube#measure> ?measure .
                ?c <http://www.w3.org/2000/01/rdf-schema#label> ?label .
                ?measure <http://www.w3.org/2000/01/rdf-schema#range> ?range
            } order by ?label
            """

        main_logger.info(measure_query)
        qres = self.dm.query(measure_query, ['gresult', 'ggroup', 'ggen'])
        if qres.__nonzero__():
            for row in qres:
                main_logger.info(row)
                measures.append( { 'uri': str(row['measure']), 'label': str(row['label']), 'range': str(row['range'])} )


        dimension_query = """
            select distinct ?dim ?label ?range ?codelist {
                ?s a <http://purl.org/linked-data/cube#DataStructureDefinition> .
                ?s <http://purl.org/linked-data/cube#component> ?c .
                ?c <http://purl.org/linked-data/cube#dimension> ?dim .
                ?c <http://www.w3.org/2000/01/rdf-schema#label> ?label .
                ?dim <http://www.w3.org/2000/01/rdf-schema#range> ?range
                OPTIONAL {
                    ?dim <http://purl.org/linked-data/cube#codeList> ?codelist
                }
            } order by ?label
            """
        main_logger.info(dimension_query)
        qres = self.dm.query(dimension_query, ['gresult', 'ggroup', 'ggen'])
        if qres.__nonzero__():
            main_logger.info('test')
            for row in qres:
                main_logger.info(row)
                dimRange = str(row['range'])
                prop = str(row['dim'])
                obj = { 'uri': prop, 'label': str(row['label']), 'range': dimRange}
                main_logger.info('codelist: ' + str(row['codelist']))
                if row['codelist'] != None and dimRange == 'http://www.w3.org/2004/02/skos/core#Concept':
                    codelist = row['codelist']
                    qres2 = self.dm.query("""
                        select distinct ?uri ?label {{
                            ?uri <http://www.w3.org/2004/02/skos/core#inScheme> <{0}> .
                            ?uri <http://www.w3.org/2004/02/skos/core#prefLabel> ?label
                        }} order by ?label
                        """.format(codelist), ['gresult', 'ggroup', 'ggen'])
                    concepts = []
                    for row2 in qres2:
                        concepts.append( { 'uri': row2['uri'], 'label': row2['label']} )
                    obj['concepts'] = concepts
                elif row['codelist'] != None and dimRange == 'http://data.hulib.helsinki.fi/ns/qb4cc#TimePeriod':
                    codelist = row['codelist']
                    qres2 = self.dm.query("""
                        select distinct ?uri ?label {{
                            ?uri <http://www.w3.org/2004/02/skos/core#inScheme> <http://lada/codelist/period> .
                            ?uri <http://www.w3.org/2004/02/skos/core#prefLabel> ?label
                        }} order by ?label
                        """, ['gresult'])
                    values = []
                    for row2 in qres2:
                        values.append( row2['label'] )
                    obj['values'] = values
                elif dimRange.startswith('http://www.w3.org/2001/XMLSchema#'): # literals
                    qres2 = self.dm.query("""
                        select distinct ?value {{
                            ?uri <{0}> ?value
                        }} order by ?value
                        """.format(prop), ['gresult', 'ggroup', 'ggen'])
                    values = []
                    for row2 in qres2:
                        values.append( row2['value'] )
                    obj['values'] = values
                else: # object objects, should have rdfs:labels or preflabels
                    qres2 = self.dm.query("""
                        select distinct ?uri ?label {{
                            ?obj  <{0}> ?uri .
                            OPTIONAL {{
                                ?uri <http://www.w3.org/2000/01/rdf-schema#label> ?label
                            }}

                        }} order by ?label
                        """.format(prop), ['gresult', 'ggroup', 'ggen'])
                    objs = []
                    for row2 in qres2:
                        objs.append( { 'uri': row2['uri'], 'label': ( row2['label']  if row2['label'] != None else row2['uri']) } )
                    #obj['objs'] = objs
                    obj['concepts'] = objs

                dimensions.append(obj)


        main_logger.info('done')
        results = {}
        results['measures'] = measures
        results['dimensions'] = dimensions
        resp.data = json.dumps(results)
        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'

class QueryNormalizedCube(BaseRequest):

    def create_value_filter(self, obj):
        if len(obj['values']) == 0:
            return '?obs ' + obj['uri'] + ' ?' + obj['id'] + ' . \n OPTIONAL { ?' + obj['id'] + ' <http://www.w3.org/2000/01/rdf-schema#label> ?' + obj['id'] +'_label .}'
        else:
            return '?obs ' + obj['uri'] + ' ?' + obj['id'] + ' . \n  ?' + obj['id'] + ' <http://www.w3.org/2000/01/rdf-schema#label> ?' + obj['id'] +'_label . \n FILTER (?' + obj['id'] + '_label in(' + (','.join('"' + x['label'] + '"' for x in obj['values'])) + ')) . \n'


    def create_filter(self, obj):
        if len(obj['values']) == 0:
            return '?obs ' + obj['uri'] + ' ?' + obj['id'] + ' . \n OPTIONAL { ?' + obj['id'] + ' <http://www.w3.org/2000/01/rdf-schema#label> ?' + obj['id'] +'_label .}'
        else:
            return '?obs ' + obj['uri'] + ' ?' + obj['id'] + ' . \n OPTIONAL { ?' + obj['id'] + ' <http://www.w3.org/2000/01/rdf-schema#label> ?' + obj['id'] +'_label .} \n filter (?' + obj['id'] + ' in(' + (','.join(x['uri'] for x in obj['values'])) + ')) . \n'

    def on_post(self, req, resp):
        raw_json = req.stream.read()
        test = None
        if len(raw_json) >0:
            test = json.loads(raw_json.decode('utf-8'))

        main_logger.info(test)
        variables = []
        variables.append('?' + test['dimension']['id'] + '_label')
        # check for second dimension
        if 'dimension' in test['dimension']:
            variables.append('?' + test['dimension']['dimension']['id'] + '_label')

        slicePart = ''
        for sc in test['slices']:
            if(sc['type'] == 'value'):
                slicePart = slicePart + self.create_value_filter(sc)
            else:
                slicePart = slicePart + self.create_filter(sc)
        #slicePart = '. '.join(self.create_filter(sc) )
        dimensionPart = self.create_filter(test['dimension'])
        # check for second dimension
        if 'dimension' in test['dimension']:
            dimensionPart = dimensionPart +  self.create_filter(test['dimension']['dimension'])

        query = """
            select {0} ?obs ?value {{
                ?obs a <http://purl.org/linked-data/cube#Observation> .
                ?obs <http://lada/frequency> ?value .
                {1}
                {2}
            }} order by {0}
        """.format(' '.join(variables), slicePart, dimensionPart)

        main_logger.info(query)
        results = []
        legendItems = []

        qres = self.dm.query(query, ['gresult', 'ggroup', 'ggen', 'ginf'])
        #qres = g.query(query)


        # array order: obs, dimension.2, dimension.1
        dim1Data = []
        dim2Data = [] # legend items
        dim2Dict = {}


        if 'dimension' in test['dimension']:
            previousDim1Value = None
            previousDim2Value = None
            if qres.__nonzero__():
                for row in qres:
                    if str(row.count) != 'None':
                        dim1Value = str(row[variables[0][1:]])
                        dim2Value = str(row[variables[1][1:]])

                        if previousDim2Value == None or previousDim2Value != dim2Value:
                            dim2Data.append(dim2Value)

                        if not dim2Dict.has_key(dim1Value):
                            dim2Dict[dim1Value] = {}

                        if not dim2Dict[dim1Value].has_key(dim2Value):
                            dim2Dict[dim1Value][dim2Value] = float(row['value'])
                        else:
                            dim2Dict[dim1Value][dim2Value] = dim2Dict[dim1Value][dim2Value] + float(row['value'])
                        main_logger.info('added ' + row['value'] + " to " +dim1Value + ":" + dim2Value)


                        if previousDim1Value == None:
                            dim1Data.append(dim1Value)

                        elif previousDim1Value !=  dim1Value:
                            dim1Data.append(dim1Value)

                        previousDim1Value = dim1Value
                        previousDim2Value = dim2Value

            main_logger.info(dim1Data)
            main_logger.info(dim2Data)
            main_logger.info(dim2Dict)

            main_logger.info('step 2')

            for v2 in sorted(dim2Data):
                if not v2 in legendItems:
                    legendItems.append(v2)
                    inner = []
                    for v1 in sorted(dim2Dict):
                        obj = {}
                        obj['x'] = v1
                        if  dim2Dict[v1].has_key(v2):
                            obj['y'] = dim2Dict[v1][v2]
                            obj['label'] = v2

                        else:
                            obj['y'] = None
                            obj['label'] = v2



                        inner.append(obj)
                    results.append(inner)




            #for dim2Obj in test['dimension']['dimension']['values']:
            #    dim2 = dim2Obj['label']
            #    legendItems.append(dim2)
            #    inner = []
            #    for dim1Obj in test['dimension']['values']:
            #        dim1 = dim1Obj['label']
            #        if dim2Dict.has_key(dim1) and dim2Dict[dim1].has_key(dim2):
            #            obj = { 'x': dim1, 'y': dim2Dict[dim1][dim2]}
            #            inner.append( obj)
            #        else:
            #            obj = { 'x': dim1, 'y': 0}
            #            inner.append( obj)
            #        main_logger.info(inner)
            #    results.append(inner)




            main_logger.info('done')


        else:
            previousDimValue = None
            sum = 0
            if qres.__nonzero__():
                _results = []
                for row in qres:
                    if str(row.count) != 'None':
                        dimValue = row[variables[0][1:]]
                        if previousDimValue == None or previousDimValue == dimValue:
                            sum = sum + float(row['value'])

                        else:

                            _results.append({
                                'x': previousDimValue,
                                'y': sum
                            })
                            sum = float(row['value'])

                        previousDimValue = dimValue
                _results.append({
                    'x': previousDimValue,
                    'y': sum
                })
                results.append(_results)

        data = {}

        data['results'] = results
        data['legend'] = legendItems
        resp.data = json.dumps(data)
        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'
