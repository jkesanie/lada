import React from 'react';
import ReactDom from 'react-dom'
import {Router, browserHistory} from 'react-router';
import routes from './routes';

// Include the the reactions in order
// to respond to the state changes.
var _ = require('lodash');

ReactDom.render(
	<Router history={ browserHistory }>{ routes }</Router>,
	document.getElementById('root')
);
