import { Link } from 'react-router-dom'

const NotFoundPage = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4 text-center">
      <h1 className="text-6xl font-bold text-primary-600">404</h1>
      <h2 className="mt-4 text-2xl font-semibold">Page Not Found</h2>
      <p className="mt-2 text-gray-600">
        The page you are looking for doesn't exist or has been moved.
      </p>
      <Link 
        to="/"
        className="mt-6 px-4 py-2 text-white bg-primary-600 rounded-md hover:bg-primary-700 transition-colors"
      >
        Go Home
      </Link>
    </div>
  )
}

export default NotFoundPage