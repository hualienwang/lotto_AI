from flask import Blueprint, render_template

page_bp = Blueprint('pages', __name__)


@page_bp.route('/')
def index():
    return render_template('index.html')


@page_bp.route('/history.html')
def history_page():
    return render_template('history.html')


@page_bp.route('/predict.html')
def predict_page():
    return render_template('predict.html')


@page_bp.route('/manual.html')
def manual_page():
    return render_template('manual.html')


@page_bp.route('/pridict.html')
def predict_typo():
    from flask import redirect
    return redirect('/predict.html', code=302)
