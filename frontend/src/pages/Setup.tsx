import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Setup = () => {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState({
        db_host: 'localhost',
        db_port: 3306,
        db_user: 'sysui',
        db_password: 'sysui',
        db_name: 'sysui',
        admin_user: 'admin',
        admin_email: 'admin@admin.com',
        admin_password: 'Admin123!',
    });
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [isInstalling, setIsInstalling] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const nextStep = () => setStep(step + 1);
    const prevStep = () => setStep(step - 1);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setMessage('');
        setIsInstalling(true);
        
        try {
            const response = await fetch('/api/setup', { // Using the correct API endpoint
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });
            
            const result = await response.json();
            
            if (response.ok) {
                setMessage(result.message || 'Installation completed successfully!');
                
                // Wait a moment to show the success message before redirecting
                setTimeout(() => {
                    // Redirect to login page after successful installation
                    window.location.href = '/login';
                }, 3000);
            } else {
                setError(result.detail || 'An error occurred during installation.');
                setIsInstalling(false);
            }
        } catch (err) {
            setError('Failed to connect to the server. Please check your connection and try again.');
            setIsInstalling(false);
        }
    };

    return (
        <div style={{ fontFamily: 'sans-serif', display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: '#f0f2f5' }}>
            <div style={{ background: 'white', padding: '2rem', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', width: '400px' }}>
                <h1 style={{ textAlign: 'center' }}>SysUI Installation</h1>
                <p>Welcome! Please provide the following information to complete the installation.</p>
                <form onSubmit={handleSubmit}>
                    {step === 1 && (
                        <>
                            <h2>Database Configuration</h2>
                            <div style={{ marginBottom: '1rem' }}>
                                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Database Host</label>
                                <input type="text" name="db_host" value={formData.db_host} onChange={handleChange} required style={{ width: '100%', padding: '0.5rem', border: '1px solid #ccc', borderRadius: '4px' }} />
                            </div>
                            <div style={{ marginBottom: '1rem' }}>
                                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Database Port</label>
                                <input type="number" name="db_port" value={formData.db_port} onChange={handleChange} required style={{ width: '100%', padding: '0.5rem', border: '1px solid #ccc', borderRadius: '4px' }} />
                            </div>
                            <div style={{ marginBottom: '1rem' }}>
                                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Database User</label>
                                <input type="text" name="db_user" value={formData.db_user} onChange={handleChange} required style={{ width: '100%', padding: '0.5rem', border: '1px solid #ccc', borderRadius: '4px' }} />
                            </div>
                            <div style={{ marginBottom: '1rem' }}>
                                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Database Password</label>
                                <input type="password" name="db_password" value={formData.db_password} onChange={handleChange} style={{ width: '100%', padding: '0.5rem', border: '1px solid #ccc', borderRadius: '4px' }} />
                            </div>
                            <div style={{ marginBottom: '1rem' }}>
                                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Database Name</label>
                                <input type="text" name="db_name" value={formData.db_name} onChange={handleChange} required style={{ width: '100%', padding: '0.5rem', border: '1px solid #ccc', borderRadius: '4px' }} />
                            </div>
                            <button type="button" onClick={nextStep} style={{ width: '100%', padding: '0.75rem', border: 'none', borderRadius: '4px', backgroundColor: '#007bff', color: 'white', fontSize: '1rem', cursor: 'pointer' }}>Next</button>
                        </>
                    )}
                    {step === 2 && (
                        <>
                            <h2>Admin User</h2>
                            <div style={{ marginBottom: '1rem' }}>
                                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Admin Username</label>
                                <input type="text" name="admin_user" value={formData.admin_user} onChange={handleChange} required style={{ width: '100%', padding: '0.5rem', border: '1px solid #ccc', borderRadius: '4px' }} />
                            </div>
                            <div style={{ marginBottom: '1rem' }}>
                                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Admin Email</label>
                                <input type="email" name="admin_email" value={formData.admin_email} onChange={handleChange} required style={{ width: '100%', padding: '0.5rem', border: '1px solid #ccc', borderRadius: '4px' }} />
                            </div>
                            <div style={{ marginBottom: '1rem' }}>
                                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Admin Password</label>
                                <input type="password" name="admin_password" value={formData.admin_password} onChange={handleChange} required style={{ width: '100%', padding: '0.5rem', border: '1px solid #ccc', borderRadius: '4px' }} />
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <button type="button" onClick={prevStep} style={{ padding: '0.75rem', border: 'none', borderRadius: '4px', backgroundColor: '#6c757d', color: 'white', fontSize: '1rem', cursor: 'pointer' }}>Back</button>
                                <button 
                                    type="submit" 
                                    disabled={isInstalling}
                                    style={{ 
                                        padding: '0.75rem', 
                                        border: 'none', 
                                        borderRadius: '4px', 
                                        backgroundColor: '#007bff', 
                                        color: 'white', 
                                        fontSize: '1rem', 
                                        cursor: isInstalling ? 'not-allowed' : 'pointer',
                                        opacity: isInstalling ? 0.7 : 1
                                    }}
                                >
                                    {isInstalling ? 'Installing...' : 'Install'}
                                </button>
                            </div>
                        </>
                    )}
                </form>
                {message && (
                    <div style={{ color: 'green', marginTop: '1rem', textAlign: 'center' }}>
                        <p>{message}</p>
                        <p style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>Redirecting to login page...</p>
                    </div>
                )}
                {error && <p style={{ color: 'red', marginTop: '1rem' }}>{error}</p>}
            </div>
        </div>
    );
};

export default Setup;