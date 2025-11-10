from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db, login_manager


# 中介表 Need：食譜與食材多對多，附帶 quantity/unit
class Need(db.Model):
    __tablename__ = "need"
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredient.id"), primary_key=True)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(32), nullable=False)
    # 輔助唯一鍵已由複合主鍵涵蓋（recipe_id, ingredient_id）


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    recipes = db.relationship("Recipe", back_populates="author", cascade="all, delete-orphan")
    reviews = db.relationship("Review", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    recipes = db.relationship("Recipe", back_populates="category")


class Ingredient(db.Model):
    __tablename__ = "ingredient"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    is_allergen = db.Column(db.Boolean, default=False, nullable=False)

    recipes = db.relationship(
        "Recipe",
        secondary="need",
        back_populates="ingredients",
    )


class Recipe(db.Model):
    __tablename__ = "recipe"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    cook_time_min = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    cate_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)

    author = db.relationship("User", back_populates="recipes")
    category = db.relationship("Category", back_populates="recipes")

    steps = db.relationship("CookInstruction", back_populates="recipe", cascade="all, delete-orphan", order_by="CookInstruction.id")
    ingredients = db.relationship("Ingredient", secondary="need", back_populates="recipes")
    reviews = db.relationship("Review", back_populates="recipe", cascade="all, delete-orphan")
    image_url = db.Column(db.String(255))  


class CookInstruction(db.Model):
    __tablename__ = "cook_instruction"
    id = db.Column(db.Integer, primary_key=True)
    step = db.Column(db.Text, nullable=False)  # 文字內容
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), nullable=False)

    recipe = db.relationship("Recipe", back_populates="steps")


class Review(db.Model):
    __tablename__ = "review"
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    comment = db.Column(db.Text)
    rating = db.Column(db.Integer, nullable=False)

    recipe = db.relationship("Recipe", back_populates="reviews")
    user = db.relationship("User", back_populates="reviews")

    __table_args__ = (
        db.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating_range"),
    )
