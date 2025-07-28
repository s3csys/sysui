import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Formik, Form, Field, ErrorMessage } from 'formik'
import * as Yup from 'yup'
import { QRCodeSVG } from 'qrcode.react'
import { useAuth } from '../../context/AuthContext'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

interface TwoFactorSetupFormValues {
  token: string
  rememberDevice: boolean
}

const TwoFactorSetupSchema = Yup.object().shape({
  token: Yup.string()
    .required('Verification code is required')
    .matches(/^\d{6}$/, 'Verification code must be 6 digits'),
  rememberDevice: Yup.boolean(),
})

const SetupTwoFactorPage = () => {
  const { setupTwoFactor, verifyTwoFactor, user } = useAuth()
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(true)
  const [qrCodeUrl, setQrCodeUrl] = useState('')
  const [secret, setSecret] = useState('')
  const [error, setError] = useState('')
  const [verificationError, setVerificationError] = useState('')

  useEffect(() => {
    // Redirect if user is not authenticated
    if (!user) {
      navigate('/login')
      return
    }

    // Skip setup if 2FA is already enabled
    if (user.isTwoFactorEnabled) {
      navigate('/profile')
      return
    }

    // Generate 2FA setup
    generateTwoFactorSetup()
  }, [user, navigate])

  const generateTwoFactorSetup = async () => {
    try {
      const response = await setupTwoFactor()
      setQrCodeUrl(response.qrCodeUrl)
      setSecret(response.secret)
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to setup two-factor authentication.')
    } finally {
      setIsLoading(false)
    }
  }

  const initialValues: TwoFactorSetupFormValues = {
    token: '',
    rememberDevice: false,
  }

  const handleSubmit = async (values: TwoFactorSetupFormValues) => {
    setVerificationError('')

    try {
      await verifyTwoFactor(values.token, values.rememberDevice)
      navigate('/profile')
    } catch (err: any) {
      setVerificationError(err.response?.data?.message || 'Invalid verification code. Please try again.')
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center">
        <h3 className="text-lg font-medium text-red-600">Setup Failed</h3>
        <p className="mt-2 text-sm text-gray-600">{error}</p>
        <button
          onClick={() => navigate('/profile')}
          className="mt-6 btn btn-primary w-full"
        >
          Return to Profile
        </button>
      </div>
    )
  }

  return (
    <div>
      <h3 className="text-lg font-medium text-gray-900">Set up Two-Factor Authentication</h3>
      <p className="mt-2 text-sm text-gray-600">
        Enhance your account security by setting up two-factor authentication.
      </p>

      <div className="mt-6 space-y-6">
        <div>
          <h4 className="text-sm font-medium text-gray-900">1. Scan QR Code</h4>
          <p className="mt-1 text-xs text-gray-500">
            Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.).
          </p>
          <div className="mt-4 flex justify-center">
            {qrCodeUrl && <QRCodeSVG value={qrCodeUrl} size={200} />}
          </div>
        </div>

        <div>
          <h4 className="text-sm font-medium text-gray-900">2. Manual Setup</h4>
          <p className="mt-1 text-xs text-gray-500">
            If you can't scan the QR code, enter this code manually in your authenticator app:
          </p>
          <div className="mt-2 p-2 bg-gray-100 rounded-md font-mono text-center select-all">
            {secret}
          </div>
        </div>

        <div>
          <h4 className="text-sm font-medium text-gray-900">3. Verify Setup</h4>
          <p className="mt-1 text-xs text-gray-500">
            Enter the 6-digit verification code from your authenticator app to complete the setup.
          </p>
          <div className="mt-4">
            <Formik
              initialValues={initialValues}
              validationSchema={TwoFactorSetupSchema}
              onSubmit={handleSubmit}
            >
              {({ isSubmitting }) => (
                <Form className="space-y-4">
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
                      />
                      <ErrorMessage name="token" component="div" className="mt-1 text-sm text-red-600" />
                    </div>
                  </div>

                  <div className="flex items-center">
                    <Field
                      id="rememberDevice"
                      name="rememberDevice"
                      type="checkbox"
                      className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-600"
                    />
                    <label htmlFor="rememberDevice" className="ml-3 block text-sm leading-6 text-gray-900">
                      Remember this device for 30 days
                    </label>
                  </div>

                  {verificationError && <div className="text-sm text-red-600">{verificationError}</div>}

                  <div className="flex space-x-4">
                    <button
                      type="button"
                      onClick={() => navigate('/profile')}
                      className="btn btn-outline flex-1"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="btn btn-primary flex-1"
                      disabled={isSubmitting}
                    >
                      {isSubmitting ? <LoadingSpinner size="sm" /> : 'Verify & Enable'}
                    </button>
                  </div>
                </Form>
              )}
            </Formik>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SetupTwoFactorPage