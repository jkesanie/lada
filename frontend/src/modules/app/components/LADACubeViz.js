import React, { Component, PropTypes } from 'react';
import ReactDOM from 'react-dom'

import { Sidebar, Segment, Button, Menu, Image, Icon, Header, Modal, Input } from 'semantic-ui-react'
import { Checkbox, Form , Dropdown} from 'semantic-ui-react'

import {Hint,XYPlot, XAxis, YAxis, HorizontalGridLines,
  LineSeries,LineMarkSeries,VerticalBarSeries, VerticalBar, DiscreteColorLegend, LabelSeries
  } from 'react-vis';

import request from 'superagent'
import MeasureIt from 'react-measure-it'


const styles = {
  listitem: {
    padding: '10px',
    backgroundColor: '#ccc',
    marginBottom: '5px'

  },
  graph: {
    width: '100%',
    height: '900px'
  },
  moreMargin: {
    marginTop: '20px'
  }
};

function getWidth(element)  {
return ReactDOM.findDOMNode(element).parentNode.getBoundingClientRect().width
}

function getHeight(element) {
return ReactDOM.findDOMNode(element).parentNode.getBoundingClientRect().height
}


class CubeViz extends Component {


  constructor(props) {
    super(props);
    if(props.conf != null) {

      this.state = props.conf;
    }
    else {
      this.state = {
        modalVisible: false,
        modalLoading: false,
        value: null,
        measures: [],
        dimensions: [],
        selectedMeasure: null,
        selectedFilter: null,
        selectedDimensionOne: null,
        selectedDimensionTwo: null,
        vizdata: [],
        vizlegend: [],
        stacked: false,
        showDataLabels: false,
        type: 'VerticalBarSeries',
        labelData: [
          {x:0, y:0, label:'Title', size:10}
        ]

      };

    }


  }

  toggleModal = () => this.setState({modalVisible: !this.state.modalVisible})


  createMeasureField = () => {
    if(this.state.measures) {
      if(this.state.measures.length == 1) {
        return this.state.measures[0].label
      }
      else {
        var options = this.state.measures.map((o) => { return {'text': o.label, 'key': o.uri, 'value': o.uri} });
        return (<Dropdown placeholder='select' selection options={options } />)
      }
    }
    else {
      return;
    }
  }

  createDimensionUI = (d, did) => {
    if(d == null || d.uri == '')
      return;
    var dim = _.find(this.state.dimensions, {uri: d.uri});
    var options = [];
    if(dim.concepts) {
      options = dim.concepts.map( (c) => { return { 'text': c.label, 'key': did + c.uri, 'value': c.uri} });
    }
    else {
      options = dim.values.map( (c) => { return { 'text': c, 'key': did + c, 'value': c} });
    }

    return (<Form.Field key={dim.uri}>
      <Dropdown fluid multiple search selection
        options={options}
        defaultValue={d.values}
        onChange={
        (e, {value}) => {
          var newValues = d.values;
          d.values = value;
          this.setState({did: d})
        }
      }/></Form.Field>)
  }


  openModal = (e) => {

    this.setState({modalVisible: true, modalLoading: true});
    const req = request.get(this.props.endpoint + '/obs/norm/defs')
    req.end( (err, res) => {
      var newState = res.body;
      console.log(newState);
      newState['modalLoading'] = false;
      this.setState( newState);

    });

  }

  filterUI = () => {
    console.log('selected filter');
    console.log(this.state.selectedFilter);
    if(this.state.selectedFilter != null && this.state.selectedFilter.uri != '') {
      return (
        <div>
          Filter: {this.state.selectedFilter.uri} IN {this.state.selectedFilter.values.join(' , ')}
        </div>

      );

    }
  }

  getDimensionOptions = () => {
    var options = this.state.dimensions.map( (o) => { return { 'text': o.label, 'value': o.uri, 'key': 'one-' + o.uri} });
    options.unshift({ 'text': 'None', 'value': '', 'key': 'none'});
    return options;
  }

  getMeasureOptions = () => {
    var options = this.state.measures.map( (o) => { return { 'text': o.label, 'value': o.uri, 'key': 'one-' + o.uri} });
    return options;
  }

