import os
import unittest
import requests

app_url = os.environ.get('APP_URL')

class TestIntegration(unittest.TestCase):

    def test_index(self):
        response = requests.get(f'{app_url}/')
        self.assertEqual(response.status_code, 200)

    def test_form_submission(self):
        with requests.Session() as session:
            response = session.get(f'{app_url}/posts')
            self.assertEqual(response.status_code, 200)

            form_data = {'board': 'Gossiping', 'num_pages': 1}
            response = session.post(f'{app_url}/posts', data=form_data)
            self.assertEqual(response.status_code, 200)
            self.assertIn('<div class="post">', response.text) # check if there's at least one post content
