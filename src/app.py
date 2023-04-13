from flask import Flask, request, render_template, jsonify
import os

from models.models import db, Post, Prediction

from components.posts_collector.DataCollectorClass import DataCollector
from components.posts_analyzer.DataAnalyzerClass import DataAnalyzer

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# local
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

# heroku
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://qqbjdftfomapyt:8edf6ccebf49940d554574508e6a7bdf3793e2b7d3ead39ff353c2fe8ad6ed4f@ec2-34-236-199-229.compute-1.amazonaws.com:5432/d9d64867psc2p8'

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

@app.route('/analyze')
def analyze():
    mapping_file_path = os.path.join(app.instance_path, 'mapping.json')
    analyzer = DataAnalyzer(db, mapping_file_path)
    analyzer.get_posts()
    analyzer.classifiy()
    analyzer.save_categorized_data()
    return 'Worked!'

if __name__ == '__main__':
    app.run(debug=True)
