import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../../lib/supabase'
import { useAuthStore } from '../../store/authStore'
import { getCompany, getCompanySettings, ensureCompanyExists } from './authService'

/** Hook per gestire l'autenticazione — carica user, company e settings */
export function useAuth() {
  const { user, company, settings, isLoading, setUser, setCompany, setSettings, setLoading, clear } = useAuthStore()

  useEffect(() => {
    // Carica sessione iniziale
    const loadSession = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession()

        if (session?.user) {
          setUser(session.user)
          let comp = await getCompany()
          // Per utenti OAuth senza company, creala automaticamente
          if (!comp) comp = await ensureCompanyExists()
          const sett = await getCompanySettings()
          setCompany(comp)
          setSettings(sett)
        }
      } catch (err) {
        console.error('Auth load error:', err)
      } finally {
        setLoading(false)
      }
    }

    loadSession()

    // Ascolta cambiamenti auth
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (event === 'SIGNED_IN' && session?.user) {
          setUser(session.user)
          let comp = await getCompany()
          // Per utenti OAuth senza company, creala automaticamente
          if (!comp) comp = await ensureCompanyExists()
          const sett = await getCompanySettings()
          setCompany(comp)
          setSettings(sett)
        } else if (event === 'SIGNED_OUT') {
          clear()
        }
      }
    )

    return () => subscription.unsubscribe()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return { user, company, settings, isLoading }
}

/** Hook per proteggere una route — redirect a /login se non autenticato */
export function useRequireAuth() {
  const { user, isLoading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isLoading && !user) {
      navigate('/login', { replace: true })
    }
  }, [user, isLoading, navigate])

  return { user, isLoading }
}
