import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///library.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default="Available")

    def to_dict(self):
        return {"id": self.id, "title": self.title, "author": self.author, "status": self.status}

with app.app_context():
    db.create_all()

@app.route("/health")
def health():
    return jsonify({"status": "UP", "service": "library-management-system"}), 200

@app.route("/", methods=["GET"])
def index():
    if not session.get("logged_in"):
        return render_template("index.html", logged_in=False)
    books = Book.query.all()
    return render_template("index.html", logged_in=True, books=books, user=session.get("user"))

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    if username == "admin" and password == "admin123":
        session["logged_in"] = True
        session["user"] = username
        return redirect(url_for("index"))
    return render_template("index.html", logged_in=False, error="Invalid credentials! Use admin / admin123")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/add", methods=["POST"])
def add_book():
    if not session.get("logged_in"):
        return redirect(url_for("index"))
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    if title and author:
        db.session.add(Book(title=title, author=author))
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/toggle/<int:book_id>")
def toggle_book(book_id):
    if not session.get("logged_in"):
        return redirect(url_for("index"))
    book = db.session.get(Book, book_id)
    if book:
        book.status = "Issued" if book.status == "Available" else "Available"
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/delete/<int:book_id>")
def delete_book(book_id):
    if not session.get("logged_in"):
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
        book = Book(title=data["title"], author=data["author"])
        db.session.add(book)
        db.session.commit()
        return jsonify(book.to_dict()), 201
    return jsonify([b.to_dict() for b in Book.query.all()]), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
