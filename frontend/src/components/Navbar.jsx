// src/components/Navbar.jsx
import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { BookOpen, LogOut, User, LayoutDashboard, Library } from 'lucide-react';

const Navbar = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };

    const isActive = (path) => location.pathname === path;

    return (
        <nav className="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16 items-center">
                    {/* Logo */}
                    <Link to="/dashboard" className="flex items-center gap-3 group">
                        <div className="bg-gradient-to-br from-blue-600 to-indigo-600 p-2 rounded-xl text-white shadow-md group-hover:shadow-lg transition-all duration-300">
                            <BookOpen className="w-5 h-5" />
                        </div>
                        <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-700 to-indigo-700">
                            Bookyard
                        </span>
                    </Link>

                    {/* Navigation Links */}
                    <div className="hidden md:flex items-center space-x-1">
                        <Link
                            to="/dashboard"
                            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${isActive('/dashboard')
                                    ? 'bg-blue-50 text-blue-700'
                                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                }`}
                        >
                            <LayoutDashboard className="w-4 h-4" />
                            Dashboard
                        </Link>
                        <Link
                            to="/books"
                            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${isActive('/books')
                                    ? 'bg-blue-50 text-blue-700'
                                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                }`}
                        >
                            <Library className="w-4 h-4" />
                            Library
                        </Link>
                    </div>

                    {/* User & Profile */}
                    <div className="flex items-center gap-4">
                        <Link
                            to="/profile"
                            className={`flex items-center gap-3 px-3 py-1.5 rounded-full border transition-all ${isActive('/profile')
                                    ? 'bg-blue-50 border-blue-200 ring-2 ring-blue-100'
                                    : 'bg-white border-gray-200 hover:border-blue-300 hover:shadow-sm'
                                }`}
                        >
                            {user?.photoUrl ? (
                                <img
                                    src={user.photoUrl}
                                    alt={user.name}
                                    className="w-8 h-8 rounded-full object-cover border border-gray-200"
                                />
                            ) : (
                                <div className="w-8 h-8 bg-gradient-to-br from-blue-100 to-indigo-100 text-blue-600 rounded-full flex items-center justify-center">
                                    <User className="w-4 h-4" />
                                </div>
                            )}
                            <span className="text-sm font-semibold text-gray-700 hidden sm:block">
                                {user?.name?.split(' ')[0]}
                            </span>
                        </Link>

                        <button
                            onClick={handleLogout}
                            className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                            title="Sign Out"
                        >
                            <LogOut className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
