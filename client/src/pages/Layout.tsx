import { Outlet } from 'react-router-dom'

// Internal Dependencies
import Navbar from '@/components/Navbar'
import { AuthProvider } from '@/contexts/AuthContext'

export default function Layout() {
  return (
    <AuthProvider>
      <Navbar />
      <Outlet />
    </AuthProvider>
  )
}
