import React from 'react';
import { Button, Dimmer, Image, Loader, Segment, Header, List, Icon, Modal, Label, Menu} from 'semantic-ui-react'
import { Checkbox, Form , Dropdown, Input, Card, Grid, Item, Sidebar, Table} from 'semantic-ui-react'
import request from 'superagent'
import * as d3 from "d3";

import FilterLabels from './components/FilterLabels'

var hash = require('object-hash');

var State = require('../../freezer')
var SpreadsheetComponent = require('react-spreadsheet-component');
var Dispatcher = require('react-spreadsheet-component/lib/dispatcher');

var $ = require('jquery');


const tableConfig = {
    // Initial number of row
    rows:99,
    // Initial number of columns
    columns:99,
    // True if the first column in each row is a header (th)
    hasHeadColumn: false,
    // True if the data for the first column is just a string.
    // Set to false if you want to pass custom DOM elements.
    isHeadColumnString: true,
    // True if the first row is a header (th)
    hasHeadRow: false,
    // True if the data for the cells in the first row contains strings.
    // Set to false if you want to pass custom DOM elements.
    isHeadRowString: true,
    // True if the user can add rows (by navigating down from the last row)
    canAddRow: false,
    // True if the user can add columns (by navigating right from the last column)
    canAddColumn: false,
    // Override the display value for an empty cell
    emptyValueSymbol: '',
    // Fills the first column with index numbers (1...n) and the first row with index letters (A...ZZZ)
    hasLetterNumberHeads: false
};




export default class Review extends React.Component {
  constructor(props) {
    super(props);
    var pubs = [];
    this.state = {

      //pubs: pubs,
      //tables: {}
    };

    if(State.get().reload.review) {
      console.log('dirty publications or filters data -> updating observations');
      State.get().reload.set('review', false);

      State.get().set({'working': true, 'workingMessage': 'Saving filters'});
      var r1 = this.storeFilters();
      r1.end( (err, res) => {
        State.get().set({'workingMessage': 'Processing mappings'});
        const req = request.post('http://localhost:4001/infer');
        req.end( (err, res) => {
          var data = res.body;
          console.log(data);
          this.getObservations();

        });

      });
    }
    else {

      State.get().filteredObs.map( (pub) => {
        pub.sheets.map( (sheet) => {
          this.generateTable(pub.pub, sheet, pub.excluded);
          console.log('dis2');


        });
      })
      this.updateFilteredResults();
    }

  }



  storeFilters = () => {
    const req = request.post('http://localhost:4001/groups');
    // convert labels to uris
    //var selectedURIs = this.state.selected.map( (label) => { console.log(label); return this.state.data[this.state.type][label][0]}); // why is this an array?

    return req.send(State.get().filters);
  }

  getObservations = () => {
    State.get().set({'working': true, 'workingMessage': 'Retrieving observations'});

    var filters = State.get().filters;
    console.log('getObservations');
    console.log(filters);
    const del = request.delete('http://localhost:4001/obs/filtered');
    const req2 = del.then( (err, res) => {
      var r = request.post('http://localhost:4001/obs/filtered');
      r.send(filters);
      return r;
    });
    const get = req2.then( (res) => {
      console.log('filtered post done');
      //return request.get('http://localhost:4001/obs/filtered').timeout({deadline:120000});
      var post = request.post('http://localhost:4001/obs/filtered/query').timeout({deadline:120000});
      post.send(State.get().filters);
      return post;
    });
    get.then( (res) => {
      console.log('filtered get done');
      var data = res.body;
      console.log(data);
      State.get().set({'working': false, filteredObs: data}).now();

      //this.setState({'pubs': data});

      State.get().filteredObs.map( (pub) => {
      //data.map( (pub) => {
        pub.sheets.map( (sheet) => {
          this.generateTable(pub.pub, sheet, pub.excluded);
          console.log('dis1');
          //Dispatcher.subscribe('cellSelected', this.cellSelected.bind(this, pub.pub, sheet), pub.pub + sheet.name);
        });
      })


      this.updateFilteredResults();
    });

  }

