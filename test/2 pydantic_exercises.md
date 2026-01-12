# Pydantic Validation Exercise

## Overview
This exercise will help you practice data validation in Python, progressing from manual validation to using Pydantic. You'll build a library management system step by step.

**Learning Objectives:**
- Understand the limitations of manual validation
- Learn to use Pydantic BaseModel
- Master Field validators and constraints
- Work with Optional fields
- Create custom validators
- Build complex nested models

---

## Part 1: Manual Validation (The Hard Way)

### Exercise 1.1: Basic User Validation

Write a function `create_user(name, age, email)` that validates:
- Name must not be empty and must be a string
- Age must be an integer between 0 and 120
- Email must contain '@' symbol

If any validation fails, raise a `ValueError` with an appropriate message.

**Test Cases:**
```python
# Should work
create_user("Alice", 25, "alice@example.com")

# Should raise ValueError
create_user("", 25, "alice@example.com")  # Empty name
create_user("Bob", -5, "bob@example.com")  # Negative age
create_user("Charlie", 150, "charlie@example.com")  # Age too high
create_user("Dave", 30, "dave.example.com")  # No @ in email
```

**Your Code Here:**
```python
def create_user(name, age, email):
    # TODO: Write your validation logic here
    pass
```

---

### Exercise 1.2: Book Validation with Try-Catch

Write a function `create_book(title, author, isbn, year, price)` that validates:
- Title must be a non-empty string
- Author must be a non-empty string
- ISBN must be exactly 13 digits (string)
- Year must be an integer between 1900 and current year
- Price must be a positive float

Use try-catch blocks to handle type conversion errors.

**Your Code Here:**
```python
def create_book(title, author, isbn, year, price):
    # TODO: Write your validation logic with try-catch
    pass
```

---

## Part 2: Introduction to Pydantic

### Exercise 2.1: Your First Pydantic Model

Create a Pydantic `User` model with the following fields:
- `username`: string
- `age`: integer
- `email`: string

Then create three user instances with valid data.

**Your Code Here:**
```python
from pydantic import BaseModel

# TODO: Define your User model here


# TODO: Create three user instances
```

---

### Exercise 2.2: Automatic Type Conversion

Create a `Book` model with:
- `title`: string
- `pages`: integer
- `price`: float
- `in_stock`: boolean

Test that Pydantic automatically converts types by creating a book with:
- pages as a string: "350"
- price as a string: "29.99"
- in_stock as an integer: 1

Print the types of each field to verify conversion.

**Your Code Here:**
```python
from pydantic import BaseModel

# TODO: Define Book model


# TODO: Create book with string values and verify type conversion
```

---

## Part 3: Field Validators and Constraints

### Exercise 3.1: Library Member

Create a `LibraryMember` model with Field constraints:
- `member_id`: string, exactly 8 characters long
- `full_name`: string, minimum 2 characters, maximum 100 characters
- `age`: integer, must be >= 0 and <= 120
- `email`: string, must match email pattern `r'^[\w\.-]+@[\w\.-]+\.\w+$'`
- `phone`: string, optional (can be None), maximum 15 characters

Test with both valid and invalid data.

**Your Code Here:**
```python
from pydantic import BaseModel, Field
from typing import Optional

# TODO: Define LibraryMember model with Field constraints


# TODO: Test with valid data


# TODO: Test with invalid data (wrap in try-except to see errors)
```

---

### Exercise 3.2: Product Catalog

Create a `Product` model for a bookstore:
- `product_id`: integer, must be greater than 0
- `name`: string, 3-200 characters
- `description`: optional string, can be None
- `price`: float, must be > 0
- `discount_percentage`: float, must be >= 0 and <= 100
- `quantity`: integer, must be >= 0
- `category`: optional string with default value "General"

**Your Code Here:**
```python
from pydantic import BaseModel, Field
from typing import Optional

# TODO: Define Product model


# TODO: Create a product with all fields


# TODO: Create a product without optional fields
```

---

## Part 4: Custom Validators

### Exercise 4.1: Book with ISBN Validation

Create a `Book` model with a custom validator for ISBN:
- `title`: string
- `author`: string
- `isbn`: string (must be exactly 13 digits)
- `publication_year`: integer

Write a `@field_validator` for `isbn` that:
1. Removes any hyphens or spaces
2. Checks that the result is exactly 13 digits
3. Raises ValueError if invalid

**Your Code Here:**
```python
from pydantic import BaseModel, field_validator

# TODO: Define Book model with ISBN validator


# TODO: Test with valid ISBN: "978-0-13-110362-7"


# TODO: Test with invalid ISBN
```

---

### Exercise 4.2: User Registration with Password Strength

Create a `UserRegistration` model with password validation:
- `username`: string, 3-20 characters
- `email`: string
- `password`: string, minimum 8 characters
- `confirm_password`: string

Create custom validators for:
1. **Username**: Must contain only letters, numbers, and underscores
2. **Password strength**: Must contain at least:
   - One uppercase letter
   - One lowercase letter
   - One digit
   - One special character from: !@#$%^&*
3. **Email**: Convert to lowercase

