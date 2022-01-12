from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename

app = Flask(__name__)

from pymongo import MongoClient


client = MongoClient('15.164.226.215', 27017, username="test", password="test")

db = client.hanghae99_007
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

import jwt

from datetime import datetime, timedelta

import hashlib


# 페이지 접속-----------------------------
@app.route('/', methods=['GET'])
def home():
    print('href=/')
    token_receive = request.cookies.get('mytoken')  # 사용자의 토큰을 받아옵니다.

    # 여러개 찾기 - 예시 ( _id 값은 제외하고 출력)
    posts = list(db.post.find({}))
    comments = list(db.comment.find({}))

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})  # 받아온 토큰으로 유저의 정보를 가져옵니다

        for post in posts:
            post["_id"] = str(post["_id"])
            post["like_count"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
            post["heart_by_me"] = bool(
                db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": payload['id']}))
        return render_template('index.html', user_info=user_info, posts=posts, comments=comments)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/register')
def register():
    return render_template('register.html')


# 유저페이지 추가
@app.route('/user/<id>')
def user(id):
    token_receive = request.cookies.get('mytoken')  # 사용자의 토큰을 받아옵니다.

    # 여러개 찾기 - 예시 ( _id 값은 제외하고 출력)
    posts = list(db.post.find({}))

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (id == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.user.find_one({"id": id}, {"_id": False})
        for post in posts:
            post["_id"] = str(post["_id"])
            post["like_count"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
            post["heart_by_me"] = bool(
                db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": payload['id']}))
        return render_template('user.html', user_info=user_info, posts=posts, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/post')
def post():
    token_receive = request.cookies.get('mytoken')  # 사용자의 토큰을 받아옵니다.
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})  # 받아온 토큰으로 유저의 정보를 가져옵니다
        return render_template('post.html', user_info=user_info, nickname=user_info["nickname"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 회원가입-------------------------------
@app.route("/addUser", methods=["POST"])
def addUser():
    id = request.form['id']
    pw = request.form['pw']
    nickname = request.form['nickname']

    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

    if (id == "" or pw == "" or nickname == ""):
        return jsonify({'result': 'fail', 'msg': 'please check input'});
    doc = {
        'id': id,
        'pw': pw_hash,
        'nickname': nickname,
        "profile_pic": "",  # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지
        "profile_info": ""  # 프로필 한 마디

    }
    db.user.insert_one(doc)
    return jsonify({'msg': "입력."});


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    id = request.form['id']
    exists = bool(db.user.find_one({"id": id}))
    return jsonify({'result': 'success', 'exists': exists})


# 로그인--------------------------------
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']  # 사용자단에서 넘겨받은 id값
    pw_receive = request.form['pw_give']  # 사용자단에서 넘겨받은 id값

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/api/nickname', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    # try / catch 문?
    # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.

    try:
        # token을 시크릿키로 디코딩합니다.
        # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.
        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nickname']})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


# 메인---------------------------------------
@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload["id"]})
        print(user_info)
        post_id_receive = request.form["post_id_give"]  # post id
        print(post_id_receive)
        type_receive = request.form["type_give"]  # type heart
        print(type_receive)
        action_receive = request.form["action_give"]  # like unlike
        print(action_receive)
        doc = {
            "post_id": post_id_receive,
            "username": user_info["id"],
            "type": type_receive
        }

        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents({"post_id": post_id_receive, "type": type_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/del', methods=['POST'])
def delete_star():
    id = request.form['post_id']
    print(id)

    db.post.delete_one({'_id': ObjectId(id)})

    return jsonify({'msg': '삭제했습니다'})


@app.route('/comment_insert', methods=['POST'])
def comment_insert():

    doc = {
        "post_id": request.form['post_id_give'],
        "comment": request.form['comment_give'],
        "nickname": request.form['nickname_give'],
        "id": request.form['id_give'],
        "profile": request.form['profile_give'],
    }

    db.comment.insert_one(doc)

    print(doc)

    return jsonify({'msg': '덧글을 등록했습니다'})


# 작성페이지---------------------------------
@app.route('/save_post', methods=['POST'])
def save_post():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 게시글 저장하기
        user_info = db.user.find_one({"id": payload["id"]})
        id_receive = user_info['id']
        print(id_receive)
        title_receive = request.form['title_give']
        img_url_receive = request.form['img_url_give']
        address_receive = request.form['address_give']
        review_receive = request.form['review_give']
        # if (title_receive == "" or img_url_receive == "" or address_receive == "" or review_receive == ""):
        #     return jsonify({'result': 'fail', 'msg': '모두 입력하세요'});
        # if (title_receive != "" or img_url_receive != "" or address_receive != "" or review_receive != ""):
        doc = {
            "img_url": img_url_receive,
            "nickname": user_info["nickname"],
            "title": title_receive,
            "address": address_receive,
            "review": review_receive,
            "id": id_receive
        }
        db.post.insert_one(doc)
        return jsonify({'result': 'success', 'msg': f'{user_info["nickname"]}님 게시글 저장!'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("/"))


# 유저페이지---------------------------------
@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        id = payload["id"]
        name_receive = request.form["name_give"]
        about_receive = request.form["about_give"]
        new_doc = {
            "nickname": name_receive,
            "profile_info": about_receive
        }
        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{id}.{extension}"
            file.save("./static/" + file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path
        db.user.update_one({'id': payload['id']}, {'$set': new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
