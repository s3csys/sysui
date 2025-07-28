import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

const VerifyEmailPage = () => {
  const { verifyEmail } = useAuth()
  const location = useLocation()
  const [token, setToken] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    // Extract token from URL query parameters
    const searchParams = new URLSearchParams(location.search)
    const tokenParam = searchParams.get('token')
    
    if (!tokenParam) {
      setError('Invalid or missing verification token.')
      setIsLoading(false)
      return
    }
    
    setToken(tokenParam)
    verifyEmailToken(tokenParam)
  }, [location])

  const verifyEmailToken = async (token: string) => {
    try {
      await verifyEmail(token)
      setSuccess(true)
    } catch (err: any) {
      setError(err.response?.data?.message || 'Email verification failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="text-center">
        <h3 className="text-lg font-medium text-gray-900">Verifying your email</h3>
        <div className="mt-4 flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center">
        <h3 className="text-lg font-medium text-red-600">Verification Failed</h3>
        <p className="mt-2 text-sm text-gray-600">{error}</p>
        <div className="mt-6">
          <Link to="/login" className="btn btn-primary w-full">
            Return to Login
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="text-center">
      <h3 className="text-lg font-medium text-green-600">Email Verified!</h3>
      <p className="mt-2 text-sm text-gray-600">
        Your email has been successfully verified. You can now log in to your account.
      </p>
      <div className="mt-6">
        <Link to="/login" className="btn btn-primary w-full">
          Go to Login
        </Link>
      </div>
    </div>
  )
}

export default VerifyEmailPage