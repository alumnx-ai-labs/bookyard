// src/pages/Login.jsx
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import { BookOpen, Mail, Lock, ArrowRight, Loader2, Eye, EyeOff, Sparkles } from 'lucide-react';
import ThemeToggle from '../components/ThemeToggle';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [touched, setTouched] = useState({ email: false, password: false });
    const { login } = useAuth();
    const navigate = useNavigate();

    // Validation
    const emailError = touched.email && !email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/) ? 'Please enter a valid email address' : '';
    const passwordError = touched.password && password.length < 1 ? 'Password is required' : '';

    const handleSubmit = async (e) => {
        e.preventDefault();
        setTouched({ email: true, password: true });

        if (!email || !password) {
            setError('Please fill in all fields');
            return;
        }

        setError('');
        setLoading(true);
        try {
            await login(email, password);
            navigate('/dashboard');
        } catch (err) {
            setError('Invalid email or password');
        } finally {
            setLoading(false);
        }
    };

    const handleBlur = (field) => {
        setTouched(prev => ({ ...prev, [field]: true }));
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 flex">
            {/* Theme Toggle - Fixed Position */}
            <div className="absolute top-4 right-4 z-10">
                <ThemeToggle />
            </div>

            {/* Left Panel - Branding (Hidden on mobile) */}
            <div className="hidden lg:flex lg:w-1/2 xl:w-[55%] relative overflow-hidden">
                {/* Gradient Background */}
                <div className="absolute inset-0 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 dark:from-blue-700 dark:via-indigo-800 dark:to-purple-900" />

                {/* Decorative Elements */}
                <div className="absolute top-20 left-20 w-72 h-72 bg-white/10 rounded-full blur-3xl" />
                <div className="absolute bottom-20 right-20 w-96 h-96 bg-purple-400/20 rounded-full blur-3xl" />
                <div className="absolute top-1/2 left-1/3 w-48 h-48 bg-blue-300/10 rounded-full blur-2xl" />

                {/* Floating Books Animation */}
                <div className="absolute top-1/4 right-1/4 opacity-20">
                    <div className="w-16 h-20 bg-white/30 rounded-lg transform rotate-12 animate-pulse" />
                </div>
                <div className="absolute bottom-1/3 left-1/4 opacity-15">
                    <div className="w-12 h-16 bg-white/30 rounded-lg transform -rotate-6 animate-pulse" style={{ animationDelay: '1s' }} />
                </div>

                {/* Content */}
                <div className="relative z-10 flex flex-col justify-center px-12 xl:px-20 text-white">
                    {/* Logo */}
                    <div className="flex items-center gap-4 mb-8">
                        <div className="bg-white/20 backdrop-blur-sm p-4 rounded-2xl shadow-2xl">
                            <BookOpen className="w-10 h-10 text-white" />
                        </div>
                        <span className="text-4xl font-bold tracking-tight">Bookyard</span>
                    </div>

                    {/* Tagline */}
                    <h1 className="text-4xl xl:text-5xl font-bold leading-tight mb-6">
                        Your Digital
                        <br />
                        <span className="text-blue-200">Library Hub</span>
                    </h1>

                    <p className="text-lg text-blue-100/80 max-w-md leading-relaxed mb-8">
                        Organize, discover, and share your book collection with a beautiful,
                        intuitive library management system.
                    </p>

                    {/* Features */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-3 text-blue-100">
                            <div className="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center">
                                <Sparkles className="w-4 h-4" />
                            </div>
                            <span>Smart book organization</span>
                        </div>
                        <div className="flex items-center gap-3 text-blue-100">
                            <div className="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center">
                                <Sparkles className="w-4 h-4" />
                            </div>
                            <span>Collaborative library sharing</span>
                        </div>
                        <div className="flex items-center gap-3 text-blue-100">
                            <div className="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center">
                                <Sparkles className="w-4 h-4" />
                            </div>
                            <span>Beautiful reading insights</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Panel - Login Form */}
            <div className="w-full lg:w-1/2 xl:w-[45%] flex items-center justify-center p-6 sm:p-8 lg:p-12">
                <div className="w-full max-w-md">
                    {/* Mobile Logo */}
                    <div className="flex justify-center mb-8 lg:hidden">
                        <div className="flex items-center gap-3">
                            <div className="bg-gradient-to-br from-blue-600 to-indigo-600 p-3 rounded-xl shadow-lg shadow-blue-200 dark:shadow-blue-900/30">
                                <BookOpen className="w-7 h-7 text-white" />
                            </div>
                            <span className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
                                Bookyard
                            </span>
                        </div>
                    </div>

                    {/* Form Card */}
                    <div className="bg-white dark:bg-slate-800 rounded-3xl shadow-xl shadow-gray-200/50 dark:shadow-black/20 p-8 sm:p-10 border border-gray-100 dark:border-slate-700">
                        <div className="text-center mb-8">
                            <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-2">
                                Welcome Back
                            </h2>
                            <p className="text-gray-500 dark:text-slate-400">
                                Sign in to continue to your library
                            </p>
                        </div>

                        {/* Error Alert */}
                        {error && (
                            <div className="bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-800 text-red-600 dark:text-red-400 px-4 py-3 rounded-xl mb-6 text-sm flex items-center gap-2 animate-shake">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 shrink-0" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                </svg>
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-5">
                            {/* Email Field */}
                            <div className="relative">
                                <div className="relative group">
                                    <Mail className={`absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 transition-colors
                                        ${emailError ? 'text-red-400' : 'text-gray-400 group-focus-within:text-blue-500'}`}
                                    />
                                    <input
                                        type="email"
                                        id="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        onBlur={() => handleBlur('email')}
                                        className={`peer w-full pl-12 pr-4 pt-6 pb-2 bg-gray-50 dark:bg-slate-700/50 border-2 rounded-xl 
                                            transition-all duration-200 outline-none text-gray-900 dark:text-white
                                            placeholder-transparent
                                            ${emailError
                                                ? 'border-red-300 dark:border-red-500 focus:border-red-500 focus:ring-4 focus:ring-red-100 dark:focus:ring-red-900/30'
                                                : 'border-gray-200 dark:border-slate-600 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:focus:ring-blue-900/30'
                                            }
                                            hover:border-gray-300 dark:hover:border-slate-500`}
                                        placeholder="Email"
                                    />
                                    <label
                                        htmlFor="email"
                                        className={`absolute left-12 transition-all duration-200 pointer-events-none
                                            peer-placeholder-shown:top-1/2 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:text-base
                                            peer-focus:top-2 peer-focus:translate-y-0 peer-focus:text-xs
                                            top-2 translate-y-0 text-xs
                                            ${email ? 'top-2 translate-y-0 text-xs' : ''}
                                            ${emailError ? 'text-red-500' : 'text-gray-500 dark:text-slate-400 peer-focus:text-blue-500'}`}
                                    >
                                        Email Address
                                    </label>
                                </div>
                                {emailError && (
                                    <p className="mt-1.5 text-xs text-red-500 dark:text-red-400 flex items-center gap-1 ml-1">
                                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                        </svg>
                                        {emailError}
                                    </p>
                                )}
                            </div>

                            {/* Password Field */}
                            <div className="relative">
                                <div className="relative group">
                                    <Lock className={`absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 transition-colors
                                        ${passwordError ? 'text-red-400' : 'text-gray-400 group-focus-within:text-blue-500'}`}
                                    />
                                    <input
                                        type={showPassword ? 'text' : 'password'}
                                        id="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        onBlur={() => handleBlur('password')}
                                        className={`peer w-full pl-12 pr-12 pt-6 pb-2 bg-gray-50 dark:bg-slate-700/50 border-2 rounded-xl 
                                            transition-all duration-200 outline-none text-gray-900 dark:text-white
                                            placeholder-transparent
                                            ${passwordError
                                                ? 'border-red-300 dark:border-red-500 focus:border-red-500 focus:ring-4 focus:ring-red-100 dark:focus:ring-red-900/30'
                                                : 'border-gray-200 dark:border-slate-600 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:focus:ring-blue-900/30'
                                            }
                                            hover:border-gray-300 dark:hover:border-slate-500`}
                                        placeholder="Password"
                                    />
                                    <label
                                        htmlFor="password"
                                        className={`absolute left-12 transition-all duration-200 pointer-events-none
                                            peer-placeholder-shown:top-1/2 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:text-base
                                            peer-focus:top-2 peer-focus:translate-y-0 peer-focus:text-xs
                                            top-2 translate-y-0 text-xs
                                            ${password ? 'top-2 translate-y-0 text-xs' : ''}
                                            ${passwordError ? 'text-red-500' : 'text-gray-500 dark:text-slate-400 peer-focus:text-blue-500'}`}
                                    >
                                        Password
                                    </label>
                                    <button
                                        type="button"
                                        onClick={() => setShowPassword(!showPassword)}
                                        className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-slate-300 transition-colors p-1"
                                        tabIndex={-1}
                                    >
                                        {showPassword ? (
                                            <EyeOff className="w-5 h-5" />
                                        ) : (
                                            <Eye className="w-5 h-5" />
                                        )}
                                    </button>
                                </div>
                                {passwordError && (
                                    <p className="mt-1.5 text-xs text-red-500 dark:text-red-400 flex items-center gap-1 ml-1">
                                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                        </svg>
                                        {passwordError}
                                    </p>
                                )}
                            </div>

                            {/* Submit Button */}
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 
                                    text-white py-4 rounded-xl font-semibold 
                                    transition-all duration-300
                                    hover:shadow-xl hover:shadow-blue-500/25 hover:-translate-y-0.5
                                    active:translate-y-0 active:shadow-lg
                                    disabled:opacity-70 disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:hover:shadow-none
                                    flex items-center justify-center gap-2 group"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        <span>Signing in...</span>
                                    </>
                                ) : (
                                    <>
                                        <span>Sign In</span>
                                        <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                                    </>
                                )}
                            </button>
                        </form>

                        {/* Signup Link */}
                        <div className="mt-8 text-center">
                            <p className="text-gray-500 dark:text-slate-400">
                                Don't have an account?{' '}
                                <Link
                                    to="/signup"
                                    className="text-blue-600 dark:text-blue-400 font-semibold hover:text-blue-700 dark:hover:text-blue-300 hover:underline transition-colors"
                                >
                                    Create one now
                                </Link>
                            </p>
                        </div>
                    </div>

                    {/* Footer */}
                    <p className="text-center text-sm text-gray-400 dark:text-slate-500 mt-8">
                        © 2026 Bookyard. All rights reserved.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Login;
