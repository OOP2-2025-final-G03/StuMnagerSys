from flask import Flask, render_template, request, redirect, url_for, session, abort, g
import datetime
from flask_login import LoginManager, current_user
from models import Credential, Student, Teacher
from config import Config
from routes import blueprints
from utils.auth import load_current_user, is_logged_in, get_current_user_info


app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

@login_manager.user_loader
def load_user(user_id):
    try:
        return Credential.get(Credential.user_id == user_id)
    except Credential.DoesNotExist:
        return None

# セッション管理のミドルウェア
@app.before_request
def before_request():
    """
    リクエスト前処理：
    - セッションからユーザー情報を読み込む
    - テンプレート側で使用できるグローバル変数を設定
    """
    # セッションからユーザー情報を読み込む
    load_current_user()
    
    # テンプレートで使用するグローバル変数を設定
    g.is_logged_in = is_logged_in()
    g.user_info = get_current_user_info()
    g.user_role = g.user_info.get('role') if g.user_info else None

# コンテキストプロセッサでテンプレートに変数を渡す
@app.context_processor
def inject_user_context():
    """
    すべてのテンプレートにユーザー情報を注入する。
    """
    return {
        'is_logged_in': is_logged_in(),
        'current_user_info': get_current_user_info(),
        'user_role': g.user_role if hasattr(g, 'user_role') else None
    }

for bp in blueprints:
    app.register_blueprint(bp)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login/<role_type>')
def login(role_type):
    if role_type not in Config.ROLE_TITLES:
        abort(404)
    
    # ログイン済みの場合はダッシュボードにリダイレクト
    if is_logged_in():
        return redirect(url_for('dashboard', role_type=session.get('role', role_type)))
    
    page_title = Config.ROLE_TITLES[role_type]

    return render_template("login.html", title=page_title, role=role_type)

@app.route('/dashboard/<role_type>')
def dashboard(role_type):
    # ロールタイプの検証
    if role_type not in Config.ROLE_TITLES:
        abort(404)
    
    # セッションチェック：ログインしているかつロールが一致するか確認
    if not is_logged_in():
        return redirect(url_for('login', role_type=role_type))
    
    if session.get('role') != role_type:
        return redirect(url_for('dashboard', role_type=session.get('role')))

    template_name = f"dashboard/{role_type}.html"

    # 現在の日付を取得
    current_date = datetime.datetime.now().strftime('%Y年%m月%d日')
    
    # セッションからユーザー情報を取得
    user_info = get_current_user_info()
    user_name = user_info.get('info', {}).get('name', 'ユーザー') if user_info else 'ユーザー'

    return render_template(template_name, 
                         role=role_type, 
                         user_name=user_name,
                         user_role_name=Config.ROLE_TITLES[role_type],
                         current_date=current_date,
                         active_page='dashboard')

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
