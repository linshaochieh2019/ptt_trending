from flask import Flask, request, render_template
import os

from models.post import db, Post

from components.posts_collector.DataCollectorClass import DataCollector

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if os.environ.get('DATABASE_URL') is None:
    # heroku
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://qqbjdftfomapyt:8edf6ccebf49940d554574508e6a7bdf3793e2b7d3ead39ff353c2fe8ad6ed4f@ec2-34-236-199-229.compute-1.amazonaws.com:5432/d9d64867psc2p8'

else:
    # local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ptt_trending_user:1234@localhost:5432/ptt_trending_db'

print(f"Current db URL config: {app.config['SQLALCHEMY_DATABASE_URI']}")

if app.config['SQLALCHEMY_DATABASE_URI'] is None:
    raise ValueError('No database URL set')

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
        collector.save_posts()
        return render_template('posts.html', posts=collector.posts)
    
    # GET request
    return render_template('form.html')


@app.route('/posts')
def posts():
    posts = Post.query.all()
    return render_template('posts.html', posts=posts)

if __name__ == '__main__':
    app.run(debug=True)
