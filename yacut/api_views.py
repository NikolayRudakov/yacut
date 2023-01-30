import re

from flask import jsonify, request, url_for
from http import HTTPStatus as st

from . import app, db
from . import constants as c
from .models import URLMap
from .views import get_unique_short_id
from .error_handlers import InvalidAPIUsage


@app.route("/api/id/<short_id>/", methods=["GET"])
def get_url(short_id):
    get_url = URLMap.query.filter_by(short=short_id).first()
    if get_url is None:
        raise InvalidAPIUsage("Указанный id не найден", st.NOT_FOUND)
    return jsonify({"url": get_url.original}), st.OK


@app.route("/api/id/", methods=["POST"])
def add_url():
    data = request.get_json()
    if not data:
        raise InvalidAPIUsage("Отсутствует тело запроса")
    if "url" not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')
    if "custom_id" not in data or data["custom_id"] is None:
        data["custom_id"] = get_unique_short_id(c.AUTO_LINK_SIZE)
    if len(data["custom_id"]) < 1:
        data["custom_id"] = get_unique_short_id(c.AUTO_LINK_SIZE)
    if len(data["custom_id"]) > c.MANUAL_LINK_MAX_SIZE:
        raise InvalidAPIUsage("Указано недопустимое имя для короткой ссылки")
    if not re.fullmatch(c.AUTO_LINK_PATTERN, data["custom_id"]):
        raise InvalidAPIUsage("Указано недопустимое имя для короткой ссылки")
    if URLMap.query.filter_by(short=data["custom_id"]).first() is not None:
        short_link = data["custom_id"]
        raise InvalidAPIUsage(f'Имя "{short_link}" уже занято.')
    if URLMap.query.filter_by(original=data["url"]).first() is not None:
        raise InvalidAPIUsage("Такая ссылка уже есть в базе данных!")
    urlmap = URLMap()
    urlmap.from_dict(data)
    db.session.add(urlmap)
    db.session.commit()
    short_link = url_for("add_link_view", _external=True) + urlmap.short

    return jsonify({"short_link": short_link, "url": urlmap.original}), st.CREATED
