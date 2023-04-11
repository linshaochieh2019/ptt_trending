import unittest
import requests

class TestIntegration(unittest.TestCase):

    def test_index(self):
        response = requests.get('http://localhost:5000/')
        self.assertEqual(response.status_code, 200)

    def test_form_submission(self):
        with requests.Session() as session:
            response = session.get('http://localhost:5000/posts')
            self.assertEqual(response.status_code, 200)

            form_data = {'board': 'Gossiping', 'num_pages': 1}
            response = session.post('http://localhost:5000/posts', data=form_data)
            self.assertEqual(response.status_code, 200)
            self.assertIn('<div class="post">', response.text) # check if there's at least one post content
