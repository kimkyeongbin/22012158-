# app.py

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)
from used_market.db import init_db, get_db_connection
from repositories import UserRepository, ItemRepository, ChatRepository
from used_market.models import User, Item, ChatMessage
import sqlite3
import datetime

app = Flask(__name__)
app.url_map.strict_slashes = False
app.secret_key = 'YOUR_SECRET_KEY'

# 초기 실행 시 DB와 테이블을 생성한다 (최초 1회)
init_db()

# Repository 인스턴스
user_repo = UserRepository()
item_repo = ItemRepository()
chat_repo = ChatRepository()


# ──────────────────────────────────────────────
# 1) 홈 페이지: 환영 문구 + 로그인 버튼
@app.route('/')
def home():
    return render_template('home.html')


# ──────────────────────────────────────────────
# 2) 회원가입
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']
        created_id = user_repo.create(email, password)
        if created_id is None:
            # 이미 존재하는 이메일
            return render_template('signup.html', error="이미 등록된 이메일입니다.")
        return redirect(url_for('login'))
    return render_template('signup.html')


# ──────────────────────────────────────────────
# 3) 로그인
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']
        user = user_repo.find_by_email(email)
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('items_page'))
        return render_template('login.html', error="이메일 또는 비밀번호가 올바르지 않습니다.")
    return render_template('login.html')


# ──────────────────────────────────────────────
# 4) 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ──────────────────────────────────────────────
# 5) 상품 등록 (로그인 필요)
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        category    = request.form['category']
        title       = request.form['title']
        description = request.form['description']
        price       = request.form['price']

        if not (category and title and price):
            flash('모든 필드를 입력해 주세요.')
            return redirect(request.url)

        owner_id = session['user_id']
        new_id = item_repo.create(category, title, description, price, owner_id)
        return redirect(url_for('item_detail', item_id=new_id))

    return render_template('upload.html')


# ──────────────────────────────────────────────
# 6) 상품 목록 (검색 기능 포함)
@app.route('/items')
def items_page():
    search_query = request.args.get('search', '').strip()
    items = item_repo.find_all(search_query)
    return render_template('items.html', items=items)


# ──────────────────────────────────────────────
# 7) 상품 상세 페이지
@app.route('/item/<int:item_id>')
def item_detail(item_id):
    item = item_repo.find_by_id(item_id)
    if not item:
        return "<h1>해당 상품이 존재하지 않습니다.</h1>", 404
    return render_template('item_detail.html', item=item)


# ──────────────────────────────────────────────
# 8) 채팅 페이지: 메시지 조회/전송
@app.route('/chat/<int:item_id>', methods=['GET', 'POST'])
def chat(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # POST 요청: 새로운 메시지를 저장
    if request.method == 'POST':
        message_text = request.form['message']
        timestamp = datetime.datetime.now().isoformat()
        sender_id = session['user_id']
        chat_repo.create(item_id, sender_id, message_text, timestamp)
        return redirect(url_for('chat', item_id=item_id))

    # GET 요청: 해당 상품(item_id)에 달린 채팅 메시지를 모두 가져옴
    messages = chat_repo.find_by_item(item_id)
    return render_template('chat.html', item=item_repo.find_by_id(item_id), messages=messages)


if __name__ == '__main__':
    app.run(debug=True)

