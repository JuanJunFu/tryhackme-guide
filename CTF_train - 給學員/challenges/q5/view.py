from flask import Blueprint, render_template_string, request, session, make_response, jsonify
from utils import gen_flag

q5_bp = Blueprint('q5', __name__)

HINTS = [
    "本題考察 Cookie 竄改，請思考如何用瀏覽器 DevTools 操作 cookie。",
    "請將 is_admin 的 cookie 值改為 1，重新整理頁面。"
]

@q5_bp.route('/', methods=['GET', 'POST'])
def q5():
    flag = gen_flag(5)
    msg = ''
    admin_cookie = request.cookies.get('is_admin', '0')
    show_flag = False
    hint_level = session.get('hint_q5', 0)
    if request.method == 'POST':
        user_flag = request.form.get('flag', '').strip()
        if user_flag == flag:
            progress = session.get('progress', 1)
            solved_list = session.get('solved', [])
            if 5 not in solved_list:
                solved_list.append(5)
                session['solved'] = solved_list
                if progress < 6:
                    session['progress'] = 6
            msg = '✅ 恭喜，flag 正確！已解鎖下一題。'
        else:
            msg = '❌ flag 錯誤，請再試一次。'
    html = '''
    <h3>[Q5] Cookie Tampering</h3>
    <p>請設法讓 is_admin=1，取得 flag。</p>
    <form method="post">
      <input name="flag" placeholder="flag{...}" required>
      <button type="submit">提交 flag</button>
    </form>
    <button id="hint-btn">顯示提示</button>
    <div id="hint-area"></div>
    <script>
    let hintLevel = {{ hint_level }};
    document.getElementById('hint-btn').onclick = function() {
      fetch('/q5/hint', {method: 'POST'})
        .then(r => r.json())
        .then(data => {
          document.getElementById('hint-area').innerHTML = '<div style=\"color:blue;\">' + data.hint + '</div>';
          hintLevel = data.level;
          if (hintLevel >= 2) document.getElementById('hint-btn').disabled = true;
        });
    }
    if (hintLevel >= 1) {
      fetch('/q5/hint', {method: 'POST'}).then(r => r.json()).then(data => {
        document.getElementById('hint-area').innerHTML = '<div style=\"color:blue;\">' + data.hint + '</div>';
        if (data.level >= 2) document.getElementById('hint-btn').disabled = true;
      });
    }
    </script>
    {% if admin_cookie == '1' %}<div>flag: {{ flag }}</div>{% endif %}
    <p>{{msg}}</p>
    <a href="/">回題目列表</a>
    '''
    resp = make_response(render_template_string(html, msg=msg, flag=flag, admin_cookie=admin_cookie, hint_level=hint_level))
    if 'is_admin' not in request.cookies:
        resp.set_cookie('is_admin', '0')
    return resp

@q5_bp.route('/hint', methods=['POST'])
def q5_hint():
    hint_level = session.get('hint_q5', 0)
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
    session['hint_q5'] = hint_level
    session['hint_penalty'] = penalty
    return jsonify({'hint': hint, 'level': hint_level})
