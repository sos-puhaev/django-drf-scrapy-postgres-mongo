# docker-django-drf(jwt)-nginx-scrapy-cron
Full Admin panel project: Docker, Django, Nginx, DRF(JWT), Scrapy, Cron.

<h1>Install:</h1>
What is required for installation: Python 3.11, Docker.

1. docker-compose up -d --build<br>
2. docker-compose run app python3 manage.py makemigrations<br>
3. docker-compose run app python3 manage.py migrate<br>
docker-compose run app python3 manage.py createsuperuser<br>
4. docker exec -it mongo bash<br>
5. In bash mongo run the command: mongo<br>
6. db.createUser({user: "admin", pwd: "password", roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]})
This is how you create an administrator in Mongo.<br>
7. After creating the administrator, exit the container (exit), restart the docker-compose down / up -d containers, and log back into the mongo container as indicated in step 4. Next, enter the mongo command in the terminal.<br>
8. "use admin" -> db.auth("admin", "password").<br>
9. "use mongo_db" -> db.createUser({user: "jonnijonni", pwd: "abc234Def", roles: [ { role: "readWrite", db: "mongo_db" } ]})
In the files where the connection to mongo is specified (I apologize for not adding all this to the .env file:) ), you can specify your own.<br>
10. Go url: http://127.0.0.1/admin/tpb
TPB scrapper settings: "Start page" and "End page" please indicate 1 and 1.
Allowed domains: "thepirate-bay.org, www.pirate-bay.net, tpb.party"
Start url parse: "https://tpb.party/browse, https://tpb.party/top"
When you click on start, the parser will start.<br>
10. http://127.0.0.1/admin/list there will be records that the scrapper took, they will be stored in mongo.
Go to page 127.0.0.1 there will be all the links.<br>

<h1>Api:</h1>
api/token/ <br>
api/comment/<br>
api/list/<br>

All information is also provided via the API; access via a JWT token is set; to receive it, you need to log in. Using the API you can get: comments, posts, and also perform get requests for filters and sorting posts. It takes too long to write documentation, but if I interested you in my skills, write to telegram: <b>@JonniLoka</b> or email: <b>faceblog22@gmail.com</b>.
<br>
<h1>Screens</h1>
<br>

![Image alt](https://github.com/sos-puhaev/django-drf-scrapy-postgres-mongo/blob/main/image1.png)

![Image alt](https://github.com/sos-puhaev/django-drf-scrapy-postgres-mongo/blob/main/image2.png)

![Image alt](https://github.com/sos-puhaev/django-drf-scrapy-postgres-mongo/blob/main/image3.png)

![Image alt](https://github.com/sos-puhaev/django-drf-scrapy-postgres-mongo/blob/main/image4.png)

![Image alt](https://github.com/sos-puhaev/django-drf-scrapy-postgres-mongo/blob/main/image5.png)

![Image alt](https://github.com/sos-puhaev/django-drf-scrapy-postgres-mongo/blob/main/image6.png)
