import os
from datetime import datetime

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
    workout_parser.add_argument('duration', type=float, required=True, help='Duration in minutes is required')
    workout_parser.add_argument('distance', type=float, required=True, help='Distance in miles is required')
    workout_parser.add_argument('route_nickname', type=str, required=True, help='Route nickname is required')
    workout_parser.add_argument('date', type=str, required=True, help='Date in ISO8601 format is required')
    workout_parser.add_argument('heart_rate', type=int)
    workout_parser.add_argument('image', type=FileStorage, location='files')

    # Request parser for user profile update
    profile_parser = reqparse.RequestParser()
    profile_parser.add_argument('weight', type=float, required=True, help='Weight in lbs is required')

    class WorkoutListAPI(Resource):
        def get(self):
            workouts = Workout.query.order_by(Workout.date.desc()).all()
            user_profile = UserProfile.query.first()
            weight_lbs = user_profile.weight if user_profile else 150  # Default weight in lbs

            workout_dicts = []
            for workout in workouts:
                workout_dict = workout.to_dict()
                workout_dict['calories_burned'] = workout.calculate_calories_burned(weight_lbs)
                workout_dicts.append(workout_dict)

            return workout_dicts

        def post(self):
            print("Content-Type:", request.content_type)
            print("Form Data:", request.form)
            print("Files:", request.files)
            
            try:
                if request.content_type.startswith('multipart/form-data'):
                    # Handle form data manually
                    duration = request.form.get('duration')
                    distance = request.form.get('distance')
                    route_nickname = request.form.get('route_nickname')
                    date = request.form.get('date')
                    heart_rate = request.form.get('heart_rate')
                    image = request.files.get('image')
                else:
                    # For JSON data
                    data = request.get_json()
                    duration = data.get('duration')
                    distance = data.get('distance')
                    route_nickname = data.get('route_nickname')
                    date = data.get('date')
                    heart_rate = data.get('heart_rate')
                    image = None

                print("Parsed data:", {
                    'duration': duration,
                    'distance': distance,
                    'route_nickname': route_nickname,
                    'date': date,
                    'heart_rate': heart_rate,
                    'image': image.filename if image else None
                })
                
                new_workout = Workout(
                    duration=float(duration),
                    distance=float(distance),
                    route_nickname=route_nickname,
                    date=datetime.fromisoformat(date),
                    heart_rate=int(heart_rate) if heart_rate else None
                )
                
                if image and image.filename != '':
                    filename = secure_filename(image.filename)
                    image_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
                    new_workout.image_filename = image_filename
                
                db.session.add(new_workout)
                db.session.commit()
                
                # Get the user's weight (or use default)
                user_profile = UserProfile.query.first()
                weight_lbs = user_profile.weight if user_profile else 150  # Default weight in lbs
                
                # Calculate calories burned
                calories_burned = new_workout.calculate_calories_burned(weight_lbs)
                
                response_data = new_workout.to_dict()
                response_data['calories_burned'] = calories_burned
                
                return response_data, 201
            except Exception as e:
                print("Error occurred:")
                print(traceback.format_exc())
                return {'message': str(e)}, 500

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

    print("App creation completed in app.py")
    return app

if __name__ == '__main__':
    app = create_app()
    print(f"Database file location: {app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')}")
    app.run(debug=True)