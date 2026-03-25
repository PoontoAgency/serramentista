import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { toast } from 'sonner'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import { signUp } from './authService'

export default function RegisterPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    companyName: '',
    ownerName: '',
    phone: '',
    email: '',
    password: '',
    confirmPassword: '',
  })

  const set = (key: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (form.password !== form.confirmPassword) {
      toast.error('Le password non coincidono')
      return
    }

    if (form.password.length < 6) {
      toast.error('La password deve avere almeno 6 caratteri')
      return
    }

    setLoading(true)
    try {
      await signUp(form.email, form.password, form.companyName, form.ownerName, form.phone)
      toast.success('Registrazione completata! Benvenuto.')
      navigate('/', { replace: true })
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Errore di registrazione')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-neutral-900">🪟 Serramentista</h1>
          <p className="text-neutral-600 mt-2">Crea il tuo account gratuito</p>
        </div>

        {/* Form */}
        <div className="bg-white rounded-2xl border border-neutral-200 shadow-sm p-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Nome azienda"
              placeholder="Serramenti Rossi S.r.l."
              value={form.companyName}
              onChange={set('companyName')}
              required
              autoFocus
            />
            <Input
              label="Nome e cognome"
              placeholder="Mario Rossi"
              value={form.ownerName}
              onChange={set('ownerName')}
              required
            />
            <Input
              label="Telefono"
              type="tel"
              placeholder="+39 333 1234567"
              value={form.phone}
              onChange={set('phone')}
              required
            />
            <Input
              label="Email"
              type="email"
              placeholder="nome@azienda.it"
              value={form.email}
              onChange={set('email')}
              required
            />
            <Input
              label="Password"
              type="password"
              placeholder="Almeno 6 caratteri"
              value={form.password}
              onChange={set('password')}
              required
            />
            <Input
              label="Conferma password"
              type="password"
              placeholder="Ripeti la password"
              value={form.confirmPassword}
              onChange={set('confirmPassword')}
              required
            />
            <Button type="submit" loading={loading} className="w-full mt-2">
              Registrati
            </Button>
          </form>
        </div>

        {/* Link login */}
        <p className="text-center text-sm text-neutral-600 mt-6">
          Hai già un account?{' '}
          <Link to="/login" className="text-primary font-medium hover:underline">
            Accedi
          </Link>
        </p>
      </div>
    </div>
  )
}
