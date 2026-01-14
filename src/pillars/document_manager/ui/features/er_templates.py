"""
ER Diagram Templates and Examples.

**Purpose**:
Provide pre-built ER diagram examples for common use cases.
Users can select from templates or learn from examples.

**Usage**:
```python
from .er_templates import ER_TEMPLATES, create_template

# Get template by name
code = ER_TEMPLATES["E-Commerce"]

# Or create programmatically
ast = create_template("blog")
code = ERDiagramGenerator.generate(ast)
```
"""

from .er_ast import ERDiagramAST, Cardinality


# ============================================================================
# TEMPLATE CREATORS
# ============================================================================

def create_ecommerce_template() -> ERDiagramAST:
    """E-Commerce system with users, products, orders."""
    ast = ERDiagramAST()
    ast.title = "E-Commerce System"
    
    # USER entity
    user = ast.add_entity("USER")
    user.add_attribute("id", "int", ["PK"])
    user.add_attribute("email", "string", ["UK"])
    user.add_attribute("name", "string", [])
    user.add_attribute("password_hash", "string", [])
    user.add_attribute("created_at", "datetime", [])
    
    # PRODUCT entity
    product = ast.add_entity("PRODUCT")
    product.add_attribute("id", "int", ["PK"])
    product.add_attribute("name", "string", [])
    product.add_attribute("description", "text", [])
    product.add_attribute("price", "decimal", [])
    product.add_attribute("stock", "int", [])
    product.add_attribute("category", "string", [])
    
    # ORDER entity
    order = ast.add_entity("ORDER")
    order.add_attribute("id", "int", ["PK"])
    order.add_attribute("user_id", "int", ["FK"])
    order.add_attribute("total", "decimal", [])
    order.add_attribute("status", "enum", [])
    order.add_attribute("created_at", "datetime", [])
    order.add_attribute("shipped_at", "datetime", [])
    
    # ORDER_ITEM entity (junction table)
    item = ast.add_entity("ORDER_ITEM")
    item.add_attribute("id", "int", ["PK"])
    item.add_attribute("order_id", "int", ["FK"])
    item.add_attribute("product_id", "int", ["FK"])
    item.add_attribute("quantity", "int", [])
    item.add_attribute("price", "decimal", [])
    
    # Relationships
    ast.add_relationship("USER", "ORDER", Cardinality.EXACTLY_ONE_TO_ZERO_OR_MORE, "places")
    ast.add_relationship("ORDER", "ORDER_ITEM", Cardinality.EXACTLY_ONE_TO_ONE_OR_MORE, "contains")
    ast.add_relationship("PRODUCT", "ORDER_ITEM", Cardinality.EXACTLY_ONE_TO_ZERO_OR_MORE, "appears_in")
    
    return ast


def create_blog_template() -> ERDiagramAST:
    """Blog platform with posts, comments, tags."""
    ast = ERDiagramAST()
    ast.title = "Blog Platform"
    
    user = ast.add_entity("USER")
    user.add_attribute("id", "int", ["PK"])
    user.add_attribute("username", "string", ["UK"])
    user.add_attribute("email", "string", ["UK"])
    user.add_attribute("bio", "text", [])
    user.add_attribute("joined_at", "datetime", [])
    
    post = ast.add_entity("POST")
    post.add_attribute("id", "int", ["PK"])
    post.add_attribute("author_id", "int", ["FK"])
    post.add_attribute("title", "string", [])
    post.add_attribute("slug", "string", ["UK"])
    post.add_attribute("content", "text", [])
    post.add_attribute("published_at", "datetime", [])
    post.add_attribute("view_count", "int", [])
    
    comment = ast.add_entity("COMMENT")
    comment.add_attribute("id", "int", ["PK"])
    comment.add_attribute("post_id", "int", ["FK"])
    comment.add_attribute("author_id", "int", ["FK"])
    comment.add_attribute("content", "text", [])
    comment.add_attribute("created_at", "datetime", [])
    
    tag = ast.add_entity("TAG")
    tag.add_attribute("id", "int", ["PK"])
    tag.add_attribute("name", "string", ["UK"])
    tag.add_attribute("slug", "string", ["UK"])
    
    post_tag = ast.add_entity("POST_TAG")
    post_tag.add_attribute("post_id", "int", ["PK", "FK"])
    post_tag.add_attribute("tag_id", "int", ["PK", "FK"])
    
    ast.add_relationship("USER", "POST", Cardinality.EXACTLY_ONE_TO_ZERO_OR_MORE, "authors")
    ast.add_relationship("USER", "COMMENT", Cardinality.EXACTLY_ONE_TO_ZERO_OR_MORE, "writes")
    ast.add_relationship("POST", "COMMENT", Cardinality.EXACTLY_ONE_TO_ZERO_OR_MORE, "has")
    ast.add_relationship("POST", "POST_TAG", Cardinality.EXACTLY_ONE_TO_ZERO_OR_MORE, "tagged")
    ast.add_relationship("TAG", "POST_TAG", Cardinality.EXACTLY_ONE_TO_ZERO_OR_MORE, "applied_to")
    
    return ast


