# Workout Logger API

Workout Logger is a RESTful API service that allows users to log and track their workouts, including duration, distance, route nickname, and optionally heart rate and an image. It also calculates pace and estimated calories burned based on the user's weight.

## Backend Design Decisions

1. **RESTful Architecture**: The API follows RESTful principles, providing a clear and intuitive structure for managing workouts and user profiles.

2. **Stateless Server**: The server doesn't store any client state between requests, improving scalability and simplifying the application architecture.

3. **ORM Usage**: SQLAlchemy ORM is used to abstract database operations, providing flexibility in database choice and simplifying data management.

4. **Modular Structure**: The application is organized into separate modules (app.py, models.py, database.py) for better maintainability and separation of concerns.

5. **Secure File Handling**: Werkzeug's secure_filename is used to safely handle file uploads, preventing potential security issues.

## Backend Tools and Technologies

1. **Flask**: A lightweight Python web framework, chosen for its simplicity and flexibility in building APIs.

2. **SQLAlchemy**: An ORM tool that provides a high-level abstraction for database operations, making it easier to work with databases in Python.

3. **SQLite**: A serverless, self-contained database engine, perfect for small to medium-sized applications without the need for a separate database server.

4. **Werkzeug**: Used for secure filename handling and WSGI utilities.

## API Endpoints

1. GET `/api/v1/workouts`: Retrieve all workouts
2. POST `/api/v1/workouts`: Create a new workout
3. DELETE `/api/v1/workouts/<id>`: Delete a specific workout
4. GET `/api/v1/profile`: Get user profile
5. PUT `/api/v1/profile`: Update user profile

## Data Models

1. **Workout**:
   - id: Integer (Primary Key)
   - duration: Float (minutes)
   - distance: Float (miles)
   - route_nickname: String
   - heart_rate: Integer (optional)
   - date: DateTime
   - image_filename: String (optional)

2. **UserProfile**:
   - id: Integer (Primary Key)
   - weight: Float

## Setup and Running the Application

1. Clone the repository:
   ```
   git clone <repository-url>
   cd workout-logger
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ```

5. The API will be available at `http://localhost:5000/api/v1`

## Testing the API

You can test the API using tools like cURL or Postman. Here are some example cURL commands:

1. Get all workouts:
   ```
   curl http://localhost:5000/api/v1/workouts
   ```

2. Create a new workout:
   ```
   curl -X POST -F "duration=30" -F "distance=3.2" -F "route_nickname=Park Run" -F "date=2023-05-20T10:00:00" http://localhost:5000/api/v1/workouts
   ```

3. Delete a workout:
   ```
   curl -X DELETE http://localhost:5000/api/v1/workouts/1
   ```

4. Get user profile:
   ```
   curl http://localhost:5000/api/v1/profile
   ```

5. Update user profile:
   ```
   curl -X PUT -H "Content-Type: application/json" -d '{"weight": 70.5}' http://localhost:5000/api/v1/profile
   ```

## Backend File Structure

```
workout-logger/
├── app.py          # Main application file with route handlers
├── models.py       # Database models
├── database.py     # Database configuration
└── README.md
```

## Frontend (Secondary)

A simple HTML/JavaScript frontend is provided for demonstration purposes. It's a single-page application that interacts with the API to display and manage workouts. The frontend files are located in:

```
workout-logger/
├── static/
│   └── css/
│       └── styles.css
└── templates/
    └── index.html
```

To access the frontend, run the Flask application and navigate to `http://localhost:5000` in your web browser.
