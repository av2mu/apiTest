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

## API Documentation

Base URL: `/api/v1`

### 1. Get All Workouts

- **URL:** `/workouts`
- **Method:** GET
- **Description:** Retrieves all workouts, sorted by date in descending order.
- **Parameters:** None
- **Response:**
  - Status Code: 200 OK
  - Content-Type: application/json
  - Body: Array of workout objects
    ```json
    [
      {
        "id": 1,
        "duration": 30.5,
        "distance": 3.2,
        "route_nickname": "Park Loop",
        "heart_rate": 140,
        "date": "2023-05-15T18:30:00",
        "pace": 9.53,
        "calories_burned": 320,
        "image_url": "/static/uploads/20230515183000_workout.jpg"
      },
      ...
    ]
    ```

### 2. Create a New Workout

- **URL:** `/workouts`
- **Method:** POST
- **Description:** Creates a new workout entry.
- **Parameters:**
  - Body: multipart/form-data
    - `duration`: float (required) - Duration of the workout in minutes
    - `distance`: float (required) - Distance of the workout in miles
    - `route_nickname`: string (required) - Nickname for the workout route
    - `date`: string (required) - Date and time of the workout in ISO 8601 format (e.g., "2023-05-20T10:00:00")
    - `heart_rate`: integer (optional) - Average heart rate during the workout
    - `image`: file (optional) - Image file of the workout
- **Response:**
  - Status Code: 201 Created
  - Content-Type: application/json
  - Body: Created workout object
    ```json
    {
      "id": 2,
      "duration": 45.0,
      "distance": 5.0,
      "route_nickname": "Riverside Run",
      "heart_rate": 150,
      "date": "2023-05-16T07:15:00",
      "pace": 9.0,
      "calories_burned": 500,
      "image_url": "/static/uploads/20230516071500_workout.jpg"
    }
    ```

### 3. Delete a Workout

- **URL:** `/workouts/<id>`
- **Method:** DELETE
- **Description:** Deletes a specific workout by ID.
- **Parameters:**
  - Path Parameters:
    - `id`: integer (required) - ID of the workout to delete
- **Response:**
  - Status Code: 204 No Content

### 4. Get User Profile

- **URL:** `/profile`
- **Method:** GET
- **Description:** Retrieves the user's profile information.
- **Parameters:** None
- **Response:**
  - Status Code: 200 OK
  - Content-Type: application/json
  - Body: User profile object
    ```json
    {
      "id": 1,
      "weight": 70.5
    }
    ```

### 5. Update User Profile

- **URL:** `/profile`
- **Method:** PUT
- **Description:** Updates the user's profile information.
- **Parameters:**
  - Body: application/json
    ```json
    {
      "weight": 70.5
    }
    ```
- **Response:**
  - Status Code: 200 OK
  - Content-Type: application/json
  - Body: Updated user profile object
    ```json
    {
      "id": 1,
      "weight": 70.5
    }
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
