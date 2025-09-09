#---------------------------routes.py------------------------
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager
from models import User, Expense, Report
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

main_routes = Blueprint("main", __name__)

# ---------------- Home page ---------------- #
@main_routes.route("/")
def home():
    return redirect(url_for("main.login"))

# ---------------- Register page ---------------- #
@main_routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if User.query.filter_by(email=email).first():
            flash("⚠️ Email already registered!", "danger")
            return redirect(url_for("main.register"))

        hashed_pw = generate_password_hash(password)
        new_user = User(email=email, username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash("✅ Registration successful! Please login.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")

# ---------------- Login Page ---------------- #
@main_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("✅ Login successful!", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("❌ Invalid credentials", "danger")

    return render_template("login.html")

# ---------------- LOGOUT ---------------- #
@main_routes.route("/logout")
@login_required
def logout():
    logout_user()
    flash("✅ Logged out successfully.", "info")
    return redirect(url_for("main.login"))

# ---------------- DASHBOARD - which passes data calulate budget alert,category,etc---------------- #
@main_routes.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    query = Expense.query.filter_by(user_id=current_user.id)

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(Expense.date.between(start, end))
        except:
            flash("Invalid date format!", "danger")

    expenses = query.all()

    total_expenses = sum(exp.amount for exp in expenses)
    categories = [exp.category for exp in expenses]
    amounts = [exp.amount for exp in expenses]
    count = len(expenses)
    alert = total_expenses > current_user.budget

    return render_template(
        "dashboard.html",
        expenses=expenses,
        total_expenses=total_expenses,
        categories=categories,
        amounts=amounts,
        count=count,
        budget=current_user.budget,
        alert=alert,
        start_date=start_date,
        end_date=end_date,
    )
@main_routes.route("/update_budget", methods=["POST"])
@login_required
def update_budget():
    new_budget = request.form.get("budget")
    if new_budget:
        current_user.budget = float(new_budget)
        db.session.commit()
        flash("Budget updated successfully!", "success")
    return redirect(url_for("main.dashboard"))


# ---------------- ADD EXPENSE by which we add expemses ---------------- #
@main_routes.route("/add_expense", methods=["GET", "POST"])
@login_required
def add_expense():
    if request.method == "POST":
        title = request.form.get("title")
        amount = float(request.form.get("amount"))
        category = request.form.get("category")
        date = datetime.strptime(request.form.get("date"), "%Y-%m-%d")

        new_expense = Expense(
            title=title,
            amount=amount,
            category=category,
            date=date,
            user_id=current_user.id
        )
        db.session.add(new_expense)
        db.session.commit()

        flash("💰 Expense added!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("add_expense.html")

# ---------------- EDIT through editing of expense is done ---------------- #
@main_routes.route("/edit_expense/<int:expense_id>", methods=["GET", "POST"])
@login_required
def edit_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)

    if expense.user_id != current_user.id:
        flash("❌ Not authorized!", "danger")
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        expense.title = request.form.get("title")
        expense.category = request.form.get("category")
        expense.amount = float(request.form.get("amount"))
        expense.date = datetime.strptime(request.form.get("date"), "%Y-%m-%d")
        db.session.commit()
        flash("✏️ Expense updated!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("edit_expense.html", expense=expense)

# ---------------- VIEW EXPENSES- through which we can see all the expense ---------------- #
@main_routes.route("/view_expenses")
@login_required
def view_expenses():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    total = sum(e.amount for e in expenses)
    return render_template("view_expenses.html", expenses=expenses, total=total)

# ---------------- DELETE EXPENSE ---------------- #
@main_routes.route("/delete_expense/<int:expense_id>")
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)

    if expense.user_id != current_user.id:
        flash("❌ You are not authorized to delete this expense.", "danger")
        return redirect(url_for("main.dashboard"))

    db.session.delete(expense)
    db.session.commit()
    flash("🗑️ Expense deleted successfully!", "success")
    return redirect(url_for("main.dashboard"))

# ---------------- SET BUDGET- for setting alert  ---------------- #
@main_routes.route("/set_budget", methods=["POST"])
@login_required
def set_budget():
    budget = float(request.form.get("budget"))
    current_user.budget = budget
    db.session.commit()
    flash(f"📊 Monthly budget set to ₹{budget}", "success")
    return redirect(url_for("main.dashboard"))

# ---------------- EXPORT CSV ---------------- #
@main_routes.route("/export_csv")
@login_required
def export_csv():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    df = pd.DataFrame([(e.title, e.amount, e.category, e.date) for e in expenses],
                      columns=["Title", "Amount", "Category", "Date"])

    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return send_file(output, mimetype="text/csv",
                     download_name="expenses.csv", as_attachment=True)

# ---------------- EXPORT EXCEL ---------------- #
@main_routes.route("/export_excel")
@login_required
def export_excel():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    df = pd.DataFrame([(e.title, e.amount, e.category, e.date) for e in expenses],
                      columns=["Title", "Amount", "Category", "Date"])

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Expenses", index=False)
    output.seek(0)

    return send_file(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     download_name="expenses.xlsx", as_attachment=True)

# ---------------- UPLOAD CSV ---------------- #
@main_routes.route("/upload_csv", methods=["GET", "POST"])
@login_required
def upload_csv():
    if request.method == "POST":
        file = request.files["file"]
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file)

            for _, row in df.iterrows():
                expense = Expense(
                    title=row.get("Title", ""),
                    category=row.get("Category", "Misc"),
                    amount=float(row["Amount"]),
                    date=pd.to_datetime(row["Date"]).date(),
                    user_id=current_user.id
                )
                db.session.add(expense)
            db.session.commit()

            flash("📤 CSV uploaded successfully!", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("⚠️ Please upload a valid CSV file.", "danger")

    return render_template("upload.html")
