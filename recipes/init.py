# recipes/__init__.py
from flask import Blueprint

recipes_bp = Blueprint("recipes", __name__, template_folder="../templates/recipes")

from . import routes 