  getClasses = (tableData, obs) => {
    var classes = []
    var x = []
    var ex = {}
    obs.map( (o) => {
      var row = o.row -2 ;
      var col = o.col -1;
      var excluded = o.excluded;
      x.push(row + 'x' + col);
      ex[row + 'x' + col] = excluded;
    });
    for (var row = 0; row < tableData.length; row++) {
      classes.push([]);
      for(var col = 0; col < tableData[row].length; col++) {

        if(x.indexOf(row + 'x' + col) >= 0 && tableData[row][col] != '') {
          console.log('match');
          if(ex[row + 'x' + col])
            classes[row].push('excluded');
          else
            classes[row].push('selected');
        }
        else {
          classes[row].push('');
        }
      }
    }
    return classes;
  }


  generateTable = (pub, sheet, excluded) => {
    //console.log(pub);
    //console.log(sheet);
    const req = request.get('http://localhost:4001/annotatedFiles/json?sheet=' + sheet.name + '&uri=' + pub);
    req.end( (err, res) => {
        var data = res.body;
        var tableData = {
          rows: data
        };
        var classes = this.getClasses(data, sheet.obs);
        var tableClasses = {
          rows: classes
        }
        //console.log(data);
        //console.log(classes);
        var tables = State.get().tables.transact(); // this.state.tables;


        tables[pub + sheet.name] = {
          tableData: tableData,
          tableClasses: tableClasses
        }

        //console.log(tables);
        console.log('got tables');
        console.log(tables);
        State.get().set('tables', tables);
        //this.setState({'tables': tables});

        Dispatcher.subscribe('cellSelected', this.cellSelected.bind(this, pub, sheet.name), pub + sheet.name);
    });

  }

  cellSelected = (pubID, sheet, data) => {
    console.log('cell selected');
    console.log(State.get().filteredObs);
    var pub = _.find(State.get().filteredObs, {pub: pubID});
    var _sheet = _.find(pub.sheets, {name: sheet});
    var o2 = _.filter(_sheet.obs, { col: data[1] +1 , row: data[0] + 2})
    console.log('selected CELL OBS');
    console.log(o2);
    if(o2.length > 0) {
      var _reload = State.get().reload.transact();
      _reload.visualize = true;
      _reload.normalize = true;
      console.log(data);
      for(var i =0 ; i < o2.length; i++) {
        var o = o2[i];
        if(o.excluded) {
          // remove
          o.set('excluded', null).now();
          var classes = State.get().tables[pubID + sheet].tableClasses.transact(); // this.state.tables;
          classes['rows'][data[0]].set(data[1], 'selected');
          var r = request.delete('http://localhost:4001/obs/excluded');
          r.query({'obs': o.obs})
          r.end( (err, res) => {
            console.log('removed');
            this.updateFilteredResults();
          })
        }
        else {
          // add
          o.set('excluded', 1).now();
          var classes = State.get().tables[pubID + sheet].tableClasses.transact(); // this.state.tables;
          classes['rows'][data[0]].set(data[1], 'excluded');
          var r = request.post('http://localhost:4001/obs/excluded');
          r.query({'obs': o.obs});
          r.end( (err, res) => {
            console.log('added');
            this.updateFilteredResults();


          })
        }
      }


    }
  }

  toggleSheet = (pubID, sheet, exclude) => {
    var pub = _.find(State.get().filteredObs, {pub: pubID});
    var _sheet = _.find(pub.sheets, {name: sheet});
    _sheet.obs.map( (o) => {
      console.log('THIS');
      console.log(o);
      if(exclude) {
        console.log('excluded:' + o.excluded);
        if(o['excluded'] != 1) {
          o.set('excluded', 1).now();
          var classes = State.get().tables[pubID + sheet].tableClasses.transact(); // this.state.tables;
          classes['rows'][o.row -2].set((o.col - 1), 'excluded');
          var r = request.post('http://localhost:4001/obs/excluded');
          r.query({'obs': o.obs});
          r.end( (err, res) => {
            console.log('added');
          });

        }

      }
      else {
        if(o['excluded'] != null){
          o.set('excluded', null).now();
          var classes = State.get().tables[pubID + sheet].tableClasses.transact(); // this.state.tables;
          classes['rows'][o.row -2].set((o.col - 1), 'selected');

          var r = request.delete('http://localhost:4001/obs/excluded');
          r.query({'obs': o.obs})
          r.end( (err, res) => {
            console.log('removed');
          });

        }

      }
    });
    this.updateFilteredResults();

  }


