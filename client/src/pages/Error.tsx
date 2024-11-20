import { useRouteError, isRouteErrorResponse } from 'react-router-dom'

export default function ErrorPage() {
  // you don't need to explicitly set error to `unknown`
  const error = useRouteError()
  let errorMessage: string

  if (isRouteErrorResponse(error)) {
    // error is type `ErrorResponse`
    errorMessage = error.error?.message || error.statusText
  } else if (error instanceof Error) {
    errorMessage = error.message
  } else if (typeof error === 'string') {
    errorMessage = error
  } else {
    console.error(error)
    errorMessage = 'Unknown error'
  }

  return (
    <div
      id='error-page'
      className='flex h-screen flex-col items-center justify-center gap-8'
    >
      <h1 className='text-4xl font-bold'>Oops!</h1>
      <p>Sorry, an unexpected error has occurred.</p>
      <p className='text-slate-400'>
        <i>{errorMessage}</i>
      </p>
    </div>
  )
}
