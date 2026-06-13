CREATE TABLE IF NOT EXISTS public.pet_room (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT REFERENCES public.users(username) ON DELETE CASCADE NOT NULL UNIQUE,
    pet_type TEXT NOT NULL DEFAULT 'dog',
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS assigned_pet_type TEXT;
