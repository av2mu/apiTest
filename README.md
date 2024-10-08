# Workout Logger API

Workout Logger is a RESTful API service that allows users to log and track their workouts, including duration, distance, route nickname, and optionally heart rate and an image. It also calculates pace and estimated calories burned based on the user's weight.

## Backend Design Decisions

1. **RESTful Architecture**: The API follows RESTful principles, providing a clear and intuitive structure for managing workouts and user profiles.

2. **Stateless Server**: The server doesn't store any client state between requests, improving scalability and simplifying the application architecture.

3. **ORM Usage**: SQLAlchemy ORM is used to abstract database operations, providing flexibility in database choice and simplifying data management.

4. **Modular Structure**: The application is organized into separate modules (app.py, models.py, database.py) for better maintainability and separation of concerns.

5. **Secure File Handling**: Werkzeug's secure_filename is used to safely handle file uploads, preventing potential security issues.

6. **User Profiles**: The API now includes user profile management, allowing for personalized calorie calculations based on user weight.

## Data Validation

The Workout Logger API implements strong data validation to ensure the integrity and consistency of the data being stored and processed. Here's an overview of the validation process:

1. **Input Parsing**: 
   - The API uses Flask-RESTful's `reqparse` module to define expected arguments for each endpoint.
   - Each argument is specified with its type (e.g., float, int, string) and whether it's required.

2. **Type Checking**:
   - The parser automatically checks that the input data matches the specified types.
   - For example, 'duration' and 'distance' must be floats, 'heart_rate' must be an integer.

3. **Required Fields**:
   - Certain fields (duration, distance, route_nickname, date) are marked as required.
   - The API will return an error if these fields are missing from the request.

4. **Date Format**:
   - The 'date' field is expected to be in ISO8601 format (YYYY-MM-DDTHH:MM).
   - The API attempts to parse this string into a Python datetime object.

5. **File Uploads**:
   - For image uploads, the API checks if a file is present and has a filename.
   - The filename is sanitized using `werkzeug.utils.secure_filename()` to prevent security issues.

6. **Database Constraints**:
   - The SQLAlchemy models define additional constraints (e.g., `nullable=False` for required fields).
   - These ensure data integrity at the database level.

7. **Custom Validation**:
   - The `calculate_calories_burned()` method includes logic to handle different speed ranges.
   - This ensures that MET values are assigned correctly based on the workout intensity.

8. **Error Handling**:
   - If validation fails at any point, the API returns appropriate error messages.
   - These messages help clients understand what went wrong and how to correct their requests.

9. **Default Values**:
   - For some fields (e.g., user profile), the API provides default values if not specified.
   - This ensures that calculations can still be performed even with partial data.

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
- **Parameters:** 
  - Query Parameters:
    - `q`: string (optional) - Search query for route nickname
- **Sample API Call:**
  ```bash
  curl -X GET "http://localhost:5000/api/v1/workouts?q=Park" -H "accept: application/json"
  ```
- **Response:**
  - Status Code: 200 OK
  - Content-Type: application/json
  - Body: Array of workout objects
    ```json
    [
      {
        "id": 1,
        "profile": 1,
        "duration": 30.5,
        "distance": 3.2,
        "route_nickname": "Park Loop",
        "heart_rate": 140,
        "date": "2023-05-15T18:30:00",
        "pace": 9.53,
        "calories_burned": 320,
        "image_url": "/static/uploads/20230515183000_workout.jpg"
      },
      // ... more workouts
    ]
    ```

### 2. Create a New Workout

- **URL:** `/workouts`
- **Method:** POST
- **Description:** Creates a new workout entry.
- **Parameters:**
  - Body: multipart/form-data
    - `profile`: integer (optional) - Profile ID (defaults to 1 if not provided)
    - `duration`: float (required) - Duration of the workout in minutes
    - `distance`: float (required) - Distance of the workout in miles
    - `route_nickname`: string (required) - Nickname for the workout route
    - `date`: string (required) - Date and time of the workout in ISO 8601 format (e.g., "2023-05-20T10:00:00")
    - `heart_rate`: integer (optional) - Average heart rate during the workout
    - `image`: file (optional) - Image file of the workout
