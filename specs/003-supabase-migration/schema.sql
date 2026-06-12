-- 1. Create Users Table
CREATE TABLE public.users (
    id BIGSERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT DEFAULT '',
    google_id TEXT UNIQUE,
    email TEXT,
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    title TEXT DEFAULT 'Beginner',
    discipline INTEGER DEFAULT 50,
    consistency INTEGER DEFAULT 50,
    dedication INTEGER DEFAULT 50,
    focus INTEGER DEFAULT 50,
    creativity INTEGER DEFAULT 50,
    resilience INTEGER DEFAULT 50,
    total_streak_days INTEGER DEFAULT 0,
    total_completions INTEGER DEFAULT 0,
    habits_created INTEGER DEFAULT 0,
    events_joined INTEGER DEFAULT 0,
    events_completed INTEGER DEFAULT 0,
    onboarding_completed BOOLEAN DEFAULT FALSE,
    personality_type TEXT DEFAULT 'Balanced Builder',
    preferred_tone TEXT DEFAULT 'Friendly and direct',
    pet_name TEXT DEFAULT 'Buddy',
    pet_mood TEXT DEFAULT 'curious',
    achievements JSONB DEFAULT '[]'::jsonb,
    joined_events JSONB DEFAULT '[]'::jsonb,
    completed_events JSONB DEFAULT '[]'::jsonb,
    theme TEXT DEFAULT 'Dark',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    last_active DATE DEFAULT CURRENT_DATE
);

-- 2. Create Habits Table
CREATE TABLE public.habits (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT REFERENCES public.users(username) ON DELETE CASCADE NOT NULL,
    name TEXT NOT NULL,
    habit_type TEXT NOT NULL,
    emoji TEXT NOT NULL,
    completions JSONB DEFAULT '[]'::jsonb,
    created_at DATE DEFAULT CURRENT_DATE,
    UNIQUE(user_id, name)
);

-- 3. Create Pets Table
CREATE TABLE public.pets (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT REFERENCES public.users(username) ON DELETE CASCADE NOT NULL UNIQUE,
    name TEXT DEFAULT 'Buddy',
    growth_level INTEGER DEFAULT 1,
    hunger INTEGER DEFAULT 50,
    last_fed TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);
