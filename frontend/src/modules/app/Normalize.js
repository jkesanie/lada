import React from 'react';
import { Button, Dimmer, Image, Loader, Segment, Header, List, Icon, Modal, Label, Feed} from 'semantic-ui-react'
import { Checkbox, Form , Dropdown, Input, Card, Grid, Item} from 'semantic-ui-react'
import request from 'superagent'
import * as d3 from "d3";

import FilterLabels from './components/FilterLabels'

var hash = require('object-hash');
var State = require('../../freezer')


export default class Normalize extends React.Component {
  constructor(props) {
    super(props);
    var cobs = State.get().clusteredObs;
    var cc = State.get().cc;
    if(State.get().reload.normalize){ // check for dirty data
      console.log('Dirty data -> reloading ');
      State.get().reload.set('normalize', false);
      cc = {}; // reset cc
      cobs= this.createClusteredObs();
      var uniqueTimeperiodNames = [];

      _.forEach(cobs, (v, key) => {
        _.forEach(v, (v2) => {
          if(uniqueTimeperiodNames.indexOf(v2['periodName']) < 0)
            uniqueTimeperiodNames.push({
              uri: 'http://lada/gen/period/' + v2['periodName'],
              label: v2['periodName'],
              type: 'filtergroup'
            });
        })
      });
      State.get().filters.set('timeperiod', uniqueTimeperiodNames);
      this.updateDefaultSelected(cobs, 100000);
    }
    this.state = {
      clusteredObs: cobs,
      cc: cc,
      normalizationBase: 100000,
      genreMappings: {}, // pub + sheet + cc
      selectedGenreMappings: {}
    }
    State.get().set('clusteredObs', cobs);
  }

  createClusteredObs = () => {
    var data = {};
    State.get().filteredObs.map( (pub) => {
      console.log(pub);
      if(pub.excluded == null) {
        pub.sheets.map( (sheet) => {
          var clusteredObs = d3.nest()
            .key( (d) => {
              return this.getClusteringKey(d)

            })
            .entries(_.filter(sheet.obs, {excluded: null}));
          var objs = [];
          clusteredObs.map( (c) => {
            var values = {};
            c.values.map( (v) => {
              values[v.obs] =v;
            })
            var tempValue = c.values[0];
            var obj = {
              key: c.key,
              selected: null,
              values: values,
              period: tempValue.period,
              periodName: tempValue.periodName,
              corpus2: tempValue.corpus2,
              corpusName: tempValue.corpusName,
              genre: tempValue.genre,
              genreName: tempValue.genreName,
              exp: tempValue.exp,
              expName: tempValue.expName,
              func: tempValue.func,
              funcName: tempValue.funcName,
            };
            objs.push(obj);
          });
          data[pub.pub + sheet.name] = objs;

        });

      }
    })
    //console.log(data);
    return data;
  }

  getClusteringKey = (d) => {
    // TODO: change to d.period when using period URIs
    //return '' + d.corpus2 + d.exp + d.func + d.genre + d.periodName;
    var key  = '';
    if(State.get().filters['nocorpus'] != 2)
      key = key + d.corpus2;
    if(State.get().filters['noexpression'] != 2)
      key = key + d.exp;
    if(State.get().filters['nofunction'] != 2)
      key = key + d.func;
    if(State.get().filters['nogenre'] != 2)
      key = key + d.genre;

    key = key + d.periodName;

    return key;

  }

  updateDefaultSelected = (_c, normalizationBase) => {
    //var _c = this.state.clusteredObs;
    for (var key in _c) {
      var temp = _c[key];
      for( var index in temp) {
        var obs = temp[index];
        var status = this.getNormState(obs, normalizationBase);
        //console.log(status);
        if(status != null) {
          obs.selected = status.obs;
        }

      }
    }
  }

  getCorporaFromSheet = (sheet) => {
    var corpora = {}
    sheet.obs.map( (o) => {
        corpora[o.corpus2] = o.corpusName;
    })
    var temp = [];
    Object.keys(corpora).map( (key, index) => {
      temp.push({
        uri: key,
        label: corpora[key]
      })
    });
    return temp;
  }

  getCorporaFromSheets = (sheets) => {
    var corpora = {}
    if (!Array.isArray(sheets)) {
      sheets = [sheets];
    }
    if(sheets != null) {
      sheets.map( (sheet) => {
            sheet.obs.map( (o) => {
                corpora[o.corpus2] = o.corpusName;
            })
        });
    }
    var temp = [];
    Object.keys(corpora).map( (key, index) => {
      temp.push({
        uri: key,
        label: corpora[key]
      })
    });
    return temp;
  }

