-- ============================================================
-- MIGRAZIONE 005 — Storage Buckets
-- ============================================================

INSERT INTO storage.buckets (id, name, public) VALUES
  ('logos',  'logos',  true),
  ('photos', 'photos', false),
  ('pdfs',   'pdfs',   false),
  ('voices', 'voices', false);

-- Policy logos: lettura pubblica, scrittura solo owner
CREATE POLICY "logos_public_read" ON storage.objects FOR SELECT
  USING (bucket_id = 'logos');
CREATE POLICY "logos_owner_write" ON storage.objects FOR INSERT
  WITH CHECK (bucket_id = 'logos' AND auth.uid()::text = (storage.foldername(name))[1]);
CREATE POLICY "logos_owner_update" ON storage.objects FOR UPDATE
  USING (bucket_id = 'logos' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Policy file privati: solo owner
CREATE POLICY "private_owner_read" ON storage.objects FOR SELECT
  USING (bucket_id IN ('photos', 'pdfs', 'voices') AND auth.uid()::text = (storage.foldername(name))[1]);
CREATE POLICY "private_owner_write" ON storage.objects FOR INSERT
  WITH CHECK (bucket_id IN ('photos', 'pdfs', 'voices') AND auth.uid()::text = (storage.foldername(name))[1]);
