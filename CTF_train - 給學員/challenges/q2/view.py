from flask import Blueprint, render_template_string, request, session, redirect, url_for, jsonify
from utils import gen_flag

q2_bp = Blueprint('q2', __name__)

HINTS = [
    "本題考察 HTML 隱藏元素與註解資訊，flag 不會直接顯示在畫面上。",
    "請用 F12 或檢視原始碼，找找看有沒有隱藏 input 欄位或註解，裡面可能藏有 flag。"
]

@q2_bp.route('/', methods=['GET', 'POST'])
def q2():
    flag = gen_flag(2)
    msg = ''
    hint_level = session.get('hint_q2', 0)
    if request.method == 'POST':
        user_flag = request.form.get('flag', '').strip()
        if user_flag == flag:
            progress = session.get('progress', 1)
            solved_list = session.get('solved', [])
            if 2 not in solved_list:
                solved_list.append(2)
                session['solved'] = solved_list
                if progress < 3:
                    session['progress'] = 3
            msg = '✅ 恭喜，flag 正確！已解鎖下一題。'
        else:
            msg = '❌ flag 錯誤，請再試一次。'
    html = '''
    <h3>[Q2] Hidden in Source</h3>
    <p>本頁面有一個隱藏欄位或註解，內含 flag，請用 DevTools 或原始碼檢視找到。</p>
    <form method="post">
      <input name="flag" placeholder="flag{...}" required>
      <button type="submit">提交</button>
      <input type="hidden" id="flag_hidden" value="{{ flag }}">
    </form>
    <button id="hint-btn">顯示提示</button>
    <div id="hint-area"></div>
    <script>
    let hintLevel = {{ hint_level }};
    document.getElementById('hint-btn').onclick = function() {
      fetch('/q2/hint', {method: 'POST'})
        .then(r => r.json())
        .then(data => {
          document.getElementById('hint-area').innerHTML = '<div style="color:blue;">' + data.hint + '</div>';
          hintLevel = data.level;
          if (hintLevel >= 2) document.getElementById('hint-btn').disabled = true;
        });
    }
    if (hintLevel >= 1) {
      fetch('/q2/hint', {method: 'POST'}).then(r => r.json()).then(data => {
        document.getElementById('hint-area').innerHTML = '<div style="color:blue;">' + data.hint + '</div>';
        if (data.level >= 2) document.getElementById('hint-btn').disabled = true;
      });
    }
    </script>
    <p>{{msg}}</p>
    <a href="/">回題目列表</a>
    '''
    return render_template_string(html, msg=msg, flag=flag, hint_level=hint_level)

@q2_bp.route('/hint', methods=['POST'])
def q2_hint():
    hint_level = session.get('hint_q2', 0)
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
    session['hint_q2'] = hint_level
    session['hint_penalty'] = penalty
    return jsonify({'hint': hint, 'level': hint_level}) 