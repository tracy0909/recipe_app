# recipes/forms.py
from wtforms import Form, StringField, IntegerField, TextAreaField, validators

class RecipeForm(Form):
    name = StringField("食譜名稱", [validators.DataRequired(), validators.Length(max=120)])
    description = TextAreaField("敘述", [validators.Optional()])
    cook_time_min = IntegerField("料理時間(分鐘)", [validators.DataRequired()])
    category = StringField("分類名稱", [validators.DataRequired(), validators.Length(max=80)])
    image_url = StringField("封面圖片 URL", [validators.Optional(), validators.Length(max=255)])

    # 簡易輸入：每行一個步驟
    steps_text = TextAreaField("步驟（每行一個）", [validators.Optional()])

    # 簡易輸入：每行 `食材,數量,單位` 例如：`蛋,2,顆`
    ingredients_text = TextAreaField("食材（每行：名稱,數量,單位）", [validators.Optional()])
