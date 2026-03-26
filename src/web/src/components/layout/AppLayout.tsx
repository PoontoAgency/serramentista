import { Outlet, Navigate } from 'react-router-dom'
import { useAuth } from '../../features/auth/useAuth'
import { FullPageSpinner } from '../ui/Spinner'
import Sidebar from './Sidebar'
import Header from './Header'

/** Layout protetto: se non autenticato → login. Se onboarding incompleto → /onboarding */
export default function AppLayout() {
  const { user, company, isLoading } = useAuth()

  if (isLoading) return <FullPageSpinner />
  if (!user) return <Navigate to="/login" replace />
  if (!company || !company.onboarding_completed) return <Navigate to="/onboarding" replace />

  return (
    <div className="flex min-h-screen bg-neutral-50">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
