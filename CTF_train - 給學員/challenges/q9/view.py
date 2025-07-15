from flask import Blueprint, render_template_string, request, session, jsonify
from utils import gen_flag
import os

q9_bp = Blueprint('q9', __name__)
UPLOAD_FOLDER = 'challenges/q9/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HINTS = [
    "本題考察檔案上傳繞過，請觀察副檔名檢查邏輯。",
    "嘗試上傳 .php 檔案，看看能否繞過檢查取得 flag。"
]

@q9_bp.route('/', methods=['GET', 'POST'])
def q9():
    flag = gen_flag(9)
    msg = ''
    show_flag = False
    hint_level = session.get('hint_q9', 0)
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            filename = file.filename
            # 只允許 .png
            if filename.endswith('.png'):
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                msg = '只允許上傳 .png 檔案！'
            elif filename.endswith('.php'):
                # 繞過副檔名檢查，取得 flag
                progress = session.get('progress', 1)
                solved_list = session.get('solved', [])
                if 9 not in solved_list:
                    solved_list.append(9)
                    session['solved'] = solved_list
                    if progress < 10:
                        session['progress'] = 10
                msg = '✅ 恭喜，flag 正確！已解鎖下一題。'
                show_flag = True
            else:
                msg = '只允許上傳 .png 檔案！'
        else:
            msg = '請選擇檔案！'
    html = '''
    <h3>[Q9] File Upload Bypass</h3>
    <p>請設法繞過副檔名檢查，上傳 .php 檔案取得 flag。</p>
    <form method="post" enctype="multipart/form-data">
      <input type="file" name="file" required>
      <button type="submit">上傳</button>
    </form>
    <button id="hint-btn">顯示提示</button>
    <div id="hint-area"></div>
    {% if show_flag %}<div>flag: {{ flag }}</div>{% endif %}
    <p>{{msg}}</p>
    <a href="/">回題目列表</a>
    <script>
    let hintLevel = {{ hint_level }};
    document.getElementById('hint-btn').onclick = function() {
      fetch('/q9/hint', {method: 'POST'})
        .then(r => r.json())
        .then(data => {
          document.getElementById('hint-area').innerHTML = '<div style="color:blue;">' + data.hint + '</div>';
          hintLevel = data.level;
          if (hintLevel >= 2) document.getElementById('hint-btn').disabled = true;
        });
    }
    if (hintLevel >= 1) {
      fetch('/q9/hint', {method: 'POST'}).then(r => r.json()).then(data => {
        document.getElementById('hint-area').innerHTML = '<div style="color:blue;">' + data.hint + '</div>';
        if (data.level >= 2) document.getElementById('hint-btn').disabled = true;
      });
    }
    </script>
    '''
    return render_template_string(html, msg=msg, flag=flag, show_flag=show_flag, hint_level=hint_level)

@q9_bp.route('/hint', methods=['POST'])
def q9_hint():
    hint_level = session.get('hint_q9', 0)
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
    session['hint_q9'] = hint_level
    session['hint_penalty'] = penalty
    return jsonify({'hint': hint, 'level': hint_level}) 