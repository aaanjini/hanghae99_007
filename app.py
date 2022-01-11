from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from bson.objectid import ObjectId

app = Flask(__name__)

from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client.hanghae99_007


SECRET_KEY = 'SPARTA'

import jwt

from datetime import datetime, timedelta

import hashlib

# 페이지 접속-----------------------------
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/post')
def post():
    return render_template('post.html')

# 회원가입-------------------------------
@app.route("/addUser", methods=["POST"])
def addUser():

    id = request.form['id']
    pw = request.form['pw']
    nickname = request.form['nickname']

    if (id == "" or pw == "" or nickname == ""):
        return jsonify({'result': 'fail', 'msg': 'please check input'});
    doc = {
        'id': id,
        'pw': pw,
        'nickname': nickname,

    }
    db.user.insert_one(doc);
    return jsonify({'msg': "입력."});


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    id = request.form['id']
    exists = bool(db.user.find_one({"id": id}))
    return jsonify({'result': 'success', 'exists': exists})


# 로그인--------------------------------
@app.route('/api/login', methods=['POST'])
def api_login():
    return jsonify({'result': 'success'})

@app.route('/api/nick', methods=['GET'])
def api_valid():
    return jsonify({'result': 'success'})



# 메인---------------------------------------
@app.route('/like', methods=['POST'])
def like_star():
    return jsonify({'result': 'success'})

@app.route('/canclelike', methods=['POST'])
def cancle_like():
    return jsonify({'result': 'success'})

@app.route('/del', methods=['POST'])
def delete_star():
    return jsonify({'result': 'success'})



# 작성페이지---------------------------------











@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    return jsonify({'result': 'success'})


# 로그인--------------------------------
@app.route('/api/login', methods=['POST'])
def api_login():
    return jsonify({'result': 'success'})

@app.route('/api/nick', methods=['GET'])
def api_valid():
    return jsonify({'result': 'success'})



# 메인---------------------------------------
@app.route('/like', methods=['POST'])
def like_star():
    return jsonify({'result': 'success'})

@app.route('/canclelike', methods=['POST'])
def cancle_like():
    return jsonify({'result': 'success'})

@app.route('/del', methods=['POST'])
def delete_star():
    return jsonify({'result': 'success'})



# 작성페이지---------------------------------


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)