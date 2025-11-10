# seed.py
from app import create_app
from extensions import db
from models import User, Category, Ingredient, Recipe, CookInstruction, Review, Need

app = create_app()
with app.app_context():
    # 使用者
    u = User.query.filter_by(username="sam").first()
    if not u:
        u = User(username="sam", email="sam@example.com")
        u.set_password("secret")
        db.session.add(u)

    # 分類與食材（避免重複）
    cat = Category.query.filter_by(name="主食").first()
    if not cat:
        cat = Category(name="主食")
        db.session.add(cat)

    egg = Ingredient.query.filter_by(name="蛋").first()
    if not egg:
        egg = Ingredient(name="蛋", is_allergen=True)
        db.session.add(egg)

    milk = Ingredient.query.filter_by(name="牛奶").first()
    if not milk:
        milk = Ingredient(name="牛奶", is_allergen=True)
        db.session.add(milk)

    db.session.commit()

    # 食譜
    r = Recipe.query.filter_by(name="法式吐司").first()
    if not r:
        r = Recipe(
            name="法式吐司",
            description="早餐經典",
            cook_time_min=10,
            author=u,
            category=cat
        )
        db.session.add(r)
        db.session.commit()

        # 步驟
        r.steps.extend([
            CookInstruction(step="打散雞蛋", recipe=r),
            CookInstruction(step="吐司兩面沾蛋液", recipe=r),
        ])

        # 用量（Need）
        db.session.add_all([
            Need(recipe_id=r.id, ingredient_id=egg.id, quantity=2, unit="顆"),
            Need(recipe_id=r.id, ingredient_id=milk.id, quantity=50, unit="ml"),
        ])

        # 評論
        db.session.add(Review(recipe=r, user=u, rating=5, comment="超好吃！"))

        db.session.commit()

    print("Seeding done. Recipe count =", Recipe.query.count())
