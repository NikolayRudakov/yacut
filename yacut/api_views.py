import re
from flask import jsonify, request, url_for
from . import app, db
from .models import URLMap
from .views import get_unique_short_id
from .error_handlers import InvalidAPIUsage


@app.route("/api/id/<short_id>/", methods=["GET"])
def get_url(short_id):
    get_url = URLMap.query.filter_by(short=short_id).first()
    if get_url is None:
        raise InvalidAPIUsage("Указанный id не найден", 404)
    return jsonify({"url": get_url.original}), 200


@app.route("/api/id/", methods=["POST"])
def add_url():
    data = request.get_json()
    if not data:
        raise InvalidAPIUsage("Отсутствует тело запроса")
    if "url" not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')
    if "custom_id" not in data or data["custom_id"] is None:
        data["custom_id"] = get_unique_short_id(6)
    if len(data["custom_id"]) < 1:
        data["custom_id"] = get_unique_short_id(6)
    if len(data["custom_id"]) > 16:
        raise InvalidAPIUsage("Указано недопустимое имя для короткой ссылки")
    if not re.fullmatch(r"[a-zA-Z0-9]+", data["custom_id"]):
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

    return jsonify({"short_link": short_link, "url": urlmap.original}), 201


"""
@app.route('/api/opinions/<int:id>/', methods=['PATCH'])
def update_opinion(id):
    data = request.get_json()
    if (
        'text' in data and
        Opinion.query.filter_by(text=data['text']).first() is not None
    ):
        raise InvalidAPIUsage('Такое мнение уже есть в базе данных')
    opinion = Opinion.query.get(id)
    # Тут код ответа нужно указать явным образом
    if opinion is None:
        raise InvalidAPIUsage('Мнение с указанным id не найдено', 404)
    opinion.title = data.get('title', opinion.title)
    opinion.text = data.get('text', opinion.text)
    opinion.source = data.get('source', opinion.source)
    opinion.added_by = data.get('added_by', opinion.added_by)
    db.session.commit()
    return jsonify({'opinion': opinion.to_dict()}), 201

@app.route('/api/opinions/<int:id>/', methods=['DELETE'])
def delete_opinion(id):
    opinion = Opinion.query.get(id)
    if opinion is None:
        # Тут код ответа нужно указать явным образом
        raise InvalidAPIUsage('Мнение с указанным id не найдено', 404)
    db.session.delete(opinion)
    db.session.commit()
    return '', 204

@app.route('/api/opinions/', methods=['GET'])
def get_opinions():
    opinions = Opinion.query.all()
    opinions_list = [opinion.to_dict() for opinion in opinions]
    return jsonify({'opinions': opinions_list}), 200

@app.route('/api/opinions/', methods=['POST'])
def add_opinion():
    data = request.get_json()
    if 'title' not in data or 'text' not in data:
        raise InvalidAPIUsage('В запросе отсутствуют обязательные поля')
    if Opinion.query.filter_by(text=data['text']).first() is not None:
        raise InvalidAPIUsage('Такое мнение уже есть в базе данных')
    opinion = Opinion()
    opinion.from_dict(data)
    db.session.add(opinion)
    db.session.commit()
    return jsonify({'opinion': opinion.to_dict()}), 201

@app.route('/api/get-random-opinion/', methods=['GET'])
def get_random_opinion():
    opinion = random_opinion()
    if opinion is not None:
        return jsonify({'opinion': opinion.to_dict()}), 200
    raise InvalidAPIUsage('В базе данных нет мнений', 404)
"""
