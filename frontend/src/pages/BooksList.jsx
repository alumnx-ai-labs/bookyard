// src/pages/BooksList.jsx
import React, { useState, useEffect } from 'react';
import { booksAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Search, Plus, Edit, Trash2, Eye, X, Book, Calendar, Layers, Hash, User } from 'lucide-react';
import { Link } from 'react-router-dom';

const BooksList = () => {
  const { user } = useAuth();
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [skip, setSkip] = useState(0);
  const [limit] = useState(12);
  const [selectedBook, setSelectedBook] = useState(null);

  useEffect(() => {
    fetchBooks();
  }, [skip]);

  const fetchBooks = async () => {
    setLoading(true);
    try {
      const data = await booksAPI.list(skip, limit);
      setBooks(data);
    } catch (error) {
      console.error('Failed to fetch books:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await booksAPI.search(searchQuery);
      setBooks(data);
      setSkip(0);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    setSkip(0);
    fetchBooks();
  };

  const handleDelete = async (bookId) => {
    if (!window.confirm('Are you sure you want to delete this book?')) {
      return;
    }

    try {
      await booksAPI.delete(bookId);
      fetchBooks();
      if (selectedBook?.id === bookId) setSelectedBook(null);
    } catch (error) {
      console.error('Delete failed:', error);
      alert(error.message || 'Failed to delete book.');
    }
  };

  const handlePrevPage = () => {
    if (skip > 0) setSkip(Math.max(0, skip - limit));
  };

  const handleNextPage = () => {
    if (books.length === limit) setSkip(skip + limit);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const canManageBook = (book) => {
    return book.ownerEmail && book.ownerEmail === user?.email;
  };

  return (
    <div className="font-sans">

      {/* Header & Add Button */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Library</h1>
          <p className="text-gray-500 dark:text-slate-400 text-sm mt-1">Manage and explore your collection</p>
        </div>
        <Link
          to="/books/create"
          className="group flex items-center gap-2 bg-blue-600 text-white px-5 py-2.5 rounded-xl hover:bg-blue-700 active:bg-blue-800 transition-all duration-300 shadow-md hover:shadow-xl hover:-translate-y-0.5"
        >
          <Plus className="w-4 h-4 transition-transform group-hover:rotate-90" />
          <span className="font-medium text-sm">Add Book</span>
        </Link>
      </div>

      {/* Search Section */}
      <div className="mb-10 max-w-2xl mx-auto">
        <div className="relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-blue-100 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000"></div>
          <div className="relative bg-white dark:bg-slate-800 rounded-2xl shadow-xl shadow-gray-100 dark:shadow-slate-900/30 p-2 flex items-center border border-gray-100 dark:border-slate-700">
            <Search className="w-5 h-5 text-gray-400 dark:text-slate-500 ml-3" />
            <form onSubmit={handleSearch} className="flex-1 flex items-center">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by title, author, or ISBN..."
                className="w-full px-4 py-3 bg-transparent border-none focus:ring-0 text-gray-700 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 text-base outline-none"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={handleClearSearch}
                  className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-full transition-colors mr-2"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
              <button
                type="submit"
                disabled={loading}
                className="bg-gray-900 dark:bg-slate-600 text-white px-6 py-2.5 rounded-xl hover:bg-black dark:hover:bg-slate-500 transition-colors font-medium text-sm disabled:opacity-70"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </form>
          </div>
        </div>
      </div>

      {/* Content Area */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-20">
          <div className="relative">
            <div className="w-12 h-12 border-4 border-blue-100 dark:border-blue-900 border-t-blue-600 dark:border-t-blue-400 rounded-full animate-spin"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-2 h-2 bg-blue-600 dark:bg-blue-400 rounded-full"></div>
            </div>
          </div>
          <p className="mt-4 text-gray-500 dark:text-slate-400 font-medium animate-pulse">Fetching your library...</p>
        </div>
      ) : books.length === 0 ? (
        <div className="bg-white dark:bg-slate-800 rounded-3xl shadow-sm dark:shadow-slate-900/20 border border-gray-100 dark:border-slate-700 p-12 text-center max-w-lg mx-auto">
          <div className="bg-blue-50 dark:bg-blue-900/30 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
            <Book className="w-10 h-10 text-blue-500 dark:text-blue-400" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">No books found</h3>
          <p className="text-gray-500 dark:text-slate-400 mb-8 leading-relaxed">
            {searchQuery
              ? `We couldn't find any books matching "${searchQuery}". Try a different keyword.`
              : "Your library is empty. Add your first book to get started!"}
          </p>
          {searchQuery ? (
            <button
              onClick={handleClearSearch}
              className="text-blue-600 dark:text-blue-400 font-medium hover:text-blue-800 dark:hover:text-blue-300 transition-colors"
            >
              Clear Filters
            </button>
          ) : (
            <Link
              to="/books/create"
              className="inline-flex items-center gap-2 bg-blue-600 text-white px-8 py-3 rounded-xl hover:bg-blue-700 transition-all shadow-lg shadow-blue-200 dark:shadow-blue-900/30"
            >
              <Plus className="w-5 h-5" />
              Add Book
            </Link>
          )}
        </div>
      ) : (
        <div>
          <div className="flex items-center justify-between mb-6 px-2">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white flex items-center gap-2">
              All Books
              <span className="bg-gray-100 dark:bg-slate-700 text-gray-600 dark:text-slate-300 py-0.5 px-2.5 rounded-full text-xs font-bold border border-gray-200 dark:border-slate-600">
                {books.length}
              </span>
            </h2>
            <div className="text-sm text-gray-500 dark:text-slate-400">
              Page {Math.floor(skip / limit) + 1}
            </div>
          </div>

          {/* Grid Layout */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {books.map((book) => (
              <div
                key={book.id}
                className="group bg-white dark:bg-slate-800 rounded-2xl border border-gray-100 dark:border-slate-700 shadow-sm hover:shadow-xl dark:hover:shadow-slate-900/40 hover:-translate-y-1 transition-all duration-300 flex flex-col overflow-hidden"
              >
                <div className="p-6 flex-1 flex flex-col">
                  <div className="flex justify-between items-start mb-4">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold text-lg shadow-md shrink-0">
                      {book.title.charAt(0).toUpperCase()}
                    </div>
                    {/* Action Buttons - Only authorized */}
                    {canManageBook(book) && (
                      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                        <Link
                          to={`/books/edit/${book.id}`}
                          className="p-1.5 text-gray-400 dark:text-slate-500 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
                          title="Edit"
                        >
                          <Edit className="w-4 h-4" />
                        </Link>
                        <button
                          onClick={(e) => { e.stopPropagation(); handleDelete(book.id); }}
                          className="p-1.5 text-gray-400 dark:text-slate-500 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                  </div>

                  <h3 className="font-bold text-gray-900 dark:text-white text-lg leading-tight mb-1 line-clamp-2" title={book.title}>
                    {book.title}
                  </h3>
                  <p className="text-gray-500 dark:text-slate-400 text-sm font-medium mb-4">{book.author}</p>

                  <div className="mt-auto space-y-2">
                    <div className="flex items-center text-xs text-gray-500 dark:text-slate-400 bg-gray-50 dark:bg-slate-700/50 p-2 rounded-lg">
                      <User className="w-3.5 h-3.5 mr-2 text-gray-400 dark:text-slate-500" />
                      <span className="font-medium text-gray-600 dark:text-slate-300">{book.addedBy}</span>
                    </div>
                    <div className="flex items-center text-xs text-gray-500 dark:text-slate-400 bg-gray-50 dark:bg-slate-700/50 p-2 rounded-lg">
                      <Hash className="w-3.5 h-3.5 mr-2 text-gray-400 dark:text-slate-500" />
                      <span className="font-mono truncate">{book.isbn || 'No ISBN'}</span>
                    </div>
                    <div className="flex items-center justify-between text-xs text-gray-500 dark:text-slate-400 px-1">
                      <span className="flex items-center">
                        <Calendar className="w-3.5 h-3.5 mr-1.5 text-gray-400 dark:text-slate-500" />
                        {book.published_year || 'N/A'}
                      </span>
                      <span className="flex items-center">
                        <Layers className="w-3.5 h-3.5 mr-1.5 text-gray-400 dark:text-slate-500" />
                        {book.pages || '-'} pgs
                      </span>
                    </div>
                  </div>
                </div>

                <div onClick={() => setSelectedBook(book)} className="bg-gray-50 dark:bg-slate-700/50 px-6 py-3 border-t border-gray-100 dark:border-slate-700 flex items-center justify-between cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors">
                  <span className="text-xs font-semibold text-blue-600 dark:text-blue-400 uppercase tracking-wider">View Details</span>
                  <Eye className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          <div className="mt-12 flex justify-center gap-4">
            <button
              onClick={handlePrevPage}
              disabled={skip === 0}
              className="px-5 py-2.5 rounded-xl border border-gray-200 dark:border-slate-600 text-gray-600 dark:text-slate-300 font-medium hover:bg-white dark:hover:bg-slate-800 hover:border-gray-300 dark:hover:border-slate-500 hover:shadow-sm disabled:opacity-50 disabled:hover:shadow-none transition-all"
            >
              Previous
            </button>
            <button
              onClick={handleNextPage}
              disabled={books.length < limit}
              className="px-5 py-2.5 rounded-xl bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-600 text-gray-800 dark:text-slate-200 font-medium hover:border-gray-300 dark:hover:border-slate-500 hover:shadow-sm disabled:opacity-50 disabled:hover:shadow-none transition-all"
            >
              Next Page
            </button>
          </div>
        </div>
      )}

      {/* Book Details Modal */}
      {selectedBook && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="absolute inset-0 bg-gray-900/60 dark:bg-black/70 backdrop-blur-sm transition-opacity"
            onClick={() => setSelectedBook(null)}
          ></div>
          <div className="relative bg-white dark:bg-slate-800 rounded-3xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto transform transition-all scale-100">
            <div className="p-8">
              <div className="flex justify-between items-start mb-8">
                <div>
                  <div className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 mb-3 border border-blue-100 dark:border-blue-800">
                    ID #{selectedBook.id}
                  </div>
                  <h2 className="text-3xl font-bold text-gray-900 dark:text-white leading-tight">{selectedBook.title}</h2>
                  <p className="text-lg text-gray-500 dark:text-slate-400 mt-1 font-medium">{selectedBook.author}</p>
                </div>
                <button
                  onClick={() => setSelectedBook(null)}
                  className="p-2 bg-gray-100 dark:bg-slate-700 hover:bg-gray-200 dark:hover:bg-slate-600 rounded-full transition-colors"
                >
                  <X className="w-5 h-5 text-gray-500 dark:text-slate-400" />
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
                <div className="md:col-span-2 space-y-6">
                  <div>
                    <h4 className="text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wide mb-2">Description</h4>
                    <p className="text-gray-600 dark:text-slate-400 leading-relaxed text-sm">
                      {selectedBook.description || "No description available for this book."}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-50 dark:bg-slate-700/50 p-4 rounded-xl border border-gray-100 dark:border-slate-600">
                      <p className="text-xs text-gray-500 dark:text-slate-500 mb-1">Published Year</p>
                      <p className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-blue-500 dark:text-blue-400" />
                        {selectedBook.published_year || 'N/A'}
                      </p>
                    </div>
                    <div className="bg-gray-50 dark:bg-slate-700/50 p-4 rounded-xl border border-gray-100 dark:border-slate-600">
                      <p className="text-xs text-gray-500 dark:text-slate-500 mb-1">Pages</p>
                      <p className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                        <Layers className="w-4 h-4 text-blue-500 dark:text-blue-400" />
                        {selectedBook.pages || 'N/A'}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="md:col-span-1 space-y-4">
                  <div className="bg-slate-50 dark:bg-slate-700/50 p-5 rounded-2xl border border-slate-100 dark:border-slate-600">
                    <div className="mb-4">
                      <p className="text-xs text-gray-500 dark:text-slate-500 mb-1">Added By</p>
                      <p className="font-medium text-slate-700 dark:text-slate-200 flex items-center gap-2">
                        <User className="w-4 h-4 text-blue-500 dark:text-blue-400" />
                        {selectedBook.addedBy}
                      </p>
                    </div>
                    <div className="mb-4">
                      <p className="text-xs text-gray-500 dark:text-slate-500 mb-1">ISBN</p>
                      <p className="font-mono text-sm font-medium text-slate-700 dark:text-slate-200 break-all">
                        {selectedBook.isbn || 'N/A'}
                      </p>
                    </div>
                    <div className="border-t border-slate-200 dark:border-slate-600 my-3"></div>
                    <div className="space-y-3">
                      <div>
                        <p className="text-xs text-gray-400 dark:text-slate-500">Added</p>
                        <p className="text-xs font-medium text-slate-600 dark:text-slate-300">{formatDate(selectedBook.created_at)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-400 dark:text-slate-500">Updated</p>
                        <p className="text-xs font-medium text-slate-600 dark:text-slate-300">{formatDate(selectedBook.updated_at)}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Only show buttons if authorized */}
              {canManageBook(selectedBook) && (
                <div className="flex gap-4 pt-4 border-t border-gray-100 dark:border-slate-700">
                  <Link
                    to={`/books/edit/${selectedBook.id}`}
                    className="flex-1 bg-blue-600 text-white py-3.5 rounded-xl hover:bg-blue-700 font-semibold transition-all shadow-lg shadow-blue-200 dark:shadow-blue-900/30 flex items-center justify-center gap-2 hover:-translate-y-0.5"
                  >
                    <Edit className="w-4 h-4" />
                    Edit Details
                  </Link>
                  <button
                    onClick={() => handleDelete(selectedBook.id)}
                    className="px-6 py-3.5 bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 text-red-600 dark:text-red-400 rounded-xl hover:bg-red-50 dark:hover:bg-red-900/20 hover:border-red-100 dark:hover:border-red-800 font-semibold transition-all flex items-center gap-2"
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BooksList;