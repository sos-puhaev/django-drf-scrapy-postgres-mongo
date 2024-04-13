from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_xml.renderers import XMLRenderer
from rest_framework.renderers import BaseRenderer
import requests
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
import xml.dom.minidom

class NoRootElementXMLRenderer(BaseRenderer):
    media_type = 'application/xml'
    format = 'xml'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

class XMLView(APIView):
    renderer_classes = [NoRootElementXMLRenderer]
    permission_classes = [AllowAny]

    def get(self, request):
        trackers_url = 'https://cf.trackerslist.com/best.txt'

        response = requests.get(trackers_url)

        if response.status_code == 200:
            trackers_list = response.text.split('\n')

            root_element = Element('trackers_list')

            trackers_element = SubElement(root_element, 'trackers')

            for tracker in trackers_list:
                if tracker.strip():
                    item_element = SubElement(trackers_element, 'item')
                    tracker_name_element = SubElement(item_element, 'tracker_name')
                    tracker_name_element.text = tracker

            xml_data = xml.dom.minidom.parseString(tostring(root_element)).toprettyxml(indent="    ")

            xml_data = xml_data.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')

            tree = ElementTree(root_element)
            root_element = tree.getroot()
            root_element.tag = 'trackers_list'

            xml_data = xml.dom.minidom.parseString(tostring(root_element)).toprettyxml(indent="    ")

            return Response(xml_data, content_type='application/xml')

        return Response({'error': 'Failed to fetch data from the API'}, status=response.status_code)