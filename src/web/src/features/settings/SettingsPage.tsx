/**
 * SettingsPage.tsx — Pagina impostazioni con 3 tab
 */
import { useState } from 'react';
import { useCompanyProfile, useUpdateCompanyProfile, useUploadLogo,
         useCompanySettings, useUpdateCompanySettings } from './useSettings';
import { TelegramConnect } from './TelegramConnect';
import './settings.css';

type Tab = 'profile' | 'quote' | 'telegram';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<Tab>('profile');

  const { data: profile, isLoading: profileLoading } = useCompanyProfile();
  const { data: settings, isLoading: settingsLoading } = useCompanySettings();
  const updateProfile = useUpdateCompanyProfile();
  const updateSettings = useUpdateCompanySettings();
  const uploadLogo = useUploadLogo();

  // Profile form state
  const [profileForm, setProfileForm] = useState<Record<string, string>>({});
  const [settingsForm, setSettingsForm] = useState<Record<string, string>>({});
  const [saved, setSaved] = useState('');

  const showSaved = (msg: string) => {
    setSaved(msg);
    setTimeout(() => setSaved(''), 2000);
  };

  const handleProfileSave = async () => {
    if (!profile?.id) return;
    await updateProfile.mutateAsync({ id: profile.id, ...profileForm });
    showSaved('Profilo salvato!');
  };

  const handleSettingsSave = async () => {
    if (!settings?.id) return;
    const updates: any = {};
    if (settingsForm.default_margin_pct) updates.default_margin_pct = parseFloat(settingsForm.default_margin_pct);
    if (settingsForm.iva_pct) updates.iva_pct = parseFloat(settingsForm.iva_pct);
    if (settingsForm.quote_validity_days) updates.quote_validity_days = parseInt(settingsForm.quote_validity_days);
    if (settingsForm.quote_prefix) updates.quote_prefix = settingsForm.quote_prefix;
    await updateSettings.mutateAsync({ id: settings.id, ...updates });
    showSaved('Impostazioni salvate!');
  };

  const handleLogoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !profile?.id) return;
    await uploadLogo.mutateAsync({ companyId: profile.id, file });
    showSaved('Logo aggiornato!');
  };

  return (
    <div className="settings-page">
      <div className="settings-header">
        <h2>⚙️ Impostazioni</h2>
        {saved && <span className="saved-toast">✅ {saved}</span>}
      </div>

      <div className="settings-tabs">
        <button className={`tab ${activeTab === 'profile' ? 'active' : ''}`}
                onClick={() => setActiveTab('profile')}>
          👤 Profilo azienda
        </button>
        <button className={`tab ${activeTab === 'quote' ? 'active' : ''}`}
                onClick={() => setActiveTab('quote')}>
          📋 Preventivo
        </button>
        <button className={`tab ${activeTab === 'telegram' ? 'active' : ''}`}
                onClick={() => setActiveTab('telegram')}>
          🤖 Telegram
        </button>
      </div>

      {/* Tab Profilo */}
      {activeTab === 'profile' && (
        <div className="tab-content">
          {profileLoading ? (
            <div className="loading">Caricamento...</div>
          ) : profile ? (
            <div className="settings-form">
              <h3>Dati azienda</h3>
              <div className="form-grid">
                <div className="form-group">
                  <label>Nome azienda</label>
                  <input type="text" defaultValue={profile.name || ''}
                         onChange={e => setProfileForm({...profileForm, name: e.target.value})} />
                </div>
                <div className="form-group">
                  <label>P.IVA</label>
                  <input type="text" defaultValue={profile.vat_number || ''}
                         onChange={e => setProfileForm({...profileForm, vat_number: e.target.value})} />
                </div>
                <div className="form-group">
                  <label>Indirizzo</label>
                  <input type="text" defaultValue={profile.address || ''}
                         onChange={e => setProfileForm({...profileForm, address: e.target.value})} />
                </div>
                <div className="form-group">
                  <label>Città</label>
                  <input type="text" defaultValue={profile.city || ''}
                         onChange={e => setProfileForm({...profileForm, city: e.target.value})} />
                </div>
                <div className="form-group">
                  <label>Provincia</label>
                  <input type="text" defaultValue={profile.province || ''} maxLength={2}
                         onChange={e => setProfileForm({...profileForm, province: e.target.value})} />
                </div>
                <div className="form-group">
                  <label>Telefono</label>
                  <input type="tel" defaultValue={profile.phone || ''}
                         onChange={e => setProfileForm({...profileForm, phone: e.target.value})} />
                </div>
                <div className="form-group">
                  <label>Email</label>
                  <input type="email" defaultValue={profile.email || ''}
                         onChange={e => setProfileForm({...profileForm, email: e.target.value})} />
                </div>
              </div>

              <div className="logo-section">
                <h3>Logo</h3>
                {profile.logo_url && (
                  <img src={profile.logo_url} alt="Logo" className="logo-preview" />
                )}
                <label className="logo-upload btn-secondary">
                  {uploadLogo.isPending ? 'Caricamento...' : '📤 Carica logo'}
                  <input type="file" accept="image/*" onChange={handleLogoUpload} hidden />
                </label>
              </div>

              <div className="form-actions">
                <button onClick={handleProfileSave} className="btn-primary"
                        disabled={updateProfile.isPending}>
                  {updateProfile.isPending ? 'Salvataggio...' : 'Salva profilo'}
                </button>
              </div>
            </div>
          ) : (
            <div className="empty-state">Profilo non trovato.</div>
          )}
        </div>
      )}

      {/* Tab Preventivo */}
      {activeTab === 'quote' && (
        <div className="tab-content">
          {settingsLoading ? (
            <div className="loading">Caricamento...</div>
          ) : settings ? (
            <div className="settings-form">
              <h3>Impostazioni preventivo</h3>
              <div className="form-grid">
                <div className="form-group">
                  <label>Margine default (%)</label>
                  <input type="number" min="0" max="100" step="1"
                         defaultValue={settings.default_margin_pct}
                         onChange={e => setSettingsForm({...settingsForm, default_margin_pct: e.target.value})} />
                </div>
                <div className="form-group">
                  <label>IVA (%)</label>
                  <input type="number" min="0" max="100" step="1"
                         defaultValue={settings.iva_pct}
                         onChange={e => setSettingsForm({...settingsForm, iva_pct: e.target.value})} />
                </div>
                <div className="form-group">
                  <label>Validità preventivo (giorni)</label>
                  <input type="number" min="1" max="365"
                         defaultValue={settings.quote_validity_days}
                         onChange={e => setSettingsForm({...settingsForm, quote_validity_days: e.target.value})} />
                </div>
                <div className="form-group">
                  <label>Prefisso numerazione</label>
                  <input type="text" maxLength={5}
                         defaultValue={settings.quote_prefix}
                         onChange={e => setSettingsForm({...settingsForm, quote_prefix: e.target.value})} />
                </div>
              </div>
              <div className="form-actions">
                <button onClick={handleSettingsSave} className="btn-primary"
                        disabled={updateSettings.isPending}>
                  {updateSettings.isPending ? 'Salvataggio...' : 'Salva impostazioni'}
                </button>
              </div>
            </div>
          ) : (
            <div className="empty-state">Impostazioni non trovate.</div>
          )}
        </div>
      )}

      {/* Tab Telegram */}
      {activeTab === 'telegram' && (
        <div className="tab-content">
          {profile ? (
            <TelegramConnect companyId={profile.id} />
          ) : (
            <div className="loading">Caricamento...</div>
          )}
        </div>
      )}
    </div>
  );
}
