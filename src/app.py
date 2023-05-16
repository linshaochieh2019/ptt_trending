from flask import Flask, request, render_template, jsonify
from prometheus_flask_exporter import PrometheusMetrics

import os
from sqlalchemy import func
from collections import defaultdict
from datetime import datetime, date, timedelta
import pandas as pd
import json
import time

from models.models import db, Post, Prediction

from components.posts_collector.DataCollectorClass import DataCollector
from components.posts_analyzer.DataAnalyzerClass import DataAnalyzer

app = Flask(__name__, static_folder='static')
metrics = PrometheusMetrics(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if os.environ.get('DYNO'):  # running on Heroku
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://qqbjdftfomapyt:8edf6ccebf49940d554574508e6a7bdf3793e2b7d3ead39ff353c2fe8ad6ed4f@ec2-34-236-199-229.compute-1.amazonaws.com:5432/d9d64867psc2p8'
else:  # running locally
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/posts')
def posts():
    posts = Post.query.all()
    return render_template('posts.html', posts=posts)

@app.route('/scrape', methods=('GET', 'POST'))
def scrape():
    if request.method == 'POST':
        board = request.form['board']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        collector = DataCollector()
        collector.scrape_ptt_posts(board, start_date, end_date)
        collector.save_posts()
        return render_template('posts.html', posts=collector.posts)
    
    # GET request
    return render_template('form_collecting.html')


@app.route('/classify', methods=('GET', 'POST'))
def classify():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        mapping_file_path = os.path.join(app.instance_path, 'mapping.json')
        analyzer = DataAnalyzer(db, mapping_file_path)
        analyzer.get_posts_by_dates(start_date, end_date)
        analyzer.classifiy()
        analyzer.save_categorized_data()
        return analyzer.categorized_data

    # GET request
    return render_template('form_classifying.html')


@app.route('/mapping')
def get_mapping():
    instance_path = app.instance_path
    with open(f"{instance_path}/mapping.json", "r") as f:
        mapping = json.load(f)
    return jsonify(mapping)

@app.route('/colors')
def get_colors():
    instance_path = app.instance_path
    with open(f"{instance_path}/colors.json", "r") as f:
        mapping = json.load(f)
    return jsonify(mapping)

@app.route('/data')
def get_data():
    
    predictions = db.session.query(
        func.date_trunc('day', Post.created),
        Prediction.category,
        func.count()
    ).join(Prediction, Prediction.post_id == Post.id)\
    .group_by(func.date_trunc('day', Post.created), Prediction.category)\
    .all()

    df = pd.DataFrame(predictions, columns=['date', 'category', 'count'])
    df = df.pivot(index='date', columns='category', values='count')
    df = df.fillna(0)

    data = {
        'dates': df.index.strftime('%Y-%m-%d').tolist(),
        'counts': dict()
    }

    for i in range(1, 12):
        try:
            data['counts'][i] = df[i].values.tolist()
        except:
            pass

    
    return jsonify(data)
        

@app.route('/health')
def health_check():
    return '200 OK'

@app.route('/metrics')
def metrics():
    metrics.counter('requests_total', 'Total number of requests', labels={'endpoint': '/metrics'}).inc()
    return '200 OK'

if __name__ == '__main__':
    app.run(debug=True)
