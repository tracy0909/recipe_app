# recipes/routes.py
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from . import recipes_bp                     # Blueprint 由 recipes/__init__.py 建立 
from .forms import RecipeForm                # 表單（名稱需與 templates 對應）         
from extensions import db
from models import (
    Recipe, Category, Ingredient, CookInstruction, Review, Need
)

# =========================
# 食譜清單 + 篩選
# =========================
@recipes_bp.route('/')
def index():
    q = (request.args.get('q') or '').strip()
    category_id = request.args.get('category_id', type=int)
    allergen_id = request.args.get('allergen_id', type=int)  # 新增過敏原篩選

    # 抓出所有分類、過敏原資料
    categories = (
        db.session.query(
            Category,
            db.func.count(Recipe.id).label('recipe_count')
        )
        .outerjoin(Recipe, Recipe.cate_id == Category.id)
        .group_by(Category.id)
        .order_by(Category.id)
        .all()
    )

    allergens = Ingredient.query.filter_by(is_allergen=True).order_by(Ingredient.id).all()

    # 建立查詢
    query = Recipe.query

    # 關鍵字搜尋
    if q:
        like = f"%{q}%"
        query = query.filter(
            (Recipe.name.ilike(like)) |
            (Recipe.description.ilike(like))
        )

    # 分類篩選
    current_category = None
    if category_id:
        query = query.filter_by(cate_id=category_id)
        current_category = Category.query.get(category_id)

    # 過敏原篩選（排除含有該過敏原的食譜）
    if allergen_id:
        query = query.filter(
            ~Recipe.id.in_(
                db.session.query(Need.recipe_id)
                .filter(Need.ingredient_id == allergen_id)
            )
        )

    # 取得結果
    recipes = query.order_by(Recipe.created_at.desc()).all()

    return render_template(
        'recipes/index.html',
        recipes=recipes,
        categories=categories,
        allergens=allergens,
        current_category=current_category,
        q=q,
        selected_category_id=category_id,
        selected_allergen_id=allergen_id
    )


# =========================
# 新增食譜
# =========================
@recipes_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    form = RecipeForm(request.form)
    if request.method == "POST" and form.validate():
        try:
            # 1) 分類（若不存在自動建立） 
            cate = Category.query.filter(
                func.lower(Category.name) == func.lower(form.category.data)
            ).first()
            if not cate:
                cate = Category(name=form.category.data)
                db.session.add(cate)
                db.session.flush()

            # 2) 食譜本體 
            r = Recipe(
                name=form.name.data,
                description=form.description.data,
                cook_time_min=form.cook_time_min.data or 0,
                category=cate,
                author=current_user,
                image_url=form.image_url.data or None,
            )
            db.session.add(r)
            db.session.flush()  # 取得 r.id

            # 3) 步驟（每行一筆） 
            steps = [s.strip() for s in (form.steps_text.data or "").splitlines() if s.strip()]
            for s in steps:
                db.session.add(CookInstruction(step=s, recipe=r))

            # 4) 食材 + 用量（Need） 
            ing_lines = [ln.strip() for ln in (form.ingredients_text.data or "").splitlines() if ln.strip()]
            for ln in ing_lines:
                parts = [p.strip() for p in ln.split(",")]
                if len(parts) < 3:
                    continue  # 不合法的行就略過
                name, qty, unit = parts[0], parts[1], parts[2]
                try:
                    qty_val = float(qty)
                except ValueError:
                    qty_val = 0
                ing = Ingredient.query.filter(
                    func.lower(Ingredient.name) == func.lower(name)
                ).first()
                if not ing:
                    ing = Ingredient(name=name)
                    db.session.add(ing)
                    db.session.flush()
                db.session.add(Need(
                    recipe_id=r.id, ingredient_id=ing.id,
                    quantity=qty_val, unit=unit
                ))

            # 5) 一次提交 
            db.session.commit()
            flash("已新增食譜", "success")
            return redirect(url_for("recipes.show", rid=r.id))

        except SQLAlchemyError:
            db.session.rollback()
            flash("儲存失敗，請檢查欄位格式。", "danger")

    return render_template("recipes/new.html", form=form)


# =========================
# 食譜詳細頁（含用量顯示）
# =========================
# @recipes_bp.route("/<int:rid>")
# def show(rid: int):
#     r = Recipe.query.get_or_404(rid)
#     # 連 Need + Ingredient 以顯示數量/單位 
#     needs = (
#         db.session.query(Need, Ingredient)
#         .join(Ingredient, Need.ingredient_id == Ingredient.id)
#         .filter(Need.recipe_id == r.id)
#         .all()
#     )
#     return render_template("recipes/show.html", r=r, needs=needs)


