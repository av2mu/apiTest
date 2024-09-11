from database import db
from datetime import datetime

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    duration = db.Column(db.Float, nullable=False)  # Duration in minutes
    distance = db.Column(db.Float, nullable=False)  # Distance in miles
    route_nickname = db.Column(db.String(100), nullable=False)  # Name of the route
    heart_rate = db.Column(db.Integer)  # Average heart rate, optional
    date = db.Column(db.DateTime, nullable=False)  # Date and time of the workout
    image_filename = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'duration': self.duration,
            'distance': self.distance,
            'route_nickname': self.route_nickname,
            'heart_rate': self.heart_rate,
            'date': self.date.isoformat(),
            'pace': round(self.duration / self.distance, 2),
            'calories_burned': round(self.distance * 100), 
            'image_url': f"/static/uploads/{self.image_filename}" if self.image_filename else None
        }

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'weight': self.weight
        }

