from flask import Flask, render_template
from flask_login import login_required, current_user
import datetime
from models import User, initialize_database, Student, Teacher
from routes import blueprints
from utils import login_manager, Config, role_required, register_login_signals


app = Flask(__name__)
app.config.from_object(Config)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

register_login_signals(app)

for bp in blueprints:
    app.register_blueprint(bp)
        
@app.context_processor
def inject_user():
    if current_user.profile_dict():
        return dict(
            user_name=current_user.profile_dict().get('name', 'ユーザー'),
            user_role=current_user.role,
        )
    return {}

@app.route('/')
def index():
    return render_template("login.html", title="学生管理システム")

@app.route('/dashboard')
@role_required('admin', 'teacher', 'student')
@login_required
def dashboard():
    role_type = current_user.role

    template_name = f"dashboard/{role_type}.html"

    # 現在の日付を取得
    current_date = datetime.datetime.now().strftime('%Y年%m月%d日')

    return render_template(template_name,
                         current_date=current_date,
                         active_page='dashboard')

if __name__ == '__main__':
    # データベースの初期化
    initialize_database()
    
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
