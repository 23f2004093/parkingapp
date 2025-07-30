from flask import Flask
from controllers.admin import admin_blueprint
from controllers.user import user_blueprint
from controllers.auth import auth_blueprint
from models.models import db, Admin, User
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'SUPERSECRETKEY'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # FIXED: User loader that properly handles different user types
    @login_manager.user_loader
    def load_user(user_id):
        if user_id.startswith('admin_'):
            admin_id = user_id.replace('admin_', '')
            return Admin.query.get(int(admin_id))
        elif user_id.startswith('user_'):
            actual_user_id = user_id.replace('user_', '')
            return User.query.get(int(actual_user_id))
        return None

    # Register Blueprints
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(auth_blueprint)

    with app.app_context():
        db.create_all()
        # Add default admin if not exists
        if not Admin.query.first():
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin created: username='admin', password='admin123'")
    
    return app

if __name__ == "__main__":
    app = create_app()
    print("🚀 Starting Parking Management System...")
    print("🌐 Access at: http://127.0.0.1:5000")
    print("👤 Admin login: username='admin', password='admin123'")
    app.run(debug=True, host='127.0.0.1', port=5000)
