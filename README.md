# Neofi API

This is the API backend for a note-taking application. It provides endpoints for user authentication, note management, and sharing notes with other users.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/bakharia/neofi_note_api.git
   ```
2. Navigate to the project directory:

   ```bash
   cd neofi_api
   ```
3. Install Poetry: Poetry is used for managing dependencies and packaging the project. If you haven't installed Poetry yet, you can do so by following the instructions at: [python-poetry.org](https://python-poetry.org/docs/#installation)
4. Install dependencies using Poetry:

   ```bash
   poetry install
   ```
5. Apply database migrations:

   ```bash
   python manage.py makemigrations backend
   python manage.py migrate
   ```
7. Run the development server:

   ```bash
   python manage.py runserver
   ```

## Endpoints

- User Registration

  **Route:** `/signup/`\
  **Method:** POST\
  **Description:** Register a new user account.\
  **Request Body:** JSON object containing `username`, `email`, and `password`.\
  **Headers:** No additional headers required.\
  **Response:**

  ```json
  {
      "message": "User created successfully"
  }
  ```

  - `200 OK` if registration is successful, returns a success message.
  - `400 BAD REQUEST` if request data is invalid, returns error details.
- User Login

  **Route:** `/login/`\
  **Method:** POST\
  **Description:** Log in to an existing user account.\
  **Request Body:** JSON object containing `username` and `password`.\
  **Headers:** No additional headers required.\
  **Response:**

  ```json
  {
      "message": "Login successful",
      "token": "<user-auth-token>"
  }
  ```

  - `200 OK` if login is successful, returns a success message and authentication token in the response headers.
  - `401 UNAUTHORIZED` if login fails, returns error details.
- Create Note

  **Route:** `/notes/create/`\
  **Method:** POST\
  **Description:** Create a new note.\
  **Request Body:** JSON object containing `title` and `content` of the note.\
  **Headers:**

  ```
  Authorization: Token <user-auth-token>
  ```

  **Response:**

  ```json
  {
      "message": "Note created successfully!",
      "id": "<note-id>",
      "title": "<note-title>",
      "created_at": "<formatted-utc-timestamp>"
  }
  ```

  - `201 CREATED` if note creation is successful, returns the created note details.
  - `400 BAD REQUEST` if request data is invalid, returns error details.
- List Notes

  **Route:** `/notes/list/`\
  **Method:** GET\
  **Description:** List all notes accessible to the authenticated user.\
  **Headers:**

  ```
  Authorization: Token <user-auth-token>
  ```

  **Response:**

  ```json
  [
      {
          "id": "<note-id>",
          "title": "<note-title>"
      },
      {
          "id": "<note-id>",
          "title": "<note-title>"
      },
      ...
  ]
  ```

  - `200 OK` if notes are found, returns a list of note IDs and titles.
  - `404 NOT FOUND` if no notes are found.
- Get Note

  **Route:** `/notes/<int:id>/`\
  **Method:** GET\
  **Description:** Retrieve details of a specific note by its ID.\
  **Headers:**

  ```
  Authorization: Token <user-auth-token>
  ```

  **Response:**

  ```json
  {
      "title": "<note-title>",
      "content": "<note-content>",
      "created_at": "<formatted-utc-timestamp>",
      "updated_at": "<formatted-utc-timestamp>"
  }
  ```

  - `200 OK` if note is found and accessible, returns note details.
  - `403 FORBIDDEN` if user does not have access to the note.
  - `404 NOT FOUND` if note does not exist.
- Share Note

  **Route:** `/notes/share/`\
  **Method:** POST\
  **Description:** Share a note with other users.\
  **Request Body:** JSON object containing `note_id` and list of `usernames` to share with.\
  **Headers:**

  ```
  Authorization: Token <user-auth-token>
  ```

  **Response:**

  ```json
  {
      "message": "Note shared successfully"
  }
  ```

  - `200 OK` if note sharing is successful, returns success message.
  - `400 BAD REQUEST` if request data is invalid, returns error details.
  - `404 NOT FOUND` if note does not exist or user does not have permission to share it.
- Update Note

  **Route:** `/notes/update/<int:id>/`\
  **Method:** PUT\
  **Description:** Update the content of a note.\
  **Request Body:** JSON object containing updated `content` of the note.\
  **Headers:**

  ```
  Authorization: Token <user-auth-token>
  ```

  **Response:**

  ```json
  {
      "title": "<updated-note-title>",
      "updated_content": "<updated-note-content>",
      "created_at": "<formatted-utc-timestamp>",
      "updated_at": "<formatted-utc-timestamp>"
  }
  ```

  - `200 OK` if note update is successful, returns updated note details.
  - `403 FORBIDDEN` if user does not have permission to update the note.
  - `404 NOT FOUND` if note does not exist.
- Get Note Version History

  **Route:** `/notes/version-history/<int:id>/`\
  **Method:** GET\
  **Description:** Retrieve the version history of a note.\
  **Headers:**

  ```
  Authorization: Token <user-auth-token>
  ```

  **Response:**

  ```json
  [
      {
          "timestamp": "<formatted-utc-timestamp>",
          "user": "<username>",
          "changes": "<note-changes>"
      },
      {
          "timestamp": "<formatted-utc-timestamp>",
          "user": "<username>",
          "changes": "<note-changes>"
      },
      ...
  ]
  ```

  - `200 OK` if version history is found, returns a list of note versions.
  - `403 FORBIDDEN` if user does not have access to the note.
  - `404 NOT FOUND` if note does not exist.

## Example Usage

### 1. User Registration (`POST /signup/`)

```bash
curl -X POST http://localhost:8000/signup/ -d "username=<username>&email=<email>&password=<password>"
```

### 2. User Login (`POST /login/`)

```bash
curl -X POST http://localhost:8000/notes/create/ -H "Authorization: Token <token>" -d "title=<title>&content=<content>"
```

### 3. Create a Note (`POST /notes/create/`)

```bash
curl -X POST http://localhost:8000/notes/create/ -H "Authorization: Token <token>" -d "title=<title>&content=<content>"
```

### 4. List Notes (`GET /notes/list/`)

```bash
curl -X GET http://localhost:8000/notes/list/ -H "Authorization: Token <token>"
```

### 5. Retrieve a Note (`GET /notes/<id>/`)

```bash
curl -X GET http://localhost:8000/notes/<id>/ -H "Authorization: Token <token>"
```

### 6. Share a Note (`POST /notes/share/`)

```bash
curl -X POST http://localhost:8000/notes/share/ -H "Authorization: Token <token>" -d "note_id=<note_id>&usernames=<user1,user2>"
```

### 7. Retrieve Note Version History (`GET /notes/version-history/<id>/`)

```bash
curl -X GET http://localhost:8000/notes/version-history/<id>/ -H "Authorization: Token <token>"
```

### 8. Update a Note (`PUT /notes/update/<id>/`)

```bash
curl -X PUT http://localhost:8000/notes/update/<id>/ -H "Authorization: Token <token>" -d "content=<new_content>"
```


## Testing

### `tests.py`

The `tests.py` file contains automated tests for the API endpoints. It includes tests for user registration, login, note creation, retrieval, sharing, updating, and version history.

- **User Registration**: This test ensures that users can successfully register on the platform. It sends a POST request to the `/signup/` endpoint with valid user registration data and verifies that the response status code is `201 CREATED`.
- **User Login**: Verifies that users can log in with valid credentials. It sends a POST request to the `/login/` endpoint with correct username and password and checks if the response status code is `200 OK`, indicating successful login.
- **Note Creation**: Tests the creation of a new note by an authenticated user. It sends a POST request to the `/notes/create/` endpoint with the required data and validates that the response status code is `201 CREATED`.
- **List Notes**: Checks if the API successfully lists all notes accessible to the authenticated user. It sends a GET request to the `/notes/list/` endpoint and expects a `200 OK` response with a list of note IDs and titles.
- **Get Note**: Verifies the retrieval of a specific note by its ID. It sends a GET request to the `/notes/<int:id>/` endpoint with a valid note ID and ensures that the response status code is `200 OK`.
- **Share Note**: Tests the functionality to share a note with other users. It sends a POST request to the `/notes/share/` endpoint with the note ID and usernames to share with and expects a `200 OK` response upon successful sharing.
- **Update Note**: Validates the ability to update the content of a note. It sends a PUT request to the `/notes/update/<int:id>/` endpoint with updated content and verifies that the response status code is `200 OK`.
- **Get Note Version History**: Ensures that the API returns the version history of a note. It sends a GET request to the `/notes/version-history/<int:id>/` endpoint with a valid note ID and expects a `200 OK` response with the version history.

These tests help ensure the reliability and functionality of the API endpoints, providing confidence in the application's behavior under different scenarios.
