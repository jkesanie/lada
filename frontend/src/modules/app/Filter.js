import React from 'react';
import { Button, Dimmer, Image, Loader, Segment, Header, List, Icon, Modal, Label} from 'semantic-ui-react'
import { Tab, Checkbox, Form , Dropdown, Input, Card, Grid} from 'semantic-ui-react'
import request from 'superagent'

var hash = require('object-hash');
var State = require('../../freezer')

export default class Select extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      modalVisible: false,
      uri: '',
      type: '',
      name : '',
      function: 'filtergroup',
      data: {
        corpus: {},
        expression: {},
        genre: {},
        function: {}
      },
      options: [],
      selected: [],
      defaultValues: [],
      groups: {
        corpus: [],
        expression: [],
        genre: [],
        function: []
      },
      preview: []

    };
    //if(State.get().reload.filter) {
      this.updatePreview();
    //  State.get().reload.set('filter', false);
    //}

  }

  updatePreview = () => {
    var r =  request.post('http://localhost:4001/obs/filtered/preview').timeout({deadline:120000});
    r.send(State.get().filters);
    r.end( (err, res) => {
      console.log('filtered preview done');
      console.log(res.body);
      console.log('setting state');
      this.setState({preview: res.body});
    });
  }

  openGrouping = (type, obj) => {
    var options = [];
    var data = this.state.data;
    if(true) {
      console.log('dirty publications data -> updating ' + type + ' values');
      const req = request.get('http://localhost:4001/' + type);
      req.end((err, res) => {
        var newData = res.body;
        var me = this;
        Object.keys(newData).map(function(key, index) {
           var uri = newData[key][0];
           //console.log(uri);
           options.push(
             {
               'text': key,
               //'value':uri,
               'value': key,
               'key': key
             }
           );
        });
        data[type] = newData;
        var values = [];
        var id = '';
        var name = '';
        var func = 'filtergroup';
        console.log(obj);
        if(obj != null) {
          values = obj.labels;
          id = obj.uri;
          name = obj.label;
          func = obj.type;

        }
        console.log('default values: ');
        console.log(values);
        this.setState({modalVisible: true, function: func, type: type, uri: id, defaultValues: values, selected: values, name: name, options: options, data: data});

      });
    }
    else {
      Object.keys(this.state.data[type]).map(function(key, index) {
        var uri = data[type][key][0];
         options.push(
           {
             'text': key,
             //'value': data[type][key][0],
             'value': key,
             'key': key
           }
         );
      });
      console.log(obj);
      var values = [];
      var id = '';
      var name = '';

      if(obj != null) {
        values = obj.labels;
        id = obj.uri;
        name = obj.label;

      }
      console.log('default values: ');
      console.log(values);
      this.setState({modalVisible: true, type: type, uri: id, defaultValues: values, selected: values, name: name, options: options, data: data});

    }
  }

  onCloseGrouping = (e) => {
    console.log('close grouping');
    var values = [];
    var oldFilters = State.get().filters[this.state.type].transact();
    var group = _.find(oldFilters, { uri: this.state.uri});

    var newValues = [];
    this.state.selected.map( (key) => {
      this.state.data[this.state.type][key].map( (uri) => { newValues.push(uri)})
    })

    var label = this.state.name;
    if(label == '' && this.state.selected.length > 0) {
      label = this.state.selected[0];
    }

    if(group) {
      // update existing
      group.set({values:newValues, label:label, labels: this.state.selected, type: this.state.function});
    }
    else {
      // add new
      oldFilters.push(
        {
          //uri: '' + Math.random(),
          uri: 'http://lada/' + this.state.type + '/' + Math.random(),
          label: label,
          type: this.state.function,
          //values: this.state.selected
          values: newValues,
          labels: this.state.selected
        }
      );
    }
    if(this.state.selected.length > 0 && this.state.function != 'group' ) {
      console.log('setting filters to null');
      State.get().filters.set('no' + this.state.type, null);
    }

    State.get().filters[this.state.type].run();

    console.log(State.get().filters);
    //State.get().filters.set(this.state.type, oldFilters);
    this.setState({modalVisible: false});

    // TODO: change this, so that reload is set only when things actually change
    var r = State.get().reload.transact();
    r['review'] = true;
    r['normalize'] = true;
    State.get().reload.run();
    this.updatePreview()
  }

  removeGroup = (type, uri) => {

    var filters = State.get().filters[type];
    console.log(filters);
    var index = _.findIndex(filters, {uri: uri});
    console.log('index:' + index);
    filters.splice(index, 1);
    console.log(filters);
    if(filters.length == 1) {
      console.log('no more filters');
      State.get().filters.set('no'+type, 1).now();
    }
    this.updatePreview();
  }

  toggleNoAny = (filter) => {
    var value = State.get().filters['no'+ filter];

    if(value == 1) {
      value = 2;
    }
    else if(value == 2) {
      value = 3;
    }
    else {
      value = 1;
    }
    console.log('new value: ' +  value);
    State.get().filters.set('no' + filter, value).now();
    State.get().reload.set('review', true);
    State.get().reload.set('normalize', true);
    this.updatePreview();
  }

  getColor = (type) => {
    if(type === 'corpus')
      return 'purple';
    if(type === 'expression')
      return 'yellow';
    if(type === 'genre')
      return 'teal'
    if(type === 'function')
      return 'olive';
    if(type === 'timeperiod')
      return 'black';

  }

  getFilterCards = (type) => {
    var cards = [];
    var color = this.getColor(type);
    if(State.get().filters['no' + type] != null) {
        var noValue = State.get().filters['no' + type];
        if(noValue == 1) {
          cards.push( (
            <Card color={color} key={type} link >
              <Card.Content>
                <Card.Header onClick={this.toggleNoAny.bind(this, type)} >No {type}</Card.Header>
                <Card.Meta>filter</Card.Meta>
              </Card.Content>
            </Card>
          ))
        }

        else if(noValue == 2) {
          cards.push( (
            <Card color={color} key={type} link >
              <Card.Content>
                <Card.Header onClick={this.toggleNoAny.bind(this, type)} >Any or no value</Card.Header>
                <Card.Meta>filter</Card.Meta>
              </Card.Content>
            </Card>
          ))

        }
        else {
          cards.push( (
            <Card color={color} key={type} link >
              <Card.Content>
                <Card.Header onClick={this.toggleNoAny.bind(this, type)}>Some {type}</Card.Header>
                <Card.Meta>{type != 'timeperiod' ? 'filter' : 'filtergroup'}</Card.Meta>
              </Card.Content>
            </Card>
          ))
        }
    }
    if(type != 'timeperiod') { // TODO: remove this!
      State.get().filters[type].map( (g) => {
          cards.push( (
            <Card color={color} key={g.uri} link >
              <Card.Content>
                <Card.Header onClick={this.openGrouping.bind(this, type, g)}>{g.label}</Card.Header>
                <Card.Meta>{g.type}</Card.Meta>
                <Label  attached='top right' onClick={this.removeGroup.bind(this, type, g.uri)}><Icon name='remove'/></Label>
              </Card.Content>
            </Card>
          ))
        })

    }


    return cards;
  }

  handleFunctionChange = (e, { value }) => {
    console.log(value);
    this.setState({ function: value })
  }

  getLabelColor = (key) => {
    if(this.state.selected.indexOf(key) >= 0) {
      return 'purple';
    }
    else {
      return 'grey';
    }
  }

  onLabelClick = (label) => {
    console.log(label);
    var selected = this.state.selected;
    var index = selected.indexOf(label);
    if(index >= 0) {
      selected.splice(index, 1);
    }
    else {
      selected.push(label);

    }
    console.log(selected);
    console.log(selected);
    this.setState({'selected': selected});
  }
  render() {
    console.log('render');
    return (

      <Segment basic>

        <Modal open={this.state.modalVisible}
          >
          <Modal.Header>Configure {this.state.type} grouping</Modal.Header>
          <Modal.Content>
            <Form loading={false}>
              <Form.Field>
                <label>Name</label>
                <Input placeholder='' value={this.state.name}
                onChange={ (event, data) => {
                    this.setState({'name': data.value})
                  }
                } />
              </Form.Field>
              <Form.Field>
                <label>Clustered values</label>

                <Dropdown fluid multiple search selection
                  options={this.state.options}
                  defaultValue={this.state.defaultValues}
                  onChange={ (event, data ) =>
                    {console.log(data); this.setState({'selected': data.value}) }
                  }
                  />


              </Form.Field>
              <Form.Field>
              <Label.Group>
              {
                this.state.options.map( (o) => {
                  return (
                    <Label onClick={this.onLabelClick.bind(this, o.text)} color={this.getLabelColor(o.key)}>{o.text}</Label>
                  )
                })
              }
              </Label.Group>
              </Form.Field>
              <Form.Group inline>
              <Form.Radio label='Filter group' value='filtergroup' checked={this.state.function == 'filtergroup'} onChange={this.handleFunctionChange} />

              <Form.Radio label='Filter' value='filter' checked={this.state.function == 'filter'} onChange={this.handleFunctionChange} />
              <Form.Radio label='Group' value='group' checked={this.state.function == 'group'} onChange={this.handleFunctionChange}></Form.Radio>
              </Form.Group>
            </Form>


          </Modal.Content>
          <Modal.Actions>
            <Button onClick={ (e) => { this.setState({modalVisible: false})}}>Cancel</Button>
            <Button onClick={this.onCloseGrouping}>Save</Button>
          </Modal.Actions>
        </Modal>
        <Segment basic>
          <Header as='h1'>
            Filter and group
          </Header>

          <Grid columns={5} divided>
            <Grid.Row>
              <Grid.Column>
                <Header as='h3' color='purple'>
                  Corpora <Icon onClick={this.openGrouping.bind(this, 'corpus', null)} name='add' />
                </Header>
                <Card.Group>
                  {
                    this.getFilterCards('corpus')
                  }
                </Card.Group>
              </Grid.Column>
              <Grid.Column>
                <Header as='h3' color='yellow'>
                  Expressions <Icon onClick={this.openGrouping.bind(this, 'expression', null)} name='add' />
                </Header>
                <Card.Group>
                  {
                    this.getFilterCards('expression')
                  }

                </Card.Group>
              </Grid.Column>
              <Grid.Column>
                <Header as='h3' color='teal'>
                  Genres <Icon onClick={this.openGrouping.bind(this, 'genre', null)} name='add' />
                </Header>
                <Card.Group>
                  {
                    this.getFilterCards('genre')
                  }
                </Card.Group>
              </Grid.Column>
              <Grid.Column>
                <Header as='h3' color='olive'>
                  Functions <Icon onClick={this.openGrouping.bind(this, 'function', null)} name='add' />
                </Header>
                <Card.Group>
                  {
                    this.getFilterCards('function')
                  }
                </Card.Group>
              </Grid.Column>
              <Grid.Column>
                <Header as='h3' color='black'>
                  Time period <Icon onClick={this.openGrouping.bind(this, 'timeperiod', null)} name='add' />
                </Header>
                <Card.Group>
                  {
                    this.getFilterCards('timeperiod')
                  }
                </Card.Group>
              </Grid.Column>


            </Grid.Row>
          </Grid>
        </Segment>
        <Segment basic>
          <Header as='h2'>
            Results ({this.state.preview.length})
          </Header>
          <List relaxed='very' divided verticalAlign='middle'>
          {
            this.state.preview.map( (pub) => {
              return (
                <List.Item key={pub.uri}>
                  <List.Content>
                    <Header as='h3'>
                      {pub.title}
                        <Header.Subheader>
                          Tables: {pub.ds} Values: {pub.obs}
                        </Header.Subheader>
                    </Header>
                  </List.Content>
                </List.Item>
              )
            })
          }
          </List>

        </Segment>

      </Segment>
    );
  }

}
