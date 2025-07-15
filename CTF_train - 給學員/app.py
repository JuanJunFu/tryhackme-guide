from flask import Flask, render_template_string, session, redirect, url_for
import os
import random
import string
from utils import gen_flag
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('CTF_SECRET_KEY', 'ctf4beginner')

# 題目清單
QUESTIONS = [
    {'id': 1, 'title': 'Service Discovery'},
    {'id': 2, 'title': 'Hidden in Source'},
    {'id': 3, 'title': 'Weak Login', 'desc': '弱密碼登入測試。'},
    {'id': 4, 'title': 'Simple XSS', 'desc': '反射型 XSS 測試。'},
    {'id': 5, 'title': 'Cookie Tampering', 'desc': 'Cookie 竄改練習。'},
    {'id': 6, 'title': 'JWT Decode', 'desc': 'JWT 解碼與驗證。'},
    {'id': 7, 'title': 'CORS Demo', 'desc': 'CORS 配置錯誤示範。'},
    {'id': 8, 'title': 'Simple SQLi', 'desc': 'SQL Injection 基礎。'},
    {'id': 9, 'title': 'File Upload Bypass', 'desc': '檔案上傳繞過。'},
    {'id': 10, 'title': 'Access Control Logic', 'desc': '存取控制邏輯漏洞。'},
]

# 註冊題目 Blueprint
from challenges.q1.view import q1_bp
from challenges.q2.view import q2_bp
from challenges.q3.view import q3_bp
from challenges.q4.view import q4_bp
from challenges.q5.view import q5_bp
from challenges.q6.view import q6_bp
from challenges.q7.view import q7_bp
from challenges.q8.view import q8_bp
from challenges.q9.view import q9_bp
from challenges.q10.view import q10_bp
app.register_blueprint(q1_bp, url_prefix='/q1')
app.register_blueprint(q2_bp, url_prefix='/q2')
app.register_blueprint(q3_bp, url_prefix='/q3')
app.register_blueprint(q4_bp, url_prefix='/q4')
app.register_blueprint(q5_bp, url_prefix='/q5')
app.register_blueprint(q6_bp, url_prefix='/q6')
app.register_blueprint(q7_bp, url_prefix='/q7')
app.register_blueprint(q8_bp, url_prefix='/q8')
app.register_blueprint(q9_bp, url_prefix='/q9')
app.register_blueprint(q10_bp, url_prefix='/q10')

# 檢查題目是否已解鎖/完成
@app.context_processor
def inject_progress():
    progress = session.get('progress', 1)
    solved_list = session.get('solved', [])
    return dict(progress=progress, solved_list=solved_list)

@app.route('/')
def index():
    if 'flag_seed' not in session:
        import random, string
        session['flag_seed'] = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    if 'start_time' not in session:
        session['start_time'] = datetime.now().isoformat()
    progress = session.get('progress', 1)
    solved_list = session.get('solved', [])
    total_time = None
    total_wrong = None
    if progress > 10 and 'start_time' in session and 'end_time' in session:
        start = datetime.fromisoformat(session['start_time'])
        end = datetime.fromisoformat(session['end_time'])
        total_time = str(end - start).split('.')[0]  # 去除微秒
        total_wrong = session.get('wrong_count', 0)
    return render_template_string('''
    <h2>CTF 練習平台（題目需依序解鎖）</h2>
    {% if total_time %}<div style="color:green;font-size:18px;">🎉 全部完成！總花費時間：{{ total_time }}，總錯誤次數：{{ total_wrong }}</div>{% endif %}
    <ul>
    {% for q in questions %}
      <li>
        {% if q.id <= progress %}
          <a href="/q{{q.id}}/">[Q{{q.id}}] {{q.title}}</a>
          {% if q.id in solved_list %}✅{% endif %}
        {% else %}
          <span style="color:gray;">[Q{{q.id}}] {{q.title}}（未解鎖）</span>
        {% endif %}
      </li>
    {% endfor %}
    </ul>
    <form method="post" action="/reset"><button type="submit">重置進度</button></form>
    ''', questions=QUESTIONS, total_time=total_time)

@app.route('/reset', methods=['POST'])
def reset():
    session.clear()
    from flask import make_response
    import random, string
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('session', '', expires=0)
    resp.set_cookie('flag_seed', '', expires=0)
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True) 