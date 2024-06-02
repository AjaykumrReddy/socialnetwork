# Social Networking API

This is a social networking API built using Django Rest Framework. The API supports user login/signup, searching for users, sending/accepting/rejecting friend requests, listing friends, and listing pending friend requests. The project is containerized using Docker.

## Features

- User Login/Signup
- Search Users by Email and Name
- Send/Accept/Reject Friend Requests
- List Friends
- List Pending Friend Requests

## Installation

### Prerequisites

- Docker
- Python 3.x
- Git

### Steps

1. **Clone the repository:**

   git clone https://github.com/AjaykumrReddy/socialnetwork.git
   
   cd socialnetwork

3. **Run in Local**

    python3 -m venv venv
   
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`

    pip install -r requirements.txt

    python manage.py makemigrations

    python manage.py migrate

    python manage.py runserver

5. **Using Docker**

    docker-compose up --build

6. **Postman Collection**

    A Postman collection for testing the API endpoints is provided. You can import the collection into Postman and test the endpoints.


    Also You can test the API endpoints using the Postman collection available [here.](https://www.postman.com/technical-cosmonaut-63989386/workspace/social-network-api/collection/25506646-3131e478-7924-4f0a-9f51-048830c13e80?action=share&creator=25506646)

