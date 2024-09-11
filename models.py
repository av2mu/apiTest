from database import db
from datetime import datetime

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    duration = db.Column(db.Float, nullable=False)  # Duration in minutes
    distance = db.Column(db.Float, nullable=False)  # Distance in miles
    route_nickname = db.Column(db.String(100), nullable=False)  # Name of the route
    heart_rate = db.Column(db.Integer)  # Average heart rate, optional
    date = db.Column(db.DateTime, nullable=False)  # Date and time of the workout
    image_filename = db.Column(db.String(255)) # Filename of the image

    def to_dict(self):
        return {
            'id': self.id,
            'duration': self.duration,
            'distance': self.distance,
            'route_nickname': self.route_nickname,
            'heart_rate': self.heart_rate,
            'date': self.date.isoformat(),
            'pace': round(self.duration / self.distance, 2),
            'image_url': f"/static/uploads/{self.image_filename}" if self.image_filename else None
        }

    def calculate_calories_burned(self, weight_lbs):
        # Convert weight from lbs to kg for calculation
        weight_kg = weight_lbs * 0.453592
        
        # Calculate speed in mph
        speed_mph = (self.distance / self.duration) * 60
        
        # Determine MET value based on speed (mph)
        if speed_mph < 5:
            met = 6.0
        elif speed_mph < 6:
            met = 8.3
        elif speed_mph < 7:
            met = 9.8
        elif speed_mph < 8:
            met = 11.0
        elif speed_mph < 9:
            met = 11.8
        else:
            met = 12.8

        # Calculate calories burned
        # Formula: calories = MET * weight in kg * duration in hours
        duration_hours = self.duration / 60
        calories = met * weight_kg * duration_hours
        
        return round(calories, 2)

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)  # in lbs

    def to_dict(self):
        return {
            'id': self.id,
            'weight': self.weight
        }

