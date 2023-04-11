from flask import Flask, request, render_template
from components.posts_collector.DataCollectorClass import DataCollector

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/posts', methods=('GET', 'POST'))
def posts():
        
    if request.method == 'POST':
        board = request.form['board']
        num_pages = int(request.form['num_pages'])
        collector = DataCollector()
        collector.scrape_ptt_posts(board, num_pages)

        return render_template('posts.html', posts=collector.posts)

    # GET method
    return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=True)
