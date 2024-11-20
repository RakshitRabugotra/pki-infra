import {
  createContext,
  type PropsWithChildren,
  useEffect,
  useState,
} from 'react'
import {
  AuthCredentials,
  getUser,
  signInWithEmail,
  signOut,
} from '@/actions/auth'
import { APIResponse, LoginInfoResponse, User } from '@/types'

export const AuthContext = createContext<{
  user: User | null
  error: any | null,
  signIn: (props: AuthCredentials) => Promise<LoginInfoResponse | null>
  signOut: () => Promise<APIResponse | null>
  isLoading: boolean
}>({
  user: null,
  error: null,
  isLoading: false,
  signIn: async () => ({}) as LoginInfoResponse | null,
  signOut: async () => ({}) as APIResponse | null,
})

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<User | null>(null)
  const [error, setError] = useState<APIResponse | null>(null)
  const [isLoading, setLoading] = useState<boolean>(false)

  useEffect(() => {
    setLoading(true)
    // Get the current logged-in use
    getUser().then(({ response, error }) => {
      if (error || !response) {
        setError(error)
        console.error("Couldn't get the user, error: ", error)
      } else {
        setUser(response.user)
      }
      setLoading(false)
    })
    setLoading(false)
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        error,
        signIn: async (props) => {
          const { response: signInResp, error: signInError } =
            await signInWithEmail(props)
          if (signInError || !signInResp) {
            setError(signInError)
            return null
          }
          // Else, get the current user and set it
          const { response: userResp, error: userError } = await getUser()
          if (userError || !userError) {
            setError(userError)
            return null
          }
          return userResp
        },
        signOut: async () => {
          // Try to signout
          const { response, error } = await signOut()
          if (error) {
            setError(error)
            return null
          }
          return response
        },
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
