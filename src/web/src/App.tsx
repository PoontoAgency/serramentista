import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={
          <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
            <div className="text-center">
              <h1 className="text-4xl font-bold text-neutral-900 mb-4">
                🪟 Serramentista
              </h1>
              <p className="text-neutral-600 text-lg mb-8">
                Il preventivo in tasca. Per ogni finestra, in ogni casa.
              </p>
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-light text-primary rounded-lg text-sm font-medium">
                🚧 Dashboard in sviluppo — M1
              </div>
            </div>
          </div>
        } />
      </Routes>
    </BrowserRouter>
  )
}

export default App
