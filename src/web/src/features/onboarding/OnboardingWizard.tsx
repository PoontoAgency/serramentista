import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { useAuthStore } from '../../store/authStore'
import { updateCompany } from '../auth/authService'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'

const steps = [
  { title: 'Profilo azienda', description: 'Completa i dati della tua azienda' },
  { title: 'Primo prodotto', description: 'Aggiungi almeno un prodotto al catalogo' },
  { title: 'Collega Telegram', description: 'Collega il bot per fare i preventivi dal cantiere' },
]

export default function OnboardingWizard() {
  const navigate = useNavigate()
  const company = useAuthStore((s) => s.company)
  const setCompany = useAuthStore((s) => s.setCompany)
  const [currentStep, setCurrentStep] = useState(0)
  const [loading, setLoading] = useState(false)

  const [profile, setProfile] = useState({
    vat_number: company?.vat_number || '',
    address: company?.address || '',
    city: company?.city || '',
    province: company?.province || '',
  })

  const handleCompleteOnboarding = async () => {
    setLoading(true)
    try {
      const updated = await updateCompany({ onboarding_completed: true })
      setCompany(updated)
      toast.success('Onboarding completato! Benvenuto in Serramentista 🪟')
      navigate('/', { replace: true })
    } catch {
      toast.error('Errore nel completamento')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveProfile = async () => {
    setLoading(true)
    try {
      const updated = await updateCompany(profile)
      setCompany(updated)
      toast.success('Profilo salvato!')
      setCurrentStep(1)
    } catch {
      toast.error('Errore nel salvataggio')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-lg">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-neutral-900">🪟 Configuriamo tutto</h1>
          <p className="text-neutral-600 mt-2">3 passi e sei operativo</p>
        </div>

        {/* Progress bar */}
        <div className="flex items-center gap-2 mb-8">
          {steps.map((step, i) => (
            <div key={i} className="flex-1">
              <div
                className={`h-1.5 rounded-full transition-colors ${
                  i <= currentStep ? 'bg-primary' : 'bg-neutral-200'
                }`}
              />
              <p className={`text-xs mt-2 ${i <= currentStep ? 'text-primary font-medium' : 'text-neutral-600'}`}>
                {step.title}
              </p>
            </div>
          ))}
        </div>

        {/* Step content */}
        <div className="bg-white rounded-2xl border border-neutral-200 shadow-sm p-8">
          <h2 className="text-lg font-semibold text-neutral-900 mb-1">
            {steps[currentStep].title}
          </h2>
          <p className="text-sm text-neutral-600 mb-6">
            {steps[currentStep].description}
          </p>

          {/* Step 1: Profilo */}
          {currentStep === 0 && (
            <div className="space-y-4">
              <Input
                label="Partita IVA"
                placeholder="IT01234567890"
                value={profile.vat_number}
                onChange={(e) => setProfile((p) => ({ ...p, vat_number: e.target.value }))}
              />
              <Input
                label="Indirizzo"
                placeholder="Via Roma 1"
                value={profile.address}
                onChange={(e) => setProfile((p) => ({ ...p, address: e.target.value }))}
              />
              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="Città"
                  placeholder="Milano"
                  value={profile.city}
                  onChange={(e) => setProfile((p) => ({ ...p, city: e.target.value }))}
                />
                <Input
                  label="Provincia"
                  placeholder="MI"
                  value={profile.province}
                  onChange={(e) => setProfile((p) => ({ ...p, province: e.target.value }))}
                />
              </div>
              <Button onClick={handleSaveProfile} loading={loading} className="w-full mt-2">
                Salva e continua →
              </Button>
            </div>
          )}

          {/* Step 2: Catalogo (skip per MVP) */}
          {currentStep === 1 && (
            <div className="space-y-4">
              <div className="bg-primary-light/50 rounded-lg p-4 text-sm text-primary">
                <p className="font-medium">Per ora puoi saltare questo passo</p>
                <p className="mt-1 text-primary/80">
                  Potrai aggiungere prodotti in qualsiasi momento dalla sezione Catalogo.
                </p>
              </div>
              <div className="flex gap-3">
                <Button variant="secondary" onClick={() => setCurrentStep(0)} className="flex-1">
                  ← Indietro
                </Button>
                <Button onClick={() => setCurrentStep(2)} className="flex-1">
                  Continua →
                </Button>
              </div>
            </div>
          )}

          {/* Step 3: Telegram */}
          {currentStep === 2 && (
            <div className="space-y-4">
              <div className="bg-neutral-50 rounded-lg p-4 text-sm space-y-3">
                <p className="font-medium text-neutral-900">
                  Come collegare il bot Telegram:
                </p>
                <ol className="list-decimal list-inside space-y-2 text-neutral-600">
                  <li>Apri Telegram e cerca <span className="font-mono text-primary">@SerrBot</span></li>
                  <li>Premi <strong>Avvia</strong></li>
                  <li>Invia il comando con il tuo token:</li>
                </ol>
                <div className="bg-white rounded border border-neutral-200 p-3 font-mono text-sm text-center">
                  /connect {company?.telegram_token || 'caricamento...'}
                </div>
                <p className="text-xs text-neutral-600">
                  Puoi farlo anche dopo, dalla sezione Impostazioni.
                </p>
              </div>
              <div className="flex gap-3">
                <Button variant="secondary" onClick={() => setCurrentStep(1)} className="flex-1">
                  ← Indietro
                </Button>
                <Button onClick={handleCompleteOnboarding} loading={loading} className="flex-1">
                  Completa setup ✓
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
