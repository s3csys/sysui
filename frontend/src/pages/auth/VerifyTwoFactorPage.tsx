import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Formik, Form, Field, ErrorMessage } from 'formik'
import * as Yup from 'yup'
import { useAuth } from '../../context/AuthContext'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

interface TwoFactorVerifyFormValues {
  token: string
}

const TwoFactorVerifySchema = Yup.object().shape({
  token: Yup.string()
    .required('Verification code is required')
    .matches(/^\d{6}$/, 'Verification code must be 6 digits'),
})

const VerifyTwoFactorPage = () => {
  const { verifyTwoFactorLogin } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const initialValues: TwoFactorVerifyFormValues = {
    token: '',
  }

  const handleSubmit = async (values: TwoFactorVerifyFormValues) => {
    setIsLoading(true)
    setError('')

    try {
      await verifyTwoFactorLogin(values.token)
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.message || 'Invalid verification code. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <>
      <h3 className="text-lg font-medium text-gray-900">Two-Factor Authentication</h3>
      <p className="mt-2 text-sm text-gray-600">
        Enter the 6-digit verification code from your authenticator app.
      </p>

      <div className="mt-6">
        <Formik
          initialValues={initialValues}
          validationSchema={TwoFactorVerifySchema}
          onSubmit={handleSubmit}
        >
          {({ isSubmitting }) => (
            <Form className="space-y-6">
              <div>
                <label htmlFor="token" className="block text-sm font-medium leading-6 text-gray-900">
                  Verification Code
                </label>
                <div className="mt-2">
                  <Field
                    id="token"
                    name="token"
                    type="text"
                    placeholder="000000"
                    className="input text-center tracking-widest font-mono"
                    maxLength={6}
                    disabled={isLoading}
                  />
                  <ErrorMessage name="token" component="div" className="mt-1 text-sm text-red-600" />
                </div>
              </div>

              {error && <div className="text-sm text-red-600">{error}</div>}

              <div>
                <button
                  type="submit"
                  className="btn btn-primary w-full"
                  disabled={isLoading || isSubmitting}
                >
                  {isLoading ? <LoadingSpinner size="sm" /> : 'Verify'}
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

export default VerifyTwoFactorPage