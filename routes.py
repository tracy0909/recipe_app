# routes.py
# CHANGE: 在 dashboard 顯示最近食譜
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Recipe  

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    recipes = Recipe.query.order_by(Recipe.created_at.desc()).limit(8).all()  
    return render_template("dashboard.html", user=current_user, recipes=recipes)  

