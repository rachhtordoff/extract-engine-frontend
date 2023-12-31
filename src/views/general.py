from flask import request, Blueprint, Response, current_app, render_template
from src import app
import json

general = Blueprint('general', __name__)


@general.route("/health")
def check_status():
    return Response(response=json.dumps({
        "app": current_app.config["APP_NAME"],
        "status": "OK",
        "headers": request.headers.to_list()
    }),  mimetype='application/json', status=200)


@app.errorhandler(400)
def Internal_server_error(e):
    return render_template('pages/500.html'), 500


@app.errorhandler(Exception)
def unhandled_exception(e):
    return render_template('pages/503.html'), 503


@app.errorhandler(404)
def page_not_found(e):
    return render_template('pages/404.html'), 404