  getNormState = (obs, normalizationBase = this.state.normalizationBase) => {
    var vkeys = Object.keys(obs.values);
    for (var i = 0; i < vkeys.length; i++) {
      var key = vkeys[i];
      var base = key.substring(key.lastIndexOf('_') + 1)
      if(base == ''+normalizationBase) {
        return { type: 'a', obs: key};
      }
      if(base == 'gen') {
        return { type: 'g', obs: key};
      }
    }
    return null;
  }

  getCardColor = (obs) => {
    var status = this.getNormState(obs);
    if(status != null)
      return 'green';
    return 'red';

  }
  getCheckMark = (obs, key) => {

    if(obs.selected === key) {
      return (<Icon name='checkmark'color='green'  />);
    }

  }
  getNormalizedFreq = (obs) => {
    var freq = '';
    if(obs.values[obs.key + 'gen'] != undefined) {
      freq = obs.values[obs.key + 'gen'];
    }

    return (
      <Feed.Event key={obs.key + 'generated'}>
        <Feed.Content>
          <Feed.Meta>
            generated
          </Feed.Meta>
          <Feed.Summary>
            <Feed.User as='a'>{freq}</Feed.User>
          </Feed.Summary>
        </Feed.Content>
        <Feed.Label>
          {
            this.getCheckMark(obs, obs.key + 'gen')
          }

        </Feed.Label>

      </Feed.Event>

    )
  }

  mapCCOptions = (values) => {
    return values.map( (v) => {
      return {
        key: v.uri,
        text: v.label,
        value: v.uri
      }
    });
  }


  getCC = (pub, sheet) => {
    if(this.state.cc) {
      if(this.state.cc[pub.pub + sheet.name]) {

        return this.state.cc[pub.pub + sheet.name]
      }
      else {
        var corpora = this.getCorporaFromSheet(sheet);
        var req = request.post('http://localhost:4001/cc/filtered');
        req.query({pubURI: pub.pub, sheet: sheet.name});
        req.send({
          filters: State.get().filters,
          corpora: corpora
        }).end( (err, res) => {
          var cc = State.get().cc.transact();
          var data = res.body;
          var key = Object.keys(data)[0];
          cc[key] = data[key];
          this.setState({cc: cc});
          State.get().set('cc', cc);
          return data[key];
        });
      }
    }
    return [];

  }
  onCCGenreMappingChange = (pub, sheet, ccURI, selectedCCURI, genreURI, event, element) => {
    var selectedCCGenreURI = element.value;
    var genreMappings = this.state.genreMappings;
    if(!genreMappings[pub.pub + sheet.name ])
      genreMappings[pub.pub + sheet.name ] = {};

    genreMappings[pub.pub + sheet.name ][genreURI] = selectedCCGenreURI;
    console.log('genreMappings');
    console.log(genreMappings);
    console.log(selectedCCURI);
    console.log(ccURI);
    this.calculateNormalizedValues(pub, sheet, selectedCCURI, ccURI, genreMappings);
    this.setState({genreMappings: genreMappings});
    State.get().reload.set('visualize', true);
  }
  onCCMappingChange = (pub, sheet, _cc, event, element) => {
    var selectedCCURI = element.value;
    var ccs = State.get().cc[pub.pub + sheet.name];
    var cc = _.find(ccs, {uri: _cc.uri});
    console.log(cc);

    cc.set('selected', selectedCCURI);
    this.calculateNormalizedValues(pub, sheet, selectedCCURI, cc.uri, {});
    State.get().reload.set('visualize', true);
  }

