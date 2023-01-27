from random import sample
import string
from flask import abort, flash, redirect, render_template, url_for

from . import app, db
from .forms import URLForm
from .models import URLMap

"""
def random_opinion():
    quantity = Opinion.query.count()
    if quantity:
        offset_value = randrange(quantity)
        opinion = Opinion.query.offset(offset_value).first()
        return opinion


@app.route('/')
def index_view():
    opinion = random_opinion()
    if opinion is not None:
        return render_template('opinion.html', opinion=opinion)
    abort(404)
"""


def get_unique_short_id(length):

    letters = string.digits + string.ascii_letters
    fetch = "".join(sample(letters, length))
    if URLMap.query.filter_by(short=fetch).first():
        get_unique_short_id(length)
    return fetch


@app.route("/", methods=["GET", "POST"])
def add_link_view():
    form = URLForm()

    if form.validate_on_submit():
        original = form.original_link.data

        if form.custom_id.data:
            short = form.custom_id.data
            if URLMap.query.filter_by(short=short).first():
                return render_template(
                    "make_url.html", form=form, mess=f"Имя {short} уже занято!"
                )
        else:
            short = get_unique_short_id(6)
        urls = URLMap(original=original, short=short)

        if URLMap.query.filter_by(original=original).first():
            show_url = (
                url_for("add_link_view", _external=True)
                + URLMap.query.filter_by(original=original).first().short
            )
            return render_template(
                "make_url.html",
                form=form,
                mess="Такая ссылка уже была обработана ранее:",
                show_url=show_url,
            )

        db.session.add(urls)
        db.session.commit()
        return render_template(
            "make_url.html",
            form=form,
            mess="Ваша новая ссылка готова:",
            show_url=url_for("add_link_view", _external=True) + short,
        )

    return render_template("make_url.html", form=form)


@app.route("/<id>")
def url_redirect(id):
    get_url = URLMap.query.filter_by(short=id).first()
    if get_url:
        return redirect(get_url.original)
    abort(404)
