"""
アプリケーションの設定
"""
import os
from datetime import timedelta


class Config:
    """
    アプリケーション全体の設定クラス。

    flaskのappに読み込んだはずです、current_app.config["KEY"]でアクセスできます。
    使用する際にfrom flask import current_appで導入してください。
    """

    # アプリケーション名
    APP_NAME = "学生管理システム"

    # セッション管理用の秘密鍵（開発時のみ使用）
    SECRET_KEY = "secret-key-for-development"

    HOST = os.getenv("HOST", "0.0.0.0") # ホスト名
    PORT = int(os.getenv("PORT", "8000")) # ポート番号

    # デバッグモード（開発時のみ True）
    DEBUG = True

    # セッション設定
    SESSION_PERMANENT = False # セッションが期限切れになった後でも保持するかどうか
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60) # セッションの有効期限（分）

    # Remember Me機能の設定
    REMEMBER_COOKIE_DURATION = timedelta(days=7)  # Remember Meクッキーの有効期間（7日間）
    REMEMBER_COOKIE_SECURE = False  # 本番環境ではTrue推奨（HTTPS環境でのみ送信）
    REMEMBER_COOKIE_HTTPONLY = True  # JavaScriptからアクセス不可
    REMEMBER_COOKIE_SAMESITE = 'Lax'  # CSRF対策

    # ユーザーロールと表示名のマッピング
    ROLE_TITLES = {
        'student': '学生',
        'teacher': '教師',
        'admin': '管理者'
    }