def create_university_template() -> ERDiagramAST:
    """University system with students, courses, instructors."""
    ast = ERDiagramAST()
    ast.title = "University System"
    
    student = ast.add_entity("STUDENT")
    student.add_attribute("id", "int", ["PK"])
    student.add_attribute("student_number", "string", ["UK"])
    student.add_attribute("name", "string", [])
    student.add_attribute("email", "string", ["UK"])
    student.add_attribute("major", "string", [])
    student.add_attribute("enrolled_date", "date", [])
    
    course = ast.add_entity("COURSE")
    course.add_attribute("id", "int", ["PK"])
    course.add_attribute("code", "string", ["UK"])
    course.add_attribute("title", "string", [])
    course.add_attribute("description", "text", [])
    course.add_attribute("credits", "int", [])
    
    instructor = ast.add_entity("INSTRUCTOR")
    instructor.add_attribute("id", "int", ["PK"])
    instructor.add_attribute("name", "string", [])
    instructor.add_attribute("department", "string", [])
    instructor.add_attribute("email", "string", ["UK"])
    instructor.add_attribute("office", "string", [])
    
    enrollment = ast.add_entity("ENROLLMENT")
    enrollment.add_attribute("student_id", "int", ["PK", "FK"])
    enrollment.add_attribute("course_id", "int", ["PK", "FK"])
    enrollment.add_attribute("semester", "string", ["PK"])
    enrollment.add_attribute("grade", "string", [])
    enrollment.add_attribute("enrolled_at", "datetime", [])
    
    ast.add_relationship("STUDENT", "ENROLLMENT", Cardinality.EXACTLY_ONE_TO_ZERO_OR_MORE, "enrolls")
    ast.add_relationship("COURSE", "ENROLLMENT", Cardinality.EXACTLY_ONE_TO_ZERO_OR_MORE, "offered_in")
    ast.add_relationship("INSTRUCTOR", "COURSE", Cardinality.EXACTLY_ONE_TO_ZERO_OR_MORE, "teaches")
    
    return ast


def create_library_template() -> ERDiagramAST:
    """Library management system."""
    ast = ERDiagramAST()
    ast.title = "Library Management"
    
    member = ast.add_entity("MEMBER")
    member.add_attribute("id", "int", ["PK"])
    member.add_attribute("card_number", "string", ["UK"])
    member.add_attribute("name", "string", [])
    member.add_attribute("email", "string", ["UK"])
    member.add_attribute("joined_date", "date", [])
    
    book = ast.add_entity("BOOK")
    book.add_attribute("id", "int", ["PK"])
    book.add_attribute("isbn", "string", ["UK"])
    book.add_attribute("title", "string", [])
    book.add_attribute("author", "string", [])
    book.add_attribute("publisher", "string", [])
    book.add_attribute("year", "int", [])
    book.add_attribute("copies", "int", [])
    
    loan = ast.add_entity("LOAN")
    loan.add_attribute("id", "int", ["PK"])
    loan.add_attribute("member_id", "int", ["FK"])
    loan.add_attribute("book_id", "int", ["FK"])
    loan.add_attribute("borrowed_at", "datetime", [])
    loan.add_attribute("due_date", "date", [])
    loan.add_attribute("returned_at", "datetime", [])
    
    reservation = ast.add_entity("RESERVATION")
    reservation.add_attribute("id", "int", ["PK"])
    reservation.add_attribute("member_id", "int", ["FK"])
    reservation.add_attribute("book_id", "int", ["FK"])
    reservation.add_attribute("reserved_at", "datetime", [])
    reservation.add_attribute("expires_at", "datetime", [])
    
    ast.add_relationship("MEMBER", "LOAN", Cardinality.EXACTLY_ONE_TO_ZERO_OR_MORE, "borrows")
    ast.add_relationship("BOOK", "LOAN", Cardinality.EXACTLY_ONE_TO_ZERO_OR_MORE, "loaned")
    ast.add_relationship("MEMBER", "RESERVATION", Cardinality.EXACTLY_ONE_TO_ZERO_OR_MORE, "reserves")
    ast.add_relationship("BOOK", "RESERVATION", Cardinality.EXACTLY_ONE_TO_ZERO_OR_MORE, "reserved")
    
    return ast


