import { BrowserRouter, Routes, Route } from 'react-router-dom'
import AppLayout from './components/layout/AppLayout'
import LoginPage from './features/auth/LoginPage'
import RegisterPage from './features/auth/RegisterPage'
import OnboardingWizard from './features/onboarding/OnboardingWizard'
import CatalogPage from './features/catalog/CatalogPage'
import DashboardPage from './features/dashboard/DashboardPage'
import QuotesPage from './features/quotes/QuotesPage'
import CustomersPage from './features/customers/CustomersPage'
import {
  SettingsPage,
} from './features/placeholder/PlaceholderPages'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Pagine pubbliche */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/onboarding" element={<OnboardingWizard />} />

        {/* Pagine protette con layout */}
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/quotes" element={<QuotesPage />} />
          <Route path="/customers" element={<CustomersPage />} />
          <Route path="/catalog" element={<CatalogPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
