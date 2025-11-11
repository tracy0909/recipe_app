"""init models

Revision ID: 8f163e897934
Revises: 
Create Date: 2025-11-06 18:32:49.183402
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "8f163e897934"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # --- Category ---
    op.create_table(
        "category",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False, unique=True),
    )

    # --- Ingredient ---
    op.create_table(
        "ingredient",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("is_allergen", sa.Boolean(), nullable=False),
    )

    # --- User ---
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False, unique=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
    )

    # --- Recipe ---
    op.create_table(
        "recipe",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("cook_time_min", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("cate_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["cate_id"], ["category.id"]),
    )

    # --- CookInstruction ---
    op.create_table(
        "cook_instruction",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("step", sa.Text(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipe.id"]),
    )

    # --- Need (recipe <-> ingredient, with quantity/unit) ---
    op.create_table(
        "need",
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("ingredient_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipe.id"]),
        sa.ForeignKeyConstraint(["ingredient_id"], ["ingredient.id"]),
        sa.PrimaryKeyConstraint("recipe_id", "ingredient_id"),
    )

    # --- Review ---
    op.create_table(
        "review",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "rating >= 1 AND rating <= 5", name="ck_review_rating_range"
        ),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipe.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
    )


def downgrade():
    # 反向順序刪除本遷移建立的表
    op.drop_table("review")
    op.drop_table("need")
    op.drop_table("cook_instruction")
    op.drop_table("recipe")
    op.drop_table("user")
    op.drop_table("ingredient")
    op.drop_table("category")
