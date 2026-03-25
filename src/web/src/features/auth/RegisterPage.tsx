import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { toast } from 'sonner'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import { signUp, signInWithGoogle } from './authService'

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

  const handleGoogle = async () => {
    try {
      await signInWithGoogle()
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Errore con Google')
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
          {/* Google Button */}
          <button
            type="button"
            onClick={handleGoogle}
            className="w-full flex items-center justify-center gap-3 px-4 py-2.5 rounded-lg border border-neutral-200 bg-white text-neutral-700 font-medium text-sm hover:bg-neutral-50 hover:border-neutral-300 transition-all duration-150 mb-5"
          >
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844a4.14 4.14 0 01-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" fill="#4285F4"/>
              <path d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 009 18z" fill="#34A853"/>
              <path d="M3.964 10.71A5.41 5.41 0 013.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 000 9c0 1.452.348 2.827.957 4.042l3.007-2.332z" fill="#FBBC05"/>
              <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 00.957 4.958L3.964 6.29C4.672 4.163 6.656 2.58 9 3.58z" fill="#EA4335"/>
            </svg>
            Registrati con Google
          </button>

          {/* Divider */}
          <div className="flex items-center gap-3 mb-5">
            <div className="flex-1 h-px bg-neutral-200"></div>
            <span className="text-xs text-neutral-400 uppercase">oppure</span>
            <div className="flex-1 h-px bg-neutral-200"></div>
          </div>

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
