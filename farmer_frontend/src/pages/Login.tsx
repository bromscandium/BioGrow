import React, {useState} from 'react';
import Header from "../components/Header";

const Login: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = () => {
        alert(`Email: ${email}\nPassword: ${password}`);
    };

    return (
        <div style={styles.container}>
            <Header/>
            <div style={styles.card}>
                <h1 style={styles.title}>Welcome Back</h1>
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    style={styles.input}
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    style={styles.input}
                />
                <button style={styles.button} onClick={handleLogin}>
                    Log In
                </button>
            </div>
        </div>
    );
};

export default Login;

const styles: { [key: string]: React.CSSProperties } = {
    container: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        backgroundColor: '#F5F5F5',
    },
    card: {
        width: '100%',
        maxWidth: 400,
        backgroundColor: '#fff',
        padding: 24,
        borderRadius: 16,
        boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
        display: 'flex',
        flexDirection: 'column',
        gap: 16,
    },
    title: {
        fontFamily: 'Poppins, sans-serif',
        fontSize: 32,
        color: '#1F3A93',
        textAlign: 'center',
    },
    input: {
        height: 48,
        padding: '0 16px',
        fontSize: 16,
        fontFamily: 'Poppins, sans-serif',
        borderRadius: 12,
        border: '1px solid #E0E0E0',
    },
    button: {
        height: 48,
        backgroundColor: '#00A651',
        color: '#fff',
        fontSize: 18,
        fontFamily: 'Poppins, sans-serif',
        border: 'none',
        borderRadius: 12,
        cursor: 'pointer',
    },
};
