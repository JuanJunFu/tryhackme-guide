from flask import Blueprint, render_template_string, request, session, make_response, jsonify
from utils import gen_flag
import base64
import json

q6_bp = Blueprint('q6', __name__)

HINTS = [
    "本題考察 JWT 結構與權限竄改，請觀察 cookie 裡的 jwt。",
    "將 jwt payload 內的 admin 改為 true，重新整理頁面。"
]

@q6_bp.route('/', methods=['GET', 'POST'])
def q6():
    flag = gen_flag(6)
    msg = ''
    jwt = request.cookies.get('jwt', None)
    show_flag = False
    hint_level = session.get('hint_q6', 0)

    # 預設 JWT: {"admin": false}
    if not jwt:
        header = base64.urlsafe_b64encode(json.dumps({"alg": "none", "typ": "JWT"}).encode()).decode().rstrip('=')
        payload = base64.urlsafe_b64encode(json.dumps({"admin": False}).encode()).decode().rstrip('=')
        jwt = f"{header}.{payload}."
        resp = make_response(render_template_string(
            '''
            <h3>[Q6] JWT Decode</h3>
            <p>請設法讓 JWT payload 內 admin=true，取得 flag。</p>
            <form method="post">
              <input name="flag" placeholder="flag{...}" required>
              <button type="submit">提交 flag</button>
            </form>
            <button id="hint-btn">顯示提示</button>
            <div id="hint-area"></div>
            <script>
            let hintLevel = {{ hint_level }};
            document.getElementById('hint-btn').onclick = function() {
              fetch('/q6/hint', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                  document.getElementById('hint-area').innerHTML = '<div style="color:blue;">' + data.hint + '</div>';
                  hintLevel = data.level;
                  if (hintLevel >= 2) document.getElementById('hint-btn').disabled = true;
                });
            }
            if (hintLevel >= 1) {
              fetch('/q6/hint', {method: 'POST'}).then(r => r.json()).then(data => {
                document.getElementById('hint-area').innerHTML = '<div style="color:blue;">' + data.hint + '</div>';
                if (data.level >= 2) document.getElementById('hint-btn').disabled = true;
              });
            }
            </script>
            <p>{{msg}}</p>
            <a href="/">回題目列表</a>
            ''', msg=msg, flag=flag, show_flag=show_flag, hint_level=hint_level
        ))
        resp.set_cookie('jwt', jwt)
        return resp

    if request.method == 'POST':
        user_flag = request.form.get('flag', '').strip()
        if user_flag == flag:
            progress = session.get('progress', 1)
            solved_list = session.get('solved', [])
            if 6 not in solved_list:
                solved_list.append(6)
                session['solved'] = solved_list
                if progress < 7:
                    session['progress'] = 7
            msg = '✅ 恭喜，flag 正確！已解鎖下一題。'
        else:
            msg = '❌ flag 錯誤，請再試一次。'
    try:
        parts = jwt.split('.')
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
        if payload.get('admin') == True:
            show_flag = True
    except Exception:
        pass
    resp = make_response(render_template_string(
        '''
        <h3>[Q6] JWT Decode</h3>
        <p>請設法讓 JWT payload 內 admin=true，取得 flag。</p>
        <form method="post">
          <input name="flag" placeholder="flag{...}" required>
          <button type="submit">提交 flag</button>
        </form>
        <button id="hint-btn">顯示提示</button>
        <div id="hint-area"></div>
        <script>
        let hintLevel = {{ hint_level }};
        document.getElementById('hint-btn').onclick = function() {
          fetch('/q6/hint', {method: 'POST'})
            .then(r => r.json())
            .then(data => {
              document.getElementById('hint-area').innerHTML = '<div style="color:blue;">' + data.hint + '</div>';
              hintLevel = data.level;
              if (hintLevel >= 2) document.getElementById('hint-btn').disabled = true;
            });
        }
        if (hintLevel >= 1) {
          fetch('/q6/hint', {method: 'POST'}).then(r => r.json()).then(data => {
            document.getElementById('hint-area').innerHTML = '<div style="color:blue;">' + data.hint + '</div>';
            if (data.level >= 2) document.getElementById('hint-btn').disabled = true;
          });
        }
        </script>
        {% if show_flag %}<div>flag: {{ flag }}</div>{% endif %}
        <p>{{msg}}</p>
        <a href="/">回題目列表</a>
        ''', msg=msg, flag=flag, show_flag=show_flag, hint_level=hint_level
    ))
    resp.set_cookie('jwt', jwt)
    return resp

@q6_bp.route('/hint', methods=['POST'])
def q6_hint():
    hint_level = session.get('hint_q6', 0)
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
    session['hint_q6'] = hint_level
    session['hint_penalty'] = penalty
    return jsonify({'hint': hint, 'level': hint_level}) 