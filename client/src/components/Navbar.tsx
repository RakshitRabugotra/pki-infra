import { NavLink } from 'react-router-dom'

export default function Navbar() {
  return (
    <nav>
      <NavLink className={navLinkState} to='/'>
        Home
      </NavLink>
      <NavLink className={navLinkState} to='profile'>
        Profile
      </NavLink>
      <NavLink className={navLinkState} to='settings'>
        Settings
      </NavLink>
    </nav>
  )
}

const navLinkState = ({
  isActive,
  isPending,
}: {
  isActive: boolean
  isPending: boolean
}) => {
  const pending = 'text-gray-500'
  const active = 'text-red-200'

  return isPending ? pending : isActive ? active : ''
}
