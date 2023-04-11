from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

from models.post import db, Post

from components.posts_collector.DataCollectorClass import DataCollector

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'

db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/scrape', methods=('GET', 'POST'))
def scrape():
    if request.method == 'POST':
        board = request.form['board']
        num_pages = int(request.form['num_pages'])
        collector = DataCollector()
        collector.scrape_ptt_posts(board, num_pages)
        return render_template('posts.html', posts=collector.posts)
    
    # GET request
    return render_template('form.html')


@app.route('/posts')
def posts():
    posts = Post.query.all()
    return render_template('posts.html', posts=posts)

if __name__ == '__main__':
    app.run(debug=True)