- **Sample API Call:**
  ```bash
  curl -X POST "http://localhost:5000/api/v1/workouts" \
  -H "Content-Type: multipart/form-data" \
  -F "profile=1" \
  -F "duration=45.0" \
  -F "distance=5.0" \
  -F "route_nickname=Riverside Run" \
  -F "date=2023-05-16T07:15:00" \
  -F "heart_rate=150" \
  -F "image=@/path/to/image.jpg"
  ```
- **Response:**
  - Status Code: 201 Created
  - Content-Type: application/json
  - Body: Created workout object
    ```json
    {
      "id": 2,
      "profile": 1,
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
- **Sample API Call:**
  ```bash
  curl -X DELETE "http://localhost:5000/api/v1/workouts/1"
  ```
- **Response:**
  - Status Code: 204 No Content

### 4. Get User Profile

- **URL:** `/profile` or `/profile/<id>`
- **Method:** GET
- **Description:** Retrieves the user's profile information.
- **Parameters:** 
  - Path Parameters:
    - `id`: integer (optional) - ID of the profile to retrieve
- **Sample API Call:**
  ```bash
  curl -X GET "http://localhost:5000/api/v1/profile/1" -H "accept: application/json"
  ```
- **Response:**
  - Status Code: 200 OK
  - Content-Type: application/json
  - Body: User profile object
    ```json
    {
      "id": 1,
      "name": "John Doe",
      "weight": 70
    }
    ```

### 5. Create or Update User Profile

- **URL:** `/profile` or `/profile/<id>`
- **Method:** PUT
- **Description:** Creates a new profile or updates an existing one.
- **Parameters:**
  - Path Parameters:
    - `id`: integer (optional) - ID of the profile to update
  - Body: application/json
    ```json
    {
      "name": "John Doe",
      "weight": 70
    }
    ```
  - `name`: string (required) - User's name
  - `weight`: float (required) - User's weight in pounds (lbs)
- **Sample API Call:**
  ```bash
  curl -X PUT "http://localhost:5000/api/v1/profile/1" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "weight": 70}'
  ```
- **Response:**
  - Status Code: 200 OK (for update) or 201 Created (for new profile)
  - Content-Type: application/json
  - Body: Updated or created user profile object
    ```json
    {
      "id": 1,
      "name": "John Doe",
      "weight": 70
    }
    ```

### 6. Update User Weight

- **URL:** `/profile/<id>`
- **Method:** PATCH
- **Description:** Updates only the weight of an existing profile.
- **Parameters:**
  - Path Parameters:
    - `id`: integer (required) - ID of the profile to update
  - Body: application/json
    ```json
    {
      "weight": 75
    }
    ```
  - `weight`: float (required) - User's new weight in pounds (lbs)
- **Sample API Call:**
  ```bash
  curl -X PATCH "http://localhost:5000/api/v1/profile/1" \
  -H "Content-Type: application/json" \
  -d '{"weight": 75}'
  ```
- **Response:**
  - Status Code: 200 OK
  - Content-Type: application/json
  - Body: Updated user profile object
    ```json
    {
      "id": 1,
      "name": "John Doe",
      "weight": 75
    }
    ```

### 7. Delete User Profile

- **URL:** `/profile/<id>`
- **Method:** DELETE
- **Description:** Deletes a specific user profile by ID.
- **Parameters:**
  - Path Parameters:
    - `id`: integer (required) - ID of the profile to delete
- **Sample API Call:**
  ```bash
  curl -X DELETE "http://localhost:5000/api/v1/profile/1"
  ```
- **Response:**
  - Status Code: 204 No Content

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
│ ├── css/
│ │ └── styles.css
│ └── uploads/ # Folder for uploaded workout images
├── templates/
│ └── index.html
```

The frontend now includes functionality to create and manage user profiles, which are used for personalized calorie calculations in workouts.
