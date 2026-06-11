# Habit Builder App - Game Edition 🎮

A gamified habit-tracking application that turns building habits into an addictive game. Level up your life, one habit at a time!

## 🎯 Features

### Core Habit Tracking
- **Create Habits**: Organize your daily routines with custom emojis
- **Track Completion**: Mark habits as completed each day
- **Streaks**: Visualize your consistency with current and longest streak tracking
- **Habit Ranks**: Each habit has its own rank (Bronze → Silver → Gold → Legend)

### 🎮 Gamification System
- **User Accounts**: Register and login to track your progress
- **XP & Levels**: Earn experience points for completing habits
  - 10 XP per habit completion
  - Bonus XP for maintaining streaks
  - Level up to unlock new titles
- **Character Stats**: Track your habit-building attributes
  - 💪 **Discipline**: How consistent you are with daily habits
  - 🔄 **Consistency**: Your streak maintenance ability
  - 🎯 **Dedication**: Total effort and time invested
  - 🧠 **Focus**: Completion rate across all habits
- **Global Rankings**: See where you stand among all habit builders
- **Achievements**: Earn badges for milestones (first habit, streaks, levels, etc.)

### 🏆 Challenges & Events
- **Community Challenges**: Join time-bound events like "10 Pushups Daily" or "Read 10 Pages"
- **Event Rewards**: Earn bonus XP for participating and completing challenges
- **Suggested Habits**: Each event suggests a habit you can create

### 🎨 User Experience
- **Dark/Light Theme**: Switch between themes with high contrast for readability
- **Glass Morphism Design**: Modern, premium UI with frosted glass effects
- **Celebration Effects**: Satisfying animations when completing habits
- **Motivational Messages**: Context-aware encouragement based on your progress

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or later

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/habittracker.git
   cd habittracker
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   streamlit run main.py
   ```

5. Open your browser to `http://localhost:8501`

### First Time Use
1. Click "Register" to create a new account
2. Choose a unique username and password
3. Login with your credentials
4. Start by creating your first habit in the "Habit Lab"
5. Check in daily to earn XP and level up!

## 📁 Project Structure

```
habittracker/
├── main.py              # Entry point with all page routes
├── src/
│   ├── __init__.py
│   ├── habits.py        # Habit data model and management
│   ├── storage.py       # JSON data persistence for habits
│   ├── auth.py          # User authentication & gamification
│   ├── ui_components.py # Reusable UI components
│   └── calendars.py     # Calendar visualization
├── assets/
│   └── style.css        # Custom CSS styling
├── data/
│   ├── habits.json      # Habit data storage
│   ├── users.json       # User accounts & progress
│   └── events.json      # Community challenges
├── tests/
│   └── unit/            # Unit tests
└── requirements.txt     # Python dependencies
```

## 🎮 How Gamification Works

### Earning XP
| Action | XP Earned |
|--------|-----------|
| Complete a habit | 10 XP |
| Streak bonus | +5 XP |
| Create a habit | 25 XP |
| Join an event | 25 XP |
| Achievement unlocked | 25-500 XP |

### Level System
- Each level requires `level × 100` XP
- Level up to unlock new titles (Novice → Apprentice → Explorer → ... → Grand Master)
- Your rank badge changes based on your level

### Habit Ranks
Each habit has its own rank based on streak length:
| Streak | Rank |
|--------|------|
| 0 days | Not Started |
| 1-2 days | Starter 🌱 |
| 3-6 days | Bronze 🥉 |
| 7-13 days | Silver 🥈 |
| 14-29 days | Gold 🥇 |
| 30+ days | Legend 🏅 |

## 🏆 Achievements

Unlock badges for various milestones:
- 🌟 **First Step**: Create your first habit
- 🔥 **Getting Started**: Achieve a 3-day streak
- ⚡ **Week Warrior**: Achieve a 7-day streak
- 💪 **Fortnight Fighter**: Achieve a 14-day streak
- 🏆 **Monthly Master**: Achieve a 30-day streak
- ⭐ **Rising Star**: Reach level 5
- 🌟 **Dedicated Builder**: Reach level 10
- 🦋 **Social Butterfly**: Join your first event
- 🥇 **Champion**: Complete an event
- 📋 **Habit Collector**: Create 5 habits

## 📊 User Parameters

Your character has 4 stats that evolve based on your behavior:

1. **Discipline** (💪): Based on daily completion rate
2. **Consistency** (🔄): Based on average streak length
3. **Dedication** (🎯): Based on total completions
4. **Focus** (🧠): Based on 30-day completion rate

These stats range from 1-100 and provide a holistic view of your habit-building prowess!

## Running Tests

To run the unit tests:
```bash
PYTHONPATH=. pytest tests/unit/
```

## Data Storage

All data is stored locally in JSON files:
- `data/habits.json`: Habit definitions and completion history
- `data/users.json`: User accounts, levels, XP, and achievements
- `data/events.json`: Community challenges

## Contributing

Feel free to fork this project and add your own features! Some ideas:
- More achievement types
- Weekly/monthly reports
- Habit categories
- Social features (friends, groups)
- Push notifications

## License

Educational purpose - feel free to use and learn!

---

**Built with ❤️ using Python & Streamlit**