Install:

What is required for installation: Python 3.11, Docker, docker-compose.

1. docker-compose up -d --build
2. docker-compose run app python3 manage.py createsuperuser

Scrapy settings:
	1. 127.0.0.1/admin - Log in using the details you entered from docker-compose run app python3 manage.py createsuperuser.

	2. Open url: http://127.0.0.1/admin/tpb
		TPB scrapper settings:
			+ "Start page" and "End page" please indicate 1 and 1.
			+ Allowed domains: thepirate-bay.org, www.pirate-bay.net, tpb.party
			+ Start url parse: https://tpb.party/browse, https://tpb.party/top
			+ Set the checkbox taimer to enabled.
			+ Specify time.
			+ Click save button. Refresh the page to make sure the data has been recorded. (Repeat if data is not recorded)
			+ When you click on start, the parser will start.

	3. Open url: http://127.0.0.1/admin/eztv
		EZTV scrapper settings:
			+ "Limit" and "Offset" please indicate 10 and 10.
			+ Parse url: https://eztvx.to
			+ Allowed url: eztvx.to
			+ Set the checkbox taimer to enabled.
			+ Specify time.
			+ Click save button. Refresh the page to make sure the data has been recorded. (Repeat if data is not recorded)
			+ When you click on start, the parser will start.

	4. Open url: http://127.0.0.1/admin/yts
		YTS scrapper settings:
			+ "Limit" and "Offset" please indicate 10 and 10.
			+ Parse url: https://yts.torrentz3.org/
			+ Allowed url: yts.torrentz3.org
			+ Set the checkbox taimer to enabled.
			+ Specify time.
			+ Click save button. Refresh the page to make sure the data has been recorded. (Repeat if data is not recorded)
			+ When you click on start, the parser will start.

Endpoints:
	* http://127.0.0.1/admindjango/ - Superuser admin panel.
	* http://127.0.0.1/admin/ - Admin control panel BLS.
	* http://127.0.0.1/admin/list - List torrents
	* http://127.0.0.1/admin/torr_delete - Torrents delete
	* http://127.0.0.1/admin/list_comments - List comments and delete comments
	* http://127.0.0.1/admin/adult_filter - Adult filter
	* http://127.0.0.1/admin/tpb - TPB scrapy settings
	* http://127.0.0.1/admin/backup - Backup Mongo and Postgres
	* http://127.0.0.1/trackers/ - Trackers list XML
	* http://127.0.0.1/admin/eztv - EZTV scrapy settings
	* http://127.0.0.1/admin/yts - YTS scrapy settings

			
Api endpoints:

1. Method POST endpoint: http://127.0.0.1/api/token/
	- Authorization, obtaining access token Bearer. 
	* from-data: 	{
			  username: "the user you specified in the superuser admin panel"
			  password: "password you specified in the superuser admin panel"
			}

2. Method POST endpoint: http://127.0.0.1/api/token/refresh
	- Token refresh.
	
3. Method GET endpoint: http://127.0.0.1/api/list/
	- Working with torrent recordings.
	* Params:
		+ offset|limit - output number of records (default 15).
		+ title - search for a record by title (pass the title of the torrent here, or part of it). Example: title="Warcraft III Reign of Chaos"
		+ category  - filter by category (Insert category name here). Example: category="Games"
		+ is_verified - filter by risk (pass true/false). Example: is_verified="true/false"
		+ adult - filter by 18+ (pass true/false). Example: adult="true/false"
		+ sort_seeds - sort by seeds (pass up/down). Example: sort_seeds="up/down"
		+ sort_peers - sort by peers (pass up/down). Example: sort_peers="up/down"
		+ sort_date - sort by date (pass up/down). Example: sort_date="up/date"
		+ sort_title - sort by title (pass up/down). Example: sort_title="up/date"
		+ spacing - select the number of records by interval (pass parameters: 24h, 1w, 1y). Example: spacing="24h/1w/1y".

4. Method POST endpoint: http://127.0.0.1/api/comment/
	- Post a comment.
	* form-data:	{
				name: "Name user" (type String)
				email: "Email" (type String)
				data-comment: "%Y-%M-%D %h:%m:%s" (type String)
				comments: "text comments" (type String)
				id_torrent: "id torrent recording" (type String)
				audio: "" (type String)
				video: "" (type String)
			}
5. Method GET endpoint: http://127.0.0.1/api/comment/
	- GET a comment.
	* Params:
		+ id_torrent: "id torrent" (type String)



6. Method GET endpoint: http://127.0.0.1/api/list/serials/
	- GET a serials.
	* Params:
		+ imdb_id: "imdb_id serials" (type String)
		+ season: "Number season" (type Int)

7. Method GET endpoint: http://127.0.0.1/api/list/share/
	- GET list share torrent.
	* Params:
	+ offset|limit - output number of records (default 15).
	+ torrent_id - id torrents

<br>

![Image alt](https://github.com/sos-puhaev/django-drf-scrapy-postgres-mongo/blob/main/image1.png)

![Image alt](https://github.com/sos-puhaev/django-drf-scrapy-postgres-mongo/blob/main/image2.png)

![Image alt](https://github.com/sos-puhaev/django-drf-scrapy-postgres-mongo/blob/main/image3.png)

![Image alt](https://github.com/sos-puhaev/django-drf-scrapy-postgres-mongo/blob/main/image4.png)

![Image alt](https://github.com/sos-puhaev/django-drf-scrapy-postgres-mongo/blob/main/image5.png)

![Image alt](https://github.com/sos-puhaev/django-drf-scrapy-postgres-mongo/blob/main/image6.png)


























