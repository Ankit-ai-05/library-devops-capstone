import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///library.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

DEPARTMENTS = ["Computer Science", "AI & ML", "Literature", "Engineering", "Management"]
DEFAULT_COVER = "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=400&q=80"

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50), default="Computer Science")
    image_url = db.Column(db.String(300), default=DEFAULT_COVER)
    status = db.Column(db.String(20), default="Available")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "department": self.department,
            "image_url": self.image_url,
            "status": self.status,
        }

def seed_books():
    if Book.query.count() == 0:
        sample_books = [
            Book(title="Clean Code", author="Robert C. Martin", department="Computer Science",
                 image_url="https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=400&q=80"),
            Book(title="Deep Learning", author="Ian Goodfellow", department="AI & ML",
                 image_url="https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=400&q=80"),
            Book(title="The Guide", author="R.K. Narayan", department="Literature",
                 image_url="https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=400&q=80"),
            Book(title="Gitanjali", author="Rabindranath Tagore", department="Literature",
                 image_url="https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=400&q=80"),
            Book(title="Engineering Mechanics", author="R.S. Khurmi", department="Engineering",
                 image_url="https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=400&q=80"),
            Book(title="The DevOps Handbook", author="Gene Kim", department="Management",
                 image_url="https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=400&q=80"),
        ]
        db.session.bulk_save_objects(sample_books)
        db.session.commit()

with app.app_context():
    db.create_all()
    seed_books()

@app.route("/health")
def health():
    return jsonify({"status": "UP", "service": "library-management-system"}), 200

@app.route("/", methods=["GET"])
def index():
    if not session.get("logged_in"):
        return render_template("index.html", logged_in=False)
    selected_dept = request.args.get("dept", "All")
    if selected_dept != "All":
        books = Book.query.filter_by(department=selected_dept).all()
    else:
        books = Book.query.all()
    return render_template(
        "index.html",
        logged_in=True,
        books=books,
        user=session.get("user"),
        role=session.get("role"),
        departments=DEPARTMENTS,
        selected_dept=selected_dept,
    )

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    if username == "admin" and password == "admin123":
        session["logged_in"] = True
        session["user"] = "Admin"
        session["role"] = "admin"
        return redirect(url_for("index"))
    elif username == "student" and password == "student123":
        session["logged_in"] = True
        session["user"] = "Student"
        session["role"] = "student"
        return redirect(url_for("index"))
    return render_template("index.html", logged_in=False, error="Invalid credentials! Use admin/admin123 or student/student123")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/add", methods=["POST"])
def add_book():
    if session.get("role") != "admin":
        return redirect(url_for("index"))
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    department = request.form.get("department", "Computer Science")
    image_url = request.form.get("image_url", "").strip() or DEFAULT_COVER
    if title and author:
        db.session.add(Book(title=title, author=author, department=department, image_url=image_url))
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/toggle/<int:book_id>")
def toggle_book(book_id):
    if session.get("role") != "admin":
        return redirect(url_for("index"))
    book = db.session.get(Book, book_id)
    if book:
        book.status = "Issued" if book.status == "Available" else "Available"
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/borrow/<int:book_id>")
def borrow_book(book_id):
    if not session.get("logged_in"):
        return redirect(url_for("index"))
    book = db.session.get(Book, book_id)
    if book and book.status == "Available":
        book.status = "Issued"
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/delete/<int:book_id>")
def delete_book(book_id):
    if session.get("role") != "admin":
        return redirect(url_for("index"))
    book = db.session.get(Book, book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
    return redirect(url_for("index"))

# --- REST APIs ---
@app.route("/api/books", methods=["GET", "POST"])
def api_books():
    if request.method == "POST":
        data = request.get_json() or {}
        if not data.get("title") or not data.get("author"):
            return jsonify({"error": "title and author are required"}), 400
        book = Book(
            title=data["title"],
            author=data["author"],
            department=data.get("department", "Computer Science"),
            image_url=data.get("image_url", DEFAULT_COVER),
        )
        db.session.add(book)
        db.session.commit()
        return jsonify(book.to_dict()), 201
    return jsonify([b.to_dict() for b in Book.query.all()]), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
