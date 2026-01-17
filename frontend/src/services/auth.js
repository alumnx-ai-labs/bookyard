// src/services/auth.js

// Mock authentication service
const DELAY = 800; // Simulate network latency

export const authAPI = {
    login: async (email, password) => {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                // Simple mock validation
                if (email && password.length >= 6) {
                    const user = {
                        id: '1',
                        email: email,
                        name: email.split('@')[0], // Generate name from email
                        token: 'mock-jwt-token-' + Date.now()
                    };
                    localStorage.setItem('user', JSON.stringify(user));
                    resolve(user);
                } else {
                    reject(new Error('Invalid email or password'));
                }
            }, DELAY);
        });
    },

    signup: async (name, email, password) => {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                if (email && password.length >= 6) {
                    const user = {
                        id: '1',
                        email: email,
                        name: name,
                        token: 'mock-jwt-token-' + Date.now()
                    };
                    localStorage.setItem('user', JSON.stringify(user));
                    resolve(user);
                } else {
                    reject(new Error('Failed to create account'));
                }
            }, DELAY);
        });
    },

    logout: () => {
        localStorage.removeItem('user');
        return Promise.resolve();
    },

    getCurrentUser: () => {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    }
};
