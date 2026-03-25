-- ============================================================
-- MIGRAZIONE 004 — Indici
-- ============================================================

CREATE INDEX idx_customers_company     ON customers(company_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_customers_search      ON customers(company_id, name);
CREATE INDEX idx_products_company_tier ON products(company_id, tier) WHERE is_active = true;
CREATE INDEX idx_products_category     ON products(category_id) WHERE is_active = true;
CREATE INDEX idx_quotes_company        ON quotes(company_id);
CREATE INDEX idx_quotes_status         ON quotes(company_id, status);
CREATE INDEX idx_quotes_customer       ON quotes(customer_id);
CREATE INDEX idx_quotes_number         ON quotes(company_id, year, number);
CREATE INDEX idx_windows_quote         ON windows(quote_id);
CREATE INDEX idx_line_items_quote      ON line_items(quote_id);
CREATE INDEX idx_line_items_window     ON line_items(window_id);
CREATE INDEX idx_bot_sessions_chat     ON bot_sessions(telegram_chat_id);
CREATE INDEX idx_activity_entity       ON activity_log(company_id, entity_type, entity_id);
CREATE INDEX idx_activity_date         ON activity_log(company_id, created_at DESC);
