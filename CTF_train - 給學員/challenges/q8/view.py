from flask import Blueprint, render_template_string, request, session, jsonify
from utils import gen_flag
import sqlite3
import os

q8_bp = Blueprint('q8', __name__)
DB_PATH = 'challenges/q8/q8.db'

HINTS = [
    "本題考察 SQL Injection，請觀察查詢語句與輸入資料的關係。",
    "嘗試在帳號欄位輸入 ' OR 1=1 --，繞過密碼驗證。"
]

# 初始化資料庫
if not os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', 'adminpass'))
    conn.commit()
    conn.close()

@q8_bp.route('/', methods=['GET', 'POST'])
def q8():
    flag = gen_flag(8)
    msg = ''
    show_flag = False
    sql_query = ""
    hint_level = session.get('hint_q8', 0)
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        # SQL Injection 漏洞
        sql_query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute(sql_query)
            user = c.fetchone()
            if user and username != 'admin':  # 不能用 admin 正常密碼
                progress = session.get('progress', 1)
                solved_list = session.get('solved', [])
                if 8 not in solved_list:
                    solved_list.append(8)
                    session['solved'] = solved_list
                    if progress < 9:
                        session['progress'] = 9
                msg = '✅ 恭喜，flag 正確！已解鎖下一題。'
                show_flag = True
            else:
                msg = '❌ 登入失敗，請再試一次。'
        except Exception as e:
            msg = f'❌ SQL 錯誤: {e}'
        finally:
            conn.close()
    html = '''
    <h3>[Q8] Simple SQLi</h3>
    <p>請利用 SQL Injection 登入非 admin 帳號，取得 flag。</p>
    <form method="post">
      <input name="username" placeholder="Username" required>
      <input name="password" type="password" placeholder="Password" required>
      <button type="submit">登入</button>
    </form>
    <button id="hint-btn">顯示提示</button>
    <div id="hint-area"></div>
    <pre style="background:#f8f8f8;padding:8px;border-radius:4px;">-- 目前查詢語句：
{{ sql_query }}
</pre>
    {% if show_flag %}<div>flag: {{ flag }}</div>{% endif %}
    <p>{{msg}}</p>
    <a href="/">回題目列表</a>
    <script>
    let hintLevel = {{ hint_level }};
    document.getElementById('hint-btn').onclick = function() {
      fetch('/q8/hint', {method: 'POST'})
        .then(r => r.json())
        .then(data => {
          document.getElementById('hint-area').innerHTML = '<div style="color:blue;">' + data.hint + '</div>';
          hintLevel = data.level;
          if (hintLevel >= 2) document.getElementById('hint-btn').disabled = true;
        });
    }
    if (hintLevel >= 1) {
      fetch('/q8/hint', {method: 'POST'}).then(r => r.json()).then(data => {
        document.getElementById('hint-area').innerHTML = '<div style="color:blue;">' + data.hint + '</div>';
        if (data.level >= 2) document.getElementById('hint-btn').disabled = true;
      });
    }
    </script>
    '''
    return render_template_string(html, msg=msg, flag=flag, show_flag=show_flag, sql_query=sql_query, hint_level=hint_level)

@q8_bp.route('/hint', methods=['POST'])
def q8_hint():
    hint_level = session.get('hint_q8', 0)
    penalty = session.get('hint_penalty', 0)
    if hint_level == 0:
        hint = HINTS[0]
        hint_level = 1
        penalty += 30
    elif hint_level == 1:
        hint = HINTS[1]
        hint_level = 2
        penalty += 60
    else:
        hint = HINTS[1]
    session['hint_q8'] = hint_level
    session['hint_penalty'] = penalty
    return jsonify({'hint': hint, 'level': hint_level}) 