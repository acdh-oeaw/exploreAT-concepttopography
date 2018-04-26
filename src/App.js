import React, { Component } from 'react';
import { ReactiveBase, SingleList } from '@appbaseio/reactivesearch'
import { ReactiveMap } from '@appbaseio/reactivemaps';

import ReactDOM from "react-dom";

import CountryMap from './CountryMap'

import './App.css'


class App extends Component {

	render() {
		return (
			<ReactiveBase
				app="dboe"
				url="http://localhost:9200"
				type="dboe-type"
				mapKey="AIzaSyAe92NwI94op_5edlU9AH0XzHOP2cSqh6M">
				<div className="row">
					<div className="col">
						<SingleList
							title="Questionnaires"
							componentId="questionnaires"
							dataField="questionnaire.keyword"
							size={50}
							showSearch={true}/>
					</div>
					<div className="col">
						<CountryMap />
					</div>
				</div>
			</ReactiveBase>
		);
	}
}


export default App;