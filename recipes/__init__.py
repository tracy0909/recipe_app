from flask import Blueprint

recipes_bp = Blueprint("recipes", __name__, template_folder="../templates/recipes")

from . import routes  # keep this last to avoid circular imports
