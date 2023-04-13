import requests
from sqlalchemy import text

import os
import json
import openai

from models.models import Post, Prediction

from datetime import datetime, date


class DataAnalyzer:
    def __init__(self, db, mapping_file_path):
        self.db = db
        self.mapping_file_path = mapping_file_path
        self.mapping = self.get_mapping()
        self.categorized_data = list()
        self.posts = None
        
    def get_mapping(self):
        with open(self.mapping_file_path) as f:
            mapping = json.load(f)
        return mapping

    def get_posts(self):
        today = date.today()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        self.posts = Post.query.filter(Post.created >= start_of_day, Post.created <= end_of_day)\
            .with_entities(Post.id, Post.content).limit(20).all()

        print(f'Number of posts retrieve: {len(self.posts)}')
            
    def classifiy(self):
        if self.posts == None: 
            return # The analyzer doesn't have any posts to categorize.

        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        for post_id,post in self.posts:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=f'''Given a text, categorize it into one of the following categories: 
                News, Sports, Technology, Business, Entertainment, Politics, Education, Health, Science, Travel.
                Text: {post[:200]}"
                Category: ''',
                temperature=0.5,
                max_tokens=60,
                top_p=1.0,
                frequency_penalty=0.8,
                presence_penalty=0.0
            )

            category = response['choices'][0]['text']
            category = category.strip()
            swapped_mapping = {value: key for key, value in self.mapping.items()}

            try:
                self.categorized_data.append({'post_id': post_id, 'category': swapped_mapping[category]})
            except: # in case not exsiting category
                self.categorized_data.append({'post_id': post_id, 'category': 11}) # gossiping

    def save_categorized_data(self):
        for categorized_data in self.categorized_data:
            # Check if post already exists in the database
            existing_post = Prediction.query.filter_by(post_id=categorized_data['post_id']).first()
            if not existing_post:
                # Post does not exist, so add it to the database
                new_categorized_data = Prediction(post_id=categorized_data['post_id'], category=categorized_data['category'])
                self.db.session.add(new_categorized_data)
        self.db.session.commit()
       