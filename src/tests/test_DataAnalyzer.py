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
        with app.app_context():
            mapping_file_path = os.path.join(app.instance_path, 'mapping.json')
            self.analyzer = DataAnalyzer(db, mapping_file_path)
            self.analyzer.posts = [
                (
                    987654321, #post_id, 
                    'This is just a test content' #post_content
                )
            ]
            self.assertEqual(self.analyzer.db, db)
            self.assertEqual(self.analyzer.mapping_file_path, mapping_file_path)
            self.assertEqual(len(self.analyzer.posts), 1)

    def tearDown(self):
        with app.app_context():
            Prediction.query.filter_by(id=987654321).delete()
            db.session.commit()

    def test_classify(self):
        with app.app_context():
            self.analyzer.classifiy()
            self.assertEqual(len(self.analyzer.categorized_data), 1)
            prediction = self.analyzer.categorized_data[0]
            self.assertIsInstance(prediction, dict)