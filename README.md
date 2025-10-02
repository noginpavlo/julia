# Julia 🧠📚

**Use spaced repetition to learn English words — and never forget them!**  

🚧 **Status:** Master branch under construction/MVP is complete.
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
- User authentication (Google/GitHub + email/password)  
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

| Layer | Technology | Icon |
|-------|------------|------|
| Backend | Django | 🐍 |
| API | Django REST Framework | 🔗 |
| Database | PostgreSQL | 🗄️ |
| Caching/Queue | Redis & Celery | ⚡ |
| Frontend | React | ⚛️ |
| Templates | Django Templates / HTML5 UP | 🎨 |
| Authentication | Google / GitHub OAuth + local | 🔑 |
| Testing | pytest | 🧪 |

---

## **Installation (Development Only)**

> Currently, only the code is available. Deployment instructions are not provided yet.  

1. Ensure Python, pip, and PostgreSQL are installed.  
2. Clone the repository:

```bash
git clone https://github.com/noginpavlo/julia.git
cd julia
```

## **Usage**

- Use Django admin or React mock frontend to **create decks and cards**.  
- Review cards using **spaced repetition (SM2)** — cards appear just before you forget.  
- Track your **progress and statistics** in the app.  
- Automatically generate new word cards via **[dictionaryapi.dev](https://dictionaryapi.dev/)**.  

> Frontend is primarily for testing backend compatibility and basic CRUD workflow.

---

## **Screenshots**  

*(Add your screenshots below)*  

- **Card & Deck Browser:** Search, update, delete cards/decks  
- **Learning Interface:** Review cards one by one  
- **Progress / Test Interface:** Track learning progress  

---

## License

This project is released under the [MIT License](https://opensource.org/license/MIT), allowing users to freely use, modify, and distribute Julia's code while retaining the original copyright notice. However, Julia's frontend is built using an [HTML5 UP](https://html5up.net/) template, which falls under the [Creative Commons Attribution 3.0 License](https://html5up.net/license)—proper credit must be given to HTML5 UP if frontend components are used or modified.
