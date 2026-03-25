-- ============================================================
-- MIGRAZIONE 003 — Trigger e Funzioni
-- ============================================================

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_companies_updated BEFORE UPDATE ON companies
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_customers_updated BEFORE UPDATE ON customers
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_products_updated BEFORE UPDATE ON products
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_quotes_updated BEFORE UPDATE ON quotes
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_bot_sessions_updated BEFORE UPDATE ON bot_sessions
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Aggiorna statistiche cliente
CREATE OR REPLACE FUNCTION update_customer_stats()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.customer_id IS NOT NULL THEN
    UPDATE customers SET
      total_quotes = (SELECT COUNT(*) FROM quotes WHERE customer_id = NEW.customer_id AND status != 'draft'),
      total_accepted = (SELECT COUNT(*) FROM quotes WHERE customer_id = NEW.customer_id AND status = 'accepted'),
      total_value = COALESCE((SELECT SUM(total_top) FROM quotes WHERE customer_id = NEW.customer_id AND status = 'accepted'), 0)
    WHERE id = NEW.customer_id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_quote_stats AFTER INSERT OR UPDATE OF status ON quotes
  FOR EACH ROW EXECUTE FUNCTION update_customer_stats();

-- Genera numero preventivo progressivo
CREATE OR REPLACE FUNCTION generate_quote_number(p_company_id UUID)
RETURNS TEXT AS $$
DECLARE
  v_prefix TEXT;
  v_year INTEGER;
  v_count INTEGER;
BEGIN
  SELECT quote_prefix INTO v_prefix FROM company_settings WHERE company_id = p_company_id;
  v_year := EXTRACT(YEAR FROM NOW());
  SELECT COUNT(*) + 1 INTO v_count FROM quotes
    WHERE company_id = p_company_id AND year = v_year;
  RETURN v_prefix || '-' || v_year || '-' || LPAD(v_count::TEXT, 4, '0');
END;
$$ LANGUAGE plpgsql;

-- Seed dati default per nuova azienda
CREATE OR REPLACE FUNCTION seed_new_company()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO company_settings (company_id) VALUES (NEW.id);

  INSERT INTO extra_presets (company_id, name, default_price, unit, sort_order) VALUES
    (NEW.id, 'Posa in opera',     0, 'pz', 1),
    (NEW.id, 'Smaltimento vecchi', 0, 'pz', 2),
    (NEW.id, 'Ponteggio',         0, 'forfait', 3),
    (NEW.id, 'Trasferta',         0, 'forfait', 4),
    (NEW.id, 'Controtelaio',      0, 'pz', 5);

  INSERT INTO product_categories (company_id, name, sort_order) VALUES
    (NEW.id, 'Profili',    1),
    (NEW.id, 'Vetri',      2),
    (NEW.id, 'Accessori',  3);

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_seed_company AFTER INSERT ON companies
  FOR EACH ROW EXECUTE FUNCTION seed_new_company();
