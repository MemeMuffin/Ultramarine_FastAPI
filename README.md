# Ultramarines-FastAPI

A RESTful API built with **FastAPI** and **SQLModel** featuring full CRUD functionality, user registration, dynamic scope-based permission control, and automatic dummy data generation at startup.

## 🚀 Features

- 🔐 User registration with secure password hashing
- 🔓 Login with JWT authentication
- 🛡️ Dynamic scopes assigned based on user rank for fine-grained permissions
- 📦 Dummy Ultramarine data auto-generated at app startup
- ✍️ Dummy credentials written to `dummy_data.txt` for testing
- 📡 Full usage of all HTTP methods (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`)
- 🧠 SQLModel with SQLAlchemy for ORM

---

## 🛠️ Setup Instructions

```bash
# Clone the repo
git clone https://github.com/your-username/ultramarines-api.git
cd ultramarines-api

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn main:app --reload
```

---

📘 API Endpoints  
🔐 Authentication  
POST /register  
Register a new user:  
{  
"username": "primarch",  
"password": "securepassword",  
"rank": "Captain",  
etc.  
}  
POST /login  
Login and receive a JWT token with appropriate scopes.

---

👤 User & Permissions  
Scopes are dynamically assigned based on the user’s rank:

| Rank           | Scopes                      |
| -------------- | --------------------------- |
| Legionary      | view                        |
| Sergeant       | view                        |
| Lieutenant     | view, update                |
| Captain        | view, update                |
| Legatus        | view, update, delete        |
| Chapter Master | view, update, delete, admin |

These scopes are included in the JWT token and used to restrict access to certain routes.

---

🧪 Ultramarines Routes  
All routes are protected and use scope-based access control.

- GET /ultramarines_chapter/all/ – Get list of Ultramarines (requires view scope)

- POST /ultramarines_chapter/register/ – Create a new Ultramarine (requires update scope)

- PUT /ultramarines_chapter/rewrite/{id} – Fully update an Ultramarine (requires update)

- PATCH /ultramarines_chapter/update/{id} – Partially update an Ultramarine (requires update)

- DELETE /ultramarines_chapter/delete/{id} – Delete an Ultramarine (requires delete)

![image](https://github.com/user-attachments/assets/d70925c6-bb3a-454f-a66e-6750063ee79b)

---

🧪 Dummy Data Generation  
When the application starts for the first time:

It generates random dummy Ultramarines in the database.

A test user is created with a plaintext password.

These credentials are written to a file named: "dummy_data.txt"

🔐 Example contents of dummy_data.txt:

test_user: test123  
 **Note: Password is hashed in the database**

---

🧩 Tech Stack

- FastAPI – Web framework

- SQLModel – ORM based on SQLAlchemy

- SQLite – Lightweight DB

- JWT (PyJWT) – Token-based auth

- Passlib – Password hashing

---

📂 Project Structure

.  
├── main.py  
├── models/  
│ └── ultramarines.py  
├── routes/  
│ ├── ultramarines.py  
│ └── utils.py  
├── config/  
│ └── config_db.py  
├── static/  
│ └── **init**.py (is empty)  
├── dummy_data.txt  
└── requirements.txt

---

🛡️ Permissions Overview  
Permissions are checked using OAuth2 scopes and FastAPI’s Security system.

Each protected route includes dependencies like:  
@router.get("/ultramarines/", dependencies=[Security(get_current_user, scopes=["view"])])  
The scopes are injected into the token at login depending on the user's rank.

---

📬 Feedback / Contributions  
Feel free to open issues or submit pull requests!
