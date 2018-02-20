import React from 'react';
import { Form, Divider, Input, Button, Dimmer, Image, Loader, Segment, Header, List, Icon, Label} from 'semantic-ui-react'
import Dropzone from 'react-dropzone'
import request from 'superagent'

var hash = require('object-hash');
var State = require('../../freezer')


var styles = {
  zone: {
    heigth: 'auto',
    width: '200px',
    borderWidth: '2px',
    borderStyle: 'dashed',
    padding: '10px'
  }
}
export default class Select extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      newPubURI: ''
    };

    this.updatePublications();


  }

  updatePublications = () => {
    const req = request.get('http://localhost:4001/publications');
    req.end((err, res) => {
      console.log(res.body);
      var pubs = res.body;
      State.get().set('publications', pubs);
    });
  }
  sleepFor = ( sleepDuration ) => {
      var now = new Date().getTime();
      while(new Date().getTime() < now + sleepDuration){ /* do nothing */ }
  }
  onDrop = (acceptedFiles, rejectedFiles) => {
      State.get().set('working', true);
      const req = request.post('http://localhost:4001/annotatedFiles');
      acceptedFiles.forEach(file => {
        console.log('file:' + file.name);
        req.attach(file.name, file);
      });
      req.end((err, res) => {
        console.log(res.body);
        State.get().reload.set('filter', true);
        this.updatePublications();
        State.get().set('working',false);
      });
  }

  onRemove = (pub, e, v) => {
    console.log('removing:' + pub.uri);
    const req = request.delete('http://localhost:4001/annotatedFiles?uri=' + encodeURIComponent(pub.uri) + "&file=" + encodeURIComponent(pub.rdfPath));
    req.end((err, res) => {
      console.log('done');
      State.get().reload.set('filter', true);
      this.updatePublications();
    })
  }

  onAddURI = (e, v) => {
    e.preventDefault();
    console.log('adding URI:');

  }

  render() {
    return (
      <Segment basic>
        <Segment basic>
          <Header as='h1'>
            Select
          </Header>

          <Dropzone
            style={styles.zone}
            accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            onDrop={this.onDrop}>
            {({ isDragActive, isDragReject }) => {
              if (isDragActive) {
                return "All files will be accepted";
              }
              if (isDragReject) {
                return "Files must of type Excel spreadsheet!";
              }
              return "Drag and drop annotated Excel files here.";
            }}
          </Dropzone>
          <Divider horizontal>Or</Divider>
          <Form onSubmit={this.onAddURI}>
            <Form.Field>
              <label>Publication URI</label>
              <Input placeholder='' value={this.state.newPubURI}
              onChange={ (event, data) => {
                  this.setState({'newPubURI': data.value})
                }
              } />
            </Form.Field>
            <Button type="submit">Add</Button>
          </Form>


        </Segment>
        <Segment basic>
          <Header as='h2'>
            Included publications
            <Header.Subheader>
              List of publications whose data files have been included in the project
            </Header.Subheader>
          </Header>
          <List relaxed='very' divided verticalAlign='middle'>
            {State.get().publications.map( (pub) => {
              return(
              <List.Item key={pub.uri}>
                <List.Content floated='right'>
                  <Button onClick={this.onRemove.bind(this, pub)}>Remove</Button>
                </List.Content>
                <Icon name='file' />
                <List.Content>
                  <Header as='h3'>
                    {pub.title} <Label as='a' href={pub.uri} target='_blank'>Show in LCD</Label>
                      <Header.Subheader>
                        {pub.authors}, {pub.year}
                      </Header.Subheader>
                  </Header>
                  <List.List>
                    <List.Item>
                     <List.Content>
                       <List.Description><a target="_blank" href={pub.fileURI + '?view'}>{pub.fileURI.substring(pub.fileURI.lastIndexOf('/publication/') + 13)}</a></List.Description>
                     </List.Content>
                   </List.Item>
                  </List.List>
                </List.Content>
              </List.Item>
              )
            })}
          </List>

        </Segment>
      </Segment>
    );
  }

}
