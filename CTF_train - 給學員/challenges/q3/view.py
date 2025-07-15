from flask import Blueprint, render_template_string, request, session, jsonify
from utils import gen_flag

q3_bp = Blueprint('q3', __name__)

USERNAME = 'admin'
PASSWORD = 'admin12345'  # 弱密碼

HINTS = [
    "本題考察弱密碼與暴力破解，請思考常見的預設帳號密碼。",
    "試試看 admin/12345 或其他常見弱密碼組合。"
]

@q3_bp.route('/', methods=['GET', 'POST'])
def q3():
    flag = gen_flag(3)
    msg = ''
    show_flag = False
    hint_level = session.get('hint_q3', 0)
    if request.method == 'POST':
        user = request.form.get('username', '')
        pw = request.form.get('password', '')
        if user == USERNAME and pw == PASSWORD:
            progress = session.get('progress', 1)
            solved_list = session.get('solved', [])
            if 3 not in solved_list:
                solved_list.append(3)
                session['solved'] = solved_list
                if progress < 4:
                    session['progress'] = 4
            msg = '✅ 恭喜，flag 正確！已解鎖下一題。'
            show_flag = True
        else:
            msg = '❌ 帳號或密碼錯誤，請再試一次。'
    html = '''
    <h3>[Q3] Weak Login</h3>
    <p>請嘗試登入弱密碼帳號（admin），取得 flag。</p>
    <form method="post">
      <input name="username" placeholder="Username" required>
      <input name="password" type="password" placeholder="Password" required>
      <button type="submit">登入</button>
    </form>
    <button id="hint-btn">顯示提示</button>
    <div id="hint-area"></div>
    <script>
    let hintLevel = {{ hint_level }};
    document.getElementById('hint-btn').onclick = function() {
      fetch('/q3/hint', {method: 'POST'})
        .then(r => r.json())
        .then(data => {
          document.getElementById('hint-area').innerHTML = '<div style=\"color:blue;\">' + data.hint + '</div>';
          hintLevel = data.level;
          if (hintLevel >= 2) document.getElementById('hint-btn').disabled = true;
        });
    }
    if (hintLevel >= 1) {
      fetch('/q3/hint', {method: 'POST'}).then(r => r.json()).then(data => {
        document.getElementById('hint-area').innerHTML = '<div style=\"color:blue;\">' + data.hint + '</div>';
        if (data.level >= 2) document.getElementById('hint-btn').disabled = true;
      });
    }
    </script>
    {% if show_flag %}<div>flag: {{ flag }}</div>{% endif %}
    <p>{{msg}}</p>
    <a href="/">回題目列表</a>
    '''
    return render_template_string(html, msg=msg, flag=flag, show_flag=show_flag, hint_level=hint_level)

@q3_bp.route('/hint', methods=['POST'])
def q3_hint():
    hint_level = session.get('hint_q3', 0)
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
    session['hint_q3'] = hint_level
    session['hint_penalty'] = penalty
    return jsonify({'hint': hint, 'level': hint_level}) 