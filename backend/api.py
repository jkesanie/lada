import falcon
from falcon_cors import CORS
from falcon_multipart.middleware import MultipartMiddleware
from logs import main_logger, app_logger

from datamanager import DataManager
from storage.inmemory import InMemoryStorage

from endpoints.lcd import GetPublications
from endpoints.lcd import CheckForLCDConnection

from endpoints.annotatedfile import AnnotatedFiles
from endpoints.annotatedfile import AnnotatedFilesJSON

from endpoints.obs import CubeExpressions
from endpoints.obs import CubeCorpora
from endpoints.obs import CubeGenres
from endpoints.obs import CubeFunctions

from endpoints.group import GroupCorpora
from endpoints.group import GroupExpressions
from endpoints.group import GroupFunctions
from endpoints.group import GroupGenres
from endpoints.group import Groups

from endpoints.filteredobs import FilteredObservations
from endpoints.filteredobs import QueryFilteredObservations
from endpoints.filteredobs import FilteredResultObservations
from endpoints.filteredobs import FilteredObservationsPreview

from endpoints.infer import Infer

from endpoints.corpuscomposition import CCFiltered

from endpoints.normalizedobs import Normalize
from endpoints.normalizedobs import CreateNormalizedCube
from endpoints.normalizedobs import QueryNormalizedCube
from endpoints.normalizedobs import NormalizedCubeDefinitions

from endpoints.excluded import ExcludedObservations
from endpoints.excluded import ExcludedPublications

from endpoints.image import Image

lcdURL = "h224.it.helsinki.fi"
lcdPort = 8080
data_folder = '/Users/jkesa/Documents/LCD/LaDa/data/work/annotatedFiles'
image_folder = '/Users/jkesa/Documents/LCD/LaDa/data/work/images'


def create():

    """Create the API endpoints."""
    cors = CORS(allow_all_origins=True,allow_all_methods=True, allow_all_headers=True)
    app = falcon.API(middleware=[cors.middleware, MultipartMiddleware()])

    dm = DataManager(InMemoryStorage(), InMemoryStorage(), data_folder, lcdURL, lcdPort)


    app.add_route('/annotatedFiles', AnnotatedFiles(dm))
    app.add_route('/annotatedFiles/json', AnnotatedFilesJSON(dm))
    app.add_route('/publications', GetPublications(dm))

    app.add_route('/expression', CubeExpressions(dm))
    app.add_route('/corpus', CubeCorpora(dm))
    app.add_route('/genre', CubeGenres(dm))
    app.add_route('/function', CubeFunctions(dm))

    app.add_route('/corpus/groups', GroupCorpora(dm))
    app.add_route('/expression/groups', GroupExpressions(dm))
    app.add_route('/function/groups', GroupFunctions(dm))
    app.add_route('/genre/groups', GroupGenres(dm))

    app.add_route('/groups', Groups(dm))


    app.add_route('/obs/filtered', FilteredObservations(dm))
    app.add_route('/obs/filtered/query', QueryFilteredObservations(dm))
    app.add_route('/obs/filtered/result', FilteredResultObservations(dm))

    app.add_route('/obs/filtered/preview', FilteredObservationsPreview(dm))

    app.add_route('/infer', Infer(dm))


    app.add_route('/cc/filtered', CCFiltered(dm))

    app.add_route('/normalize', Normalize(dm))
    app.add_route('/obs/norm2', CreateNormalizedCube(dm))
    app.add_route('/obs/norm/query', QueryNormalizedCube(dm))
    app.add_route('/obs/norm/defs', NormalizedCubeDefinitions(dm))

    app.add_route('/obs/excluded', ExcludedObservations(dm))
    app.add_route('/pub/excluded', ExcludedPublications(dm))


    app.add_route('/image', Image(image_folder))

    app.add_route('/lcd/status', CheckForLCDConnection(dm))

    main_logger.info('App2 is running.')
    return app
