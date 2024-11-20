/**
 * Declaring all the modal types
 */
export interface SessionModel {
  id: string
  user_id: string
  session_id: string
  login_time: Date
}

export interface User {
  id: string
  full_name: string
  email: string
  public_key: string
  is_verified: string
}

export interface Message {
  id: string
  sender_id: string
  receiver_id: string
  message: string
  timestamp: Date
}


/**
 * The response returned from the server
 */
export interface APIResponse {
  status: 'success' | 'error' | string
  message: string
}

// Specific responses from the server
export interface LoginInfoResponse extends APIResponse {
  user: User | null
}