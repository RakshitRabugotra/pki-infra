import { APIResponse, LoginInfoResponse } from '@/types'

export interface AuthCredentials {
  email: string
  password: string
}

export interface SignUpCredentials extends AuthCredentials {
  fullname: string
  email: string
  password: string
  pemFile: File
}

/**
 * Gets the current logged-in user
 */
export async function getUser(): Promise<Response<LoginInfoResponse>> {
  let response = null,
    error = null
  await fetch('/api/@me', {
    method: 'GET',
    credentials: 'include', // Send cookies (session) along with the request
  })
    .then((resp) => (resp ? (resp.json() as Promise<LoginInfoResponse>) : null))
    .then((json) => {
      if (json && json.status === 'error') {
        Promise.reject(json)
      } else {
        response = json
      }
    })
    .catch((err) => {
      error = err
    })

  return { response, error }
}

// The response from the API calls
interface Response<T> {
  response: T | null
  error: any | null
}

/**
 For authentication
*/

export async function signInWithEmail({
  email,
  password,
}: AuthCredentials): Promise<Response<LoginInfoResponse>> {
  const fd = new FormData()
  fd.append('email', email)
  fd.append('password', password)

  let response = null,
    error = null

  await fetch('/api/login', {
    method: 'POST',
    credentials: 'include', // Send cookies (session) along with the request
    body: fd,
  })
    .then((resp) => (resp ? (resp.json() as Promise<LoginInfoResponse>) : null))
    .then((json) => {
      if (json && json.status === 'error') {
        return Promise.reject(json)
      } else {
        response = json
      }
    })
    .catch((err) => {
      error = err
    })

  return { response, error }
}

export async function signUpWithEmail({
  fullname,
  email,
  password,
  pemFile,
}: SignUpCredentials): Promise<Response<APIResponse>> {
  const fd = new FormData()
  fd.append('fullname', fullname)
  fd.append('email', email)
  fd.append('password', password)
  fd.append('public_key', pemFile)

  let response = null,
    error = null

  await fetch('/api/register', {
    method: 'POST',
    credentials: 'include', // Send cookies (session) along with the request
    body: fd,
  })
    .then((resp) => (resp ? (resp.json() as Promise<APIResponse>) : null))
    .then((json) => {
      if (json && json.status === 'error') {
        return Promise.reject(json)
      } else {
        response = json
      }
    })
    .catch((err) => {
      error = err
    })

  return { response, error }
}

export async function signOut(): Promise<Response<APIResponse>> {
  let response = null,
    error = null

  await fetch('/api/logout', {
    method: 'GET',
  })
    .then((resp) => (resp ? (resp.json() as Promise<APIResponse>) : null))
    .then((json) => {
      if (json && json.status === 'error') {
        Promise.reject(json)
      } else {
        response = json
      }
    })
    .catch((err) => {
      error = err
    })

  return { response, error }
}
