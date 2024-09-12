import os
from datetime import datetime
import traceback
from flask import Flask, render_template, request, jsonify
from flask_restful import Api, Resource, reqparse
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from models import Workout, UserProfile
from database import db

print("Starting app creation in app.py")

def create_app():
    app = Flask(__name__)
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'workouts.db')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    db.init_app(app)
    api = Api(app)

    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created.")

    @app.route('/')
    def index():
        return render_template('index.html')

    # Request parser for workout creation
    workout_parser = reqparse.RequestParser()
    workout_parser.add_argument('profile', type=int, default=1, help='Profile ID')
    workout_parser.add_argument('duration', type=float, required=True, help='Duration in minutes is required')
    workout_parser.add_argument('distance', type=float, required=True, help='Distance in miles is required')
    workout_parser.add_argument('route_nickname', type=str, required=True, help='Route nickname is required')
    workout_parser.add_argument('date', type=str, required=True, help='Date in ISO8601 format is required')
    workout_parser.add_argument('heart_rate', type=int)
    workout_parser.add_argument('image', type=FileStorage, location='files')

    # Request parser for user profile update
    profile_parser = reqparse.RequestParser()
    profile_parser.add_argument('name', type=str, required=True, help='Name is required')
    profile_parser.add_argument('weight', type=float, required=True, help='Weight in lbs is required')

    class WorkoutAPI(Resource):
        def get(self):
            query = request.args.get('q', '')
            if query:
                workouts = Workout.query.filter(Workout.route_nickname.ilike(f'%{query}%')).order_by(Workout.date.desc()).all()
            else:
                workouts = Workout.query.order_by(Workout.date.desc()).all()

            workout_dicts = []
            profiles = {profile.id: profile for profile in UserProfile.query.all()}
            default_profile = UserProfile(id=0, name="Unknown", weight=150)  # Default profile

            for workout in workouts:
                workout_dict = workout.to_dict()
                profile = profiles.get(workout.profile, default_profile)
                workout_dict['profile_name'] = profile.name
                workout_dict['calories_burned'] = workout.calculate_calories_burned(profile.weight)
                workout_dicts.append(workout_dict)

            return workout_dicts

        def post(self):
            if not request.content_type.startswith('multipart/form-data'):
                return {"message": "Unsupported Media Type. Use multipart/form-data for workout creation."}, 415
            
            try:
                # Handle form data manually
                data = request.form.to_dict()
                image = request.files.get('image')
                
                new_workout = Workout(
                    profile=int(data.get('profile', 1)),
                    duration=float(data['duration']),
                    distance=float(data['distance']),
                    route_nickname=data['route_nickname'],
                    date=datetime.fromisoformat(data['date']),
                    heart_rate=int(data['heart_rate']) if data.get('heart_rate') else None
                )
                
                if image and image.filename != '':
                    filename = secure_filename(image.filename)
                    image_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
                    new_workout.image_filename = image_filename
                
                db.session.add(new_workout)
                db.session.commit()
                
                profile = UserProfile.query.get(new_workout.profile)
                if not profile:
                    # If the profile doesn't exist, create a default one
                    profile = UserProfile(id=1, name="Unknown", weight=150)
                    db.session.add(profile)
                    db.session.commit()
                
                calories_burned = new_workout.calculate_calories_burned(profile.weight)

                response_data = new_workout.to_dict()
                response_data['calories_burned'] = calories_burned

                return response_data, 201
            except Exception as e:
                print("Error occurred:")
                print(traceback.format_exc())
                return {'message': str(e)}, 500

        def delete(self, id):
            workout = Workout.query.get_or_404(id)
            db.session.delete(workout)
            db.session.commit()
            return '', 204

    class UserProfileAPI(Resource):
        def get(self, id=None):
            if id is None:
                profiles = UserProfile.query.all()
                if not profiles:
                    default_profile = UserProfile(id=1, name="Unknown", weight=150)  # Default values
                    db.session.add(default_profile)
                    db.session.commit()
                    profiles = [default_profile]
                return [profile.to_dict() for profile in profiles]
            else:
                profile = UserProfile.query.get_or_404(id)
                return profile.to_dict()

        def put(self, id=None):
            if not request.is_json:
                return {"message": "Unsupported Media Type. Use application/json for profile updates."}, 415
            
            if id is None:
                # Creating a new profile
                profile = UserProfile()
                db.session.add(profile)
            else:
                # Updating existing profile
                profile = UserProfile.query.get_or_404(id)

            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str, required=True, help='Name is required')
            parser.add_argument('weight', type=float, required=True, help='Weight in lbs is required')
            args = parser.parse_args()

            profile.name = args['name']
            profile.weight = args['weight']

            db.session.commit()
            return profile.to_dict(), 201 if id is None else 200

        def patch(self, id):
            if not request.is_json:
                return {"message": "Unsupported Media Type. Use application/json for profile updates."}, 415
            
            profile = UserProfile.query.get_or_404(id)
            parser = reqparse.RequestParser()
            parser.add_argument('weight', type=float, required=True, help='Weight in lbs is required')
            args = parser.parse_args()

            profile.weight = args['weight']
            db.session.commit()
            return profile.to_dict()

        def delete(self, id):
            profile = UserProfile.query.get_or_404(id)
            db.session.delete(profile)
            db.session.commit()
            return '', 204

    api.add_resource(WorkoutAPI, '/api/v1/workouts', '/api/v1/workouts/<int:id>')
    api.add_resource(UserProfileAPI, '/api/v1/profile', '/api/v1/profile/<int:id>')

    print("App creation completed in app.py")
    return app

if __name__ == '__main__':
    app = create_app()
    print(f"Database file location: {app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')}")
    app.run(debug=True)