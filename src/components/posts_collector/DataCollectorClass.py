import requests
from bs4 import BeautifulSoup

class DataCollector:
    def __init__(self):
        self.posts = None

    def scrape_ptt_posts(self, board, num_pages):

        url = f'https://www.ptt.cc/bbs/{board}/index.html'
        session = requests.Session()
        response = session.get(url, cookies={'over18': '1'})
        soup = BeautifulSoup(response.text, 'html.parser')

        # find the previous page link to determine the range of page numbers to scrape
        prev_page_link = soup.find('div', {'class': 'btn-group-paging'}).find_all('a')[1]['href']
        prev_page_link = prev_page_link.split('.html')[0]
        output = [l for l in prev_page_link if l.isnumeric()] 
        prev_page_num = int(''.join(output))
        last_page_num = prev_page_num + 1

        # iterate over the pages and scrape the posts
        posts = []
        for page_num in range(last_page_num - num_pages, last_page_num):
            page_url = f'https://www.ptt.cc/bbs/{board}/index{page_num}.html'
            response = session.get(page_url, cookies={'over18': '1'})
            soup = BeautifulSoup(response.text, 'html.parser')
            post_links = soup.find_all('div', {'class': 'title'})
            for link in post_links:

                try:
                    post_url = 'https://www.ptt.cc' + link.find('a')['href']
                except:
                    pass #a href not exist - for example the deleted posts
                
                post_response = session.get(post_url, cookies={'over18': '1'})
                post_soup = BeautifulSoup(post_response.text, 'html.parser')
                post_content = post_soup.find('div', {'id': 'main-content'}).text
                post_content = post_content.split('※ 發信站: 批踢踢實業坊(ptt.cc)', 1)[0]
                post_info = post_soup.findAll('span', {'class': 'article-meta-value'})
                post_author = post_info[0].text
                post_title = post_info[2].text
                post_created = post_info[3].text
                post_dict = {'title': post_title, 'author': post_author, 'created': post_created, 'content': post_content}
                posts.append(post_dict)

        self.posts = posts
        print(f'Retrieve {len(posts)} posts from PTT.')