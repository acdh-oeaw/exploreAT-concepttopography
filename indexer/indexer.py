import os
import fnmatch
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from bs4 import BeautifulSoup
import pymysql
import json
import re

db_cur = None

def process_listplace_node(index_soup, listplace_node):
	results = {}
	for place in listplace_node.find_all("place", recursive=False):
		results.update(process_place_node(index_soup, place))
	return results

def process_place_node(index_soup, place_node):
	result = {}

	place_type = place_node.attrs['type']
	listplace_node = place_node.find("listPlace", recursive=False)

	if listplace_node:
		result.update(process_listplace_node(index_soup, listplace_node))

	mysql_id = None
	#print(place_node.placeName.string, place_type)
	
	for entry in index_soup.find_all('placeName', text=place_node.placeName.string):
		if entry.parent.get("type") == place_type and entry.parent.mysql_id:
			mysql_id = entry.parent.mysql_id.string
			if mysql_id:
				result.update({place_type.lower() : mysql_id})
				if place_type == 'Ort':
					result.update({'placeName': place_node.placeName.string})
					point = extract_geo_point(mysql_id)
					if point:
						result.update({'location' : point})
			break
	
	return result

def extract_geo_point(mysql_id):
	point = None
	query = "SELECT ST_AsGeoJSON(dboe_1.GISort.the_geom) AS geom FROM dboe_1.GISort INNER JOIN dboe_1.ort WHERE dboe_1.ort.id='{}'".format(mysql_id)
	number_of_rows = db_cur.execute(query)

	if number_of_rows > 0:
		point = db_cur.fetchone()['geom']
		point_obj = json.loads(point)
		return {'lat': point_obj['coordinates'][1], 'lon': point_obj['coordinates'][0]}
	else: return None

def main():
	print("Connecting to ES...")
	es = Elasticsearch(hosts=[{"host":'elasticsearch'}])
	if not es.ping():
		raise ValueError("Connection failed")
	else:
		print('Connected to ES')

	print("Connecting to MySQL...")
	conn= pymysql.connect(host='conceptlights_db_1',user='root',password='password',db='dboe_1',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
	if conn.open:
		print('Connected to MySQL')
	else:
		print('Connection to MySQL failed')

	if es.indices.exists(index='dboe'):
		print('dboe index exists, deleting...')
		if es.indices.delete(index='dboe'):
			print('dboe index deleted, will reindex now.')

	body = {
				"settings" : {
					"number_of_shards": 1,
					"number_of_replicas": 0
				},
				"mappings": {
					"dboe-type": {
							"properties": {
								"location" : {
									"type" : "geo_point"
						}
					}
				}
			}}

	es.indices.create( index='dboe', ignore=400, body=body )

	global db_cur
	db_cur = conn.cursor()
	actions = []

	rootPath = './data'
	pattern = 'r*.xml' #WIP: Test only with entries starting with 'r' for the moment
	listplace_file = './data/helper_tables/listPlace-id.xml'

	with open(listplace_file, "r", encoding="utf-8") as list_place_file:
		index_soup = BeautifulSoup(list_place_file, 'xml')

		#Walk data dir extracting the different entries
		for root, dirs, files in os.walk(rootPath):
			for filename in fnmatch.filter(files, pattern):
				print(os.path.join(root, filename))
				soup = BeautifulSoup(open(os.path.join(root, filename), "r", encoding="utf-8"), 'xml')
				for entry in soup.find_all("entry"):
					entry_obj= {}

					questionnaire = entry.findAll(
										"ref", {"type": "fragebogenNummer"})
					if len(questionnaire) > 0:
						entry_obj['questionnaire'] = questionnaire[0].string
					else:
						continue
					
					entry_obj['main_lemma'] = str(entry.form.orth.string)
					if len(entry_obj['main_lemma']) == 0:
						continue

					entry_obj['id'] = entry['xml:id']
					#part of speech
					entry_obj['pos'] = str(entry.gramGrp.pos.string)
					
					if entry.sense:
						entry_obj['sense'] = entry.sense.text.replace('\n', '')

					if entry.note:
						entry_obj['note'] = entry.note.text.replace('\n', '')

					source = entry.findAll(
										"ref", {"type": "quelle"})
					if len(source) > 0:
						entry_obj['source'] = source[0].string

					revised_source = entry.findAll(
										"ref", {"type": "quelleBearbeitet"})
					if len(revised_source) > 0:
						entry_obj['revised_source'] = revised_source[0].text


					usg = entry.find('usg')
					if not usg:
						continue
					else:
						list_place = usg.find("listPlace", recursive=False)
						if not list_place:
							continue
						else:
							geo_dict = process_listplace_node(index_soup, list_place)
							entry_obj.update(geo_dict)		
					
					print(entry_obj)
					actions.append({
							'_index': 'dboe',
							'_type': 'dboe-type',
							'_source': entry_obj})

					if len(actions) > 50:
						bulk(es, actions)
						actions = []
		print('Done')

	conn.close()
	exit(0)

if __name__ == "__main__":
	main()