  saveConfig = (event) => {

    this.setState({modalVisible: false});

    var data = {}
    data.dataset = '<http://data.hulib.helsinki.fi/lcd/corpora/composition/hc-xml-0.96#dataset>';
    data.slices = [];
    console.log('selected filter');
    console.log(this.state.selectedFilter);
    if(this.state.selectedFilter != null && this.state.selectedFilter.uri != '') {

      data.slices.push({
        uri: '<' + this.state.selectedFilter.uri + '>',
        id: 'filter',
        label: 'filter',
        type: (this.state.selectedFilter.uri == 'http://lada/timeperiod' ? 'value' : 'concept'),
        values: this.state.selectedFilter.values.map(
          (v) => {
            var dim = _.find(this.state.dimensions, {uri:this.state.selectedFilter.uri});
            if(dim.concepts) {
              return {
                uri: '<' +v +'>',
                label: _.find(dim.concepts, {uri: v}).label
              }
            }
            else {
              return {
                uri: '<' + this.state.selectedFilter.uri + '>',
                label: v
              }
            }
          }
        )

      });
    }

    data.dimension = {
      uri: '<' + this.state.selectedDimensionOne.uri + '>',
      id: 'dim',
      label: 'test',
      values: this.state.selectedDimensionOne.values.map( (v) => { return {uri: '<' +v +'>', label: _.find(_.find(this.state.dimensions, {uri:this.state.selectedDimensionOne.uri}).concepts, {uri: v}).label  } })

    };

    if(this.state.selectedDimensionTwo != null && this.state.selectedDimensionTwo.uri != '') {
      data.dimension.dimension = {
        uri: '<' + this.state.selectedDimensionTwo.uri + '>',
        id: 'dim2',
        label: 'test',
        values: this.state.selectedDimensionTwo.values.map( (v) => { return {uri: '<' +v +'>', label: _.find(_.find(this.state.dimensions, {uri:this.state.selectedDimensionTwo.uri}).concepts, {uri: v}).label } })

      };
    }
    console.log('input data');
    console.log(data);
    const req = request.post(this.props.endpoint + '/obs/norm/query');
    req.send(data)
    req.end( (err, res) => {
      var o = res.body;
      console.log('viz data');
      console.log(o.results);


      this.setState({'vizdata': o.results, 'vizlegend': o.legend});
      this.props.onConfChange(this.props.id, this.state);
    });

  }

  handleTypeChange = (e, { value }) => {
    console.log(value);
    this.setState({ type: value })
    this.props.onConfChange(this.props.id, this.state, 'type', value);
  }

  exportSVG = (e) => {
    console.log(e.target.value);
    var r = ReactDOM.findDOMNode(e.target).parentNode.getElementsByClassName('rv-xy-plot__inner')
    var o = r[0]

    console.log(o);
    var w = o.attributes[1].value
    var h = o.attributes[2].value
    var content = o.innerHTML;
    console.log(w);
    console.log(h);

    r = request.post('http://localhost:4001/image')
    r.query({ id: this.props.id })
    r.query({ w: w })
    r.query({ h: h })
    r.send(content)
    r.end( (err, res) => {
      console.log(res.body);
      window.location = 'http://localhost:4001/image?id=' + this.props.id;
    })
  }

  getDataLabels = (d) => {
    var data = {}
    // {x:0, y:0, label:'Title'
    console.log(d);
    for(var i = 0; i < d.length; i++) {
      var x = d[i].x
      var y = d[i].y

      if( !(x in data) ) {
        data[x] = parseFloat(y);
      }
      else {
        data[x] = data[x] + parseFloat(y);
      }
    }
    var result = [];
    Object.keys(data).map( (key) => {
      result.push(
        {
          x: key,
          y: data[key].toFixed(2),
          label: data[key].toFixed(2)
        }
      )
    })
    console.log(result);
    return result;
  }