  calculateNormalizedValues = (pub, sheet, cc, corpusURI, genreMappings) => {
    console.log(corpusURI);
    console.log(genreMappings);
    //var norm = this.state.norm;
      var normalizationBase = 100000;
      var clusterKey = pub.pub + sheet.name;
      var clusters = this.state.clusteredObs[clusterKey];
      var rr = clusters.map( (c) => {
        //console.log(c);
        if(c.corpus2 == corpusURI) {
          // TODO: figure out which properties to use for normalization: time period and or genre
          var sum = 0;
          var periodName = null;
          var vkeys = Object.keys(c.values);
          var o = null;
          for (var i = 0; i < vkeys.length; i++) {
            var key = vkeys[i];
            var base = key.substring(key.lastIndexOf('_') + 1)
            if(base == '1') {
              o = c.values[key];
              sum = sum + parseInt(o.freq);
              periodName = o.periodName;
            }
          }
          console.log('periodname:' + periodName);
          if(periodName) {
            var parts = periodName.split('-', 2);
            var req = request.get('http://localhost:4001/normalize');
            var ccGenre = null;
            var ccGenres = [];
            console.log(genreMappings);
            if((pub.pub + sheet.name) in genreMappings) {
              Object.keys(genreMappings[pub.pub + sheet.name]).map( (gkey) => {
                ccGenres.push(genreMappings[pub.pub + sheet.name][gkey]);
              })

            }
            console.log('ccgenres:' + ccGenres);
            req.query({ccgenres: ccGenres, ckey: this.getClusteringKey(o), pub: pub.pub, sheet: sheet.name, obs: o.obs, ccURI: cc, startYear: parts[0], endYear: parts[1], absValue: sum, base: normalizationBase});
            return req;
          }
        }


      });

    //console.log(rr);
    Promise.all(rr).then( (res) => {
        console.log('all done');
        console.log(res);
        var clusters = State.get().clusteredObs.transact();
        res.map( (_res) => {
            if(_res) {
              var d = _res.body;
              var clusterKey = Object.keys(d)[0]
              var normObs = clusters[clusterKey];

              var d2 = d[clusterKey];
              var key = Object.keys(d2)[0];
              console.log(key);
              var normalizedValue = parseFloat(d2[key]).toFixed(2);
              var obs = _.find(normObs, {key: key});
              console.log(obs);
              if(obs) {
                var obsKey = obs.key + '_gen';
                if(obs.selected == null) {
                  obs.set('selected', obsKey);
                }
                obs.values.set(obsKey,{
                  freq: normalizedValue > 0 ? normalizedValue : 0 ,
                  obs: obsKey,
                  per: 'generated'
                });

              }
              else {

              }
              //obs.values[obsKey] = {
              //  freq: normalizedValue > 0 ? normalizedValue : 'error' ,
              //  obs: obsKey,
              //  per: 'generated'
              //};

            }

        })

        this.setState({'clusteredObs': clusters});
        State.get().set('clusteredObs', clusters);
    });
  }

  selectFreq = (clusteredObs, obs, event) => {
    //console.log(clusteredObs);
    //console.log(obs);
    if(obs.per == 1)
      return;
    clusteredObs.set('selected', obs.obs);
    this.setState({'clusteredObs': State.get().clusteredObs});
    State.get().reload.set('visualize', true);

  }

  getDimensionLabels = (obs) => {

    var labels = [];
    if(obs.corpus2 != null &&  State.get().filters['nocorpus'] != 2) {
      labels.push(
        (<Label key={obs.corpus2} color='purple'>{obs.corpusName}</Label>)
      );
    }


    if(obs.exp != null) {
      labels.push(
        (<Label key={obs.exp} color='yellow'>{obs.expName}</Label>)
      );
    }

    if(obs.genre != null && State.get().filters['nogenre'] != 2) {
      labels.push(
        (<Label key={obs.genre} color='teal'>{obs.genreName}</Label>)
      );
    }
/*
    if(obs.func != null) {
      labels.push(
        (<Label key={obs.func} color='olive'>{obs.funcName}</Label>)
      );
    }
*/
    if(obs.period != null) {
      labels.push(
        (<Label key={obs.period} color='black'>{obs.periodName}</Label>)
      );
    }

    return labels;

  }

/*
<Feed.Event key={obs.key + 'inputted'}>
  <Feed.Content>
    <Feed.Meta>
      inputted
    </Feed.Meta>
    <Feed.Summary>
      <Input size='mini' placeholder='' />
    </Feed.Summary>
  </Feed.Content>
</Feed.Event>

*/

  checkIfHiddenTable = (sheet) => {

    if(!_.find(sheet.obs, {excluded: null}))
      return 'hidden'

  }


  findDefaultValue = (values, needle) => {
    for(var i = 0; i < values.length ; i++) {
      console.log(values[i].label.toLowerCase());
      console.log(needle.toLowerCase());
      if(values[i].label.toLowerCase() == needle.toLowerCase()) {
        var selectedCCGenreURI = values[i].uri;
        return selectedCCGenreURI;
      }
    }
    return null;
  }

