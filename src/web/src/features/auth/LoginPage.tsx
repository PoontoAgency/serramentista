import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { toast } from 'sonner'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import { signIn } from './authService'

export default function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) return

    setLoading(true)
    try {
      await signIn(email, password)
      toast.success('Accesso effettuato!')
      navigate('/', { replace: true })
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Errore di accesso')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-neutral-900">🪟 Serramentista</h1>
          <p className="text-neutral-600 mt-2">Accedi alla tua dashboard</p>
        </div>

        {/* Form */}
        <div className="bg-white rounded-2xl border border-neutral-200 shadow-sm p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            <Input
              label="Email"
              type="email"
              placeholder="nome@azienda.it"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
            />
            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <Button type="submit" loading={loading} className="w-full">
              Accedi
            </Button>
          </form>
        </div>

        {/* Link registrazione */}
        <p className="text-center text-sm text-neutral-600 mt-6">
          Non hai un account?{' '}
          <Link to="/register" className="text-primary font-medium hover:underline">
            Registrati gratis
          </Link>
        </p>
      </div>
    </div>
  )
}
