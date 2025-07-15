from flask import Blueprint, render_template_string, request, session, send_from_directory, jsonify
from utils import gen_flag
import os

q10_bp = Blueprint('q10', __name__)

SECRET_PATH = 'super_secret_flag_path'

HINTS = [
    "本題考察資訊收集與 robots.txt，請思考如何發現隱藏路徑。",
    "先查看 /q10/robots.txt，根據 Disallow 指示找到 flag 路徑。"
]

@q10_bp.route('/', methods=['GET', 'POST'])
def q10():
    flag = gen_flag(10)
    msg = ''
    show_flag = False
    hint_level = session.get('hint_q10', 0)
    if request.method == 'POST':
        user_flag = request.form.get('flag', '').strip()
        if user_flag == flag:
            progress = session.get('progress', 1)
            solved_list = session.get('solved', [])
            if 10 not in solved_list:
                solved_list.append(10)
                session['solved'] = solved_list
            msg = '✅ 恭喜，flag 正確！全部題目完成！'
            show_flag = True
            from datetime import datetime
            session['end_time'] = datetime.now().isoformat()
        else:
            msg = '❌ flag 錯誤，請再試一次。'
            session['wrong_count'] = session.get('wrong_count', 0) + 1
    html = '''
    <h3>[Q10] Access Control Logic</h3>
    <p>請設法發現本題的 flag 隱藏路徑，取得 flag。</p>
    <div style="color:#888;font-size:13px;">（提示：有些網站會用 robots.txt 隱藏重要路徑）</div>
    <form method="post">
      <input name="flag" placeholder="flag{...}" required>
      <button type="submit">提交 flag</button>
    </form>
    <button id="hint-btn">顯示提示</button>
    <div id="hint-area"></div>
    {% if show_flag %}<div>flag: {{ flag }}</div>{% endif %}
    <p>{{msg}}</p>
    <a href="/">回題目列表</a>
    <script>
    let hintLevel = {{ hint_level }};
    document.getElementById('hint-btn').onclick = function() {
      fetch('/q10/hint', {method: 'POST'})
        .then(r => r.json())
        .then(data => {
          document.getElementById('hint-area').innerHTML = '<div style="color:blue;">' + data.hint + '</div>';
          hintLevel = data.level;
          if (hintLevel >= 2) document.getElementById('hint-btn').disabled = true;
        });
    }
    if (hintLevel >= 1) {
      fetch('/q10/hint', {method: 'POST'}).then(r => r.json()).then(data => {
        document.getElementById('hint-area').innerHTML = '<div style="color:blue;">' + data.hint + '</div>';
        if (data.level >= 2) document.getElementById('hint-btn').disabled = true;
      });
    }
    </script>
    '''
    return render_template_string(html, msg=msg, flag=flag, show_flag=show_flag, hint_level=hint_level)

@q10_bp.route('/robots.txt')
def robots():
    # robots.txt 內容指向真正的 flag 路徑
    return f"User-agent: *\nDisallow: /q10/{SECRET_PATH}\n"

@q10_bp.route(f'/{SECRET_PATH}')
def secret():
    flag = gen_flag(10)
    return f'<h4>flag: {flag}</h4><a href="/q10/">回上一頁</a>'

@q10_bp.route('/hint', methods=['POST'])
def q10_hint():
    hint_level = session.get('hint_q10', 0)
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
    session['hint_q10'] = hint_level
    session['hint_penalty'] = penalty
    return jsonify({'hint': hint, 'level': hint_level}) 