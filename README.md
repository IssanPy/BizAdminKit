Demo: Business Website + Admin Panel

1) Create and activate venv:
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate

2) Install:
   pip install -r requirements.txt

3) Run (first run will create sqlite DB):
   python app.py

4) Open http://127.0.0.1:5000
   Admin: http://127.0.0.1:5000/admin/

5) Create admin via CLI: (in new terminal with venv active)
   flask create-admin
   flask seed

Notes: Default DB is `app.db` in project folder.
