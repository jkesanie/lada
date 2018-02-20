import React from 'react';
import { Route, IndexRoute } from 'react-router';

import App from './modules/app/App';
import Select from './modules/app/Select';
import Filter from './modules/app/Filter';
import Review from './modules/app/Review';
import Normalize from './modules/app/Normalize';
import Visualize from './modules/app/Visualize';

var routes = (
	<Route path="/" component={ App } >
		<IndexRoute component={ Select } />
    <Route path="/select" component={ Select } />
    <Route path="/filter" component={ Filter } />
    <Route path="/review" component={ Review } />
		<Route path="/normalize" component={ Normalize } />
    <Route path="/visualize" component={ Visualize } />
  </Route>
);

export default routes;
