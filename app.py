from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse, inputs
from werkzeug.utils import secure_filename
from models import Workout, UserProfile
from database import db
from datetime import datetime
import os

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workouts.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    
    db.init_app(app)
    api = Api(app)

    with app.app_context():
        db.create_all()

    # Request parser for workout creation
    workout_parser = reqparse.RequestParser()
    workout_parser.add_argument('duration', type=float, required=True, help='Duration in minutes is required')
    workout_parser.add_argument('distance', type=float, required=True, help='Distance in miles is required')
    workout_parser.add_argument('route_nickname', type=str, required=True, help='Route nickname is required')
    workout_parser.add_argument('date', type=inputs.datetime_from_iso8601, required=True, help='Date in ISO8601 format is required')
    workout_parser.add_argument('heart_rate', type=int)
    workout_parser.add_argument('image', type=inputs.FileStorage, location='files')

    # Request parser for user profile update
    profile_parser = reqparse.RequestParser()
    profile_parser.add_argument('weight', type=float, required=True, help='Weight in lbs is required')

    class WorkoutListAPI(Resource):
        def get(self):
            workouts = Workout.query.order_by(Workout.date.desc()).all()
            user_profile = UserProfile.query.first()
            weight_lbs = user_profile.weight if user_profile else 154  # Default weight in lbs

            workout_dicts = []
            for workout in workouts:
                workout_dict = workout.to_dict()
                workout_dict['calories_burned'] = workout.calculate_calories_burned(weight_lbs)
                workout_dicts.append(workout_dict)

            return workout_dicts

        def post(self):
            args = workout_parser.parse_args()
            
            new_workout = Workout(
                duration=args['duration'],
                distance=args['distance'],
                route_nickname=args['route_nickname'],
                date=args['date'],
                heart_rate=args['heart_rate']
            )
            
            if args['image']:
                image = args['image']
                if image.filename != '':
                    filename = secure_filename(image.filename)
                    image_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
                    new_workout.image_filename = image_filename
            
            db.session.add(new_workout)
            db.session.commit()
            
            return new_workout.to_dict(), 201

    class WorkoutAPI(Resource):
        def delete(self, id):
            workout = Workout.query.get_or_404(id)
            db.session.delete(workout)
            db.session.commit()
            return '', 204

    class UserProfileAPI(Resource):
        def get(self):
            profile = UserProfile.query.first()
            if not profile:
                profile = UserProfile(weight=154)  # Default weight in lbs
                db.session.add(profile)
                db.session.commit()
            return profile.to_dict()

        def put(self):
            args = profile_parser.parse_args()
            profile = UserProfile.query.first()
            if not profile:
                profile = UserProfile(weight=args['weight'])
                db.session.add(profile)
            else:
                profile.weight = args['weight']
            
            db.session.commit()
            return profile.to_dict()

    class WorkoutSearchAPI(Resource):
        def get(self):
            query = request.args.get('q', '')
            workouts = Workout.query.filter(Workout.route_nickname.ilike(f'%{query}%')).order_by(Workout.date.desc()).all()
            user_profile = UserProfile.query.first()
            weight = user_profile.weight if user_profile else 150  # Default weight if not set (150 lbs)

            workout_dicts = []
            for workout in workouts:
                workout_dict = workout.to_dict()
                workout_dict['calories_burned'] = workout.calculate_calories_burned(weight)
                workout_dicts.append(workout_dict)

            return workout_dicts

    api.add_resource(WorkoutListAPI, '/api/v1/workouts')
    api.add_resource(WorkoutAPI, '/api/v1/workouts/<int:id>')
    api.add_resource(UserProfileAPI, '/api/v1/profile')
    api.add_resource(WorkoutSearchAPI, '/api/v1/workouts/search')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)