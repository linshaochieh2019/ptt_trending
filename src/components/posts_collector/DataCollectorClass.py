import requests
from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup

from app import db
from models.models import Post

class DataCollector:
    def __init__(self):
        self.session = self.get_ptt_session()
        self.maximum_posts_retrieved = 30
        self.board = None
        self.posts = None

    def get_ptt_session(self):
        session = requests.Session()
        session.cookies['over18'] = '1'
        return session
    
    def get_lastest_page_num(self, board):
        self.board = board
        url = f'https://www.ptt.cc/bbs/{board}/index.html'
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        prev_page_link = soup.find('div', {'class': 'btn-group-paging'}).find_all('a')[1]['href']
        prev_page_link = prev_page_link.split('.html')[0]
        output = [l for l in prev_page_link if l.isnumeric()] 
        prev_page_num = int(''.join(output))
        current_page_num = prev_page_num + 1
        return current_page_num

    def retrieve_ptt_html(self, board, page_num):
        url = f'https://www.ptt.cc/bbs/{board}/index{page_num}.html'
        response = self.session.get(url)
        return response.text

    def get_post_urls(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        divs = soup.find_all('div', {'class': 'title'})
        post_urls = []
        for div in divs:
            try:
                post_url = 'https://www.ptt.cc' + div.find('a')['href']
                post_urls.append(post_url)
            except:
                continue #a href not exist - for example the deleted posts

        return post_urls
    
    def get_posts(self, post_urls):
        posts = []
        for post_url in post_urls:
            post_response = self.session.get(post_url)
            post_soup = BeautifulSoup(post_response.text, 'html.parser')
            post_content_div = post_soup.find('div', {'id': 'main-content'})
            if post_content_div is None:
                print(f'Main-content not found for post {post_url}:')
                print(post_response.text)
                continue
            post_content = post_content_div.text
            post_content = post_content.split('※ 發信站: 批踢踢實業坊(ptt.cc)', 1)[0]
            post_info = post_soup.findAll('span', {'class': 'article-meta-value'})
            if post_info:
                pass
            else:
                continue
            post_author = post_info[0].text
            post_title = post_info[2].text
            post_created = post_info[3].text
            post_created = datetime.strptime(post_created, '%a %b %d %H:%M:%S %Y').date()
            post_dict = {'title': post_title, 'author': post_author, 'created': post_created, 'content': post_content, 'board': self.board}
            posts.append(post_dict)
        return posts

    def filter_posts_by_date(self, posts, start_date, end_date):
        filtered_posts = []
        for post in posts:
            if start_date <= post['created'] <= end_date:
                filtered_posts.append(post)
        return filtered_posts
    

    def scrape_ptt_posts(self, board, start_date=None, end_date=None):
        # convert start and end dates to datetime objects
        # if not specified then date == today
        if start_date == '':
            start_date = datetime.today().date()
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date == '':
            end_date = datetime.today().date()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        # iterate over the pages and scrape the posts
        current_page_num = self.get_lastest_page_num(board)
        results = []
        while True:
            print(f'Current page num: {current_page_num}')
            html = self.retrieve_ptt_html(board, current_page_num)
            post_urls = self.get_post_urls(html)

            posts = self.get_posts(post_urls)
            print(f'Number of posts retrieved: {len(posts)}')
            
            filtered_posts = self.filter_posts_by_date(posts, start_date, end_date)
            print(f'Number of posts added: {len(filtered_posts)}')
            
            results.extend(filtered_posts)
            current_page_num -= 1 # iterarte to the previous page
            
            if len(results) > self.maximum_posts_retrieved:
                break

        print(f'Retrieve {len(results)} posts from PTT.')
        self.posts = results

    def save_posts(self):
        for post in self.posts:
            # Check if post already exists in the database
            existing_post = Post.query.filter_by(title=post['title'], author=post['author'], created=post['created']).first()
            if not existing_post:
                # Post does not exist, so add it to the database
                p = Post(title=post['title'], author=post['author'], created=post['created'], content=post['content'], board=post['board'])
                db.session.add(p)
        db.session.commit()