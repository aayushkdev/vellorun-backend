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
  -d '{"username": "user1", "email": "user@example.com", "password": "password123"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "password123"}'
```
### Response
```bash
{
  "access": "JWT_ACCESS_TOKEN",
  "refresh": "JWT_REFRESH_TOKEN"
}
```

## Place APIs
### Get All Places
```bash
curl http://localhost:8000/api/places/
```

### Filter Places
```bash
http://localhost:8000/api/places?type=inside&visits__gte=100
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
