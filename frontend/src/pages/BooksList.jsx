// src/pages/BooksList.jsx
import React, { useState, useEffect } from 'react';
import { booksAPI, reviewsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { BookOpen, Search, Plus, Edit, Trash2, Eye, X, Book, Calendar, Layers, Hash, User, Star, MessageSquare, Send } from 'lucide-react';
import { Link } from 'react-router-dom';

const BooksList = () => {
  const { user } = useAuth();
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [skip, setSkip] = useState(0);
  const [limit] = useState(12); // Increased limit for grid view
  const [selectedBook, setSelectedBook] = useState(null);

  // Reviews State
  const [reviews, setReviews] = useState([]);
  const [reviewStats, setReviewStats] = useState({ average_rating: 0, review_count: 0 });
  const [userRating, setUserRating] = useState(5);
  const [userReviewText, setUserReviewText] = useState('');
  const [reviewSubmitting, setReviewSubmitting] = useState(false);

  useEffect(() => {
    if (selectedBook) {
      fetchReviews(selectedBook.id);
    }
  }, [selectedBook]);

  const fetchReviews = async (bookId) => {
    try {
      const [stats, reviewsList] = await Promise.all([
        reviewsAPI.getStats(bookId),
        reviewsAPI.list(bookId)
      ]);
      setReviewStats(stats);
      setReviews(reviewsList.items || []); // API returns paginated response
    } catch (error) {
      console.error('Failed to fetch reviews:', error);
    }
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    if (!selectedBook) return;

    setReviewSubmitting(true);
    try {
      await reviewsAPI.create({
        book_id: selectedBook.id,
        rating: userRating,
        text: userReviewText
      });

      // Reset form and refresh
      setUserReviewText('');
      setUserRating(5);
      fetchReviews(selectedBook.id);

    } catch (error) {
      console.error('Review submission failed:', error);
      alert(error.response?.data?.detail || 'Failed to submit review. You may have already reviewed this book.');
    } finally {
      setReviewSubmitting(false);
    }
  };

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
    // Strict ownership check
    // 1. If the book records an ownerEmail, it MUST match the current user.
    // 2. If the book marks NO owner (legacy), we default to disabling edit/delete 
    //    to prevent "another user" from modifying it. (Safe default)
    //    OR: If we assume "no owner" = public, we violate the user's request.
    //    Let's go with strict: You can only edit what you explicitly own.
    return book.ownerEmail && book.ownerEmail === user?.email;
  };

  return (
    <div className="font-sans">

      {/* Header & Add Button */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Library</h1>
          <p className="text-gray-500 text-sm mt-1">Manage and explore your collection</p>
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
          <div className="absolute -inset-1 bg-gradient-to-r from-blue-100 to-indigo-100 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000"></div>
          <div className="relative bg-white rounded-2xl shadow-xl shadow-gray-100 p-2 flex items-center border border-gray-100">
            <Search className="w-5 h-5 text-gray-400 ml-3" />
            <form onSubmit={handleSearch} className="flex-1 flex items-center">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by title, author, or ISBN..."
                className="w-full px-4 py-3 bg-transparent border-none focus:ring-0 text-gray-700 placeholder-gray-400 text-base"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={handleClearSearch}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors mr-2"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
              <button
                type="submit"
                disabled={loading}
                className="bg-gray-900 text-white px-6 py-2.5 rounded-xl hover:bg-black transition-colors font-medium text-sm disabled:opacity-70"
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
            <div className="w-12 h-12 border-4 border-blue-100 border-t-blue-600 rounded-full animate-spin"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
            </div>
          </div>
          <p className="mt-4 text-gray-500 font-medium animate-pulse">Fetching your library...</p>
        </div>
      ) : books.length === 0 ? (
        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-12 text-center max-w-lg mx-auto">
          <div className="bg-blue-50 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
            <Book className="w-10 h-10 text-blue-500" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-2">No books found</h3>
          <p className="text-gray-500 mb-8 leading-relaxed">
            {searchQuery
              ? `We couldn't find any books matching "${searchQuery}". Try a different keyword.`
              : "Your library is empty. Add your first book to get started!"}
          </p>
          {searchQuery ? (
            <button
              onClick={handleClearSearch}
              className="text-blue-600 font-medium hover:text-blue-800 transition-colors"
            >
              Clear Filters
            </button>
          ) : (
            <Link
              to="/books/create"
              className="inline-flex items-center gap-2 bg-blue-600 text-white px-8 py-3 rounded-xl hover:bg-blue-700 transition-all shadow-lg shadow-blue-200"
            >
              <Plus className="w-5 h-5" />
              Add Book
            </Link>
          )}
        </div>
      ) : (
        <div>
          <div className="flex items-center justify-between mb-6 px-2">
            <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
              All Books
              <span className="bg-gray-100 text-gray-600 py-0.5 px-2.5 rounded-full text-xs font-bold border border-gray-200">
                {books.length}
              </span>
            </h2>
            <div className="text-sm text-gray-500">
              Page {Math.floor(skip / limit) + 1}
            </div>
          </div>

          {/* Grid Layout */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {books.map((book) => (
              <div
                key={book.id}
                className="group bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 flex flex-col overflow-hidden"
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
                          className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          title="Edit"
                        >
                          <Edit className="w-4 h-4" />
                        </Link>
                        <button
                          onClick={(e) => { e.stopPropagation(); handleDelete(book.id); }}
                          className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                  </div>

                  <h3 className="font-bold text-gray-900 text-lg leading-tight mb-1 line-clamp-2" title={book.title}>
                    {book.title}
                  </h3>
                  <p className="text-gray-500 text-sm font-medium mb-4">{book.author}</p>

                  <div className="mt-auto space-y-2">
                    <div className="flex items-center text-xs text-gray-500 bg-gray-50 p-2 rounded-lg">
                      <User className="w-3.5 h-3.5 mr-2 text-gray-400" />
                      <span className="font-medium text-gray-600">{book.addedBy}</span>
                    </div>
                    <div className="flex items-center text-xs text-gray-500 bg-gray-50 p-2 rounded-lg">
                      <Hash className="w-3.5 h-3.5 mr-2 text-gray-400" />
                      <span className="font-mono truncate">{book.isbn || 'No ISBN'}</span>
                    </div>
                    <div className="flex items-center justify-between text-xs text-gray-500 px-1">
                      <span className="flex items-center">
                        <Calendar className="w-3.5 h-3.5 mr-1.5 text-gray-400" />
                        {book.published_year || 'N/A'}
                      </span>
                      <span className="flex items-center">
                        <Layers className="w-3.5 h-3.5 mr-1.5 text-gray-400" />
                        {book.pages || '-'} pgs
                      </span>
                    </div>
                  </div>
                </div>

                <div onClick={() => setSelectedBook(book)} className="bg-gray-50 px-6 py-3 border-t border-gray-100 flex items-center justify-between cursor-pointer hover:bg-blue-50/50 transition-colors">
                  <span className="text-xs font-semibold text-blue-600 uppercase tracking-wider">View Details</span>
                  <Eye className="w-4 h-4 text-blue-600" />
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          <div className="mt-12 flex justify-center gap-4">
            <button
              onClick={handlePrevPage}
              disabled={skip === 0}
              className="px-5 py-2.5 rounded-xl border border-gray-200 text-gray-600 font-medium hover:bg-white hover:border-gray-300 hover:shadow-sm disabled:opacity-50 disabled:hover:shadow-none transition-all"
            >
              Previous
            </button>
            <button
              onClick={handleNextPage}
              disabled={books.length < limit}
              className="px-5 py-2.5 rounded-xl bg-white border border-gray-200 text-gray-800 font-medium hover:border-gray-300 hover:shadow-sm disabled:opacity-50 disabled:hover:shadow-none transition-all"
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
            className="absolute inset-0 bg-gray-900/60 backdrop-blur-sm transition-opacity"
            onClick={() => setSelectedBook(null)}
          ></div>
          <div className="relative bg-white rounded-3xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto transform transition-all scale-100">
            <div className="p-8">
              <div className="flex justify-between items-start mb-8">
                <div>
                  <div className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 mb-3 border border-blue-100">
                    ID #{selectedBook.id}
                  </div>
                  <h2 className="text-3xl font-bold text-gray-900 leading-tight">{selectedBook.title}</h2>
                  <p className="text-lg text-gray-500 mt-1 font-medium">{selectedBook.author}</p>
                </div>
                <button
                  onClick={() => setSelectedBook(null)}
                  className="p-2 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
                >
                  <X className="w-5 h-5 text-gray-500" />
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
                <div className="md:col-span-2 space-y-6">
                  <div>
                    <h4 className="text-sm font-bold text-gray-900 uppercase tracking-wide mb-2">Description</h4>
                    <p className="text-gray-600 leading-relaxed text-sm">
                      {selectedBook.description || "No description available for this book."}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-50 p-4 rounded-xl border border-gray-100">
                      <p className="text-xs text-gray-500 mb-1">Published Year</p>
                      <p className="font-semibold text-gray-900 flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-blue-500" />
                        {selectedBook.published_year || 'N/A'}
                      </p>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-xl border border-gray-100">
                      <p className="text-xs text-gray-500 mb-1">Pages</p>
                      <p className="font-semibold text-gray-900 flex items-center gap-2">
                        <Layers className="w-4 h-4 text-blue-500" />
                        {selectedBook.pages || 'N/A'}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="md:col-span-1 space-y-4">
                  <div className="bg-slate-50 p-5 rounded-2xl border border-slate-100">
                    <div className="mb-4">
                      <p className="text-xs text-gray-500 mb-1">Added By</p>
                      <p className="font-medium text-slate-700 flex items-center gap-2">
                        <User className="w-4 h-4 text-blue-500" />
                        {selectedBook.addedBy}
                      </p>
                    </div>
                    <div className="mb-4">
                      <p className="text-xs text-gray-500 mb-1">ISBN</p>
                      <p className="font-mono text-sm font-medium text-slate-700 break-all">
                        {selectedBook.isbn || 'N/A'}
                      </p>
                    </div>
                    <div className="border-t border-slate-200 my-3"></div>
                    <div className="space-y-3">
                      <div>
                        <p className="text-xs text-gray-400">Added</p>
                        <p className="text-xs font-medium text-slate-600">{formatDate(selectedBook.created_at)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-400">Updated</p>
                        <p className="text-xs font-medium text-slate-600">{formatDate(selectedBook.updated_at)}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Reviews Section */}
              <div className="border-t border-gray-100 pt-8 mb-8">
                <h3 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
                  <MessageSquare className="w-5 h-5 text-blue-600" />
                  Reviews & Ratings
                </h3>

                {/* Stats */}
                <div className="flex items-center gap-8 mb-8 bg-gray-50 p-6 rounded-2xl">
                  <div className="text-center">
                    <div className="text-4xl font-bold text-gray-900 mb-1">{reviewStats.average_rating.toFixed(1)}</div>
                    <div className="flex gap-1 justify-center mb-1">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <Star
                          key={star}
                          className={`w-4 h-4 ${star <= Math.round(reviewStats.average_rating) ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}`}
                        />
                      ))}
                    </div>
                    <div className="text-xs text-gray-500">{reviewStats.review_count} reviews</div>
                  </div>
                  <div className="h-12 w-px bg-gray-200"></div>
                  <div className="flex-1">
                    {/* Add Review Form */}
                    <form onSubmit={handleReviewSubmit} className="space-y-3">
                      <div>
                        <label className="block text-xs font-semibold text-gray-700 mb-1">Rate this book</label>
                        <div className="flex gap-2">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <button
                              key={star}
                              type="button"
                              onClick={() => setUserRating(star)}
                              className="focus:outline-none transition-transform hover:scale-110"
                            >
                              <Star
                                className={`w-6 h-6 ${star <= userRating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}`}
                              />
                            </button>
                          ))}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <input
                          type="text"
                          value={userReviewText}
                          onChange={(e) => setUserReviewText(e.target.value)}
                          placeholder="Write a review..."
                          className="flex-1 px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-100 focus:border-blue-400 outline-none transition-all"
                        />
                        <button
                          type="submit"
                          disabled={reviewSubmitting}
                          className="bg-blue-600 text-white p-2 rounded-xl hover:bg-blue-700 disabled:opacity-50 transition-colors"
                        >
                          <Send className="w-5 h-5" />
                        </button>
                      </div>
                    </form>
                  </div>
                </div>

                {/* Review List */}
                <div className="space-y-4 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
                  {reviews.length === 0 ? (
                    <p className="text-center text-gray-500 text-sm py-4">No reviews yet. Be the first to review!</p>
                  ) : (
                    reviews.map((review) => (
                      <div key={review.id} className="bg-gray-50 p-4 rounded-xl border border-gray-100">
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex gap-1">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <Star
                                key={star}
                                className={`w-3 h-3 ${star <= review.rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}`}
                              />
                            ))}
                          </div>
                          <span className="text-xs text-gray-400">{formatDate(review.created_at)}</span>
                        </div>
                        {review.text && (
                          <p className="text-gray-700 text-sm leading-relaxed">{review.text}</p>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Only show buttons if authorized */}
              {canManageBook(selectedBook) && (
                <div className="flex gap-4 pt-4 border-t border-gray-100">
                  <Link
                    to={`/books/edit/${selectedBook.id}`}
                    className="flex-1 bg-blue-600 text-white py-3.5 rounded-xl hover:bg-blue-700 font-semibold transition-all shadow-lg shadow-blue-200 flex items-center justify-center gap-2 hover:-translate-y-0.5"
                  >
                    <Edit className="w-4 h-4" />
                    Edit Details
                  </Link>
                  <button
                    onClick={() => handleDelete(selectedBook.id)}
                    className="px-6 py-3.5 bg-white border border-gray-200 text-red-600 rounded-xl hover:bg-red-50 hover:border-red-100 font-semibold transition-all flex items-center gap-2"
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