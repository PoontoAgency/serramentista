-- seed_catalog_demo.sql
-- Seed di esempio per catalogo demo — 3 prodotti per tier per categoria
-- Eseguire con: psql o tramite Supabase SQL Editor
-- NOTA: sostituire '__COMPANY_ID__' con l'UUID dell'azienda reale

-- Categorie
INSERT INTO product_categories (id, company_id, name, sort_order) VALUES
  ('cat-profili',  '__COMPANY_ID__', 'Profili',     1),
  ('cat-vetri',    '__COMPANY_ID__', 'Vetri',       2),
  ('cat-accessori','__COMPANY_ID__', 'Accessori',   3)
ON CONFLICT DO NOTHING;

-- Profili
INSERT INTO products (company_id, category_id, name, sku, supplier, tier, unit, price_per_unit, window_types) VALUES
  ('__COMPANY_ID__', 'cat-profili', 'Profilo PVC Standard',    'PRF-B01', 'Rehau',         'base',  'mq', 85.00,  '["battente","vasistas"]'),
  ('__COMPANY_ID__', 'cat-profili', 'Profilo PVC Rinforzato',  'PRF-M01', 'Schüco',        'medio', 'mq', 120.00, '["battente","vasistas","scorrevole"]'),
  ('__COMPANY_ID__', 'cat-profili', 'Profilo Alluminio Taglio','PRF-T01', 'Metra',          'top',   'mq', 175.00, '["battente","vasistas","scorrevole","portafinestra"]')
ON CONFLICT DO NOTHING;

-- Vetri
INSERT INTO products (company_id, category_id, name, sku, supplier, tier, unit, price_per_unit, window_types) VALUES
  ('__COMPANY_ID__', 'cat-vetri', 'Vetro 4/16/4 Argon',       'VTR-B01', 'Saint-Gobain',  'base',  'mq', 45.00,  '["battente","vasistas","scorrevole","portafinestra"]'),
  ('__COMPANY_ID__', 'cat-vetri', 'Vetro Basso Emissivo',      'VTR-M01', 'Guardian',      'medio', 'mq', 68.00,  '["battente","vasistas","scorrevole","portafinestra"]'),
  ('__COMPANY_ID__', 'cat-vetri', 'Vetro Triplo Selettivo',    'VTR-T01', 'AGC',           'top',   'mq', 95.00,  '["battente","vasistas","scorrevole","portafinestra"]')
ON CONFLICT DO NOTHING;

-- Accessori
INSERT INTO products (company_id, category_id, name, sku, supplier, tier, unit, price_per_unit, window_types) VALUES
  ('__COMPANY_ID__', 'cat-accessori', 'Maniglia Standard',      'ACC-B01', 'Hoppe',   'base',  'pz', 15.00,  '["battente","portafinestra"]'),
  ('__COMPANY_ID__', 'cat-accessori', 'Maniglia Design Satinata','ACC-M01', 'Olivari', 'medio', 'pz', 28.00,  '["battente","portafinestra"]'),
  ('__COMPANY_ID__', 'cat-accessori', 'Maniglia Minimal Cromo',  'ACC-T01', 'FSB',     'top',   'pz', 45.00,  '["battente","portafinestra"]')
ON CONFLICT DO NOTHING;

-- Extra presets
INSERT INTO extra_presets (company_id, name, description, default_unit, default_price) VALUES
  ('__COMPANY_ID__', 'Posa in opera',              'Installazione completa', 'pz', 150.00),
  ('__COMPANY_ID__', 'Smaltimento vecchi infissi', 'Rimozione e smaltimento', 'pz', 50.00),
  ('__COMPANY_ID__', 'Controtelaio',               'Controtelaio metallico',  'pz', 35.00),
  ('__COMPANY_ID__', 'Davanzale marmo',            'Davanzale in marmo',      'ml', 45.00),
  ('__COMPANY_ID__', 'Cassonetto coibentato',      'Cassonetto isolato',      'pz', 80.00)
ON CONFLICT DO NOTHING;
