from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
import psycopg2
import docker
from ...management.db_connects import ConnectionDb

class YtsTorrent(LoginRequiredMixin, TemplateView):
    template_name = 'admin/dashboard/yts_torrent.html'
    login_url = 'admin/'

    def __init__(self):
        self.connection_db = ConnectionDb()

    def get_context_data(self, **kwargs):

        limitPage = self.request.GET.get('limitPage')
        offsetPage = self.request.GET.get('offsetPage')
        urlParse = self.request.GET.get('urlParse')
        allowedParse = self.request.GET.get('allowedParse')
        timer = self.request.GET.get('timer')
        timer_working = self.request.GET.get('timer_working')
        start_scrapy = self.request.GET.get('flag')

        yts_status = self.yts_status()

        if start_scrapy == 'start':
            self.run_spider()

        if all([limitPage, offsetPage, urlParse, allowedParse, timer, timer_working]):
            self.saved_settings(limitPage, offsetPage, urlParse, allowedParse, timer, timer_working)


        default_result = self.show_settings()

        yts_context = super().get_context_data(**kwargs)
        yts_context['yts_page'] = default_result
        yts_context['yts_status'] = yts_status

        return yts_context

    def run_spider(self):
        client = docker.from_env()
        project_path = 'bls_scrapy'
        image_name = 'bls_scrapy'
        command = 'scrapy crawl yts_torrent'
        self.yts_set_status(1)

        try:
            container = client.containers.get('bls_scrapy')
            if container.status != 'running':
                container.start()
        except docker.errors.NotFound:
            container = client.containers.run(
                image=image_name,
                volumes={project_path: {
                    'bind': '/app/bls_scrapy', 'mode': 'rw'
                    },
                    '/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'}},
                working_dir='/app/bls_scrapy',
                command=command,
                detach=True,
            )

        if container.status == 'running':
            exec_result = container.exec_run(command)
            container_output = exec_result.output.decode('utf-8')
            print(container_output)
            self.yts_set_status(0)
        else:
            print(f"Container '{container.name}' is not running.")

    def yts_set_status(self, status_num):
        try:
            self.connection_db.connect_pg()
            cursor = self.connection_db.cursor

            cursor.execute("UPDATE yts_status SET status = %s WHERE id = %s;", (status_num, 1))
            self.connection_db.connection.commit()

            cursor.close()
            self.connection_db.connection.close()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def yts_status(self):
        try:
            self.connection_db.connect_pg()
            cursor = self.connection_db.cursor
            cursor.execute("SELECT * FROM yts_status;")
            existing_data = cursor.fetchone()

            cursor.close()
            self.connection_db.connection.close()

            if existing_data:
                return existing_data[1]
            else:
                self.connection_db.connect_pg()
                cursor = self.connection_db.cursor
                cursor.execute("INSERT INTO yts_status (status) VALUES (0) RETURNING status;")
                new_status = cursor.fetchone()[0]
                self.connection_db.connection.commit()
                cursor.close()
                self.connection_db.connection.close()
            
                return new_status

        except Exception as e:
            print(f"Error: {e}")
            return []


    def show_settings(self):
        try:
            self.connection_db.connect_pg()
            cursor = self.connection_db.cursor

            cursor.execute("SELECT * FROM settings_yts WHERE name = 'yts_torrent';")
            existing_data = cursor.fetchone()


            cursor.close()
            self.connection_db.connection.close()
            return existing_data
        except Exception as e:
            print(f"Error: {e}")
            return []

    def saved_settings(self, limitPage, offsetPage, urlParse, allowedParse, timer, timer_working):
        result = False
        try:
            self.connection_db.connect_pg()
            cursor = self.connection_db.cursor

            cursor.execute("SELECT * FROM settings_yts WHERE name = 'yts_torrent';")
            existing_data = cursor.fetchone()

            if existing_data:
                update_query = f"UPDATE settings_yts SET \"limit\" = %s, \"offset\" = %s, url_parse = %s, allowed_domains = %s, timer = %s, auto_scraper = %s WHERE name = 'yts_torrent';"
                cursor.execute(update_query, (limitPage, offsetPage, urlParse, allowedParse, timer, timer_working))
                result = True
            else:
                insert_query = f"INSERT INTO settings_yts (\"limit\", \"offset\", url_parse, allowed_domains, timer, name, auto_scraper) VALUES (%s, %s, %s, %s, %s, %s, %s);"
                cursor.execute(insert_query, (str(limitPage), str(offsetPage), str(urlParse), str(allowedParse), str(timer), 'yts_torrent', str(timer_working)))
                result = True

            self.connection_db.connection.commit()

            cursor.close()
            self.connection_db.connection.close()
            return result

        except Exception as e:
            print(f"Error: {e}")
            return []

    def cron_yts_start(self):
        cursor = self.show_settings()
        if int(cursor[7]) == 0:
            print("-=-=-=-=-= Timer YTS Off =-=-=-=-=-")
        else:
            print("-=-=-=-=-= Cron task YTS_TORRENT start =-=-=-=-=-")
            self.run_spider()