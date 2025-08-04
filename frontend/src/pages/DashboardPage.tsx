import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import LoadingSpinner from '../components/ui/LoadingSpinner'

const DashboardPage = () => {
  const { user } = useAuth()
  const [isLoading, setIsLoading] = useState(true)

  console.log('DashboardPage - Rendering with user:', user)

  // Simulate data loading
  useEffect(() => {
    console.log('DashboardPage - Loading effect started')
    const timer = setTimeout(() => {
      console.log('DashboardPage - Setting isLoading to false')
      setIsLoading(false)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-2">Welcome, {user?.name || 'User'}!</h1>
        <p className="text-gray-600">
          This is your SysUI dashboard. Here you can manage your servers, execute remote commands, and monitor system performance.
        </p>
      </div>

      {/* Quick Stats Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium">Servers</h3>
            <span className="text-primary-600">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </span>
          </div>
          <div className="text-3xl font-bold mb-2">0</div>
          <p className="text-sm text-gray-500">No servers configured yet</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium">Recent Commands</h3>
            <span className="text-primary-600">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </span>
          </div>
          <div className="text-3xl font-bold mb-2">0</div>
          <p className="text-sm text-gray-500">No commands executed yet</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium">Active Sessions</h3>
            <span className="text-primary-600">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </span>
          </div>
          <div className="text-3xl font-bold mb-2">1</div>
          <p className="text-sm text-gray-500">Your current session</p>
        </div>
      </div>

      {/* Getting Started Section */}
      <div className="bg-white rounded-lg shadow overflow-hidden mb-8">
        <div className="px-6 py-4 bg-primary-50 border-b border-primary-100">
          <h2 className="text-xl font-semibold text-primary-800">Getting Started</h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div className="flex items-start">
              <div className="flex-shrink-0 h-6 w-6 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center mr-3">
                <span className="text-sm font-medium">1</span>
              </div>
              <div>
                <h3 className="text-base font-medium">Add your first server</h3>
                <p className="mt-1 text-sm text-gray-600">
                  Configure your first server connection to start managing your infrastructure.
                </p>
                <button className="mt-2 btn btn-sm btn-primary">
                  Add Server
                </button>
              </div>
            </div>

            <div className="flex items-start">
              <div className="flex-shrink-0 h-6 w-6 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center mr-3">
                <span className="text-sm font-medium">2</span>
              </div>
              <div>
                <h3 className="text-base font-medium">Run your first command</h3>
                <p className="mt-1 text-sm text-gray-600">
                  Execute remote commands on your servers securely through the web interface.
                </p>
                <button className="mt-2 btn btn-sm btn-primary" disabled>
                  Run Command
                </button>
              </div>
            </div>

            <div className="flex items-start">
              <div className="flex-shrink-0 h-6 w-6 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center mr-3">
                <span className="text-sm font-medium">3</span>
              </div>
              <div>
                <h3 className="text-base font-medium">Set up monitoring</h3>
                <p className="mt-1 text-sm text-gray-600">
                  Configure monitoring for your servers to track performance and receive alerts.
                </p>
                <button className="mt-2 btn btn-sm btn-primary" disabled>
                  Setup Monitoring
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* System Status Section */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-100">
          <h2 className="text-xl font-semibold text-gray-800">System Status</h2>
        </div>
        <div className="p-6">
          <div className="text-center py-8">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Data Available</h3>
            <p className="text-gray-500 max-w-md mx-auto">
              Add servers to your dashboard to start monitoring system status and performance metrics.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage