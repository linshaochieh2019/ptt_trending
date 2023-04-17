import unittest
import requests
from datetime import datetime, date

from app import app,db
from models.models import Post

from components.posts_collector.DataCollectorClass import DataCollector

class TestDataCollector(unittest.TestCase):
    
    def setUp(self):
        self.data_collector = DataCollector()
        
    def test_get_ptt_session(self):
        self.assertIsInstance(self.data_collector.session, requests.Session)
        self.assertEqual(self.data_collector.session.cookies['over18'], '1')

    def test_get_latests_page_num(self):
        latest_page_num = self.data_collector.get_lastest_page_num('NBA')
        self.assertIsInstance(latest_page_num, int)
        self.assertGreater(latest_page_num, 6000)
        
    def test_retrieve_ptt_html(self):
        html = self.data_collector.retrieve_ptt_html('NBA', 1)
        self.assertIn('NBA', html)

    def test_get_post_urls(self):
        html = self.data_collector.retrieve_ptt_html('NBA', 1)
        post_urls = self.data_collector.get_post_urls(html)
        self.assertIsInstance(post_urls, list)
        self.assertGreater(len(post_urls), 1)

    def test_get_posts(self):
        html = self.data_collector.retrieve_ptt_html('NBA', 1)
        post_urls = self.data_collector.get_post_urls(html)
        posts = self.data_collector.get_posts(post_urls)
        self.assertIsInstance(posts, list)

        post = posts[-1]
        self.assertIsInstance(post['title'], str)
        self.assertIsInstance(post['author'], str)
        self.assertIsInstance(post['created'], date)
        
    def test_save_posts(self):
        with app.app_context():
            post = {
                'title': 'test title',
                'author': 'test author',
                'created': datetime.strptime('2022-04-10 12:34:56', '%Y-%m-%d %H:%M:%S'),
                'content': 'test content',
                'board': 'test_board'
            }
            collector = DataCollector()
            collector.posts = [post]
            collector.save_posts()
            saved_post = Post.query.filter_by(title=post['title'], author=post['author'], created=post['created']).first()
            self.assertIsNotNone(saved_post)
            self.assertEqual(saved_post.title, post['title'])
            self.assertEqual(saved_post.author, post['author'])
            self.assertEqual(saved_post.created, post['created'])
            self.assertEqual(saved_post.content, post['content'])
            self.assertEqual(saved_post.board, post['board'])

    def test_not_saving_duplicated_posts(self):
        with app.app_context():
            post = {
                'title': 'test title',
                'author': 'test author',
                'created': datetime.strptime('2022-04-10 12:34:56', '%Y-%m-%d %H:%M:%S'),
                'content': 'test content',
                'board': 'test_board'
            }
            collector = DataCollector()
            collector.posts = [post]
            collector.save_posts()
            num_saved_post = Post.query.filter_by(board='test_board').count()
            self.assertEqual(num_saved_post, 1)

    def tearDown(self):
        with app.app_context():
            Post.query.filter_by(board='test_board').delete()
            db.session.commit()

if __name__ == '__main__':
    unittest.main()