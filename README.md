# Concept-Topography: Spatial + Network visualization of lexicographic data sets
This prototype proposes a web-based interactive exploration of the DBOE collection based on previous work by other authors. It combines a custom ElasticSearch TEI ingestion pipeline with data visualization techniques, offering a thematic map of the historical sources in the collection and a network visualization showing the number of coincident terms between questions in questionnaires of the current result data set. These two, along with the text search capabilities of the prototype, allow for a fast and accurate navigation of the dataset. The frontend views were built with React + D3. The ingestion pipeline was coded in python. 


## Introduction
The prototype is related to the **ExploreAT!** Project of the [Center for Digital Humanities at the Austrian Academy of  Sciences](http://www.oeaw.ac.at/acdh/).
This project aims to reveal unique insights into the rich texture of the German Language, especially in Austria, by providing state of the art tools for exploring the unique collection (1911-1998) of the Bavarian Dialects in the region of the Austro-Hungarian Empire. This corpus is large and rich, estimated to contain 200,000 headwords in estimated 4 Million records. The collection includes a five-volume dictionary of about 50,000 headwords, covering a period from the beginning of German language until the present (DBÖ, WBÖ).

This work has generated some publications that can be found [here](https://exploreat.usal.es/our-publications)

**Please note the data necessary to run this project is currently owned by the [Center for Digital Humanities at the Austrian Academy of  Sciences](http://www.oeaw.ac.at/acdh/) and it is not in the public domain yet. Please contact the center in case you are interested in using the data.**


## Running 
Clone the repository and run `start.sh --build` to initialize the Docker environment where the project runs.
Make sure you put the DBOE MySQL dump and DBOE TEI files in the relevant folders (see beginning of `start.sh`). 
In subsequent runs the `--build` can be omitted.