  render() {
    const { modalLoading, value } = this.state
    const graphTypes = [{text:'Bars', value:'VerticalBarSeries'}, {text:'Line', value:'LineMarkSeries'}];
    return (

      <Segment basic style={styles.graph}>
        <Modal open={this.state.modalVisible} onClose={this.saveConfig}>
          <Modal.Header>Configure graph</Modal.Header>
          <Modal.Content>
            <Form loading={modalLoading}>
            <Form.Field>
              <label>Measure</label>
              <Dropdown inline
                defaultValue={this.state.selectedMeasure != null ? this.state.selectedMeasure.uri : null}
                options={this.getMeasureOptions()}
                onChange={ (event, data ) => {
                  var m = _.find(this.state.measures, {'uri': data.value});
                  this.setState({'selectedMeasure': { 'uri' : data.value, 'label': m.label, 'values': []}}) }
                } />
            </Form.Field>
              <Form.Field>
                <label>Filter</label>
                <Dropdown inline
                  defaultValue={this.state.selectedFilter != null ? this.state.selectedFilter.uri : null}
                  options={this.getDimensionOptions()}
                  onChange={ (event, data ) =>

                    { this.setState({'selectedFilter': { 'uri' : data.value, 'values': []}}) }
                  } />
              </Form.Field>
              { this.createDimensionUI(this.state.selectedFilter, 'selectedFilter')}
              <Form.Field>
                <label>First dimension</label>
                <Dropdown inline
                  defaultValue={this.state.selectedDimensionOne != null ? this.state.selectedDimensionOne.uri : null}
                  options={this.getDimensionOptions()}
                  onChange={ (event, data ) => {
                    var dim = _.find(this.state.dimensions, {'uri': data.value});
                    console.log(dim);
                    this.setState({'selectedDimensionOne': { 'uri' : data.value, 'label': dim.label, 'values': []}}) }
                  } />
              </Form.Field>
              { this.createDimensionUI(this.state.selectedDimensionOne, 'selectedDimensionOne')}
              <Form.Field>
                <label>Second dimension</label>
                <Dropdown inline
                  defaultValue={this.state.selectedDimensionTwo != null ? this.state.selectedDimensionTwo.uri : null}
                  options={this.getDimensionOptions()} onChange={ (event, data ) => {this.setState({'selectedDimensionTwo': { 'uri' : data.value, 'values': []}}) }} />
              </Form.Field>
              { this.createDimensionUI(this.state.selectedDimensionTwo, 'selectedDimensionTwo')}
               <Checkbox label='Stacked' checked={this.state.stacked} onChange={ (e, {checked} )=> { this.setState({'stacked': checked} ) }}/>
            </Form>
          </Modal.Content>
          <Modal.Actions>
            <Button onClick={this.saveConfig}>Save</Button>
          </Modal.Actions>
        </Modal>


          <Button onClick={this.openModal}>Edit graph</Button>
          <Button onClick={(e) => this.exportSVG(e)}
            //parentNode
            >Export SVG</Button>
          <Button>Export CSV</Button>
          <Form style={styles.moreMargin}>
<Form.Group inline>

          <Form.Radio label='Bar' value='VerticalBarSeries' checked={this.state.type === 'VerticalBarSeries'} onChange={this.handleTypeChange} />
          <Form.Radio label='Line' value='LineMarkSeries' checked={this.state.type === 'LineMarkSeries'} onChange={this.handleTypeChange} />
          <Checkbox label='Data labels' checked={this.state.showDataLabels} onChange={ (e, {checked} )=> { this.setState({'showDataLabels': checked} ) }}/>
          <Input placeholder='Title' value={this.state.title} onChange={ (e, d) => { this.setState({'title': d.value}); this.props.onConfChange(this.props.id, this.state, 'title', d.value); }} />

        </Form.Group>
        </Form>



            <XYPlot
              margin={50}
              stackBy={this.state.stacked ? 'y' : null}
              xType={'ordinal'}
              width={this.props.containerWidth - 50}
              height={this.props.height - 70}
              >
              <HorizontalGridLines />
              <DiscreteColorLegend  items={this.state.vizlegend} orientation={'horizontal'}/>
              { this.state.vizdata.map( d => {
                console.log(d);
                if(this.state.type == 'VerticalBarSeries') {
                  return (
                      <VerticalBarSeries key={'series-' + this.state.vizdata.indexOf(d)} data={d}
                      onValueMouseOver={ (d, e) => { this.setState({value:d})}}
                      onValueMouseOut={ (d, e) => { this.setState({value:null})}}
                      />)
                }
                else if(this.state.type == 'LineMarkSeries') {
                  return (

                      <LineMarkSeries getNull={(d) => d.y !== null}  key={'series-' + this.state.vizdata.indexOf(d)} data={d}
                      onValueMouseOver={ (d, e) => { this.setState({value:d})}}
                      onValueMouseOut={ (d, e) => { this.setState({value:null})}}
                      />

                  )
                }

                }
              )}
              { this.state.vizdata.map( d => {
                  if(this.state.showDataLabels) {
                    return (<LabelSeries key={'series-labels-' + this.state.vizdata.indexOf(d)}
                      data={this.getDataLabels(d)} allowOffsetToBeReversed={false} />)

                  }


                }
              )}
              {value ?
                <Hint value={value}/> :
                null
              }




              <XAxis style={{title: {}}} title={this.state.selectedDimensionOne ? this.state.selectedDimensionOne.label : ''}/>
              <YAxis title={this.state.measures.length > 0 ?this.state.measures[0].label : '' } />
              {
                this.state.vizdata && this.state.vizdata.length > 0  ?
                <LabelSeries data={
                  [
                    //{x:''+this.state.vizdata[0][0].x, y:0, label:this.state.title, style:{fontSize: 20}, yOffset: -(this.props.containerHeight* 0.5) }
                    {x:''+this.state.vizdata[0][0].x, y:0, label:this.state.title, style:{fontSize: 20}, yOffset: -(250) , xOffset: -((this.props.containerWidth/this.state.vizdata[0].length)/2) }
                  ]
                } /> : null

              }

            </XYPlot>



      </Segment>

  )
  }
}

export default MeasureIt()(CubeViz)
//{getWidth: getWidth, getHeight: getHeight}
