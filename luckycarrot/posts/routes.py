from flask import (render_template, url_for, flash, redirect, request,
                    abort, Blueprint)
from flask_login import current_user, login_required
from luckycarrot import db
from luckycarrot.models import Post
from luckycarrot.posts.forms import PostForm
from luckycarrot.posts.utils import save_post_picture

posts = Blueprint('posts', __name__)


@posts.route("/blog", methods=['GET', 'POST'])
def blog():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('blog.html', posts=posts)


@posts.route('/blog/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)

    return render_template('post.html', post=post)


@posts.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()

    if not current_user.admin_user:
        return redirect(url_for('main.home'))
    
    if form.validate_on_submit():

        if not form.picture.data:
            flash('Error in creating post. Please upload a picture.', 'danger')
            return redirect(url_for('posts.create_post'))

        image = save_post_picture(form.picture.data)
        post = Post(title=form.title.data, content=form.content.data, image_file=image, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Success! Post Created!', 'success')
        return redirect(url_for('posts.blog'))

    return render_template('create_post.html', form=form, legend="Create New Post")


@posts.route('/blog/<int:post_id>/update', methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author != current_user:
        abort(403)

    form = PostForm()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_post_picture(form.picture.data, post, True)
            post.image_file = picture_file

        post.title = form.title.data 
        post.content = form.content.data 
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))

    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content 


    return render_template('update_post.html', form=form, legend="Update Post")


@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)

    db.session.delete(post)
    db.session.commit()

    flash('Post has been deleted.', 'success')
    return redirect(url_for('posts.blog'))