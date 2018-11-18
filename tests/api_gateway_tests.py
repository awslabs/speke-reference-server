#!/usr/bin/env python

# Apache License
# Version 2.0, January 2004
# http://www.apache.org/licenses/

import base64
import unittest
import xml.etree.ElementTree as element_tree
import requests
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth

# UPDATE THIS CONSTANT TO MATCH YOUR CONFIGURATION

# API_HOST = "lz9w9a2g89.execute-api.us-east-1.amazonaws.com"
API_HOST = "f8aix0vkl5.execute-api.us-east-1.amazonaws.com"

# static testing values and endpoints
API_ENDPOINT = "https://{}/EkeStage".format(API_HOST)
SERVER_API_BODY_FILE = "server_api_body.xml"
API_HEADERS = {"Host": API_HOST, "Content-Type": "application/xml", "Accept": "application/xml"}
SERVER_API = "{}/copyProtection".format(API_ENDPOINT)
CLIENT_API = "{}/client/5E99137A-BD6C-4ECC-A24D-A3EE04B4E011/e2201617-57c2-4d9b-adc5-cd87b7c01944".format(API_ENDPOINT)

# keys expected from above test data
EXPECTED_SERVER_KEY = b'\x00\xbc\xcf\xd5\xa3\x93&\xfc\xdf\xaa\x0fH\xd7i6W'
EXPECTED_CLIENT_KEY = b':t\x81m\xad5u\x87\xb7\x9c\x97q\xec\x07\xb0S'


class TestSPEKEGateway(unittest.TestCase):
    """
    This class is responsible for testing the SPEKE API gateway.
    """

    def test_server(self):
        """
        This method tests the server REST API.
        """
        # read the XML document used by the server
        xml_file = open(SERVER_API_BODY_FILE, 'r')
        xml = xml_file.read()
        xml_file.close()
        # create a signature for the call
        auth = BotoAWSRequestsAuth(aws_host=API_HOST, aws_region='us-east-1', aws_service='execute-api')
        # call the api
        response = requests.post(SERVER_API, headers=API_HEADERS, data=xml, auth=auth)
        # get the XML response
        root_element = element_tree.fromstring(response.text)
        # check the key
        key = root_element.find(".//{urn:ietf:params:xml:ns:keyprov:pskc}PlainValue")
        self.assertEqual(EXPECTED_SERVER_KEY, base64.b64decode(key.text))

    def test_client(self):
        """
        This method tests the client REST API.
        """
        # send the request as a client
        response = requests.get(CLIENT_API, headers=API_HEADERS)
        # check the key response
        self.assertEqual(EXPECTED_CLIENT_KEY, response.content)


if __name__ == '__main__':
    unittest.main(verbosity=2)
