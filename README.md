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
### Register
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "password123"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "password123"}'
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
curl -X POST http://localhost:8000/api/token/refresh/ \
     -H "Content-Type: application/json" \
     -d '{"refresh": "your-refresh-token"}'
```
Response
```bash
{
  "access":<ACCESS_TOKEN>
}
```

### Fetch user profile
```bash
curl -X GET http://localhost:8000/api/user/profile/ \
             -H "Authorization: Bearer <ACCESS_TOKEN>"
```
Response
```bash
{
  "username": "vellorun",
  "avatar": "avatar3",
  "xp": 20,
  "level": 1,
  "visible": true
}
```

## Place APIs
### Get All Places
```bash
curl -X GET http://localhost:8000/api/places/
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
  },
  {
    "id": 2,
    "name": "Taara maa",
    "type": "outside",
    "description": "A restraunt",
    "coord_x": 22.123,
    "coord_y": 83.456,
    "visits": 101,
    "level": 0,
    "images": []
  }
]
```
### Filter Places
```bash
curl -X GET "http://localhost:8000/api/places/?type=inside"
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
- With >= 100 visits: ?visits__gte=100
- With <= 100 visits: ?visits__lte=100
- Name contains “lib”: ?name__icontains=lib
- Combine filters: ?type=inside&visits__gte=10

### Add Place (Only Superusers)
```bash
curl -X POST http://localhost:8000/api/places/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Library",
    "type": "inside",
    "description": "Main library",
    "coord_x": 12.34,
    "coord_y": 56.78,
    "visits": 0
  }'
```

## Visit APIs (also increments the xp of user by amount specified by place)

### Visit a place
```bash
curl -X POST http://localhost:8000/api/visit/ \
     -H "Authorization: Bearer your-access-token" \
     -H "Content-Type: application/json" \
     -d '{"place_id": 2}'

```

response (if first time visit)
```bash
{
  "message": "Place visited!",
  "place_name": "Library",
  "user_xp": 20,
  "user_level": 1,
  "total_visits_to_place": 1
}
```

response (if already visited)
```bash
{
  "message": "You have already visited this place.",
  "place_name": "Library",
  "user_xp": 20,
  "user_level": 1,
  "total_visits_to_place": 1
}
```
