import unittest
from unittest.mock import patch

from app import app,db
from models.post import Post
from datetime import datetime

from components.posts_collector.DataCollectorClass import DataCollector

class TestDataCollector(unittest.TestCase):
    
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