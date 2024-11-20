import { signInWithEmail } from '@/actions/auth'
import { APIResponse } from '@/types'
import { useState } from 'react'
import { SubmitHandler, useForm } from 'react-hook-form'
import { NavLink, useNavigate } from 'react-router-dom'

interface LoginForm {
  email: string
  password: string
}

export default function Login() {
  const navigate = useNavigate()
  const {
    register,
    handleSubmit,
    formState: { errors, isLoading },
  } = useForm<LoginForm>()

  const [submissionError, setSubmissionError] = useState<APIResponse | null>(
    null,
  )

  const onSubmit: SubmitHandler<LoginForm> = async (data) => {
    // Send a request to the server to register
    try {
      const {response, error} = await signInWithEmail({
        ...data,
      })
      if(!response || error) throw error;
      // If the response is successful, redirect to home
      if (response.status === 'success') {
        return navigate('/', { replace: true })
      }
    } catch (error) {
      setSubmissionError(error as APIResponse)
    }
  }

  return (
    <main className='flex min-h-screen w-full flex-col items-center justify-center bg-gray-50 p-4'>
      <h2 className='mb-6 text-2xl font-semibold text-gray-800'>Login</h2>

      <form
        className='w-full max-w-md space-y-4 rounded-md bg-white p-6 shadow-lg'
        onSubmit={handleSubmit(onSubmit)}
      >
        {/* Email Field */}
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

        {/* Password Field */}
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
                value: 7,
                message: 'Password must be at least 7 characters long',
              },
              required: {
                message: 'Password is required',
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

        {submissionError && (
          <span className='text-sm text-red-500'>
            {submissionError.message}
          </span>
        )}

        {/* Submit Button */}
        <button
          type='submit'
          className='w-full rounded-md bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2'
        >
          {isLoading ? 'Submitting' : 'Login'}
        </button>
      </form>

      <p className='mt-4 text-sm text-gray-600'>
        Don't have an account?{' '}
        <NavLink to='/register' className='text-indigo-600 hover:underline'>
          Register
        </NavLink>
      </p>
    </main>
  )
}
/* <!-- Flash messages (success, error) -->
  {% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
      <ul className="alert alert-info">
      {% for category, message in messages %}
          <li>{{ message }}</li>
      {% endfor %}
      </ul>
  {% endif %}
  {% endwith %} */
