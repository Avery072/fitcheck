import React from 'react';
import { Authenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';

const Auth = ({ children }) => {
  return (
    <Authenticator
      signUpAttributes={['email']}
      socialProviders={[]}
    >
      {({ signOut, user }) => (
        <div>
          <header style={styles.header}>
            <h1 style={styles.title}>FitCheck - Virtual Try-On</h1>
            <div style={styles.userInfo}>
              <span style={styles.email}>{user.signInDetails?.loginId}</span>
              <button onClick={signOut} style={styles.signOutButton}>
                Sign Out
              </button>
            </div>
          </header>
          <main style={styles.main}>
            {children}
          </main>
        </div>
      )}
    </Authenticator>
  );
};

const styles = {
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px 40px',
    backgroundColor: '#1a1a1a',
    color: 'white',
    borderBottom: '3px solid #4CAF50'
  },
  title: {
    margin: 0,
    fontSize: '24px',
    fontWeight: 'bold'
  },
  userInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px'
  },
  email: {
    fontSize: '14px',
    color: '#ccc'
  },
  signOutButton: {
    padding: '8px 16px',
    backgroundColor: '#f44336',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500'
  },
  main: {
    padding: '20px',
    maxWidth: '1200px',
    margin: '0 auto'
  }
};

export default Auth;
