import { supabase } from '../../lib/supabase'
import type { Company, CompanySettings } from '../../types'

/** Registra un nuovo serramentista */
export async function signUp(email: string, password: string, companyName: string, ownerName: string, phone: string) {
  // 1. Crea utente su Supabase Auth
  const { data: authData, error: authError } = await supabase.auth.signUp({
    email,
    password,
  })

  if (authError) throw authError
  if (!authData.user) throw new Error('Registrazione fallita')

  // 2. Crea profilo azienda (trigger seed_new_company creerà settings + presets)
  const { error: companyError } = await supabase
    .from('companies')
    .insert({
      id: authData.user.id,
      company_name: companyName,
      owner_name: ownerName,
      phone,
      email,
    })

  if (companyError) throw companyError

  return authData
}

/** Login */
export async function signIn(email: string, password: string) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  })
  if (error) throw error
  return data
}

/** Login con Google */
export async function signInWithGoogle() {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: `${window.location.origin}/`,
    },
  })
  if (error) throw error
  return data
}

/** Logout */
export async function signOut() {
  const { error } = await supabase.auth.signOut()
  if (error) throw error
}

/** Carica il profilo azienda dell'utente corrente */
export async function getCompany(): Promise<Company | null> {
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return null

  const { data, error } = await supabase
    .from('companies')
    .select('*')
    .eq('id', user.id)
    .single()

  if (error) return null
  return data as Company
}

/** Carica le impostazioni azienda */
export async function getCompanySettings(): Promise<CompanySettings | null> {
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return null

  const { data, error } = await supabase
    .from('company_settings')
    .select('*')
    .eq('company_id', user.id)
    .single()

  if (error) return null
  return data as CompanySettings
}

/** Aggiorna profilo azienda */
export async function updateCompany(updates: Partial<Company>) {
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) throw new Error('Non autenticato')

  const { data, error } = await supabase
    .from('companies')
    .update(updates)
    .eq('id', user.id)
    .select()
    .single()

  if (error) throw error
  return data as Company
}

/**
 * Assicura che esista un record company per l'utente corrente.
 * Per utenti OAuth (Google) che non hanno ancora un profilo aziendale.
 * Ritorna la company esistente o ne crea una nuova con dati dal profilo Google.
 */
export async function ensureCompanyExists(): Promise<Company | null> {
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return null

  // Controlla se esiste già
  const { data: existing } = await supabase
    .from('companies')
    .select('*')
    .eq('id', user.id)
    .single()

  if (existing) return existing as Company

  // Estrai dati dal profilo Google
  const meta = user.user_metadata || {}
  const ownerName = meta.full_name || meta.name || ''
  const email = user.email || ''
  const avatar = meta.avatar_url || meta.picture || ''

  // Crea company (trigger seed_new_company creerà settings + presets)
  const { data: newCompany, error } = await supabase
    .from('companies')
    .insert({
      id: user.id,
      company_name: ownerName ? `${ownerName}` : 'La mia azienda',
      owner_name: ownerName,
      email,
      phone: '',
      logo_url: avatar,
      onboarding_completed: false,
    })
    .select()
    .single()

  if (error) {
    console.error('Errore creazione company OAuth:', error)
    return null
  }

  return newCompany as Company
}
