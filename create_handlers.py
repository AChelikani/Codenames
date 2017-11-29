from flask import Blueprint, render_template, abort, session, request
from game_store import game_store

create = Blueprint('create', __name__, template_folder='templates')

@create.route('/create')
def create_game():
    # TODO: Note that going on the create page and refreshing results in many games being
    # added to the active games dict, which is not desired. Unclear on a resolution
    # for this issue yet.
    new_code = game_store.create_game()
    return render_template('create.html', game_code=new_code)

@create.route('/join')
def join_game():
    return render_template('join.html', error_text="")
