import React from 'react';
import { Button, Dimmer, Image, Loader, Segment, Header, List, Icon} from 'semantic-ui-react'
import CubeViz from './components/LADACubeViz'
import request from 'superagent'

import FilterLabels from './components/FilterLabels'

var State = require('../../freezer')


var styles = {

}
export default class Visualize extends React.Component {
  constructor(props) {
    super(props);

    // generate data structure description based on filters
    if(State.get().reload.visualize) {
      State.get().set({'working': true, 'workingMessage': 'Generating normalized observations'});

      console.log('filters***');
      console.log(State.get().filters);
      State.get().reload.set('visualize', false);
      const defPost = request.post('http://localhost:4001/obs/norm/defs');
      defPost.send(State.get().filters);
      defPost.then( (err, res) => {
        console.log('def done');

        const obsPost = request.post('http://localhost:4001/obs/norm2');
        obsPost.send(State.get().clusteredObs);
        obsPost.end( (err, res) => {
          console.log('obs done');
          State.get().set({'working': false});
        });
      })
    }
  }

  handleConfChange = (id, data, prop = null, value = null) => {
    console.log('new confs');
    console.log(data);
    if(prop && value) {
      data[prop] = value;
    }
    data['modalVisible'] = false;
    State.get().vis.set(id, data);

  }

  addVis = () => {
    var id = '' + Math.random();
    //var _vis = State.get().vis;
    console.log(State.get());
    State.get().vis.set(id, null);
  }

  removeVis = (key) => {
    console.log('remove');
    State.get().vis.remove(key).now();
  }



  getVis = () => {
    const styles = {
      cube: {
        width: '100%',
        height: '400px'

      },
      button: {
        marginTop: '20px'
      }
    };
    var c = [];
    for( var key in State.get().vis) {
      var v = State.get().vis[key];
      console.log(v);
      c.unshift(
        (        <Segment key={key} id={key} >
                  <CubeViz onConfChange={this.handleConfChange.bind(this)} conf={v} endpoint="http://localhost:4001/" id={key} height={800}/>
                  <Button style={styles.button} onClick={this.removeVis.bind(this, key)} >Remove graph</Button>
                </Segment>
        )
      )
    }
    return c;

  }

  render() {
    console.log('render');
    return (
    <Segment basic>
      <Segment basic>
        <Header as='h1'>
          Visualize
        </Header>

        <FilterLabels />
        <Segment basic className='noindent' >
          <Button onClick={this.addVis}>Add new graph</Button>
          {this.getVis()}
        </Segment>

      </Segment>
    </Segment>
    );
  }

}
