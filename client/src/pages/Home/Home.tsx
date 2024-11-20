import Heading from '@/components/Heading'

// Custom Hooks
import { useAuth, useTitle } from '@/utils/hooks'
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export default function App() {
  // Set the title of the page
  const title = useTitle('Home')

  const navigate = useNavigate()
  // Get the session information
  const { user } = useAuth()

  useEffect(() => {
    const handler = setTimeout(
      () => user === null && navigate('/login', { replace: true }),
      2500,
    )
    return () => clearTimeout(handler)
  }, [user])

  // Return the rendering part
  return (
    <main className='container flex min-h-screen w-full flex-col'>
      <Heading>Hello, World! - Home page</Heading>

      <h1>{user ? user.full_name : 'User not found, fuck you'}</h1>
      {/* <h2>Welcome, {{ current_user.full_name }}</h2> */}

      {/* {% if not is_verified %}
    <button class="btn btn-success" id="get-verified-btn">Get Verified</button>
    {% endif %}

    <p>Active Users:</p>
    <ul>
        {% for user in active_users %}
        <li>
            {{ user.full_name }} 
            {% if is_verified %}
                <a href="{{ url_for('chat', user_id=user.id) }}">Chat</a>
            {% else %}
                <button class="btn btn-secondary" disabled>Chat</button>
            {% endif %}
        </li>
        {% endfor %}
    </ul> */}
      {/* <a href="{{ url_for('logout') }}">Logout</a> */}
    </main>
  )
}
