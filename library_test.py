import requests

BASE_URL = "http://127.0.0.1:8000"

# Get all books
response = requests.get(f"{BASE_URL}/books")
print("All books:", response.json())

# Get statistics
response = requests.get(f"{BASE_URL}/stats")
print("\nLibrary Stats:", response.json())

# Create a new book
new_book = {
    "title": "The DevOps Handbook",
    "author": "Gene Kim",
    "category": "technology",
    "year": 2016,
    "price": 49.99,
    "rating": 4.7
}
response = requests.post(f"{BASE_URL}/books", json=new_book)
print("\nCreated book:", response.json())

# Search for books
response = requests.get(f"{BASE_URL}/books?search=python")
print("\nSearch results:", response.json())

# Get books by category
response = requests.get(f"{BASE_URL}/categories/technology/books")
print("\nTechnology books:", response.json())

# Get featured books
response = requests.get(f"{BASE_URL}/featured?limit=2")
print("\nFeatured books:", response.json())