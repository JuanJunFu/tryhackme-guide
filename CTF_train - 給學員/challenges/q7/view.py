from flask import Blueprint, render_template_string, request, session, make_response, jsonify
from utils import gen_flag

q7_bp = Blueprint('q7', __name__)

HINTS = [
    "本題考察 CORS 跨域請求，請思考如何從其他網域發送請求。",
    "用 curl 加上 Origin header，或用 JS fetch 從不同網域請求 /q7/，即可取得 flag。"
]

@q7_bp.route('/', methods=['GET', 'POST'])
def q7():
    flag = gen_flag(7)
    msg = ''
    show_flag = False
    hint_level = session.get('hint_q7', 0)
    if request.method == 'POST':
        user_flag = request.form.get('flag', '').strip()
        if user_flag == flag:
            progress = session.get('progress', 1)
            solved_list = session.get('solved', [])
            if 7 not in solved_list:
                solved_list.append(7)
                session['solved'] = solved_list
                if progress < 8:
                    session['progress'] = 8
            msg = '✅ 恭喜，flag 正確！已解鎖下一題。'
        else:
            msg = '❌ flag 錯誤，請再試一次。'
    html = '''
    <h3>[Q7] CORS Demo</h3>
    <p>請用 JS/curl 從其他網域發送請求，取得 flag。</p>
    <form method="post">
      <input name="flag" placeholder="flag{...}" required>
      <button type="submit">提交 flag</button>
    </form>
    {% if show_flag %}<div style="color:red;">flag: {{flag}}</div>{% endif %}
    <button id="hint-btn">顯示提示</button>
    <div id="hint-area"></div>
    <script>
    let hintLevel = {{ hint_level }};
    document.getElementById('hint-btn').onclick = function() {
      fetch('/q7/hint', {method: 'POST'})
        .then(r => r.json())
        .then(data => {
          document.getElementById('hint-area').innerHTML = '<div style=\"color:blue;\">' + data.hint + '</div>';
          hintLevel = data.level;
          if (hintLevel >= 2) document.getElementById('hint-btn').disabled = true;
        });
    }
    if (hintLevel >= 1) {
      fetch('/q7/hint', {method: 'POST'}).then(r => r.json()).then(data => {
        document.getElementById('hint-area').innerHTML = '<div style=\"color:blue;\">' + data.hint + '</div>';
        if (data.level >= 2) document.getElementById('hint-btn').disabled = true;
      });
    }
    </script>
    <p>{{msg}}</p>
    <a href="/">回題目列表</a>
    '''
    resp = make_response(render_template_string(html, msg=msg, flag=flag, hint_level=hint_level, show_flag=show_flag))
    # 設定 Access-Control-Allow-Origin: *
    resp.headers['Access-Control-Allow-Origin'] = '*'
    if request.method == 'OPTIONS':
        resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    # 只有跨域請求才會回傳 flag
    if request.headers.get('Origin') and request.headers.get('Origin') != request.host_url.rstrip('/'):
        show_flag = True
        resp.set_data(render_template_string(html, msg=msg, flag=flag, hint_level=hint_level, show_flag=show_flag))
    return resp

@q7_bp.route('/hint', methods=['POST'])
def q7_hint():
    hint_level = session.get('hint_q7', 0)
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
    session['hint_q7'] = hint_level
    session['hint_penalty'] = penalty
    return jsonify({'hint': hint, 'level': hint_level}) 