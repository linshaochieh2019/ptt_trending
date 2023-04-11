import unittest
from unittest.mock import patch
from components.posts_collector.DataCollectorClass import DataCollector

class TestDataCollector(unittest.TestCase):
    
    def test_scrape_ptt_posts(self):
        with patch('requests.Session.get') as mock_get:
            mock_get.return_value.text = '''
                <div class="btn-group btn-group-paging">
				<a class="btn wide" href="/bbs/Gossiping/index1.html">最舊</a>
				<a class="btn wide" href="/bbs/Gossiping/index39022.html">&lsaquo; 上頁</a>
				<a class="btn wide disabled">下頁 &rsaquo;</a>
				<a class="btn wide" href="/bbs/Gossiping/index.html">最新</a>
			</div>
            '''
            collector = DataCollector()
            collector.scrape_ptt_posts('Test', 1)
            self.assertIsNotNone(collector.posts)
            self.assertEqual(len(collector.posts), 0)
    
    def test_scrape_ptt_posts_invalid_board(self):
        collector = DataCollector()
        with self.assertRaises(Exception):
            collector.scrape_ptt_posts('InvalidBoardName', 1)
    
    def test_scrape_ptt_posts_invalid_num_pages(self):
        collector = DataCollector()
        with self.assertRaises(Exception):
            collector.scrape_ptt_posts('Test', 'invalid_num_pages')
