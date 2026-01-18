from datetime import datetime
import argparse
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

def parse_args():
    """
    コマンドライン引数を解析する
    
    Returns:
        argparse.Namespace: 解析された引数
    """
    parser = argparse.ArgumentParser(description="学生管理システム")

    parser.add_argument(
        "--host",
        type=str,
        default=Config.HOST,
        help="サーバーのホスト（例: 0.0.0.0）"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=Config.PORT,
        help="サーバーのポート番号（例: 8080）"
    )

    parser.add_argument(
        "--debug",
        type=bool,
        default=Config.DEBUG,
        help="デバッグモードを有効化"
    )

    return parser.parse_args()

if __name__ == '__main__':
    # データベースの初期化
    initialize_database()
    
    args = parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug)
