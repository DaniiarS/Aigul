# 🚌 Aigul

A FastAPI-based backend for predicting and serving real-time bus arrival times, using SQLAlchemy and PostgreSQL. Designed to support IoT displays and mobile apps with accurate bus tracking data.

For now, the project will be developed under name Aigul, inspired by a rare flower native to Batken region, south of Kyrgyzstan.

---

## 🚀 Features

- RESTful API using FastAPI
- SQLAlchemy ORM with PostgreSQL
- Modular database schema supporting reusable segments and bus routes
- Designed for real-time ETA updates
- Scalable structure for integration with IoT devices and public APIs

---

## 🧱 Tech Stack

- **Python 3.10+**
- **FastAPI** – modern, fast web framework
- **SQLAlchemy** – ORM for PostgreSQL
- **Uvicorn** – ASGI server for FastAPI
- **Pydantic** – data validation and serialization
- **Alembic** (optional) – for database migrations

---

## 📦 Installation

### 1. Clone the repo

```bash
git clone https://github.com/DaniiarS/Aigul.git
cd Aigul
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🛠 Configuration

Edit the database URL in `database.py`:

```python
DATABASE_URL = "postgresql://<username>:<password>@localhost/<dbname>"
```

You can also use environment variables for better security.

---

## 🗃 Database Models

- **BusStop**: name, address
- **Segment**: reusable route segment
- **Route**: collection of ordered segments
- **RouteSegment**: links segments to a route with index

_(Extend as needed with vehicle tracking, ETA predictions, etc.)_

---

## ▶️ Running the API

```bash
uvicorn main:app --reload
```

Access it at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📬 Example API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/bus_stop/` | List all bus stops |
| `GET`  | `/bus_stop/{id}` | Get a specific bus stop |
| `POST` | `/bus_stop/` | Add a new bus stop |
| `GET`  | `/route/` | Get all routes with segments |
| `GET`  | `/eta/{stop_id}` | Get ETA for a stop (planned) |

---

## 🧪 Testing

Use `pytest` or `unittest` (not included by default):

```bash
pip install pytest
pytest
```

---

## 📌 TODO

- [ ] Real-time vehicle tracking ingestion
- [ ] ETA prediction algorithm
- [ ] User authentication (optional)
- [ ] WebSocket support for live updates
- [ ] Integration with hardware displays

---

## 📄 License

MIT License – See `LICENSE` file for details.

---

## 🤝 Contributing

Pull requests and suggestions are welcome! Please open issues first to discuss proposed changes.

---

## ✉️ Contact

Author: [Daniiar Suiunbekov]  
Email: daniyar.suyunbekov@gmail.com  
Project Repo: [github.com/DaniiarS/Aigul](https://github.com/DaniiarS/Aigul)
