from rdflib import Namespace, Literal, URIRef, BNode

ns_lada = Namespace("http://lada/")
ns_data = Namespace("http://h224.it.helsinki.fi:8080/varieng/data/")
ns_cube = Namespace('http://purl.org/linked-data/cube#')
ns_lcd = Namespace('http://h224.it.helsinki.fi:8080/varieng/')
ns_dct = Namespace('http://purl.org/dc/terms/')
ns_xsd = Namespace('http://www.w3.org/2001/XMLSchema#')
ns_qb4cc = Namespace('http://data.hulib.helsinki.fi/ns/qb4cc#')
ns_skos = Namespace('http://www.w3.org/2004/02/skos/core#')


graph_dict = {
    'gpubs':     URIRef('http://lada/graph/pub'),
    'gpub':     URIRef('http://lada/graph/pub'),
    'ggen':     URIRef('http://lada/graph/gen'),
    'ggroup':   URIRef('http://lada/graph/group'),
    'gmap':     URIRef('http://lada/graph/gmap'),
    'ginf':     URIRef('http://lada/graph/inf'),
    'glcd':     URIRef('http://lada/graph/lcd'),
    'gfiltered':URIRef('http://lada/graph/filtered'),
    'gresult':  URIRef('http://lada/graph/result'),
    'gexc':     URIRef('http://lada/graph/exc')
}
