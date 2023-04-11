import requests
from bs4 import BeautifulSoup
import psycopg2

class DataCollector:
    def __init__(self, board, num_pages):
        self.posts = self.scrape_ptt_posts(board, num_pages)

    def scrape_ptt_posts(board, num_pages):

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
                post_date = post_info[3].text
                post_dict = {'title': post_title, 'author': post_author, 'date': post_date, 'content': post_content}
                posts.append(post_dict)

        return posts
    
    def insert_posts(self):
        conn = psycopg2.connect(
            host="your_host",
            database="your_db_name",
            user="your_username",
            password="your_password"
        )

        # create a cursor object
        cur = conn.cursor()

        # create a table
        cur.execute("CREATE TABLE posts (title TEXT, author TEXT, date TEXT, content TEXT)")

        # insert data into the table
        for post in self.posts:
            cur.execute(
                "INSERT INTO posts (title, author, date, content) VALUES (%s, %s, %s, %s)",
                (post['title'], post['author'], post['date'], post['content'])
            )

        # commit changes to the database
        conn.commit()

        # close cursor and connection
        cur.close()
        conn.close()
