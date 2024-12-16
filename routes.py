# Standard Library imports

# Core Flask imports
from flask import Blueprint, render_template, request, jsonify, redirect, url_for

# Third-party imports

# App imports
from app import db_manager
from app import login_manager
from .views import (
    error_views,
    account_management_views,
    static_views,
)
from .models import User

bp = Blueprint('routes', __name__)

# alias
db = db_manager.session

# Request management
@bp.before_app_request
def before_request():
    db()

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, validators, SelectMultipleField
from flask_wtf.file import FileField
from app.models import Parent

class TextForm(FlaskForm):
    field1 = StringField('Field1', [
        validators.DataRequired(),
        validators.Length(max=30),
        validators.Regexp(r'^[a-zA-Z0-9 ]*$', message="Only ASCII characters without punctuation are allowed.")
    ])
    field2 = StringField('Field2', [
        validators.DataRequired(),
        validators.Length(max=30),
        validators.Regexp(r'^[a-zA-Z0-9 ]*$', message="Only ASCII characters without punctuation are allowed.")
    ])

class DeleteUsersForm(FlaskForm):
    users = SelectMultipleField('Select Users to Delete', coerce=int)

@bp.route('/formular', methods=['GET', 'POST'])
def formular():
    form = TextForm()
    if form.validate_on_submit(): 
        new_parent = Parent(name=form.field1.data)
        db.add(new_parent)
        db.commit()
        return 'Success'
    return render_template('formular.html', form=form)

@bp.route('/delete_parents', methods=['GET', 'POST'])
def delete_parents():
    """
    Renders a form to select and delete a parent by ID and processes the deletion request.
    """
    parents = Parent.query.all()  # Get all parents
 
    if request.method == 'POST':
        parent_id = request.form.get('parent_id', type=int)  # Ensure parent_id is integer
        if not parent_id:
            return {"error": "Parent ID is required"}, 400
 
        parent = Parent.query.get(parent_id)
        if not parent:
            return {"error": "Parent not found"}, 404
 
        try:
            db.delete(parent)
            db.commit()
            return {"message": "Parent deleted successfully"}, 200
        except Exception as e:
            db.rollback()
            return {"error": "An error occurred while deleting the parent", "details": str(e)}, 500
 
    return render_template('delete_parents.html', parents=parents)

@bp.route('/delete/<int:item_id>', methods=['GET','DELETE'])
def delete_item(item_id):
    item = db.query.get(item_id)  # Nahraďte správným modelem
    if not item:
        return 'Item not found', 404
    db.session.delete(item)
    db.session.commit()
    return 'Item deleted'

@bp.teardown_app_request
def shutdown_session(response_or_exc):
    db.remove()

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    if user_id and user_id != "None":
        return User.query.filter_by(user_id=user_id).first()

# Error views
bp.register_error_handler(404, error_views.not_found_error)

bp.register_error_handler(500, error_views.internal_error)

# Public views
bp.add_url_rule("/", view_func=static_views.index)

bp.add_url_rule("/register", view_func=static_views.register)

bp.add_url_rule("/test", view_func=static_views.test)


bp.add_url_rule("/login", view_func=static_views.login)

# Login required views
bp.add_url_rule("/settings", view_func=static_views.settings)

# Public API
bp.add_url_rule(
   "/api/login", view_func=account_management_views.login_account, methods=["POST"]
)

bp.add_url_rule("/logout", view_func=account_management_views.logout_account)

bp.add_url_rule(
   "/api/register",
   view_func=account_management_views.register_account,
   methods=["POST"],
)

# Login Required API
bp.add_url_rule("/api/user", view_func=account_management_views.user)

bp.add_url_rule(
   "/api/email", view_func=account_management_views.email, methods=["POST"]
)

# Admin required
bp.add_url_rule("/admin", view_func=static_views.admin)
