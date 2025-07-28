import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import { Session } from '../types/user'

const SessionsPage = () => {
  const { user, getSessions, revokeSession, revokeAllOtherSessions } = useAuth()
  const [sessions, setSessions] = useState<Session[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [revokingSessionId, setRevokingSessionId] = useState<string | null>(null)
  const [isRevokingAll, setIsRevokingAll] = useState(false)

  useEffect(() => {
    fetchSessions()
  }, [])

  const fetchSessions = async () => {
    setIsLoading(true)
    setError('')

    try {
      const sessionsData = await getSessions()
      setSessions(sessionsData)
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to fetch sessions')
    } finally {
      setIsLoading(false)
    }
  }

  const handleRevokeSession = async (sessionId: string) => {
    setRevokingSessionId(sessionId)
    setError('')
    setSuccess('')

    try {
      await revokeSession(sessionId)
      setSessions(sessions.filter(session => session.id !== sessionId))
      setSuccess('Session revoked successfully')
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to revoke session')
    } finally {
      setRevokingSessionId(null)
    }
  }

  const handleRevokeAllOtherSessions = async () => {
    setIsRevokingAll(true)
    setError('')
    setSuccess('')

    try {
      await revokeAllOtherSessions()
      // Refresh sessions after revoking all others
      await fetchSessions()
      setSuccess('All other sessions revoked successfully')
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to revoke all other sessions')
    } finally {
      setIsRevokingAll(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }

  const getDeviceIcon = (userAgent: string) => {
    const ua = userAgent.toLowerCase()
    
    if (ua.includes('iphone') || ua.includes('ipad') || ua.includes('ipod')) {
      return '📱 iOS'
    } else if (ua.includes('android')) {
      return '📱 Android'
    } else if (ua.includes('windows')) {
      return '💻 Windows'
    } else if (ua.includes('mac')) {
      return '💻 Mac'
    } else if (ua.includes('linux')) {
      return '💻 Linux'
    } else {
      return '🖥️ Unknown'
    }
  }

  const getBrowserIcon = (userAgent: string) => {
    const ua = userAgent.toLowerCase()
    
    if (ua.includes('chrome') && !ua.includes('edg')) {
      return 'Chrome'
    } else if (ua.includes('firefox')) {
      return 'Firefox'
    } else if (ua.includes('safari') && !ua.includes('chrome')) {
      return 'Safari'
    } else if (ua.includes('edg')) {
      return 'Edge'
    } else if (ua.includes('opera') || ua.includes('opr')) {
      return 'Opera'
    } else {
      return 'Unknown Browser'
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Active Sessions</h1>
          <button
            onClick={handleRevokeAllOtherSessions}
            className="btn btn-outline-danger"
            disabled={isRevokingAll || sessions.length <= 1}
          >
            {isRevokingAll ? <LoadingSpinner size="sm" /> : 'Revoke All Other Sessions'}
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md text-red-600">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-md text-green-600">
            {success}
          </div>
        )}

        <div className="bg-white shadow rounded-lg overflow-hidden">
          {sessions.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              No active sessions found
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Device
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      IP Address
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Last Active
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {sessions.map((session) => (
                    <tr key={session.id} className={session.isCurrent ? 'bg-blue-50' : ''}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {getDeviceIcon(session.userAgent)}
                            </div>
                            <div className="text-sm text-gray-500">
                              {getBrowserIcon(session.userAgent)}
                              {session.isCurrent && (
                                <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                  Current
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{session.ipAddress}</div>
                        <div className="text-xs text-gray-500">{session.location || 'Unknown location'}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatDate(session.lastActiveAt)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatDate(session.createdAt)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => handleRevokeSession(session.id)}
                          className="text-red-600 hover:text-red-900 disabled:opacity-50"
                          disabled={revokingSessionId === session.id || session.isCurrent}
                        >
                          {revokingSessionId === session.id ? (
                            <LoadingSpinner size="sm" />
                          ) : (
                            session.isCurrent ? 'Current Session' : 'Revoke'
                          )}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default SessionsPage