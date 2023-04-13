import unittest
from unittest.mock import patch
import os
from datetime import datetime

from app import app,db
from models.models import Post, Prediction

from components.posts_collector.DataCollectorClass import DataCollector
from components.posts_analyzer.DataAnalyzerClass import DataAnalyzer


class TestDataAnalyzer(unittest.TestCase):
    
    def setUp(self):
        mapping_file_path = os.path.join(app.instance_path, 'mapping.json')
        self.analyzer = DataAnalyzer(db, mapping_file_path)

    def test_get_mapping(self):
        self.assertIsInstance(self.analyzer.mapping, dict)

    def test_get_posts(self):
        # Create a test post with today's date
        with app.app_context():
            self.analyzer.get_posts()
            self.assertGreaterEqual(len(self.analyzer.posts), 1)

    def tearDown(self):
        with app.app_context():
            Post.query.filter_by(board='test_board').delete()
            db.session.commit()