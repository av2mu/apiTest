from flask import Flask, request, jsonify, abort, render_template, send_from_directory
from werkzeug.utils import secure_filename
from models import Workout, UserProfile
from database import db
from datetime import datetime
import os
import logging
from flask_restful import Api, Resource, reqparse, inputs
from werkzeug.datastructures import FileStorage

logging.basicConfig(level=logging.DEBUG)

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    
    # Database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'workouts.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

    logging.debug(f"Database path: {db_path}")
    logging.debug(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Initialize the database
    db.init_app(app)

    # Create tables
    with app.app_context():
        try:
            db.create_all()
            logging.debug("Database tables created successfully")
        except Exception as e:
            logging.error(f"An error occurred while creating database tables: {e}")

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Serve index.html
    @app.route('/')
    def index():
        return render_template('index.html')

    # Serve static files
    @app.route('/static/<path:path>')
    def send_static(path):
        return send_from_directory('static', path)

    # Workouts API
    @app.route('/api/v1/workouts', methods=['GET'])
    def get_workouts():
        workouts = Workout.query.order_by(Workout.date.desc()).all()
        user_profile = UserProfile.query.first()
        weight = user_profile.weight if user_profile else 70  # Default weight if not set

        workout_dicts = []
        for workout in workouts:
            workout_dict = workout.to_dict()
            workout_dict['calories_burned'] = workout.calculate_calories_burned(weight)
            workout_dicts.append(workout_dict)

        return jsonify(workout_dicts)

    @app.route('/api/v1/workouts', methods=['POST'])
    def create_workout():
        data = request.form.to_dict()
        new_workout = Workout(
            duration=float(data['duration']),
            distance=float(data['distance']),
            route_nickname=data['route_nickname'],
            date=datetime.fromisoformat(data['date']),
            heart_rate=int(data.get('heart_rate')) if data.get('heart_rate') else None,
        )
        
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                filename = secure_filename(image.filename)
                image_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
                new_workout.image_filename = image_filename
        
        db.session.add(new_workout)
        db.session.commit()
        
        return jsonify(new_workout.to_dict()), 201

    @app.route('/api/v1/workouts/<int:id>', methods=['DELETE'])
    def delete_workout(id):
        workout = Workout.query.get_or_404(id)
        db.session.delete(workout)
        db.session.commit()
        return '', 204

    # User Profile API
    @app.route('/api/v1/profile', methods=['GET'])
    def get_profile():
        profile = UserProfile.query.first()
        if not profile:
            profile = UserProfile(weight=0)
            db.session.add(profile)
            db.session.commit()
        return jsonify(profile.to_dict())

    @app.route('/api/v1/profile', methods=['PUT'])
    def update_profile():
        data = request.json
        profile = UserProfile.query.first()
        if not profile:
            profile = UserProfile(weight=data['weight'])
            db.session.add(profile)
        else:
            profile.weight = data['weight']
        
        db.session.commit()
        return jsonify(profile.to_dict())

    # Error handling
    @app.errorhandler(400)
    @app.errorhandler(404)
    def handle_error(error):
        return jsonify(error=str(error)), error.code

    return app

if __name__ == '__main__':
    app = create_app()
    api = Api(app)
    
    # Request parser for workout creation
    workout_parser = reqparse.RequestParser()
    workout_parser.add_argument('duration', type=float, required=True, help='Duration in minutes is required')
    workout_parser.add_argument('distance', type=float, required=True, help='Distance in miles is required')
    workout_parser.add_argument('route_nickname', type=str, required=True, help='Route nickname is required')
    workout_parser.add_argument('date', type=inputs.datetime_from_iso8601, required=True, help='Date in ISO8601 format is required')
    workout_parser.add_argument('heart_rate', type=int)
    workout_parser.add_argument('image', type=FileStorage, location='files')

    # Request parser for user profile update
    profile_parser = reqparse.RequestParser()
    profile_parser.add_argument('weight', type=float, required=True, help='Weight in kg is required')

    class WorkoutListAPI(Resource):
        def get(self):
            workouts = Workout.query.order_by(Workout.date.desc()).all()
            user_profile = UserProfile.query.first()
            weight = user_profile.weight if user_profile else 70  # Default weight if not set

            workout_dicts = []
            for workout in workouts:
                workout_dict = workout.to_dict()
                workout_dict['calories_burned'] = workout.calculate_calories_burned(weight)
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
                profile = UserProfile(weight=0)
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
            weight = user_profile.weight if user_profile else 70  # Default weight if not set

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

    app.run(debug=True)