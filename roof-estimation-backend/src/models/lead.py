from src.models.user import db
from datetime import datetime

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    roof_area_sqm = db.Column(db.Float, nullable=True)
    estimated_cost_min = db.Column(db.Float, nullable=False)
    estimated_cost_max = db.Column(db.Float, nullable=False)
    client_name = db.Column(db.String(100), nullable=True)
    client_email = db.Column(db.String(120), nullable=True)
    client_phone = db.Column(db.String(20), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Lead {self.address}>'

    def to_dict(self):
        return {
            'id': self.id,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'roof_area_sqm': self.roof_area_sqm,
            'estimated_cost_min': self.estimated_cost_min,
            'estimated_cost_max': self.estimated_cost_max,
            'client_name': self.client_name,
            'client_email': self.client_email,
            'client_phone': self.client_phone,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

