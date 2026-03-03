-- Mega App — Supabase schema
-- Run this in Supabase SQL Editor after creating your project

-- profiles (extends auth.users)
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    display_name TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- projects
CREATE TABLE public.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    product_type TEXT NOT NULL DEFAULT 'subscription' CHECK (product_type IN ('subscription', 'ecommerce')),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Migration for existing data:
-- ALTER TABLE public.projects ADD COLUMN product_type TEXT NOT NULL DEFAULT 'subscription' CHECK (product_type IN ('subscription', 'ecommerce'));

-- scenarios (config stored as JSONB = ModelConfig.to_dict())
CREATE TABLE public.scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    notes TEXT DEFAULT '',
    config JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- project_shares (sharing projects between users)
CREATE TABLE public.project_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    owner_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    shared_with_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    role TEXT NOT NULL DEFAULT 'viewer' CHECK (role IN ('viewer', 'editor')),
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (project_id, shared_with_id)
);

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
    INSERT INTO public.profiles (id, email, display_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'display_name', split_part(NEW.email, '@', 1))
    );

    -- Auto-create default project
    INSERT INTO public.projects (user_id, name, description)
    VALUES (NEW.id, 'Main Project', 'Default project created on signup');

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Indexes
CREATE INDEX idx_projects_user ON public.projects(user_id);
CREATE INDEX idx_scenarios_project ON public.scenarios(project_id);
CREATE INDEX idx_scenarios_user ON public.scenarios(user_id);
CREATE INDEX idx_shares_project ON public.project_shares(project_id);
CREATE INDEX idx_shares_shared_with ON public.project_shares(shared_with_id);
CREATE INDEX idx_shares_owner ON public.project_shares(owner_id);

-- ===================== RLS =====================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scenarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_shares ENABLE ROW LEVEL SECURITY;

-- --- profiles ---
-- Open SELECT on profiles (email + display_name) for user lookup when sharing
CREATE POLICY "Anyone can view profiles"
    ON public.profiles FOR SELECT
    USING (true);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- --- projects ---
CREATE POLICY "Users can view own or shared projects"
    ON public.projects FOR SELECT
    USING (
        auth.uid() = user_id
        OR EXISTS (
            SELECT 1 FROM public.project_shares ps
            WHERE ps.project_id = id AND ps.shared_with_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own projects"
    ON public.projects FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own projects"
    ON public.projects FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own projects"
    ON public.projects FOR DELETE
    USING (auth.uid() = user_id);

-- --- scenarios ---
CREATE POLICY "Users can view scenarios of own or shared projects"
    ON public.scenarios FOR SELECT
    USING (
        auth.uid() = user_id
        OR EXISTS (
            SELECT 1 FROM public.project_shares ps
            WHERE ps.project_id = scenarios.project_id AND ps.shared_with_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert scenarios in own or editor-shared projects"
    ON public.scenarios FOR INSERT
    WITH CHECK (
        auth.uid() = user_id
        AND (
            EXISTS (SELECT 1 FROM public.projects p WHERE p.id = project_id AND p.user_id = auth.uid())
            OR EXISTS (
                SELECT 1 FROM public.project_shares ps
                WHERE ps.project_id = scenarios.project_id
                  AND ps.shared_with_id = auth.uid()
                  AND ps.role = 'editor'
            )
        )
    );

CREATE POLICY "Users can update own scenarios or editor-shared"
    ON public.scenarios FOR UPDATE
    USING (
        auth.uid() = user_id
        OR EXISTS (
            SELECT 1 FROM public.project_shares ps
            WHERE ps.project_id = scenarios.project_id
              AND ps.shared_with_id = auth.uid()
              AND ps.role = 'editor'
        )
    );

CREATE POLICY "Users can delete own scenarios or editor-shared"
    ON public.scenarios FOR DELETE
    USING (
        auth.uid() = user_id
        OR EXISTS (
            SELECT 1 FROM public.project_shares ps
            WHERE ps.project_id = scenarios.project_id
              AND ps.shared_with_id = auth.uid()
              AND ps.role = 'editor'
        )
    );

-- --- project_shares ---
CREATE POLICY "Owners can manage shares"
    ON public.project_shares FOR ALL
    USING (auth.uid() = owner_id)
    WITH CHECK (auth.uid() = owner_id);

CREATE POLICY "Shared users can view their shares"
    ON public.project_shares FOR SELECT
    USING (auth.uid() = shared_with_id);
