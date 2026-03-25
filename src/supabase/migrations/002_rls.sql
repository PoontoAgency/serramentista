-- ============================================================
-- MIGRAZIONE 002 — Row Level Security
-- Ogni azienda vede solo i propri dati
-- ============================================================

-- Companies
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
CREATE POLICY "companies_own" ON companies FOR ALL USING (id = auth.uid());

-- Company Settings
ALTER TABLE company_settings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "settings_own" ON company_settings FOR ALL USING (company_id = auth.uid());

-- Customers
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
CREATE POLICY "customers_own" ON customers FOR ALL USING (company_id = auth.uid());

-- Product Categories
ALTER TABLE product_categories ENABLE ROW LEVEL SECURITY;
CREATE POLICY "categories_own" ON product_categories FOR ALL USING (company_id = auth.uid());

-- Products
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
CREATE POLICY "products_own" ON products FOR ALL USING (company_id = auth.uid());

-- Extra Presets
ALTER TABLE extra_presets ENABLE ROW LEVEL SECURITY;
CREATE POLICY "presets_own" ON extra_presets FOR ALL USING (company_id = auth.uid());

-- Quotes
ALTER TABLE quotes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "quotes_own" ON quotes FOR ALL USING (company_id = auth.uid());

-- Windows (via quote join)
ALTER TABLE windows ENABLE ROW LEVEL SECURITY;
CREATE POLICY "windows_own" ON windows FOR ALL
  USING (quote_id IN (SELECT id FROM quotes WHERE company_id = auth.uid()));

-- Line Items (via quote join)
ALTER TABLE line_items ENABLE ROW LEVEL SECURITY;
CREATE POLICY "line_items_own" ON line_items FOR ALL
  USING (quote_id IN (SELECT id FROM quotes WHERE company_id = auth.uid()));

-- Quote Extras (via quote join)
ALTER TABLE quote_extras ENABLE ROW LEVEL SECURITY;
CREATE POLICY "quote_extras_own" ON quote_extras FOR ALL
  USING (quote_id IN (SELECT id FROM quotes WHERE company_id = auth.uid()));

-- Bot Sessions
ALTER TABLE bot_sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "sessions_own" ON bot_sessions FOR ALL USING (company_id = auth.uid());

-- Activity Log
ALTER TABLE activity_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY "activity_own" ON activity_log FOR ALL USING (company_id = auth.uid());