**Your Code Here:**
```python
from pydantic import BaseModel, Field, field_validator
import re

# TODO: Define UserRegistration model with custom validators


# TODO: Test with valid data


# TODO: Test with weak password
```

---

## Part 5: Complex Nested Models

### Exercise 5.1: Library System

Build a complete library system with nested models:

**Models needed:**
1. `Author`: 
   - `name`: string
   - `birth_year`: integer, must be >= 1800
   - `nationality`: optional string

2. `Book`:
   - `isbn`: string
   - `title`: string
   - `author`: Author object (nested)
   - `publication_year`: integer
   - `pages`: integer, must be > 0
   - `available_copies`: integer, must be >= 0

3. `Loan`:
   - `loan_id`: string
   - `book`: Book object (nested)
   - `borrower_name`: string
   - `loan_date`: string (format: YYYY-MM-DD)
   - `due_date`: string (format: YYYY-MM-DD)
   - `returned`: boolean, default False

**Your Code Here:**
```python
from pydantic import BaseModel, Field
from typing import Optional

# TODO: Define Author model


# TODO: Define Book model


# TODO: Define Loan model


# TODO: Create a complete loan record with nested author and book
```

---

### Exercise 5.2: Order Management System

Create an order system with the following models:

1. `Address`:
   - `street`: string
   - `city`: string
   - `state`: string, exactly 2 uppercase letters
   - `zip_code`: string, must match pattern `r'^\d{5}(-\d{4})?$'` (e.g., "12345" or "12345-6789")

2. `OrderItem`:
   - `product_name`: string
   - `quantity`: integer, must be between 1 and 100
   - `unit_price`: float, must be > 0
   - Add a `@property` method `total_price` that returns quantity * unit_price

3. `Order`:
   - `order_id`: string
   - `customer_name`: string
   - `email`: string
   - `items`: list of OrderItem (must have at least 1 item)
   - `shipping_address`: Address object
   - `notes`: optional string
   - Add a `@property` method `order_total` that sums all item totals

**Your Code Here:**
```python
from pydantic import BaseModel, Field
from typing import List, Optional

# TODO: Define Address model


# TODO: Define OrderItem model with total_price property


# TODO: Define Order model with order_total property


# TODO: Create a complete order with multiple items
```

---

## Part 6: Real-World Challenge

### Challenge: Complete Library Management System

Build a comprehensive library system that combines everything you've learned.

**Requirements:**

1. **Member Model**:
   - member_id (auto-generated format: "M" + 6 digits)
   - full_name (2-100 chars)
   - email (validated)
   - phone (optional)
   - membership_type: must be one of ["standard", "premium", "student"]
   - joined_date: string
   - active: boolean, default True

2. **Book Model**:
   - isbn (validated: 13 digits)
   - title (not empty)
   - authors: list of strings (at least 1 author)
   - publication_year (1800 to current year)
   - genre: optional, default "Fiction"
   - total_copies: integer >= 1
   - available_copies: integer >= 0
   - Custom validator: available_copies cannot exceed total_copies

3. **Transaction Model**:
   - transaction_id: string
   - member: Member object
   - book: Book object
   - transaction_type: must be "borrow" or "return"
   - transaction_date: string
   - due_date: optional string (required for "borrow")

**Additional Requirements:**
- Write custom validators where appropriate
- Use Field constraints for all numeric limits
- Include at least 3 test cases showing the system working
- Include at least 2 test cases showing validation errors

**Your Code Here:**
```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

# TODO: Define all models


# TODO: Create test cases (valid)


# TODO: Create test cases (should fail validation)
```

---

## Bonus Challenges

### Bonus 1: Data Transformation
Add a validator to the User model that automatically:
- Capitalizes the first letter of each word in `full_name`
- Converts email to lowercase
- Strips whitespace from all string fields

### Bonus 2: Cross-Field Validation
In the Book model, create a validator that ensures:
- If publication_year is before 2000, price must be less than $20
- If publication_year is 2020 or later, price must be at least $10

### Bonus 3: List Validation
Create a `Library` model that:
- Contains a list of Book objects
- Has a custom validator ensuring no duplicate ISBNs
- Has a method to calculate total value of all books

**Your Code Here:**
```python
# TODO: Implement bonus challenges
```

---

## Submission Checklist

Before submitting, make sure you've completed:
- [ ] Part 1: Manual validation exercises (1.1, 1.2)
- [ ] Part 2: Basic Pydantic models (2.1, 2.2)
- [ ] Part 3: Field validators (3.1, 3.2)
- [ ] Part 4: Custom validators (4.1, 4.2)
- [ ] Part 5: Nested models (5.1, 5.2)
- [ ] Part 6: Real-world challenge
- [ ] Bonus challenges (optional)

**Testing Tips:**
- Always test both valid and invalid data
- Use try-except blocks to catch and display validation errors
- Print your model instances to verify they work
- Use `model.model_dump()` to see the dictionary representation

---

## Additional Resources

- Pydantic Documentation: https://docs.pydantic.dev
- Python Type Hints: https://docs.python.org/3/library/typing.html
- Regular Expressions: https://docs.python.org/3/library/re.html

Good luck! 🚀
