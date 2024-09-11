# Workout Logger

Workout Logger is a web application that allows users to log and track their workouts, including duration, distance, route nickname, and optionally heart rate and an image. It also calculates pace and estimated calories burned based on the user's weight.

## Design Decisions

1. **Single-Page Application (SPA)**: The frontend is built as an SPA using vanilla JavaScript, HTML, and CSS. This approach keeps the application lightweight and avoids the need for a complex build process.

2. **RESTful API**: The backend follows RESTful principles, providing a clear and intuitive API structure for managing workouts and user profiles.

3. **Separation of Concerns**: The application is structured with clear separation between the frontend (HTML/JS) and backend (Python/Flask) components.

4. **Local Storage**: User weight is stored in the browser's local storage for persistence between sessions, reducing unnecessary API calls.

5. **Responsive Design**: The CSS is designed to be responsive, ensuring a good user experience on various device sizes.

## Choice of Tools

1. **Flask**: A lightweight Python web framework, chosen for its simplicity and flexibility in building web applications and APIs.

2. **SQLAlchemy**: An ORM (Object-Relational Mapping) tool that provides a high-level abstraction for database operations, making it easier to work with databases in Python.

3. **SQLite**: A serverless, self-contained database engine, perfect for small to medium-sized applications without the need for a separate database server.

4. **Werkzeug**: Used for secure filename handling during file uploads, enhancing the security of the application.

5. **Vanilla JavaScript**: Used for frontend interactivity, keeping the application lightweight and avoiding the need for additional frontend frameworks.

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

5. Open a web browser and navigate to `http://localhost:5000`

## Testing the API

You can test the API using tools like cURL, Postman, or by using the provided web interface. Here are some example cURL commands:

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

For more detailed API documentation, refer to the API Documentation section in this README.

## File Structure
workout-logger/
├── app.py
├── models.py
├── database.py
├── static/
│ ├── css/
│ │ └── styles.css
│ └── uploads/
├── templates/
│ └── index.html
└── README.md

The main application logic can be found in `app.py`, the database models are defined in `models.py`, and the frontend HTML template is located in `templates/index.html`