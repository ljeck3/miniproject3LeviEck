from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

from datetime import datetime

bp = Blueprint('blog', __name__)

#INDEX
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, publisher, release, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

#CREATE
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        publisher = request.form['publisher']
        release = request.form.get('release')  # Get date input
        #image = request.files.get('photo')  # Get uploaded image

        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()

            #NEW STUFF

            #CONVERT DATE FROM STRING TO PROPER FORMAT
            if release:
                release = datetime.strptime(release, "%Y-%m-%d").date()


            #BACK TO OLD STUFF
            db.execute(
                'INSERT INTO post (title, publisher, release,  author_id)'
                ' VALUES (?, ?, ?, ?)',
                (title, publisher, release, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

#UPDATE
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, publisher, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

#UPDATE PART 2 I THINK
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        publisher = request.form['publisher']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, publisher = ?'
                ' WHERE id = ?',
                (title, publisher, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

#DELETE
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))