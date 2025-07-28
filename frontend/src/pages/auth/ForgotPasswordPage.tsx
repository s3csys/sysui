import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Formik, Form, Field, ErrorMessage } from 'formik'
import * as Yup from 'yup'
import { useAuth } from '../../context/AuthContext'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

interface ForgotPasswordFormValues {
  email: string
}

const ForgotPasswordSchema = Yup.object().shape({
  email: Yup.string().email('Invalid email').required('Email is required'),
})

const ForgotPasswordPage = () => {
  const { forgotPassword } = useAuth()
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const initialValues: ForgotPasswordFormValues = {
    email: '',
  }

  const handleSubmit = async (values: ForgotPasswordFormValues) => {
    setIsLoading(true)
    setError('')

    try {
      await forgotPassword(values.email)
      setSuccess(true)
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to send reset email. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  if (success) {
    return (
      <div className="text-center">
        <h3 className="text-lg font-medium text-gray-900">Check your email</h3>
        <p className="mt-2 text-sm text-gray-600">
          We've sent a password reset link to your email address. Please check your inbox and follow the
          instructions to reset your password.
        </p>
        <div className="mt-6">
          <Link to="/login" className="btn btn-primary w-full">
            Return to Login
          </Link>
        </div>
      </div>
    )
  }

  return (
    <>
      <h3 className="text-lg font-medium text-gray-900">Forgot your password?</h3>
      <p className="mt-2 text-sm text-gray-600">
        Enter your email address and we'll send you a link to reset your password.
      </p>

      <div className="mt-6">
        <Formik
          initialValues={initialValues}
          validationSchema={ForgotPasswordSchema}
          onSubmit={handleSubmit}
        >
          {({ isSubmitting }) => (
            <Form className="space-y-6">
              <div>
                <label htmlFor="email" className="block text-sm font-medium leading-6 text-gray-900">
                  Email address
                </label>
                <div className="mt-2">
                  <Field
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    className="input"
                    disabled={isLoading}
                  />
                  <ErrorMessage name="email" component="div" className="mt-1 text-sm text-red-600" />
                </div>
              </div>

              {error && <div className="text-sm text-red-600">{error}</div>}

              <div>
                <button
                  type="submit"
                  className="btn btn-primary w-full"
                  disabled={isLoading || isSubmitting}
                >
                  {isLoading ? <LoadingSpinner size="sm" /> : 'Send reset link'}
                </button>
              </div>
            </Form>
          )}
        </Formik>
      </div>

      <div className="mt-6 text-center text-sm">
        <Link to="/login" className="font-semibold text-primary-600 hover:text-primary-500">
          Back to login
        </Link>
      </div>
    </>
  )
}

export default ForgotPasswordPage