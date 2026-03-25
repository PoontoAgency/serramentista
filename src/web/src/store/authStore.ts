import { create } from 'zustand'
import type { User } from '@supabase/supabase-js'
import type { Company, CompanySettings } from '../types'

interface AuthState {
  user: User | null
  company: Company | null
  settings: CompanySettings | null
  isLoading: boolean

  setUser: (user: User | null) => void
  setCompany: (company: Company | null) => void
  setSettings: (settings: CompanySettings | null) => void
  setLoading: (loading: boolean) => void
  clear: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  company: null,
  settings: null,
  isLoading: true,

  setUser: (user) => set({ user }),
  setCompany: (company) => set({ company }),
  setSettings: (settings) => set({ settings }),
  setLoading: (isLoading) => set({ isLoading }),
  clear: () => set({ user: null, company: null, settings: null, isLoading: false }),
}))