  togglePubExclude = (pub) => {
    //var pub = _.find(State.get().filteredObs, {pub: _pub.pub});
    var _reload = State.get().reload.transact();
    _reload.visualize = true;
    _reload.normalize = true;


    console.log('toggle pub exclude');
    console.log(pub);
    if(pub.excluded) {
      // remove
      pub.set('excluded', null);
      var r = request.delete('http://localhost:4001/pub/excluded');
      r.query({'pub': pub.pub});
      r.end( (err, res) => {
        console.log('removed');
        this.updateFilteredResults();
      })

    }
    else {
      pub.set('excluded', 1);
      var r = request.post('http://localhost:4001/pub/excluded');
      r.query({'pub': pub.pub});
      r.end( (err, res) => {
        console.log('added');
        this.updateFilteredResults();
      })
    }

  }

  getPubButton = (pub) => {
    //var pub = _.find(State.get().filteredObs, {pub: _pub.pub});
    if(pub.excluded) {
      return (<Button floated='right' onClick={this.togglePubExclude.bind(this, pub)}>Include publication</Button>)
    }
    else {
      return(
        <Button floated='right' onClick={this.togglePubExclude.bind(this, pub)}>Exclude publication</Button>
      )
    }

  }

  getSheetButtons = (pub, sheet) => {

    var b = [];
    if(!pub.excluded) {
      b.push( (<Button icon floated='right' onClick={this.toggleSheet.bind(this, pub.pub, sheet, true)} ><Icon name='minus' /></Button>) )
      b.push( (<Button icon floated='right' onClick={this.toggleSheet.bind(this, pub.pub, sheet, false)} ><Icon name='plus' /></Button>) )
    }
    return b;

  }

  getSpreadsheet = (pub, sheet) => {
    if(pub.excluded == null) {
      return(
      <SpreadsheetComponent
        initialData={ State.get().tables[pub.pub + sheet.name].tableData}
        config={tableConfig}
        cellClasses={State.get().tables[pub.pub + sheet.name].tableClasses}
        spreadsheetId={pub.pub + sheet.name}
         />)
    }
    else {
      return(<Segment>Excluded</Segment>)
    }


  }

  updateFilteredResults = () => {
    var r = request.post('http://localhost:4001/obs/filtered/result');
    r.send(State.get().filters);
    r.end( (err, res) => {
      var c = this.createClusteredObs(res.body);
      State.get().set('clusteredObsReview', c);
    })
  }


  isGroup = (type, value = '') => {
    //console.log('isGroup: ' + type);
    if(State.get().filters[type].length > 0) {
      var groups = _.filter(State.get().filters[type], {type: 'group'});
      var filtergroups = _.filter(State.get().filters[type], {type: 'filtergroup'});
      if(!groups)
        groups = [];
      if(!filtergroups)
        filtergroups = [];

      var all = groups.concat(filtergroups);


      if(all.length > 0) {
        for(var i = 0; i < all.length; i++) {
          var group = all[i];
          console.log(group);
          console.log(value);
          console.log(group.values.indexOf(value));
          // check if the current obs should be grouped or not
          if(group.uri == value || group.values.indexOf(value) >= 0) {
            return group.uri;
          }

        }
      }
      else {
        return '';
      }
    }

    //else if(State.get().filters['no' + type] != 2) {
    //  return 'anyornone';
    //}
    return '';
   }

  createClusteredObs = (observations) => {
    console.log(observations);
    var clusteredObs = d3.nest()
      .key( (d) => {
        var key = '';
        //TODO: change to d.period when it has generated URI

        key = key + this.isGroup('corpus', d.corpus);
        key = key + this.isGroup('expression', d.exp);
        key = key + this.isGroup('function', d.func);
        key = key + this.isGroup('genre', d.genre);
        return key + d.periodName;
      })
      .entries(observations);

    clusteredObs.map( (c) => {
      var values = {};
      c.values.map( (v) => {
        console.log(v);
        values[v.per] = v.freq;
      });
      c['resultValues'] = values;
    });
    console.log(clusteredObs);
    return clusteredObs;
  }

