import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.lead import Lead
from src.models.conversation import ConversationSession
from src.routes.user import user_bp
from src.routes.estimation import estimation_bp
from src.routes.conversation import conversation_bp
from src.routes.google_api import google_api_bp  # ⭐ NOUVEAU

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

from fastapi.middleware.cors import CORSMiddleware

# Configuration CORS plus détaillée
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://soumission-toirure-05f6ead9f71b.herokuapp.com",
        "https://jldpkzrj.manus.space",
        "https://e5h6i7cn08lj.manus.space"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type", 
        "Authorization", 
        "Accept", 
        "Origin", 
        "X-Requested-With"
    ],
)

# Ajouter handler OPTIONS pour preflight
@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    return {"message": "OK"}

# Registration des blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(estimation_bp, url_prefix='/api')
app.register_blueprint(conversation_bp, url_prefix='/api/conversation')
app.register_blueprint(google_api_bp, url_prefix='/api')  # ⭐ NOUVEAU

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
