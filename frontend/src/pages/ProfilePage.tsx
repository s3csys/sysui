import { useState } from 'react'
import { Formik, Form, Field, ErrorMessage } from 'formik'
import * as Yup from 'yup'
import { useAuth } from '../context/AuthContext'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import { Link } from 'react-router-dom'

interface ProfileFormValues {
  name: string
  email: string
  currentPassword: string
  newPassword: string
  confirmPassword: string
}

const ProfileSchema = Yup.object().shape({
  name: Yup.string().required('Name is required'),
  email: Yup.string().email('Invalid email').required('Email is required'),
  currentPassword: Yup.string().when('newPassword', {
    is: (val: string) => val && val.length > 0,
    then: (schema) => schema.required('Current password is required to set a new password'),
    otherwise: (schema) => schema,
  }),
  newPassword: Yup.string()
    .min(8, 'Password must be at least 8 characters')
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d\w\W]{8,}$/,
      'Password must contain at least one uppercase letter, one lowercase letter, and one number'
    ),
  confirmPassword: Yup.string().when('newPassword', {
    is: (val: string) => val && val.length > 0,
    then: (schema) =>
      schema
        .required('Please confirm your new password')
        .oneOf([Yup.ref('newPassword')], 'Passwords must match'),
    otherwise: (schema) => schema,
  }),
})

const ProfilePage = () => {
  const { user, updateProfile, updatePassword } = useAuth()
  const [profileSuccess, setProfileSuccess] = useState('')
  const [profileError, setProfileError] = useState('')
  const [passwordSuccess, setPasswordSuccess] = useState('')
  const [passwordError, setPasswordError] = useState('')

  if (!user) {
    return (
      <div className="flex justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  const initialValues: ProfileFormValues = {
    name: user.name || '',
    email: user.email || '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  }

  const handleSubmit = async (values: ProfileFormValues, { resetForm }: any) => {
    // Reset status messages
    setProfileSuccess('')
    setProfileError('')
    setPasswordSuccess('')
    setPasswordError('')

    // Update profile information if changed
    if (values.name !== user.name || values.email !== user.email) {
      try {
        await updateProfile({
          name: values.name,
          email: values.email,
        })
        setProfileSuccess('Profile updated successfully')
      } catch (err: any) {
        setProfileError(err.response?.data?.message || 'Failed to update profile')
      }
    }

    // Update password if provided
    if (values.newPassword) {
      try {
        await updatePassword(values.currentPassword, values.newPassword)
        setPasswordSuccess('Password updated successfully')
        // Reset password fields
        resetForm({
          values: {
            ...values,
            currentPassword: '',
            newPassword: '',
            confirmPassword: '',
          },
        })
      } catch (err: any) {
        setPasswordError(err.response?.data?.message || 'Failed to update password')
      }
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Profile Settings</h1>

        <div className="bg-white shadow rounded-lg overflow-hidden mb-6">
          <div className="p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Account Information</h2>

            <Formik
              initialValues={initialValues}
              validationSchema={ProfileSchema}
              onSubmit={handleSubmit}
              enableReinitialize
            >
              {({ isSubmitting, values }) => (
                <Form className="space-y-6">
                  {/* Profile Information Section */}
                  <div className="space-y-4">
                    <div>
                      <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                        Name
                      </label>
                      <Field
                        id="name"
                        name="name"
                        type="text"
                        className="input"
                      />
                      <ErrorMessage name="name" component="div" className="mt-1 text-sm text-red-600" />
                    </div>

                    <div>
                      <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                        Email
                      </label>
                      <Field
                        id="email"
                        name="email"
                        type="email"
                        className="input"
                      />
                      <ErrorMessage name="email" component="div" className="mt-1 text-sm text-red-600" />
                    </div>

                    {profileSuccess && (
                      <div className="text-sm text-green-600">{profileSuccess}</div>
                    )}
                    {profileError && (
                      <div className="text-sm text-red-600">{profileError}</div>
                    )}
                  </div>

                  {/* Password Change Section */}
                  <div className="pt-6 border-t border-gray-200">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Change Password</h3>
                    <div className="space-y-4">
                      <div>
                        <label htmlFor="currentPassword" className="block text-sm font-medium text-gray-700">
                          Current Password
                        </label>
                        <Field
                          id="currentPassword"
                          name="currentPassword"
                          type="password"
                          className="input"
                        />
                        <ErrorMessage
                          name="currentPassword"
                          component="div"
                          className="mt-1 text-sm text-red-600"
                        />
                      </div>

                      <div>
                        <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700">
                          New Password
                        </label>
                        <Field
                          id="newPassword"
                          name="newPassword"
                          type="password"
                          className="input"
                        />
                        <ErrorMessage
                          name="newPassword"
                          component="div"
                          className="mt-1 text-sm text-red-600"
                        />
                      </div>

                      <div>
                        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                          Confirm New Password
                        </label>
                        <Field
                          id="confirmPassword"
                          name="confirmPassword"
                          type="password"
                          className="input"
                        />
                        <ErrorMessage
                          name="confirmPassword"
                          component="div"
                          className="mt-1 text-sm text-red-600"
                        />
                      </div>

                      {passwordSuccess && (
                        <div className="text-sm text-green-600">{passwordSuccess}</div>
                      )}
                      {passwordError && (
                        <div className="text-sm text-red-600">{passwordError}</div>
                      )}
                    </div>
                  </div>

                  <div className="flex justify-end">
                    <button
                      type="submit"
                      className="btn btn-primary"
                      disabled={isSubmitting}
                    >
                      {isSubmitting ? <LoadingSpinner size="sm" /> : 'Save Changes'}
                    </button>
                  </div>
                </Form>
              )}
            </Formik>
          </div>
        </div>

        {/* Two-Factor Authentication Section */}
        <div className="bg-white shadow rounded-lg overflow-hidden mb-6">
          <div className="p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-2">Two-Factor Authentication</h2>
            <p className="text-sm text-gray-600 mb-4">
              Add an extra layer of security to your account by enabling two-factor authentication.
            </p>

            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">
                  Status: {user.isTwoFactorEnabled ? (
                    <span className="text-green-600">Enabled</span>
                  ) : (
                    <span className="text-red-600">Disabled</span>
                  )}
                </p>
              </div>
              <div>
                {user.isTwoFactorEnabled ? (
                  <button
                    type="button"
                    className="btn btn-outline-danger"
                    // This would typically open a confirmation modal
                    onClick={() => alert('Disable 2FA functionality would be implemented here')}
                  >
                    Disable
                  </button>
                ) : (
                  <Link to="/setup-two-factor" className="btn btn-primary">
                    Enable
                  </Link>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Account Sessions Section */}
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-medium text-gray-900">Active Sessions</h2>
              <Link to="/sessions" className="text-sm font-medium text-primary-600 hover:text-primary-500">
                Manage All Sessions
              </Link>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              View and manage your active sessions across different devices.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProfilePage