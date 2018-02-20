import Freezer from 'freezer-js';


var state =  {
  lcdStatus: 'offline',
  working: false,
  workingMessage: 'Waiting for data from the backend',
  publications: [],
  filters: {
    nocorpus: 2,
    corpus: [
    ],
    noexpression: 2,
    expression: [
    ],
    nogenre: 2,
    genre: [
    ],
    nofunction: 2,
    function: [
    ],
    notimeperiod: 3,
    timeperiod: [
    ],

  },
  filteredObs: [],
  tables: {},
  cc: {},
  ccs: {
    all: {},
    selected: {},
    corpora: {},
    clusters: {},
    marked: {}
  },
  normalizedObs: {},
  clusteredObs: {},
  clusteredObsReview: [],
  vis: {},
  reload: {
    select: false,
    filter: false,
    review: false,
    normalize: false,
    visualize: false
  },
  dirty: {
    publications: false,
    filters: false
  },
  hash: {
    publications: null,
    filters: null,
    filteredObs: null,
    select: null,
    filter: null,
    review: null,
    normalize: null

  },
  tocVisible: false
};

var freezer = new Freezer(state);

window.hub = freezer.getEventHub();

module.exports = freezer;
