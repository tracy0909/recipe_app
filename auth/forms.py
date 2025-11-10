from wtforms import Form, StringField, PasswordField, validators

class LoginForm(Form):
    username = StringField("使用者名稱", [validators.DataRequired()])
    password = PasswordField("密碼", [validators.DataRequired()])

class RegisterForm(Form):
    username = StringField("使用者名稱", [validators.DataRequired(), validators.Length(min=3, max=80)])
    email = StringField("Email", [validators.DataRequired(), validators.Email()])
    password = PasswordField("密碼", [
        validators.DataRequired(),
        validators.Length(min=6),
    ])
