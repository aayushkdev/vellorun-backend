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
