from flask import Blueprint, render_template_string, request, session, jsonify
from utils import gen_flag

q4_bp = Blueprint('q4', __name__)

HINTS = [
    "本題考察 Reflected XSS，請思考輸入內容如何影響頁面顯示。",
    "嘗試在搜尋框輸入 <script>alert(1)</script>，觀察是否能彈出視窗。"
]

@q4_bp.route('/', methods=['GET', 'POST'])
def q4():
    flag = gen_flag(4)
    msg = ''
    payload = request.args.get('search', '')
    show_flag = False
    hint_level = session.get('hint_q4', 0)
    if request.method == 'POST':
        user_flag = request.form.get('flag', '').strip()
        if user_flag == flag:
            progress = session.get('progress', 1)
            solved_list = session.get('solved', [])
            if 4 not in solved_list:
                solved_list.append(4)
                session['solved'] = solved_list
                if progress < 5:
                    session['progress'] = 5
            msg = '✅ 恭喜，flag 正確！已解鎖下一題。'
        else:
            msg = '❌ flag 錯誤，請再試一次。'
    html = '''
    <h3>[Q4] Simple XSS</h3>
    <p>請嘗試在下方搜尋框輸入 payload，觸發 alert 並取得 flag。</p>
    <form method="get">
      <input name="search" placeholder="請輸入搜尋內容">
      <button type="submit">搜尋</button>
    </form>
    <div>搜尋結果：''' + payload + '''</div>
    <form method="post">
      <input name="flag" placeholder="flag{...}" required>
      <button type="submit">提交 flag</button>
    </form>
    <button id="hint-btn">顯示提示</button>
    <div id="hint-area"></div>
    <script>
    let hintLevel = {{ hint_level }};
    document.getElementById('hint-btn').onclick = function() {
      fetch('/q4/hint', {method: 'POST'})
        .then(r => r.json())
        .then(data => {
          document.getElementById('hint-area').innerHTML = '<div style="color:blue;">' + data.hint + '</div>';
          hintLevel = data.level;
          if (hintLevel >= 2) document.getElementById('hint-btn').disabled = true;
        });
    }
    if (hintLevel >= 1) {
      fetch('/q4/hint', {method: 'POST'}).then(r => r.json()).then(data => {
        document.getElementById('hint-area').innerHTML = '<div style="color:blue;">' + data.hint + '</div>';
        if (data.level >= 2) document.getElementById('hint-btn').disabled = true;
      });
    }
    </script>
    <p>{{msg}}</p>
    <a href="/">回題目列表</a>
    '''
    # flag 只在 alert 彈出時顯示，需手動觸發
    if payload == '<script>alert(1)</script>':
        html += f'<script>window.onload=function(){{alert("{flag}")}}</script>'
    return render_template_string(html, msg=msg, flag=flag, hint_level=hint_level)

@q4_bp.route('/hint', methods=['POST'])
def q4_hint():
    hint_level = session.get('hint_q4', 0)
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
    session['hint_q4'] = hint_level
    session['hint_penalty'] = penalty
    return jsonify({'hint': hint, 'level': hint_level}) 