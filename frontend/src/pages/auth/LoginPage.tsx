import { useState } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { Formik, Form, Field, ErrorMessage } from 'formik'
import * as Yup from 'yup'
import { useAuth } from '../../context/AuthContext'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

interface LoginFormValues {
  email: string
  password: string
  rememberMe: boolean
}

const LoginSchema = Yup.object().shape({
  email: Yup.string().required('Email or username is required'),
  password: Yup.string().required('Password is required'),
  rememberMe: Yup.boolean(),
})

const LoginPage = () => {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  // Get return URL from query params or default to dashboard
  const searchParams = new URLSearchParams(location.search)
  const returnUrl = searchParams.get('returnUrl') || '/dashboard'

  const initialValues: LoginFormValues = {
    email: '',
    password: '',
    rememberMe: false,
  }

  const handleSubmit = async (values: LoginFormValues) => {
    console.log('LoginPage - Login attempt started for:', values.email)
    console.log('LoginPage - Return URL is:', returnUrl)
    setIsLoading(true)
    setError('')

    try {
      console.log('LoginPage - Calling login function')
      const result = await login(values.email, values.password)
      console.log('LoginPage - Login result:', result)

      if (result.requiresTwoFactor) {
        console.log('LoginPage - 2FA required, navigating to verification page')
        navigate('/verify-2fa')
      } else {
        console.log('LoginPage - Login successful, navigating to:', returnUrl)
        navigate(returnUrl)
      }
    } catch (err: any) {
      console.error('LoginPage - Login error:', err)
      setError(err.response?.data?.message || 'Failed to login. Please check your credentials.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <>
      <Formik
        initialValues={initialValues}
        validationSchema={LoginSchema}
        onSubmit={handleSubmit}
      >
        {({ isSubmitting }) => (
          <Form className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium leading-6 text-gray-900">
                Email or Username
              </label>
              <div className="mt-2">
                <Field
                  id="email"
                  name="email"
                  type="text"
                  autoComplete="email"
                  className="input"
                  disabled={isLoading}
                />
                <ErrorMessage name="email" component="div" className="mt-1 text-sm text-red-600" />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium leading-6 text-gray-900">
                Password
              </label>
              <div className="mt-2">
                <Field
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  className="input"
                  disabled={isLoading}
                />
                <ErrorMessage name="password" component="div" className="mt-1 text-sm text-red-600" />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Field
                  id="rememberMe"
                  name="rememberMe"
                  type="checkbox"
                  className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-600"
                  disabled={isLoading}
                />
                <label htmlFor="rememberMe" className="ml-3 block text-sm leading-6 text-gray-900">
                  Remember me
                </label>
              </div>

              <div className="text-sm leading-6">
                <Link to="/forgot-password" className="font-semibold text-primary-600 hover:text-primary-500">
                  Forgot password?
                </Link>
              </div>
            </div>

            {error && <div className="text-sm text-red-600">{error}</div>}

            <div>
              <button
                type="submit"
                className="btn btn-primary w-full"
                disabled={isLoading || isSubmitting}
              >
                {isLoading ? <LoadingSpinner size="sm" /> : 'Sign in'}
              </button>
            </div>
          </Form>
        )}
      </Formik>

      <p className="mt-10 text-center text-sm text-gray-500">
        Don't have an account?{' '}
        <Link to="/register" className="font-semibold leading-6 text-primary-600 hover:text-primary-500">
          Register here
        </Link>
      </p>
    </>
  )
}

export default LoginPage