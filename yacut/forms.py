from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from . import constants as c


class URLForm(FlaskForm):
    original_link = URLField(
        "Длинная ссылка",
        validators=[Length(1, 256), DataRequired(message="Обязательное поле")],
    )
    custom_id = StringField(
        "Ваш вариант короткой ссылки",
        validators=[
            Length(1, c.MANUAL_LINK_MAX_SIZE),
            Regexp(c.AUTO_LINK_PATTERN, message="Только латинские буквы и цифры"),
            Optional(),
        ],
    )
    submit = SubmitField("Создать")