def create_hotel_template() -> ERDiagramAST:
    """Hotel booking system."""
    ast = ERDiagramAST()
    ast.title = "Hotel Booking System"
    
    guest = ast.add_entity("GUEST")
    guest.add_attribute("id", "int", ["PK"])
    guest.add_attribute("email", "string", ["UK"])
    guest.add_attribute("name", "string", [])
    guest.add_attribute("phone", "string", [])
    guest.add_attribute("loyalty_points", "int", [])
    
    room = ast.add_entity("ROOM")
    room.add_attribute("id", "int", ["PK"])
    room.add_attribute("number", "string", ["UK"])
    room.add_attribute("type", "enum", [])
    room.add_attribute("floor", "int", [])
    room.add_attribute("price_per_night", "decimal", [])
    room.add_attribute("max_guests", "int", [])
    
    booking = ast.add_entity("BOOKING")
    booking.add_attribute("id", "int", ["PK"])
    booking.add_attribute("guest_id", "int", ["FK"])
    booking.add_attribute("room_id", "int", ["FK"])
    booking.add_attribute("check_in", "date", [])
    booking.add_attribute("check_out", "date", [])
    booking.add_attribute("total_price", "decimal", [])
    booking.add_attribute("status", "enum", [])
    
    payment = ast.add_entity("PAYMENT")
    payment.add_attribute("id", "int", ["PK"])
    payment.add_attribute("booking_id", "int", ["FK"])
    payment.add_attribute("amount", "decimal", [])
    payment.add_attribute("method", "enum", [])
    payment.add_attribute("paid_at", "datetime", [])
    
    ast.add_relationship("GUEST", "BOOKING", Cardinality.EXACTLY_ONE_TO_ZERO_OR_MORE, "makes")
    ast.add_relationship("ROOM", "BOOKING", Cardinality.EXACTLY_ONE_TO_ZERO_OR_MORE, "booked")
    ast.add_relationship("BOOKING", "PAYMENT", Cardinality.EXACTLY_ONE_TO_ONE_OR_MORE, "paid_by")
    
    return ast


# ============================================================================
# TEMPLATE REGISTRY
# ============================================================================

TEMPLATE_CREATORS = {
    "E-Commerce": create_ecommerce_template,
    "Blog Platform": create_blog_template,
    "University": create_university_template,
    "Library": create_library_template,
    "Hotel Booking": create_hotel_template,
}


def create_template(name: str) -> ERDiagramAST:
    """
    Create an ER diagram from a template.
    
    **Args**:
        name: Template name (case-insensitive)
    
    **Returns**:
        ERDiagramAST: The created diagram
    
    **Raises**:
        ValueError: If template name not found
    
    **Example**:
    ```python
    ast = create_template("blog platform")
    ```
    """
    # Case-insensitive lookup
    for template_name, creator in TEMPLATE_CREATORS.items():
        if template_name.lower() == name.lower():
            return creator()
    
    raise ValueError(f"Template '{name}' not found. Available: {list(TEMPLATE_CREATORS.keys())}")


def get_template_names() -> list[str]:
    """Get list of available template names."""
    return list(TEMPLATE_CREATORS.keys())


# ============================================================================
# MERMAID CODE TEMPLATES (Pre-generated for quick insertion)
# ============================================================================

ER_TEMPLATES = {
    "Simple (Two Tables)": """erDiagram
    USER {
        int id PK
        string email UK
        string name
    }
    
    ORDER {
        int id PK
        int user_id FK
        decimal total
        datetime created_at
    }
    
    USER ||--o{ ORDER : places""",
    
    "E-Commerce": """erDiagram
    USER {
        int id PK
        string email UK
        string name
        datetime created_at
    }
    
    PRODUCT {
        int id PK
        string name
        decimal price
        int stock
    }
    
    ORDER {
        int id PK
        int user_id FK
        decimal total
        enum status
        datetime created_at
    }
    
    ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal price
    }
    
    USER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : appears_in""",
    
    "Blog Platform": """erDiagram
    USER {
        int id PK
        string username UK
        string email UK
    }
    
    POST {
        int id PK
        int author_id FK
        string title
        text content
        datetime published_at
    }
    
    COMMENT {
        int id PK
        int post_id FK
        int author_id FK
        text content
        datetime created_at
    }
    
    TAG {
        int id PK
        string name UK
    }
    
    POST_TAG {
        int post_id PK FK
        int tag_id PK FK
    }
    
    USER ||--o{ POST : authors
    USER ||--o{ COMMENT : writes
    POST ||--o{ COMMENT : has
    POST ||--o{ POST_TAG : tagged
    TAG ||--o{ POST_TAG : applied_to""",
}
