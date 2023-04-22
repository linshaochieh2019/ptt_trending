import os

from app import app,db

from components.posts_collector.DataCollectorClass import DataCollector
from components.posts_analyzer.DataAnalyzerClass import DataAnalyzer

print('Hello world.')

board = 'Gossiping'
start_date = ''
end_date = ''

with app.app_context():
    collector = DataCollector()
    collector.scrape_ptt_posts(board, start_date, end_date)
    collector.save_posts()

    mapping_file_path = os.path.join(app.instance_path, 'mapping.json')
    analyzer = DataAnalyzer(db, mapping_file_path)
    print('Classifier is working ...')
    analyzer.get_posts_by_dates(start_date, end_date)
    analyzer.classifiy()
    analyzer.save_categorized_data()