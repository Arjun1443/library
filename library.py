from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

app = FastAPI(
    title="Book Library API",
    description="A comprehensive library management system",
    version="1.0.0"
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html at root
@app.get("/")
async def root():
    return FileResponse('static/index.html')

# Enums for categories
class BookCategory(str, Enum):
    FICTION = "fiction"
    NON_FICTION = "non-fiction"
    SCIENCE = "science"
    TECHNOLOGY = "technology"
    HISTORY = "history"
    BIOGRAPHY = "biography"

# Define book model
class Book(BaseModel):
    id: int
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    category: BookCategory
    year: int = Field(..., ge=1000, le=2026)
    price: float = Field(..., gt=0, le=1000)
    in_stock: bool = True
    rating: float = Field(..., ge=0, le=5)
    created_at: datetime = Field(default_factory=datetime.now)

# Create book model (without id for POST requests)
class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    category: BookCategory
    year: int = Field(..., ge=1000, le=2026)
    price: float = Field(..., gt=0, le=1000)
    in_stock: bool = True
    rating: float = Field(..., ge=0, le=5)

# Update book model (all fields optional)
class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[BookCategory] = None
    year: Optional[int] = Field(None, ge=1000, le=2026)
    price: Optional[float] = Field(None, gt=0, le=1000)
    in_stock: Optional[bool] = None
    rating: Optional[float] = Field(None, ge=0, le=5)

# Sample data
books_db = [
    Book(
        id=1,
        title="The Pragmatic Programmer",
        author="David Thomas",
        category=BookCategory.TECHNOLOGY,
        year=1999,
        price=39.99,
        in_stock=True,
        rating=4.8,
        created_at=datetime.now()
    ),
    Book(
        id=2,
        title="Sapiens",
        author="Yuval Noah Harari",
        category=BookCategory.HISTORY,
        year=2011,
        price=24.99,
        in_stock=True,
        rating=4.7,
        created_at=datetime.now()
    ),
    Book(
        id=3,
        title="Clean Code",
        author="Robert Martin",
        category=BookCategory.TECHNOLOGY,
        year=2008,
        price=45.99,
        in_stock=False,
        rating=4.9,
        created_at=datetime.now()
    )
]

# Helper function to get next ID
def get_next_id():
    return max(book.id for book in books_db) + 1 if books_db else 1

# ------------------- CRUD ENDPOINTS -------------------

# Get all books (with filtering)
@app.get("/books", response_model=List[Book])
def get_books(
    skip: int = Query(0, ge=0, description="Number of books to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum books to return"),
    category: Optional[BookCategory] = None,
    in_stock: Optional[bool] = None,
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    author: Optional[str] = None,
    search: Optional[str] = None
):
    """
    Get all books with optional filtering and pagination
    """
    result = books_db.copy()
    
    # Apply filters
    if category:
        result = [b for b in result if b.category == category]
    
    if in_stock is not None:
        result = [b for b in result if b.in_stock == in_stock]
    
    if min_rating:
        result = [b for b in result if b.rating >= min_rating]
    
    if author:
        result = [b for b in result if author.lower() in b.author.lower()]
    
    if search:
        result = [b for b in result if 
                 search.lower() in b.title.lower() or 
                 search.lower() in b.author.lower()]
    
    # Apply pagination
    return result[skip : skip + limit]

# Get single book by ID
@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    """
    Get a specific book by its ID
    """
    for book in books_db:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")

# Create new book
@app.post("/books", response_model=Book, status_code=201)
def create_book(book: BookCreate):
    """
    Add a new book to the library
    """
    # Check if book with same title and author already exists
    for existing_book in books_db:
        if existing_book.title.lower() == book.title.lower() and existing_book.author.lower() == book.author.lower():
            raise HTTPException(status_code=400, detail="Book already exists in the library")
    
    new_book = Book(
        id=get_next_id(),
        **book.dict()
    )
    books_db.append(new_book)
    return new_book

# Update existing book
@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book_update: BookUpdate):
    """
    Update an existing book's information
    """
    for index, book in enumerate(books_db):
        if book.id == book_id:
            # Update only provided fields
            update_data = book_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(book, field, value)
            books_db[index] = book
            return book
    
    raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")

# Delete book
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    """
    Remove a book from the library
    """
    for index, book in enumerate(books_db):
        if book.id == book_id:
            deleted_book = books_db.pop(index)
            return {
                "message": f"Book '{deleted_book.title}' deleted successfully",
                "deleted_book": deleted_book
            }
    
    raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")

# ------------------- ADDITIONAL USEFUL ENDPOINTS -------------------

# Get books by category
@app.get("/categories/{category}/books", response_model=List[Book])
def get_books_by_category(category: BookCategory):
    """
    Get all books in a specific category
    """
    result = [book for book in books_db if book.category == category]
    if not result:
        raise HTTPException(status_code=404, detail=f"No books found in {category} category")
    return result

# Get all unique categories
@app.get("/categories")
def get_all_categories():
    """
    Get list of all available book categories
    """
    categories = list(set(book.category.value for book in books_db))
    return {"categories": categories}

# Get statistics
@app.get("/stats")
def get_library_stats():
    """
    Get library statistics
    """
    total_books = len(books_db)
    books_in_stock = len([b for b in books_db if b.in_stock])
    books_out_of_stock = total_books - books_in_stock
    
    avg_rating = sum(b.rating for b in books_db) / total_books if total_books > 0 else 0
    
    # Books by category
    categories_count = {}
    for category in BookCategory:
        count = len([b for b in books_db if b.category == category])
        if count > 0:
            categories_count[category.value] = count
    
    # Most expensive book
    most_expensive = max(books_db, key=lambda b: b.price) if books_db else None
    
    return {
        "total_books": total_books,
        "books_in_stock": books_in_stock,
        "books_out_of_stock": books_out_of_stock,
        "average_rating": round(avg_rating, 2),
        "categories_breakdown": categories_count,
        "most_expensive_book": most_expensive.title if most_expensive else None,
        "most_expensive_price": most_expensive.price if most_expensive else None
    }

# Search books by price range
@app.get("/books/price-range")
def get_books_by_price_range(
    min_price: float = Query(..., gt=0),
    max_price: float = Query(..., gt=0)
):
    """
    Find books within a specific price range
    """
    if min_price > max_price:
        raise HTTPException(status_code=400, detail="min_price cannot be greater than max_price")
    
    result = [book for book in books_db if min_price <= book.price <= max_price]
    return {
        "count": len(result),
        "books": result,
        "price_range": f"${min_price} - ${max_price}"
    }

# Bulk create books
@app.post("/books/bulk", response_model=List[Book])
def bulk_create_books(books: List[BookCreate]):
    """
    Add multiple books at once
    """
    new_books = []
    for book in books:
        new_book = Book(
            id=get_next_id(),
            **book.dict()
        )
        books_db.append(new_book)
        new_books.append(new_book)
    
    return {
        "message": f"Successfully added {len(new_books)} books",
        "books": new_books
    }

# Get featured books (top rated)
@app.get("/featured")
def get_featured_books(limit: int = Query(3, ge=1, le=10)):
    """
    Get top-rated books
    """
    featured = sorted(books_db, key=lambda b: b.rating, reverse=True)[:limit]
    return {"featured_books": featured}

# Update stock status
@app.patch("/books/{book_id}/stock")
def update_stock_status(book_id: int, in_stock: bool):
    """
    Quickly update if a book is in stock
    """
    for book in books_db:
        if book.id == book_id:
            book.in_stock = in_stock
            return {
                "message": f"Stock status updated for '{book.title}'",
                "in_stock": in_stock
            }
    raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")