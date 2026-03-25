import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { LayoutDashboard, FileText, Users, Package, Settings, LogOut, Menu, X } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { signOut } from '../../features/auth/authService'
import { toast } from 'sonner'

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/quotes', label: 'Preventivi', icon: FileText },
  { to: '/customers', label: 'Clienti', icon: Users },
  { to: '/catalog', label: 'Catalogo', icon: Package },
  { to: '/settings', label: 'Impostazioni', icon: Settings },
]

export default function Sidebar() {
  const company = useAuthStore((s) => s.company)
  const [collapsed, setCollapsed] = useState(false)

  const handleLogout = async () => {
    try {
      await signOut()
      toast.success('Disconnesso')
    } catch {
      toast.error('Errore durante il logout')
    }
  }

  return (
    <>
      {/* Mobile toggle button */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="sidebar-toggle"
        aria-label="Toggle menu"
      >
        {collapsed ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>

      {/* Overlay (mobile) */}
      {collapsed && (
        <div className="sidebar-overlay" onClick={() => setCollapsed(false)} />
      )}

      <aside className={`sidebar ${collapsed ? 'sidebar-open' : ''}`}>
        {/* Logo */}
        <div className="p-6 border-b border-neutral-200">
          <h1 className="text-xl font-bold text-neutral-900">🪟 Serramentista</h1>
          {company && (
            <p className="text-xs text-neutral-600 mt-1 truncate">{company.company_name}</p>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              onClick={() => setCollapsed(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-primary text-white shadow-sm'
                    : 'text-neutral-600 hover:bg-neutral-200/50 hover:text-neutral-900'
                }`
              }
            >
              <Icon className="h-4.5 w-4.5" />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Logout */}
        <div className="p-3 border-t border-neutral-200">
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium text-neutral-600 hover:bg-red-50 hover:text-danger transition-all duration-150 w-full"
          >
            <LogOut className="h-4.5 w-4.5" />
            Esci
          </button>
        </div>
      </aside>
    </>
  )
}
