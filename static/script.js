const API_BASE_URL = 'https://librarysample-ghgjfmhnhxasgtdb.canadacentral-01.azurewebsites.net';
// Load books when page loads
document.addEventListener('DOMContentLoaded', () => {
    loadBooks();
    loadStats();
});

// Load all books
async function loadBooks() {
    try {
        const response = await fetch(`${API_BASE_URL}/books`);
        const books = await response.json();
        displayBooks(books);
    } catch (error) {
        console.error('Error loading books:', error);
        showError('Failed to load books');
    }
}

// Display books in grid
function displayBooks(books) {
    const booksGrid = document.getElementById('booksGrid');
    
    if (books.length === 0) {
        booksGrid.innerHTML = '<div class="loading">No books found</div>';
        return;
    }
    
    booksGrid.innerHTML = books.map(book => `
        <div class="book-card ${!book.in_stock ? 'out-of-stock' : ''}">
            <div class="book-title">${escapeHtml(book.title)}</div>
            <div class="book-author">by ${escapeHtml(book.author)}</div>
            <div class="book-details">
                <div><i class="fas fa-tag"></i> ${book.category}</div>
                <div><i class="fas fa-calendar"></i> ${book.year}</div>
                <div><i class="fas fa-dollar-sign"></i> $${book.price.toFixed(2)}</div>
                <div class="rating">
                    <i class="fas fa-star"></i> ${book.rating.toFixed(1)} / 5.0
                </div>
            </div>
            <div class="stock-badge ${book.in_stock ? 'stock-in' : 'stock-out'}">
                ${book.in_stock ? '✓ In Stock' : '✗ Out of Stock'}
            </div>
            <div class="card-actions">
                <button class="btn btn-edit" onclick="editBook(${book.id})">
                    <i class="fas fa-edit"></i> Edit
                </button>
                <button class="btn btn-danger" onclick="deleteBook(${book.id})">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
        </div>
    `).join('');
}

// Apply filters
async function applyFilters() {
    const search = document.getElementById('searchInput').value;
    const category = document.getElementById('categoryFilter').value;
    const inStock = document.getElementById('stockFilter').value;
    const minRating = document.getElementById('minRating').value;
    
    let url = `${API_BASE_URL}/books?`;
    const params = [];
    
    if (search) params.push(`search=${encodeURIComponent(search)}`);
    if (category) params.push(`category=${category}`);
    if (inStock) params.push(`in_stock=${inStock}`);
    if (minRating) params.push(`min_rating=${minRating}`);
    
    url += params.join('&');
    
    try {
        const response = await fetch(url);
        const books = await response.json();
        displayBooks(books);
    } catch (error) {
        console.error('Error filtering books:', error);
    }
}

// Show add book modal
function showAddBookModal() {
    document.getElementById('modalTitle').textContent = 'Add New Book';
    document.getElementById('bookForm').reset();
    document.getElementById('bookId').value = '';
    document.getElementById('bookModal').style.display = 'block';
}

// Edit book
async function editBook(id) {
    try {
        const response = await fetch(`${API_BASE_URL}/books/${id}`);
        const book = await response.json();
        
        document.getElementById('modalTitle').textContent = 'Edit Book';
        document.getElementById('bookId').value = book.id;
        document.getElementById('title').value = book.title;
        document.getElementById('author').value = book.author;
        document.getElementById('category').value = book.category;
        document.getElementById('year').value = book.year;
        document.getElementById('price').value = book.price;
        document.getElementById('rating').value = book.rating;
        document.getElementById('inStock').value = book.in_stock;
        
        document.getElementById('bookModal').style.display = 'block';
    } catch (error) {
        console.error('Error loading book:', error);
        showError('Failed to load book details');
    }
}

// Delete book
async function deleteBook(id) {
    if (confirm('Are you sure you want to delete this book?')) {
        try {
            const response = await fetch(`${API_BASE_URL}/books/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                showSuccess('Book deleted successfully');
                refreshBooks();
                loadStats();
            } else {
                showError('Failed to delete book');
            }
        } catch (error) {
            console.error('Error deleting book:', error);
            showError('Failed to delete book');
        }
    }
}

// Save book (create or update)
document.getElementById('bookForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const bookId = document.getElementById('bookId').value;
    const bookData = {
        title: document.getElementById('title').value,
        author: document.getElementById('author').value,
        category: document.getElementById('category').value,
        year: parseInt(document.getElementById('year').value),
        price: parseFloat(document.getElementById('price').value),
        rating: parseFloat(document.getElementById('rating').value),
        in_stock: document.getElementById('inStock').value === 'true'
    };
    
    try {
        let response;
        if (bookId) {
            // Update existing book
            response = await fetch(`${API_BASE_URL}/books/${bookId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(bookData)
            });
        } else {
            // Create new book
            response = await fetch(`${API_BASE_URL}/books`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(bookData)
            });
        }
        
        if (response.ok) {
            showSuccess(bookId ? 'Book updated successfully' : 'Book added successfully');
            closeModal();
            refreshBooks();
            loadStats();
        } else {
            const error = await response.json();
            showError(error.detail || 'Failed to save book');
        }
    } catch (error) {
        console.error('Error saving book:', error);
        showError('Failed to save book');
    }
});

// Load statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        const stats = await response.json();
        
        document.getElementById('totalBooks').textContent = stats.total_books;
        document.getElementById('inStockBooks').textContent = stats.books_in_stock;
        document.getElementById('avgRating').textContent = stats.average_rating;
        document.getElementById('categoriesCount').textContent = Object.keys(stats.categories_breakdown || {}).length;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Show detailed stats in modal
async function showStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        const stats = await response.json();
        
        const statsContent = document.getElementById('statsContent');
        statsContent.innerHTML = `
            <div class="stats-content">
                <div class="stat-item">
                    <span class="stat-label">Total Books:</span>
                    <span class="stat-value">${stats.total_books}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Books In Stock:</span>
                    <span class="stat-value">${stats.books_in_stock}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Books Out of Stock:</span>
                    <span class="stat-value">${stats.books_out_of_stock}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Average Rating:</span>
                    <span class="stat-value">${stats.average_rating} / 5.0</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Most Expensive Book:</span>
                    <span class="stat-value">${stats.most_expensive_book || 'N/A'} ($${stats.most_expensive_price || 0})</span>
                </div>
                <div class="category-breakdown">
                    <strong>Books by Category:</strong>
                    ${Object.entries(stats.categories_breakdown || {}).map(([category, count]) => `
                        <div class="category-item">
                            <span>${category}</span>
                            <span class="stat-value">${count} book(s)</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        document.getElementById('statsModal').style.display = 'block';
    } catch (error) {
        console.error('Error loading stats:', error);
        showError('Failed to load statistics');
    }
}

// Refresh books
function refreshBooks() {
    applyFilters();
}

// Close modals
function closeModal() {
    document.getElementById('bookModal').style.display = 'none';
}

function closeStatsModal() {
    document.getElementById('statsModal').style.display = 'none';
}

// Close modals when clicking outside
window.onclick = function(event) {
    const bookModal = document.getElementById('bookModal');
    const statsModal = document.getElementById('statsModal');
    if (event.target === bookModal) closeModal();
    if (event.target === statsModal) closeStatsModal();
}

// Helper functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showSuccess(message) {
    alert('✓ ' + message);
}

function showError(message) {
    alert('✗ Error: ' + message);
}