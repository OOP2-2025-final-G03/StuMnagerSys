from datetime import datetime
from flask import Flask, render_template, redirect, url_for
from flask_login import login_required, current_user

from models import initialize_database
from routes import blueprints
from utils import login_manager, Config, role_required, register_login_signals

# アプリケーションの設定
app = Flask(__name__)
app.config.from_object(Config)

# ログインマネージャーの設定
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# ログイン信号の登録
register_login_signals(app)

# ブループリントの登録
for bp in blueprints:
    app.register_blueprint(bp)

# コンテキストプロセッサの設定(ユーザー情報をテンプレートに注入)
@app.context_processor
def inject_user():
    """
    ユーザー情報をテンプレートに注入するコンテキストプロセッサ
    
    Returns:
        dict: ユーザー情報の辞書(ユーザーがログインしていない場合は空の辞書)
    """
    if current_user.profile_dict():
        return dict(
            user_name=current_user.profile_dict().get('name', 'ユーザー'),
            user_role=current_user.role,
            current_date=datetime.now().strftime('%Y年%m月%d日'),
            active_template=f"dashboard/{current_user.role}.html"
        )
    return {}

# ルートパスの設定(ログインページを表示)
@app.route('/')
def index():
    return render_template("login.html", title="学生管理システム")

@app.route('/dashboard')
@role_required('admin', 'teacher', 'student')
@login_required
def dashboard():
    
    template_name = f"dashboard/{current_user.role}.html"

    return render_template(template_name,
                         active_page='dashboard')

if __name__ == '__main__':
    # データベースの初期化
    initialize_database()
    
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)