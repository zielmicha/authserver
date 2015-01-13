from flask import Flask, redirect, request
from django.conf import settings
from django.template import Template, Context
import os
import requests
import argparse
import urllib

settings.configure()

def load_template(name):
    return Template(open(os.path.join(os.path.dirname(__file__), 'templates', name)).read())

app = Flask(__name__)

@app.route("/<token>", methods=['GET'])
def hello(token):
    if token == 'favicon.ico':
        return ''
    error = request.args.get('error')
    resp = requests.get(args.api_url + token)
    if resp.status_code != 200:
        error = 'no_such_ticket' if resp.status_code in (403, 404) else 'internal_error'
        data = {}
    else:
        data = resp.json()
    data['error'] = error
    return load_template('setpassword.html').render(Context(data)).encode('utf8')

@app.route("/<token>", methods=['POST'])
def set_password(token):
    if request.form['password1'] != request.form['password2']:
        return redirect('?error=passwords-dont-match')

    resp = requests.post(args.api_url + token, {
        'password': request.form['password1']
    })
    resp.raise_for_status()
    status = resp.json()['status']
    if status == 'ok':
        return redirect(args.redirect_url)
    else:
        return redirect('?error=' + urllib.quote(status))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=7890)
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--api-url', required=True)
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('--redirect-url', required=True)
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug)
