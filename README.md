# Julia 🧠📚

**Use spaced repetition to learn English words — and never forget them!**  

🚧 **Status:** Master branch under construction / MVP is complete.
- MVP branch: Functional but not ideal, contains working backend and simple frontend for testing.  
- Master branch: Currently being refactored to adhere to **SOLID principles, OOP best practices**, and clean architecture.  

> **Disclaimer:** The project is evolving. Stay tuned for updates!  

---

## **What is Julia?**

Julia is a Django-based web app designed to help users **learn and memorize English words efficiently**, inspired by tools like Anki. Users can **create, update, review, and delete flashcards** organized into decks, making vocabulary learning interactive and personalized.  

The goal is to provide a **lightweight, intuitive spaced repetition system** using modern web technologies and a simple UI.

---

## **Features**

- Basic Django setup and project structure  
- User authentication (Google/GitHub Oauth + email/password)  
- CRUD operations for **cards** and **decks**  
- Deck-based learning sessions  
- Card review system with progress tracking  
- Responsive frontend (React mock frontend for testing DRF compatibility)  
- Spaced repetition algorithm (**SM2**) for just-in-time reviews  
- Integration with **[dictionaryapi.dev](https://dictionaryapi.dev/)** for automatic card creation  
- User statistics and learning progress tracking  
- Tests included  

---

## **Tech Stack**

| Layer | Technologies |
|-------|--------------|
| **Backend** | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white) ![DRF](https://img.shields.io/badge/DRF-ff1709?style=flat&logo=django&logoColor=white) ![Celery](https://img.shields.io/badge/Celery-37814A?style=flat&logo=celery&logoColor=white) ![Asyncio](https://img.shields.io/badge/Asyncio-008080?style=flat&logo=python&logoColor=white) |
| **Database** | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white) ![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white) |
| **Frontend** | ![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black) |
| **Real-Time / Communication** | ![WebSockets](https://img.shields.io/badge/WebSockets-008000?style=flat) ![TCP](https://img.shields.io/badge/TCP-6A5ACD?style=flat) |
| **Authentication & Security** | ![JWT](https://img.shields.io/badge/JWT-000000?style=flat) ![OAuth](https://img.shields.io/badge/OAuth-FF6F00?style=flat)
| **Tools / DevOps** | ![Git](https://img.shields.io/badge/Git-F05032?style=flat&logo=git&logoColor=white) ![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat&logo=linux&logoColor=black) |

---


## **Installation & Usage (Development)**

### Prerequisites
Make sure you have **Python, pip, and PostgreSQL** installed.  
Also, Node.js and npm are required for the React frontend.  

### Clone the repository
```bash
git clone https://github.com/noginpavlo/julia.git
cd julia
```
### Setup Python environment and dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
### Run Backend (ASGI / Uvicorn)
```bash
uvicorn julia.asgi:application --reload
```
> ⚠️ Do not use python manage.py runserver — Julia requires an ASGI server.

### Run Celery Worker
```bash
celery -A julia worker -l info
```

### Run Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
> The frontend communicates with the backend via DRF API.

### Using the App

- Use Django admin or React mock frontend to **create decks and cards**.
- Register with username and password or Google OAuth
  ![Login GIF](assets/login.gif) 
- Review cards using **spaced repetition (SM2)** — cards appear just before you forget.  
- Track your **progress and statistics** in the app.  
- Automatically generate new word cards via **[dictionaryapi.dev](https://dictionaryapi.dev/)**.
  
---

## **Screenshots**  

*(Add your screenshots below)*  

- **Card & Deck Browser:** Search, update, delete cards/decks  
- **Learning Interface:** Review cards one by one  
- **Progress / Test Interface:** Track learning progress  

---

## License

This project is released under the [MIT License](https://opensource.org/license/MIT), allowing users to freely use, modify, and distribute Julia's code while retaining the original copyright notice. However, Julia's frontend is built using an [HTML5 UP](https://html5up.net/) template, which falls under the [Creative Commons Attribution 3.0 License](https://html5up.net/license)—proper credit must be given to HTML5 UP if frontend components are used or modified.
