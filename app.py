from flask import Flask, render_template, jsonify, request
from bson.objectid import ObjectId
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.dbsparta

## HTML을 주는 부분
@app.route('/', methods=['GET'])
def home():
    # 여러개 찾기 - 예시 ( _id 값은 제외하고 출력)
    posts = list(db.post.find({}).sort('like_count', -1))

    return render_template('index.html', posts=posts)

@app.route('/like', methods=['POST'])
def like_star():
    id = request.form['post_id']
    print(id)

    like = db.post.find_one({'_id': ObjectId(id)})['like_count']+1
    print(like)
    db.post.update_one({'_id': ObjectId(id)}, {'$set': {'like_count': like}})

    return jsonify({'msg': '좋아요 하였습니다!'})

@app.route('/del', methods=['POST'])
def delete_star():
    id = request.form['post_id']
    print(id)

    db.post.delete_one({'_id': ObjectId(id)})

    return jsonify({'msg': '삭제했습니다'})

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)