  addColumn = (type) => {
    if(State.get().filters[type].length > 0) {
      return true;
    }
    // TODO: Only showing the grouped columns for specific values for now
    // user should be able to create some X type of filter groups too instead
    // of just filters

    //if(State.get().filters['no' + type]) {
    //  if(State.get().filters['no' + type] != 2) {
    //    return true;
    //  }
    //}
    return false;

  }

  getTableHeaderCells = () => {
    var cells = []
    cells.push((<Table.HeaderCell key='value'>Value(s)</Table.HeaderCell>));
    if(this.addColumn('corpus'))
      cells.push((<Table.HeaderCell key='corpus'>Corpus</Table.HeaderCell>));
    if(this.addColumn('expression'))
      cells.push((<Table.HeaderCell key='exp'>Expression</Table.HeaderCell>));
    if(this.addColumn('genre'))
      cells.push((<Table.HeaderCell key='genre'>Genre</Table.HeaderCell>));
    if(this.addColumn('function'))
      cells.push((<Table.HeaderCell key='func'>Function</Table.HeaderCell>));

    cells.push((<Table.HeaderCell key='period'>Period</Table.HeaderCell>));
    return cells;
  }


  getTableRowCells = (obs) => {
    var cells = []
    cells.push( (<Table.Cell>{_.sortBy(obs.values, (o) => { return o.per}).map( (o) => {
      if(o.per != 1)
        return (<div>{o.freq} ({o.per})</div>)
      else
        return (<div>{o.freq}</div>)

    })}</Table.Cell>));
    if(this.addColumn('corpus'))
      cells.push( (<Table.Cell>{obs.values[0].corpusName}</Table.Cell>) );
    if(this.addColumn('expression'))
      cells.push( (<Table.Cell>{obs.values[0].expName}</Table.Cell>) );
    if(this.addColumn('genre'))
      cells.push( (<Table.Cell>{obs.values[0].genreName}</Table.Cell>) );
    if(this.addColumn('function'))
      cells.push( (<Table.Cell>{obs.values[0].funcName}</Table.Cell>) );

    cells.push( (<Table.Cell>{obs.values[0].periodName}</Table.Cell>) );
    return cells;
  }

  render() {
    console.log('render');
    console.log(State.get().clusteredObsReview);

    return (
      <Segment basic>
          <Segment basic>
            <Header as='h1'>
              Review
            </Header>
            <FilterLabels />
            <Grid>
            <Grid.Row>
            <Grid.Column width={8} className='scrollable'>
              <Header as='h2'>
                Source tables and filtered values
              </Header>

              <List relaxed='very' divided verticalAlign='middle'>
                {State.get().filteredObs.map( (pub) => {
                  return(
                  <List.Item key={pub.title} id={pub.pub}>
                    <List.Content>
                      {this.getPubButton(pub)}
                      <Header as='h3'>
                        {pub.title}
                          <Header.Subheader>
                            {pub.authors}, {pub.year}
                          </Header.Subheader>

                      </Header>

                      <List relaxed='very' divided verticalAlign='middle'>
                      {pub.sheets.map( (sheet) => {

                          //if(this.state.tables[pub.pub + sheet.name]) {
                          if(State.get().tables[pub.pub + sheet.name]) {
                              return (
                              <List.Item key={pub.pub + sheet.name}>
                                <List.Header>{sheet.name}</List.Header>
                                <List.Content>
                                  {this.getSheetButtons(pub, sheet.name)}
                                  <p>
                                    {sheet.desc}
                                  </p>
                                  {
                                    this.getSpreadsheet(pub, sheet)
                                  }

                                </List.Content>
                              </List.Item>
                              )
                          }
                        })

                      }
                      </List>
                    </List.Content>
                  </List.Item>
                  )
                })}
              </List>
            </Grid.Column>
            <Grid.Column width={8} className='scrollable'>
              <Header as='h2'>
                Selected and grouped values
              </Header>
              <Table striped>
               <Table.Header>
                 <Table.Row>
                  {this.getTableHeaderCells()}
                 </Table.Row>
               </Table.Header>
               <Table.Body>
               {
                 State.get().clusteredObsReview.map( (obs) => {
                      return(<Table.Row key={obs.key}>
                        {this.getTableRowCells(obs)}
                      </Table.Row>)
                 })
               }
               </Table.Body>
             </Table>
            </Grid.Column>
            </Grid.Row>
            </Grid>

          </Segment>
        </Segment>
    );
  }

}