# =========================
# 編輯食譜
# =========================
@recipes_bp.route("/<int:rid>/edit", methods=["GET", "POST"])
@login_required
def edit(rid: int):
    r = Recipe.query.get_or_404(rid)
    form = RecipeForm(request.form if request.method == "POST" else None)

    if request.method == "POST" and form.validate():
        try:
            # 分類（若不存在自動建立） 
            cate = Category.query.filter(
                func.lower(Category.name) == func.lower(form.category.data)
            ).first()
            if not cate:
                cate = Category(name=form.category.data)
                db.session.add(cate)
                db.session.flush()

            # 更新食譜本體 // CHANGE
            r.name = form.name.data
            r.description = form.description.data
            r.cook_time_min = form.cook_time_min.data or 0
            r.category = cate
            r.image_url = form.image_url.data or None

            # 先清空舊步驟與 Need，再重建（簡化流程） // CHANGE
            CookInstruction.query.filter_by(recipe_id=r.id).delete()
            db.session.query(Need).filter_by(recipe_id=r.id).delete()

            # 重建步驟 
            steps = [s.strip() for s in (form.steps_text.data or "").splitlines() if s.strip()]
            for s in steps:
                db.session.add(CookInstruction(step=s, recipe=r))

            db.session.flush()
            db.session.query(CookInstruction).filter_by(recipe_id=r.id).delete()
            for s in steps:
                db.session.add(CookInstruction(step=s, recipe=r))

            # 重建 Need 
            ing_lines = [ln.strip() for ln in (form.ingredients_text.data or "").splitlines() if ln.strip()]
            for ln in ing_lines:
                parts = [p.strip() for p in ln.split(",")]
                if len(parts) < 3:
                    continue
                name, qty, unit = parts[0], parts[1], parts[2]
                try:
                    qty_val = float(qty)
                except ValueError:
                    qty_val = 0
                ing = Ingredient.query.filter(
                    func.lower(Ingredient.name) == func.lower(name)
                ).first()
                if not ing:
                    ing = Ingredient(name=name)
                    db.session.add(ing)
                    db.session.flush()
                db.session.add(Need(
                    recipe_id=r.id, ingredient_id=ing.id,
                    quantity=qty_val, unit=unit
                ))

            db.session.commit()
            flash("已更新食譜", "success")
            return redirect(url_for("recipes.show", rid=r.id))

        except SQLAlchemyError:
            db.session.rollback()
            flash("更新失敗，請稍後再試。", "danger")

    # GET：把現有資料回填到表單文字區 
    if request.method == "GET":
        form.name.data = r.name
        form.description.data = r.description
        form.cook_time_min.data = r.cook_time_min
        form.category.data = r.category.name if r.category else ""
        form.image_url.data = r.image_url or ""
        form.steps_text.data = "\n".join(s.step for s in r.steps)

        current_needs = (
            db.session.query(Need, Ingredient)
            .join(Ingredient, Need.ingredient_id == Ingredient.id)
            .filter(Need.recipe_id == r.id)
            .all()
        )
        form.ingredients_text.data = "\n".join(
            f"{ing.name},{need.quantity},{need.unit}"
            for need, ing in current_needs
        )

    return render_template("recipes/edit.html", form=form, r=r)


# =========================
# 刪除食譜
# =========================
@recipes_bp.route("/<int:rid>/delete", methods=["POST"])
@login_required
def delete(rid: int):
    r = Recipe.query.get_or_404(rid)
    db.session.delete(r)
    db.session.commit()
    flash("已刪除食譜", "info")
    return redirect(url_for("recipes.index"))

# =========================
# 顯示評論
# =========================
@recipes_bp.route("/<int:rid>")
def show(rid: int):
    r = Recipe.query.get_or_404(rid)
    # 連 Need + Ingredient 以顯示數量/單位 
    needs = (
        db.session.query(Need, Ingredient)
        .join(Ingredient, Need.ingredient_id == Ingredient.id)
        .filter(Need.recipe_id == r.id)
        .all()
    )

    # ---- 顯示評論：清單、統計（平均分數與筆數） ----
    reviews = (
        Review.query
        .filter(Review.recipe_id == r.id)
        .order_by(Review.rating.desc())
        .all()
    )
    review_count, avg_rating = db.session.query(
        func.count(Review.id),
        func.coalesce(func.avg(Review.rating), 0.0)
    ).filter(Review.recipe_id == r.id).first()

    return render_template(
        "recipes/show.html",
        r=r, needs=needs,
        reviews=reviews,
        review_count=review_count,
        avg_rating=round(float(avg_rating), 2)  # 例如 4.35
    )
# =========================
# 新增評論
# =========================

@recipes_bp.route("/<int:rid>/reviews", methods=["POST"])
@login_required
def add_or_update_review(rid: int):
    r = Recipe.query.get_or_404(rid)
    rating = request.form.get("rating", type=int)
    comment = request.form.get("comment", "").strip()

    if rating is None or rating < 1 or rating > 5:
        flash("評分必須介於 1 到 5 之間。", "danger")
        return redirect(url_for("recipes.show", rid=rid))

    # 檢查是否已有評論
    existing_review = Review.query.filter_by(
        recipe_id=r.id,
        user_id=current_user.id
    ).first()

    if existing_review:
        # 更新評論
        existing_review.rating = rating
        existing_review.comment = comment
        flash("已更新您的評論。", "success")
    else:
        # 新增評論
        new_review = Review(
            recipe_id=r.id,
            user_id=current_user.id,
            rating=rating,
            comment=comment
        )
        db.session.add(new_review)
        flash("已新增您的評論。", "success")

    db.session.commit()
    return redirect(url_for("recipes.show", rid=rid))