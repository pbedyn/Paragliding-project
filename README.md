The project has several modules:
1. xcontest_extraction.py - data scraping module (currently it is able to scrape tracks from xcportal and xcontest sites)
2. xcportal_extraction.py - data scraping module from xcportal
3. new_batch_to_grid.py - takes scraped files from New Batch folder and distributes them to grids
4. data_preparation.py - data preparation module (loads tracks and prepares a pandas dataframe with relevant information for mining)
5. func_track_manipulation.py - various functions for data manipulation and calculations
6. data_processing.py - creates a numpy array with lift within each grid
7. data_to_kml.py - takes numpy arrays and creates kml files for a given location
