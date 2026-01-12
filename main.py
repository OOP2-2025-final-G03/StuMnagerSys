from flask import Flask, render_template, request, redirect, url_for, session, abort
import datetime
from models import Password, initialize_database
from utils.config import Config
from routes import blueprints
from routes.auth import login_manager


app = Flask(__name__)
app.config.from_object(Config)
login_manager.init_app(app)
login_manager.login_view = 'auth.login_page'

for bp in blueprints:
    app.register_blueprint(bp)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/dashboard/<role_type>')
def dashboard(role_type):
    # ロールタイプの検証
    if role_type not in Config.ROLE_TITLES:
        abort(404)
    
    # TODO:重要
    # ここでセッションや認証情報をチェックして、
    # ユーザーが正しいロールでログインしているか確認する必要があります。
    # if session.get('role') != role_type:
    #     return redirect(url_for('login', role_type=role_type))

    template_name = f"dashboard/{role_type}.html"

    # 現在の日付を取得
    current_date = datetime.datetime.now().strftime('%Y年%m月%d日')

    return render_template(template_name, 
                         role=role_type, 
                         user_name=role_type, # 仮のユーザー名
                         user_role_name=Config.ROLE_TITLES[role_type],
                         current_date=current_date,
                         active_page='dashboard')

if __name__ == '__main__':
    # データベースの初期化
    initialize_database()
    
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
