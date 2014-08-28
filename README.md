README

The jpod101_loader.py script is intended to download all the japanese language lessons of http://www.japanesepod101.com.<br />
It is therefore necessary to create a trail account to get credentials which are used by the script.

REQUIREMENTS

jpod101_loader.py is written in Python 3.3.4.
It requires the external packages	
	- BeautifulSoup
	- requests

USAGE

The script knows three command line arguments which are all mandatory:
	jpod101_loader.py -u username - p password [-d download_path] [-h] [--help]
