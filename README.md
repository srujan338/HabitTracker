# Habit.Space (Game Edition) 🎮

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Habit.Space** is a high-performance, gamified habit-tracking engine designed to transform behavioral science into an engaging, addictive experience. Built with a robust Python backend and a modern Streamlit frontend, it leverages gamification mechanics to drive long-term user consistency.

---

## 🚀 Technical Highlights

- **Gamification Engine**: Complex XP, Leveling, and Achievement systems.
- **Dynamic Trait Modeling**: Real-time calculation of character stats (Discipline, Consistency, etc.) based on completion patterns.
- **Glass-Morphism UI**: Premium visual design with frosted glass effects and fluid animations.
- **Multi-Tenant Ready**: User authentication and profile management via Supabase (PostgreSQL).
- **Extensible Architecture**: Modular codebase with clear separation of concerns (Business Logic, Storage, UI).
- **Internationalization (i18n)**: Built-in support for multiple languages.

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Python-based reactive framework)
- **Backend**: Python 3.10+
- **Database**: Supabase (PostgreSQL) & Local JSON fallback
- **Styling**: Custom CSS with Neon/Cyberpunk and Retro themes
- **Visualization**: Streamlit-ECharts & Custom SVG Progress Rings

---

## 📁 Project Architecture

```text
habittracker/
├── main.py              # Application orchestrator & routing
├── src/                 # Core business logic
│   ├── auth.py          # Identity & Gamification logic
│   ├── habits.py        # Habit domain models & analytics
│   ├── storage.py       # Persistence layer (Supabase/JSON)
│   ├── ui_components.py # Atomic UI building blocks
│   └── calendars.py     # Advanced progress visualizations
├── assets/              # Visual resources & CSS modules
├── data/                # Local data storage (Development)
├── specs/               # Technical specifications & migrations
└── tests/               # Automated test suite (Pytest)
```

---

## ⚙️ Installation & Deployment

### Prerequisites
- Python 3.10 or higher
- [Supabase](https://supabase.com/) account (optional for cloud persistence)

### Local Setup
1. **Clone & Navigate**:
   ```bash
   git clone https://github.com/yourusername/habittracker.git
   cd habittracker
   ```

2. **Environment Setup**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Database Configuration**:
   Create a `.env` file with your Supabase credentials (see `.env.example`).

4. **Launch**:
   ```bash
   streamlit run main.py
   ```

---

## 🧪 Quality Assurance

We maintain a rigorous testing standard. Run the unit tests using `pytest`:

```bash
PYTHONPATH=. pytest tests/unit/
```

---

## 🤝 Contributing

We welcome professional contributions. Please follow our [Development Standards](GEMINI.md) and ensure all PRs include relevant tests.

---

**Developed with precision by the Habit.Space Engineering Team.**
