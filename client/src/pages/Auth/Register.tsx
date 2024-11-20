import { signUpWithEmail } from '@/actions/auth'
import { APIResponse } from '@/types'
import { useEffect, useRef, useState } from 'react'
import { SubmitHandler, useForm } from 'react-hook-form'
import { NavLink, useNavigate } from 'react-router-dom'

interface RegisterForm {
  fullname: string
  email: string
  password: string
}

export default function Register() {
  const {
    register,
    handleSubmit,
    formState: { errors, isLoading },
  } = useForm<RegisterForm>()

  const navigate = useNavigate()
  const [isMounted, setMounted] = useState(false)
  const [submissionError, setSubmissionError] = useState<APIResponse | null>(
    null,
  )
  const fileUploadRef = useRef<HTMLInputElement | null>(null)

  const onSubmit: SubmitHandler<RegisterForm> = async (data) => {
    if (!isMounted || !fileUploadRef.current) return
    // If the files aren't uploaded return
    if (!fileUploadRef.current.files) return
    // Else, get the file content
    const registerData = {
      ...data,
      file: fileUploadRef.current.files[0],
    }
    // Send a request to the server to register
    try {
      const {response, error} = await signUpWithEmail({
        ...registerData,
        pemFile: registerData.file,
      })
      if(!response || error) throw error;
      // If the response is successful, redirect to home
      if (response.status === 'success') {
        return navigate('/login', { replace: true })
      }
    } catch (error) {
      setSubmissionError(error as APIResponse)
    }
  }

  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <main className='flex min-h-screen w-full flex-col items-center justify-center bg-gray-50 p-4'>
      <h2 className='mb-6 text-2xl font-semibold text-gray-800'>Register</h2>

      <form
        className='w-full max-w-md space-y-4 rounded-md bg-white p-6 shadow-lg'
        onSubmit={handleSubmit(onSubmit)}
      >
        <div className='form-group'>
          <label
            htmlFor='full_name'
            className='block text-sm font-medium text-gray-700'
          >
            Full Name
          </label>
          <input
            {...register('fullname', {
              maxLength: 30,
              required: {
                message: 'Fullname is required',
                value: true,
              },
            })}
            className='mt-1 w-full border-b-2 border-solid border-gray-300 p-2 text-gray-700 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500'
          />
          {errors.fullname && (
            <span className='text-sm text-red-500'>
              {errors.fullname.message}
            </span>
          )}
        </div>

        <div className='form-group'>
          <label
            htmlFor='email'
            className='block text-sm font-medium text-gray-700'
          >
            Email Address
          </label>
          <input
            {...register('email', {
              required: {
                message: 'Email address is required',
                value: true,
              },
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: 'Invalid email address',
              },
            })}
            className='mt-1 w-full border-b-2 border-solid border-gray-300 p-2 text-gray-700 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500'
          />
          {errors.email && (
            <span className='text-sm text-red-500'>{errors.email.message}</span>
          )}
        </div>

        <div className='form-group'>
          <label
            htmlFor='password'
            className='block text-sm font-medium text-gray-700'
          >
            Password
          </label>
          <input
            {...register('password', {
              minLength: {
                message: 'Password must be at least 7 characters long',
                value: 7,
              },
              required: {
                message: 'Password required',
                value: true,
              },
            })}
            type='password'
            className='mt-1 w-full border-b-2 border-solid border-gray-300 p-2 text-gray-700 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500'
          />
          {errors.password && (
            <span className='text-sm text-red-500'>
              {errors.password.message}
            </span>
          )}
        </div>

        <div className='form-group'>
          <label
            htmlFor='public_key'
            className='block text-sm font-medium text-gray-700'
          >
            Public Key (PEM format)
          </label>
          <input
            name='pem'
            type='file'
            ref={fileUploadRef}
            className='mt-1 w-full border-b-2 border-solid border-gray-300 p-2 text-gray-700 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500'
          />
        </div>

        <button
          type='submit'
          className='w-full rounded-md bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2'
        >
          {isLoading ? 'Submitting' : 'Register'}
        </button>
      </form>

      {submissionError && (
        <span className='text-sm text-red-500'>{submissionError.message}</span>
      )}

      <p className='mt-4 text-sm text-gray-600'>
        Already have an account?{' '}
        <NavLink to='/login' className='text-indigo-600 hover:underline'>
          Login
        </NavLink>
      </p>
    </main>
  )
}

// <!-- Flash messages (success, error) -->
//   {% with messages = get_flashed_messages(with_categories=true) %}
//   {% if messages %}
//       <ul className="alert alert-info">
//       {% for category, message in messages %}
//           <li>{{ message }}</li>
//       {% endfor %}
//       </ul>
//   {% endif %}
//   {% endwith %}
