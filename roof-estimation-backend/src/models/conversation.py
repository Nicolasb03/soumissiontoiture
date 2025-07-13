from src.models.user import db
from datetime import datetime
import json

class ConversationSession(db.Model):
    id = db.Column(db.String(36), primary_key=True)  # UUID
    address = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    roof_area_sqm = db.Column(db.Float, nullable=True)
    current_question_id = db.Column(db.String(50), nullable=True)
    conversation_data = db.Column(db.Text, nullable=True)  # JSON string
    estimated_cost_min = db.Column(db.Float, nullable=True)
    estimated_cost_max = db.Column(db.Float, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ConversationSession {self.id}>'

    def get_conversation_data(self):
        """Récupère les données de conversation sous forme de dictionnaire"""
        if self.conversation_data:
            return json.loads(self.conversation_data)
        return {}

    def set_conversation_data(self, data):
        """Stocke les données de conversation sous forme de JSON"""
        self.conversation_data = json.dumps(data)

    def to_dict(self):
        return {
            'id': self.id,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'roof_area_sqm': self.roof_area_sqm,
            'current_question_id': self.current_question_id,
            'conversation_data': self.get_conversation_data(),
            'estimated_cost_min': self.estimated_cost_min,
            'estimated_cost_max': self.estimated_cost_max,
            'is_completed': self.is_completed,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

