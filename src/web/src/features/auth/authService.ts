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
