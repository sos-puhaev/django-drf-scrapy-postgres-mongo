from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
import docker
import yaml
from urllib.parse import parse_qs, unquote
import re
from ...management.db_connects import ConnectionDb

class ListTpb(LoginRequiredMixin, TemplateView):
    template_name = 'admin/dashboard/tpb.html'
    login_url = 'admin/'

    def __init__(self):
        self.connection_db = ConnectionDb()

    def get_context_data(self, **kwargs):

        startPage = self.request.GET.get('startPage')
        endPage = self.request.GET.get('endPage')
        urlParse = self.request.GET.get('urlParse')
        startUrlParse = self.request.GET.get('startUrlParse')
        timer = self.request.GET.get('timer')
        timer_working = self.request.GET.get('timer_working')
        start_scrapy = self.request.GET.get('flag')
        scrapy_category = self.request.GET.get('cat')

        tpb_settings_cat = self.tpb_settings_cat()
        tpb_status = self.tpb_status()

        if scrapy_category:
            query_dict = parse_qs(scrapy_category)
            for key, value in query_dict.items():
                query_dict[key] = [unquote(val) for val in value]

            output_data = {'categories': []}

            for key, value in query_dict.items():
                match = re.match(r'categories\[(\d+)\]\[(\w+)\](\[\])?', key)
                if match:
                    index, field, is_list = match.groups()
                    index = int(index)

                    while len(output_data['categories']) <= index:
                        output_data['categories'].append({'cat': '', 'title': '', 'sub_cat': []})
                    
                    current_category = output_data['categories'][index]

                    if field == 'cat':
                        current_category['cat'] = value[0]
                    elif field == 'title':
                        current_category['title'] = value[0]
                    elif field == 'sub_cat':
                        current_category.setdefault('sub_cat', []).extend(value)


            with open('bls_scrapy/bls_scrapy/conf_spider/tbp.yml', 'w') as file:
                yaml_output = yaml.dump(output_data, default_flow_style=False, indent=2)
                indented_yaml = '\n'.join([
                    '  ' + line if line.strip().startswith('- cat:')
                    else '  ' + line if line.strip().startswith('sub_cat:')
                    else '  ' + line if line.strip().startswith('title:')
                    else '    ' + line if line.strip().startswith('- ') and not line.strip().startswith('- sub_cat:') 
                    else '    ' + line if line.strip().startswith('- sub_cat: ') 
                    else line for line in yaml_output.splitlines()
                    ])
                file.write(indented_yaml)

        if start_scrapy == 'start':
            self.run_spider()

        if all([startPage, endPage, urlParse, startUrlParse, timer, timer_working]):
            self.saved_settings(startPage, endPage, urlParse, startUrlParse, timer, timer_working)
    

        default_result = self.show_settings()

        tpb_context = super().get_context_data(**kwargs)
        tpb_context['tpb_page'] = default_result
        tpb_context['tpb_status'] = tpb_status
        tpb_context['tpb_settings_cat'] = tpb_settings_cat

        return tpb_context
    
    def tpb_settings_cat(self):
        with open('bls_scrapy/bls_scrapy/conf_spider/tbp.yml', 'r') as file:
            data = yaml.safe_load(file)
        return data

    def run_spider(self):
        client = docker.from_env()
        project_path = 'bls_scrapy'
        image_name = 'bls_scrapy'
        command = 'scrapy crawl thepirate_bay'
        self.tpb_set_status(1)

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
            self.tpb_set_status(0)
        else:
            print(f"Container '{container.name}' is not running.")

    def tpb_set_status(self, status_num):
        try:
            self.connection_db.connect_pg()
            cursor = self.connection_db.cursor

            cursor.execute("UPDATE tpb_status SET status = %s WHERE id = %s;", (status_num, 1))
            self.connection_db.connection.commit()

            cursor.close()
            self.connection_db.connection.close()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def tpb_status(self):
        try:
            self.connection_db.connect_pg()
            cursor = self.connection_db.cursor
            cursor.execute("SELECT * FROM tpb_status;")
            existing_data = cursor.fetchone()

            cursor.close()
            self.connection_db.connection.close()

            if existing_data:
                return existing_data[1]
            else:
                self.connection_db.connect_pg()
                cursor = self.connection_db.cursor
                cursor.execute("INSERT INTO tpb_status (status) VALUES (0) RETURNING status;")
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

            cursor.execute("SELECT * FROM settings_tpb WHERE name = 'thepirate_bay';")
            existing_data = cursor.fetchone()

            cursor.close()
            self.connection_db.connection.close()
            return existing_data
        except Exception as e:
            print(f"Error: {e}")
            return []

    def saved_settings(self, startPage, endPage, urlParse, startUrlParse, timer, timer_working):
        result = False
        try:
            self.connection_db.connect_pg()
            cursor = self.connection_db.cursor

            cursor.execute("SELECT * FROM settings_tpb WHERE name = 'thepirate_bay';")
            existing_data = cursor.fetchone()

            if existing_data:
                update_query = f"UPDATE settings_tpb SET start_page = %s, end_page = %s, url_parse = %s, start_url = %s, timer = %s, auto_scraper = %s WHERE name = 'thepirate_bay';"
                cursor.execute(update_query, (startPage, endPage, urlParse, startUrlParse, timer, timer_working))
                result = True
            else:
                insert_query = f"INSERT INTO settings_tpb (start_page, end_page, url_parse, start_url, timer, name, auto_scraper) VALUES (%s, %s, %s, %s, %s, %s, %s);"
                cursor.execute(insert_query, (str(startPage), str(endPage), str(urlParse), str(startUrlParse), str(timer), 'thepirate_bay', str(timer_working)))
                result = True

            self.connection_db.connection.commit()

            cursor.close()
            self.connection_db.connection.close()
            return result

        except Exception as e:
            print(f"Error: {e}")
            return []


    def cron_tpb_start(self):
        cursor = self.show_settings()
        if int(cursor[7]) == 0:
            print("-=-=-=-=-= Timer TPB Off =-=-=-=-=-")
        else:
            print("-=-=-=-=-= Cron task tpb start =-=-=-=-=-")
            self.run_spider()