## Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/vellorun-backend.git
cd vellorun-backend
```
### 2. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Run Migrations
```bash
python manage.py migrate
```
4. Create Superuser (for adding new places)
```bash
python manage.py createsuperuser
```
5. Start the Server
```bash
python manage.py runserver
```


## Authentication API
### Register/Login
creates a new account if user does not exist otherwise signs in automatically if user exists
```bash
curl -X POST https://vellorun-backend.vercel.app/api/auth/google/ \
  -H "Content-Type: application/json" \
  -d '{
    "id_token": "GOOGLE_ID_TOKEN"
}'
```
Response
```bash
{
  "access": "JWT_ACCESS_TOKEN",
  "refresh": "JWT_REFRESH_TOKEN"
}
```

### Refresh token
```bash
curl -X POST https://vellorun-backend.vercel.app/api/token/refresh/ \
     -H "Content-Type: application/json" \
     -d '{"refresh": "<REFRESH_TOKEN>"}'
```
Response
```bash
{
  "access":<ACCESS_TOKEN>
  "refresh":<REFRESH_TOKEN>
}
```

### Users api

### Fetch user profile
```bash
curl -X GET https://vellorun-backend.vercel.app/api/user/profile/ \
             -H "Authorization: Bearer <ACCESS_TOKEN>"
```
Response
```bash
{
  "username": "vellorun",
  "email": "test@gmail.com",
  "avatar": 2,
  "xp": 20,
  "level": 1,
  "visible": true,
  "online": true,
  "coord_x": 0.0,
  "coord_y": 0.0,
}
```

### Modify user profile
you can modify coordinates, visibility, username, avatar and online status
```bash
curl -X PATCH https://vellorun-backend.vercel.app/api/user/profile/ \
          -H "Authorization: Bearer <ACCESS_TOKEN>" \
          -H "Content-Type: application/json" \
          -d '{"visible": false}'
```

### fetch all online users
```bash
curl -X GET http://localhost:8000/api/user/online/
```
Response
```bash
[
  {
  "username": "vellorun",
  "email": "test@gmail.com",
  "avatar": "avatar3",
  "xp": 20,
  "level": 1,
  "visible": true,
  "online": true,
  "coord_x": 0.0,
  "coord_y": 0.0,
  "visited_places": [{...}, {...}],
  "contributed_places": [{...}, {...}],
  "saved_places": [{...}, {...}],
  },
  ...
]
```

### fetch visited places
```bash
curl -X GET http://localhost:8000/api/places/visited/ \
             -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### fetch contributed places
```bash
curl -X GET http://localhost:8000/api/places/contributed/ \
             -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Save a place
```bash
curl -X POST https://vellorun-backend.vercel.app/api/places/saved/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"place_id": 1}'
```

### Delete a saved place
```bash
curl -X DELETE https://vellorun-backend.vercel.app/api/places/saved/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"place_id": 1}'
```

### Fetch saved places
```bash
curl -X GET https://vellorun-backend.vercel.app/api/places/saved/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
```

## Place suggestion APIs
### Get a suggestion of a place to visit from the api(AI)
```bash
curl -X GET http://localhost:8000/api/suggestions/ \
          -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Suggest a new place 
requests for superusers are approved automatically, when users try to add a place it is not shown in searches until its approved.
```bash
curl -X POST https://vellorun-backend.vercel.app/api/places/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sample Place",
    "type": "inside",
    "description": "Test description",
    "coord_x": 12.3456,
    "coord_y": 78.9012,
    "level": 1,
    "xp_reward": 20,
    "tags": ["hotel", "top10"],
    "images": [
      { "image_url": "https://example.com/img1.jpg" },
      { "image_url": "https://example.com/img2.jpg" }
    ]
  }'
```

### Approve suggestion of a new place
```bash
curl -X POST https://vellorun-backend.vercel.app/api/places/<place_id>/approve/ \
          -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Place APIs
### Get All Places
```bash
curl -X GET https://vellorun-backend.vercel.app/api/places/
```
Response
```bash
[
  {
    "id": 1,
    "name": "Library",
    "type": "inside",
    "description": "Main campus library",
    "coord_x": 25.123,
    "coord_y": 85.456,
    "visits": 1,
    "level": 1,
    "xp_reward": 20,
    "tags": ["campusbuilding", "quiet"],
    "images": []
  },
  {
    "id": 2,
    "name": "Taara maa",
    "type": "outside",
    "description": "A restraunt",
    "coord_x": 22.123,
    "coord_y": 83.456,
    "visits": 101,
    "level": 1,
    "xp_reward": 20,
    "tags": ["hotel", "top10"],
    "images": []
  }
]
```

### Filter Places
```bash
curl -X GET "https://vellorun-backend.vercel.app/api/places/?type=inside"
```
Response
```bash
[
  {
    "id": 1,
    "name": "Library",
    "type": "inside",
    "description": "Main campus library",
    "coord_x": 25.123,
    "coord_y": 85.456,
    "visits": 1,
    "level": 0,
    "images": []
  }
]
```

Filter Examples
- Inside places: ?type=inside
- tags: ?tags=top10&tags=hotel
- With >= 100 visits: ?visits__gte=100
- With <= 100 visits: ?visits__lte=100
- Name contains “lib”: ?name__icontains=lib
- Combine filters: ?type=inside&visits__gte=10

## Visit APIs (also increments the xp of user by amount specified by place)

### Visit a place
```bash
curl -X POST https://vellorun-backend.vercel.app/api/visit/ \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"place_id": 2}'

```
