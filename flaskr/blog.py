'''
INF601 - Advanced Programming in Python
Assignment: Mini Project 3
I,     Levi Eck    , affirm that the work submitted for this assignment is entirely my own. I have not engaged in any form of academic dishonesty, including but not limited to cheating, plagiarism, or the use of unauthorized materials. I have neither provided nor received unauthorized assistance and have accurately cited all sources in adherence to academic standards. I understand that failing to comply with this integrity statement may result in consequences, including disciplinary actions as determined by my course instructor and outlined in institutional policies. By signing this statement, I acknowledge my commitment to upholding the principles of academic integrity.
'''


from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

from datetime import datetime
import os

bp = Blueprint('blog', __name__)

#THIS IS FOR IMAGE HANDLING
#DEFINES UPLOAD FOLDER
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'flaskr/static/uploads')

#CHECKS IF FOLDER EXISTS, IF NOT, CREATES IT
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)



#INDEX
@bp.route('/')
def index():
    if g.user is None:
        return redirect(url_for('auth.login'))
    db = get_db()
    posts = db.execute(
        '''SELECT p.id, p.title, p.publisher, p.release, p.image_filename, p.author_id, p.created
           FROM post p
           WHERE p.author_id = ?
           ORDER BY p.created DESC''',
        (g.user['id'],)
    ).fetchall()

    return render_template('blog/index.html', posts=posts)

#INDEX 2
@bp.route('/index_pub')
def index_pub():
    db = get_db()
    #ORDER TESTING
    posts = db.execute(
        '''SELECT p.id, p.title, p.publisher, p.release, p.image_filename, p.author_id, p.created
           FROM post p
           WHERE p.author_id = ?
           ORDER BY publisher DESC''',
        (g.user['id'],)
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

#CREATE
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        publisher = request.form['publisher']
        release = request.form.get('release')
        image = request.files.get('photo')


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

            #PHOTO STUFF
            image_filename = None
            if not image:
                print("no image found")
            if image:
                print(f"Image detected: {image.filename}")
                if image.filename != '':
                    image_filename = image.filename
                    image_path = os.path.join(UPLOAD_FOLDER, image_filename)
                    image.save(image_path)  # Save image file


            #BACK TO OLD STUFF
            db.execute(
                'INSERT INTO post (title, publisher, release, image_filename, author_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (title, publisher, release, image_filename, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

#UPDATE
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, publisher, release, image_filename, created, author_id, username'
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
        release = request.form.get('release')
        image = request.files.get('photo')

        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()

            # PHOTO STUFF
            image_filename = None
            if not image:
                print("no image found")
            if image:
                print(f"Image detected: {image.filename}")
                if image.filename != '':
                    image_filename = image.filename
                    image_path = os.path.join(UPLOAD_FOLDER, image_filename)
                    image.save(image_path)  # Save image file

            db.execute(
                'UPDATE post SET title = ?, publisher = ?, release = ?, image_filename = ?'
                ' WHERE id = ?',
                (title, publisher, release, image_filename, id)
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