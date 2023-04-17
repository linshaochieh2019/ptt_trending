import os
import unittest
import requests
import json
from app import app


app_url = os.environ.get('APP_URL')
print(f'app_url={app_url}')

class TestIntegration(unittest.TestCase):

    def test_index(self):
        response = requests.get(f'{app_url}/')
        self.assertEqual(response.status_code, 200)

    def test_get_mapping(self):
        # Use test client to make a GET request to /mapping
        with app.test_client() as client:
            response = client.get('/mapping')
            assert response.status_code == 200

            # Convert the JSON response to a dictionary
            mapping = json.loads(response.data)

            # Test that the dictionary has the expected keys
            assert '1' in mapping
            assert '2' in mapping
            assert '3' in mapping

            # Test that the dictionary values are of the expected types
            assert isinstance(mapping['1'], str)
            assert isinstance(mapping['2'], str)
            assert isinstance(mapping['3'], str)

    def test_get_colors(self):
        # Use test client to make a GET request to /colors
        with app.test_client() as client:
            response = client.get('/colors')
            assert response.status_code == 200

            # Convert the JSON response to a dictionary
            colors = json.loads(response.data)

            # Test that the dictionary has the expected keys
            assert 'colors' in colors

            # Test that the 'colors' value is a list with the expected length
            assert isinstance(colors['colors'], list)
            
            # Test that the list elements are of the expected type
            for color in colors['colors']:
                assert isinstance(color, str)
