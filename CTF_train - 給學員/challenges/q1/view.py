from flask import Blueprint, render_template_string, request, session, jsonify
from utils import gen_flag

q1_bp = Blueprint('q1', __name__)

HINTS = [
    "本題考察資訊收集與原始碼觀察，flag 藏在你看不到的地方。",
    "請用 F12 或檢視原始碼，找找看有沒有隱藏的 HTML 註解，裡面可能藏有 flag。"
]

@q1_bp.route('/', methods=['GET', 'POST'])
def q1():
    flag = gen_flag(1)
    msg = ''
    hint_level = session.get('hint_q1', 0)
    if request.method == 'POST':
        user_flag = request.form.get('flag', '').strip()
        if user_flag == flag:
            progress = session.get('progress', 1)
            solved_list = session.get('solved', [])
            if 1 not in solved_list:
                solved_list.append(1)
                session['solved'] = solved_list
                if progress < 2:
                    session['progress'] = 2
            msg = '✅ 恭喜，flag 正確！已解鎖下一題。'
        else:
            msg = '❌ flag 錯誤，請再試一次。'
    html = '''
    <h3>[Q1] Service Discovery</h3>
    <p>本服務啟動時會在首頁原始碼中隱藏一段特殊資訊，請用 F12 或原始碼檢視功能找到 flag。</p>
    <form method="post">
      <input name="flag" placeholder="flag{...}" required>
      <button type="submit">提交</button>
    </form>
    <button id="hint-btn">顯示提示</button>
    <div id="hint-area"></div>
    <script>
    let hintLevel = {{ hint_level }};
    document.getElementById('hint-btn').onclick = function() {
      fetch('/q1/hint', {method: 'POST'})
        .then(r => r.json())
        .then(data => {
          document.getElementById('hint-area').innerHTML = '<div style="color:blue;">' + data.hint + '</div>';
          hintLevel = data.level;
          if (hintLevel >= 2) document.getElementById('hint-btn').disabled = true;
        });
    }
    if (hintLevel >= 1) {
      fetch('/q1/hint', {method: 'POST'}).then(r => r.json()).then(data => {
        document.getElementById('hint-area').innerHTML = '<div style="color:blue;">' + data.hint + '</div>';
        if (data.level >= 2) document.getElementById('hint-btn').disabled = true;
      });
    }
    </script>
    {% if show_flag %}<div>flag: {{ flag }}</div>{% endif %}
    <p>{{msg}}</p>
    <a href="/">回題目列表</a>
    <!-- {{ flag }} -->
    '''
    return render_template_string(html, msg=msg, flag=flag, show_flag=False, hint_level=hint_level)

@q1_bp.route('/hint', methods=['POST'])
def q1_hint():
    hint_level = session.get('hint_q1', 0)
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
    session['hint_q1'] = hint_level
    session['hint_penalty'] = penalty
    return jsonify({'hint': hint, 'level': hint_level}) 