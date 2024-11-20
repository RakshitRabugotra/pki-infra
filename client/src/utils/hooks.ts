import { AuthContext } from '@/contexts/AuthContext'
import { useContext, useEffect } from 'react'
// Internal constants for the file
import * as Constants from './constants'

/**
 * To set the title of the page
 */
export const useTitle = (
  pageTitle: string,
): { currentTitle: string; baseTitle: string } => {
  // Call this function every time the pageTitle changes
  useEffect(() => {
    // Set the title of the page on load
    document.title = `${Constants.APP_NAME} — ${pageTitle}`
    // Revert the title of the page to the app name
    return () => {
      document.title = Constants.APP_NAME
    }
  }, [pageTitle])

  return {
    currentTitle: `${Constants.APP_NAME} — ${pageTitle}`,
    baseTitle: Constants.APP_NAME,
  }
}


// This hook can be used to access the user info.
export const useAuth = () => {
  const value = useContext(AuthContext)
  if (process.env.NODE_ENV !== 'production') {
    if (!value) {
      throw new Error('useSession must be wrapped in a <SessionProvider />')
    }
  }
  return value
}