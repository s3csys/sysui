import { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Formik, Form, Field, ErrorMessage } from 'formik'
import * as Yup from 'yup'
import { useAuth } from '../../context/AuthContext'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

interface ResetPasswordFormValues {
  password: string
  confirmPassword: string
}

const ResetPasswordSchema = Yup.object().shape({
  password: Yup.string()
    .min(8, 'Password must be at least 8 characters')
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d\W]{8,}$/,
      'Password must contain at least one uppercase letter, one lowercase letter, and one number'
    )
    .required('Password is required'),
  confirmPassword: Yup.string()
    .oneOf([Yup.ref('password')], 'Passwords must match')
    .required('Confirm password is required'),
})

const ResetPasswordPage = () => {
  const { resetPassword } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [token, setToken] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    // Extract token from URL query parameters
    const searchParams = new URLSearchParams(location.search)
    const tokenParam = searchParams.get('token')
    
    if (!tokenParam) {
      setError('Invalid or missing reset token. Please request a new password reset link.')
    } else {
      setToken(tokenParam)
    }
  }, [location])

  const initialValues: ResetPasswordFormValues = {
    password: '',
    confirmPassword: '',
  }

  const handleSubmit = async (values: ResetPasswordFormValues) => {
    if (!token) {
      setError('Invalid or missing reset token. Please request a new password reset link.')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      await resetPassword(token, values.password)
      setSuccess(true)
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to reset password. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  if (success) {
    return (
      <div className="text-center">
        <h3 className="text-lg font-medium text-gray-900">Password Reset Successful!</h3>
        <p className="mt-2 text-sm text-gray-600">
          Your password has been successfully reset. You can now log in with your new password.
        </p>
        <div className="mt-6">
          <Link to="/login" className="btn btn-primary w-full">
            Go to Login
          </Link>
        </div>
      </div>
    )
  }

  return (
    <>
      <h3 className="text-lg font-medium text-gray-900">Reset your password</h3>
      <p className="mt-2 text-sm text-gray-600">
        Enter your new password below.
      </p>

      {error ? (
        <div className="mt-6">
          <div className="text-sm text-red-600 mb-4">{error}</div>
          <Link to="/forgot-password" className="btn btn-primary w-full">
            Request New Reset Link
          </Link>
        </div>
      ) : (
        <div className="mt-6">
          <Formik
            initialValues={initialValues}
            validationSchema={ResetPasswordSchema}
            onSubmit={handleSubmit}
          >
            {({ isSubmitting }) => (
              <Form className="space-y-6">
                <div>
                  <label htmlFor="password" className="block text-sm font-medium leading-6 text-gray-900">
                    New Password
                  </label>
                  <div className="mt-2">
                    <Field
                      id="password"
                      name="password"
                      type="password"
                      autoComplete="new-password"
                      className="input"
                      disabled={isLoading}
                    />
                    <ErrorMessage name="password" component="div" className="mt-1 text-sm text-red-600" />
                  </div>
                </div>

                <div>
                  <label htmlFor="confirmPassword" className="block text-sm font-medium leading-6 text-gray-900">
                    Confirm New Password
                  </label>
                  <div className="mt-2">
                    <Field
                      id="confirmPassword"
                      name="confirmPassword"
                      type="password"
                      autoComplete="new-password"
                      className="input"
                      disabled={isLoading}
                    />
                    <ErrorMessage name="confirmPassword" component="div" className="mt-1 text-sm text-red-600" />
                  </div>
                </div>

                <div>
                  <button
                    type="submit"
                    className="btn btn-primary w-full"
                    disabled={isLoading || isSubmitting}
                  >
                    {isLoading ? <LoadingSpinner size="sm" /> : 'Reset Password'}
                  </button>
                </div>
              </Form>
            )}
          </Formik>
        </div>
      )}

      <div className="mt-6 text-center text-sm">
        <Link to="/login" className="font-semibold text-primary-600 hover:text-primary-500">
          Back to login
        </Link>
      </div>
    </>
  )
}

export default ResetPasswordPage