import React from 'react';
import {Router, Link} from 'react-router';
import freezer from '../../freezer';
import { Dropdown, Sidebar, Menu, Container, Icon, Step} from 'semantic-ui-react';
import { Input, Button, Dimmer, Image, Loader, Segment, Header } from 'semantic-ui-react'
import request from 'superagent'

var hash = require('object-hash');
var State = require('../../freezer')


export default class App extends React.Component {
  constructor( props ){
		super( props );
    /*
    this.state = {
      working: false,
      workingMessage: 'Working'
    }
    */

    // check for existing data in the backend
    /*
    var filters = {};
    var requests = [];

    requests.push(request.get('http://localhost:4001/corpus/groups'));
    requests.push(request.get('http://localhost:4001/expression/groups'));
    requests.push(request.get('http://localhost:4001/genre/groups'));
    requests.push(request.get('http://localhost:4001/function/groups'));
    Promise.all(requests).then( (data) => {
      var filters = {};
      var hashes = {};
      data.map( (res) =>  {
        var key = Object.keys(res.body)[0];
        filters['no' + key] = true;
        var values = res.body[key];
        filters[key] = values;
      });
      hashes['filters'] = hash(filters);
      State.get().set({'filters': filters, hash: hashes});

    })
*/
		this.publishRouter( props );
    request.get('http://localhost:4001/lcd/status').then((res) => {
      console.log(res.body);
      State.get().set('lcdStatus', res.body.status);
    });
  }

  handleFilterClick = (e, data) => {
    var working = !State.get().working;
    if(working) {

    }
    console.log('working: ' + working);
    State.set('working', working);

  }
  toggleTOC = () => {
    var v = State.get().tocVisible;
    State.get().set('tocVisible', !v);
  }

  getTOC = () => {
    var view = this.props.location.pathname;
    console.log(view);
    if(view =='/review' || view == '/normalize') {
      return (
        <Dropdown text='TOC' className='link item'>
            <Dropdown.Menu>
              <Dropdown.Menu scrolling>
                {
                  Object.keys(State.get().filteredObs).map( (key) => {
                    var pub = State.get().filteredObs[key];
                    return (
                      <Dropdown.Item key={pub.pub} as='a' href={'#' + pub.pub}>{pub.title}</Dropdown.Item>
                    )
                  })
                }

              </Dropdown.Menu>
            </Dropdown.Menu>
          </Dropdown>

      )
    }
    else if(view == '/visualize') {
      return (
        <Dropdown text='TOC' className='link item'>
            <Dropdown.Menu>
              <Dropdown.Menu scrolling>
                {
                  Object.keys(State.get().vis).map( (key) => {
                    var v = State.get().vis[key];
                    if(v) {
                      return (
                        <Dropdown.Item key={key} as='a' href={'#' + key}>{v.title}</Dropdown.Item>
                      )
                    }
                  })
                }

              </Dropdown.Menu>
            </Dropdown.Menu>
          </Dropdown>

      )
    }
    else {
      return (
        <Dropdown text='TOC' className='link item'>
            <Dropdown.Menu/>
        </Dropdown>
      )
    }
  }

  isFilterDisabled = () => {
    console.log(State.get().publications.length);
    if(State.get().publications.length > 0) {
      return false;
    }
    return true;

  }


  isVisualizeDisabled = () => {
    if(!State.get().reload.normalize && State.get().filteredObs.length > 0) {
      return false;
    }
    return true;

  }

  render(){
    // Render the updated location accessible to all the components
		Router.location = this.props.location;
    const { working, workingMessage } = State.get();
    return (
      <div>



        <Menu fixed='top' inverted compact className={'squared'}>
          {this.getTOC()}

          <Menu.Item name='Select'><Link to='/select'>Select</Link></Menu.Item>
          <Menu.Item name='Filter' disabled={this.isFilterDisabled()}><Link to='/filter'>Filter &amp; Group</Link></Menu.Item>
          <Menu.Item name='Review'><Link to='/review'>Review</Link></Menu.Item>
          <Menu.Item name='Normalize' ><Link to='/normalize'>Normalize</Link></Menu.Item>
          <Menu.Item name='Visualize' disabled={this.isVisualizeDisabled()} ><Link to='/visualize'>Visualize</Link></Menu.Item>

          <Menu.Menu position='right'>
            <Menu.Item header>LADA</Menu.Item>
            <Menu.Item active color={State.get().lcdStatus === 'online' ? 'green' : 'red'}>LCD {State.get().lcdStatus}</Menu.Item>
            <Dropdown item icon="setting">
              <Dropdown.Menu>
                  <Dropdown.Item >Import...</Dropdown.Item>
                  <Dropdown.Item >Export...</Dropdown.Item>
                  <Dropdown.Item >Settings...</Dropdown.Item>
              </Dropdown.Menu>
            </Dropdown>

          </Menu.Menu>



        </Menu>
        <Dimmer.Dimmable as={Segment} basic dimmed={working} className='content' >
          <Dimmer active={working} inverted>
            <Loader>{workingMessage}</Loader>
          </Dimmer>


              { React.cloneElement(this.props.children, {store: freezer.get()}) }
        </Dimmer.Dimmable>
      </div>

    );
  }

  componentDidMount(){
    freezer.on('update', () => this.forceUpdate() );
  }

  /**
   * Makes the current location, history and routes accessible
   * from the Router object.
   */
	publishRouter( props ){
		var routes = {};

		// Render the router accessible without contexts
		Router.history = props.history;
		Router.location = props.location;
    Router.routes = routes;

    // Use route names as constants
    if( props.routes[0].childRoutes ){
  		props.routes[0].childRoutes.forEach( function( r ){
  			var pathName = r.path[0] === '/' ? r.path.slice(1) : r.path;
  			routes[ pathName ] = r.path;
  		});
    }

		routes.home = '/';
		routes.notfound = '*';
	}
}
