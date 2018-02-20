import React from 'react';
import { Button, Dimmer, Image, Loader, Segment, Header, List, Icon, Modal, Label} from 'semantic-ui-react'
import { Checkbox, Form , Dropdown, Input, Card, Grid, Item} from 'semantic-ui-react'
var State = require('../../../freezer')


export default class FilterLabels extends React.Component {
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

  getGroupLabels = (filter) => {
    var groups = _.filter(State.get().filters[filter], {type: 'group'});
    var filtergroups = _.filter(State.get().filters[filter], {type: 'filtergroup'});
    if(!groups)
      groups = [];
    if(!filtergroups)
      filtergroups = [];

    var all = groups.concat(filtergroups);

    return all.map( (o) => {
      return (
        <Label color={this.getColor(filter)} key={o.uri}>{o.label}</Label>
      )
    })
  }
  getFilterLabels = (filter) => {
    var filters = _.filter(State.get().filters[filter], {type: 'filter'});
    var filtergroups = _.filter(State.get().filters[filter], {type: 'filtergroup'});
    if(!filters)
      filters = [];
    if(!filtergroups)
      filtergroups = [];

    var all = filters.concat(filtergroups);

    if(all.length > 0) {
      return all.map( (o) => {
        return (
          <Label color={this.getColor(filter)} key={o.uri}>{o.label}</Label>
        )
      })
    }
    else {
      if(State.get().filters['no'+filter] == 1) {
        return (
          <Label color={this.getColor(filter)}>No {filter}</Label>
        )
      }
      else if(State.get().filters['no'+filter] == 2) {
        return (
          <Label color={this.getColor(filter)}>Any or no value</Label>
        )
      }
      else if(State.get().filters['no'+filter] == 3) {
        return (
          <Label color={this.getColor(filter)}>Some {filter}</Label>
        )
      }

      else {
        return (
          <Label color={this.getColor(filter)}>Any or no value</Label>
        )

      }

    }
  }


  render = () => {
    return (
      <Grid>
      <Grid.Row>
        <Grid.Column width={8}>
          <Header as='h3'>Filters</Header>
          <Label.Group>

            {this.getFilterLabels('corpus')}
            {this.getFilterLabels('expression')}
            {this.getFilterLabels('genre')}
            {this.getFilterLabels('function')}
            <Label color='black'>Some time period</Label>
          </Label.Group>
        </Grid.Column>
        <Grid.Column width={8}>
          <Header as='h3'>Groups</Header>
          <Label.Group>
            {this.getGroupLabels('corpus')}
            {this.getGroupLabels('expression')}
            {this.getGroupLabels('genre')}
            {this.getGroupLabels('function')}
            <Label color='black'>Some time period</Label>
          </Label.Group>
        </Grid.Column>
      </Grid.Row>
    </Grid>
    )
  }
}
