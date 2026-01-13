// src/pages/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { booksAPI } from '../services/api';
import { Link } from 'react-router-dom';
import { BookOpen, Plus, BarChart2, Book, Settings, Layers, Clock, ArrowRight, User } from 'lucide-react';

const Dashboard = () => {
    const { user } = useAuth();
    const [stats, setStats] = useState({
        totalBooks: 0,
        myBooks: 0,
        totalPages: 0,
        recentBooks: []
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDashboardData();
    }, [user]);

    const fetchDashboardData = async () => {
        try {
            // Fetch a large batch to calculate stats client-side
            // In a real app, the backend should provide a /stats endpoint
            const allBooks = await booksAPI.list(0, 1000);

            const totalBooks = allBooks.length;
            const myBooks = allBooks.filter(b => b.ownerEmail === user?.email).length;
            const totalPages = allBooks.reduce((acc, book) => acc + (parseInt(book.pages) || 0), 0);

            // Sort by ID descending (assuming higher ID = newer) or created_at if available
            // Since our API currently returns list in insertion order generally, we reverse for recent
            const recentBooks = [...allBooks].reverse().slice(0, 4);

            setStats({
                totalBooks,
                myBooks,
                totalPages,
                recentBooks
            });
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        } finally {
            setLoading(false);
        }
    };

    const StatCard = ({ icon: Icon, colorClass, bgClass, label, value, subLabel }) => (
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center gap-4 hover:shadow-md transition-shadow group">
            <div className={`${bgClass} p-4 rounded-xl ${colorClass} group-hover:scale-110 transition-transform duration-300`}>
                <Icon className="w-6 h-6" />
            </div>
            <div>
                <p className="text-gray-500 text-sm font-medium">{label}</p>
                <h3 className="text-2xl font-bold text-gray-900">{loading ? '-' : value}</h3>
                {subLabel && <p className="text-xs text-slate-400 mt-0.5">{subLabel}</p>}
            </div>
        </div>
    );

    return (
        <div>
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                <p className="text-gray-500 mt-1">Welcome back, <span className="font-semibold text-gray-700">{user?.name}</span>. Here's your library overview.</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                <StatCard
                    icon={Book}
                    colorClass="text-blue-600"
                    bgClass="bg-blue-50"
                    label="Total Books"
                    value={stats.totalBooks}
                    subLabel="In the entire library"
                />
                <StatCard
                    icon={User}
                    colorClass="text-purple-600"
                    bgClass="bg-purple-50"
                    label="My Contributions"
                    value={stats.myBooks}
                    subLabel="Books added by you"
                />
                <StatCard
                    icon={Layers}
                    colorClass="text-emerald-600"
                    bgClass="bg-emerald-50"
                    label="Total Pages"
                    value={stats.totalPages.toLocaleString()}
                    subLabel="Knowledge accumulated"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Recent Activity */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="flex items-center justify-between">
                        <h2 className="text-lg font-bold text-gray-800 flex items-center gap-2">
                            <Clock className="w-5 h-5 text-gray-400" />
                            Recently Added
                        </h2>
                        <Link to="/books" className="text-sm font-semibold text-blue-600 hover:text-blue-700 hover:underline">
                            View All
                        </Link>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {loading ? (
                            [1, 2].map((i) => (
                                <div key={i} className="h-24 bg-gray-100 rounded-2xl animate-pulse"></div>
                            ))
                        ) : stats.recentBooks.length > 0 ? (
                            stats.recentBooks.map((book) => (
                                <div key={book.id} className="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-all flex gap-4 items-start group">
                                    <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold text-lg shadow-sm shrink-0">
                                        {book.title.charAt(0).toUpperCase()}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <h4 className="font-bold text-gray-900 truncate group-hover:text-blue-600 transition-colors" title={book.title}>{book.title}</h4>
                                        <p className="text-sm text-gray-500 truncate">{book.author}</p>
                                        <div className="flex items-center gap-2 mt-2">
                                            <span className="text-[10px] bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded font-medium border border-gray-200">
                                                {book.published_year || 'N/A'}
                                            </span>
                                            <span className="text-[10px] text-gray-400">
                                                Added by {book.addedBy === user?.name ? 'You' : book.addedBy}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="col-span-2 bg-gray-50 rounded-2xl p-8 text-center border border-dashed border-gray-200">
                                <p className="text-gray-500">No books found. Start adding some!</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Quick Actions */}
                <div>
                    <h2 className="text-lg font-bold text-gray-800 mb-6 flex items-center gap-2">
                        <Settings className="w-5 h-5 text-gray-400" />
                        Quick Actions
                    </h2>
                    <div className="space-y-4">
                        <Link
                            to="/books/create"
                            className="group block bg-white border border-gray-200 rounded-2xl p-5 hover:border-blue-300 hover:shadow-lg hover:-translate-y-1 transition-all"
                        >
                            <div className="flex items-center gap-4">
                                <div className="bg-blue-50 w-10 h-10 rounded-xl flex items-center justify-center text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-all">
                                    <Plus className="w-5 h-5" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-gray-900">Add New Book</h3>
                                    <p className="text-xs text-gray-500 mt-0.5">Expand the library</p>
                                </div>
                                <ArrowRight className="w-5 h-5 text-gray-300 ml-auto group-hover:text-blue-500 group-hover:translate-x-1 transition-all" />
                            </div>
                        </Link>

                        <Link
                            to="/books"
                            className="group block bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl p-5 text-white shadow-lg shadow-blue-200 hover:shadow-xl hover:-translate-y-1 transition-all"
                        >
                            <div className="flex items-center gap-4">
                                <div className="bg-white/20 w-10 h-10 rounded-xl flex items-center justify-center text-white">
                                    <BookOpen className="w-5 h-5" />
                                </div>
                                <div>
                                    <h3 className="font-bold">Manage Library</h3>
                                    <p className="text-xs text-blue-100 mt-0.5">Search and edit books</p>
                                </div>
                                <ArrowRight className="w-5 h-5 text-blue-200 ml-auto group-hover:text-white group-hover:translate-x-1 transition-all" />
                            </div>
                        </Link>
                    </div>

                    {/* System Status Mockup */}
                    <div className="mt-8 bg-slate-900 rounded-2xl p-6 text-white relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-32 bg-blue-500 rounded-full blur-3xl opacity-20 -mr-16 -mt-16"></div>
                        <div className="relative">
                            <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">System Status</p>
                            <div className="flex items-center gap-3 mb-1">
                                <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
                                <span className="font-bold text-lg">All Systems Operational</span>
                            </div>
                            <p className="text-slate-400 text-xs">Last checked: Just now</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