  showCCGenres = (pub, sheet) => {
    if(State.get().cc) {
      if(State.get().cc[pub.pub + sheet.name]) {
        var c = State.get().cc[pub.pub + sheet.name];
        var selected = c[0].selected;
        console.log(c[0]);
        if(selected != "") {
          var cc = _.find(c[0].options, { uri: selected})
          var ccGenres = cc.genres;
          // find obs genres
          // if nogenre = none -> use
          console.log(sheet.obs);
          var sheetGenres = {};

          sheet.obs.map( (o) => {
            if(o.genre != null) {
              sheetGenres[o.genre] = o.genreName
            }
          });
          console.log('sheetGenres');
          console.log(c[0]);
          console.log(cc);
          console.log(sheetGenres);

          //var defaultValue = ;
          //console.log(defaultValue);
          return (
            <Segment basic>
            <Card.Group>
              {
                Object.keys(sheetGenres).map( (key) => {
                  var defaultValue = this.findDefaultValue(ccGenres, sheetGenres[key]);
                  if(defaultValue) {
                    var genreMappings = this.state.genreMappings;
                    if(!genreMappings[pub.pub + sheet.name ])
                      genreMappings[pub.pub + sheet.name ] = {};
                    genreMappings[pub.pub + sheet.name ][key] = defaultValue

                  }


                  return (<Card color='teal' key={key}>

                      <Card.Content>
                        <Card.Header>{sheetGenres[key]}</Card.Header>
                        <Card.Description>

                        <Dropdown
                          selection
                          placeholder={sheetGenres[key]}
                          defaultValue={defaultValue}
                          options={this.mapCCOptions(ccGenres)}
                          onChange={this.onCCGenreMappingChange.bind(this, pub, sheet, c[0].uri, selected, key)}
                          />
                        </Card.Description>

                      </Card.Content>

                    </Card>)
                })
              }


            </Card.Group>
            </Segment>
          )

        }
      }
    }
  }
  render = () => {
    const normalizationBases = [{text:1000, value:1000}, {text:10000, value:10000}, {text:100000, value:100000}, {text:1000000, value:1000000}];
    //console.log(this.state.cc);
    console.log(_.filter(State.get().filteredObs, {'excluded': null}));
    console.log(this.state.clusteredObs);
    console.log(State.get().clusteredObsReview);

    return(
    <Segment basic>
      <Segment basic>
        <Header as='h1'>
          Normalize
        </Header>

        <FilterLabels />
        <List relaxed='very' divided verticalAlign='middle'>
          {_.filter(State.get().filteredObs, {'excluded': null}).map( (pub) => {

            return(
            <List.Item key={pub.title} id={pub.pub}>
              <List.Content>
                <Header as='h2'>
                  {pub.title}
                    <Header.Subheader>
                      {pub.authors}, {pub.year}
                    </Header.Subheader>
                </Header>

                {pub.sheets.map( (sheet) => {
                    return(
                    <Segment basic key={pub.pub + sheet.name} className={this.checkIfHiddenTable(sheet)}>
                      <Header as='h4'>
                        {sheet.name}
                      </Header>
                      <p>
                        {sheet.desc}
                      </p>
                      <Segment>
                          {
                            this.getCC(pub, sheet).map( (c) => {
                              return (

                                    <Dropdown
                                      key={c.uri}
                                      placeholder={c.label}
                                      defaultValue={c.selected}
                                      selection
                                      fluid
                                      options={this.mapCCOptions(c.options)}
                                      onChange={this.onCCMappingChange.bind(this, pub, sheet, c)}
                                      />

                                    )
                            })
                          }
                          {
                            this.showCCGenres(pub, sheet)
                          }
                      </Segment>
                    </Segment>)
                    })
                  }

                </List.Content>
              </List.Item>
            )
          })
        }
      </List>
      <Segment basic>
      <Card.Group>
        {_.filter(State.get().filteredObs, {'excluded': null}).map( (pub) => {
          return pub.sheets.map( (sheet) => {

            return this.state.clusteredObs[pub.pub+sheet.name].map( (obs) => {
            return (
            <Card key={obs.key} color={this.getCardColor(obs)}>

              <Card.Content>
                <Card.Header className='green'>Frequencies</Card.Header>
                <Feed size='large'>
                  {
                    Object.keys(obs.values).map( (vkey) => {
                      var o = obs.values[vkey];
                      return (
                        <Feed.Event key={o.obs}>
                          <Feed.Content>
                            <Feed.Meta>
                              {o.per == 1 ? 'absolute' : o.per}
                            </Feed.Meta>
                            <Feed.Summary>
                              <Feed.User as='a' onClick={this.selectFreq.bind(this, obs, o)} >{o.freq}</Feed.User>
                            </Feed.Summary>
                          </Feed.Content>
                          <Feed.Label>
                            {
                              this.getCheckMark(obs, o.obs)
                            }

                          </Feed.Label>
                        </Feed.Event>
                      )
                    })
                  }



                </Feed>
              </Card.Content>
              <Card.Content extra>
                <Label.Group>
                  {this.getDimensionLabels(obs).map( (o) => {return o})}
                </Label.Group>
              </Card.Content>
            </Card>
          )
          })
          })

      })
      }

      </Card.Group>
      </Segment>
    </Segment>
  </Segment>

    )
  }
}
