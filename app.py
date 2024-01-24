from flask import Flask, request, redirect, Response
import requests

app = Flask(__name__)
target_url = 'http://your-target-site.com'  # Replace with your target URL

@app.route('/')
def index():
    return redirect('/proxy/')

@app.route('/proxy/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    global target_url
    if request.method == 'GET':
        resp = requests.get(f'{target_url}/{path}')
    elif request.method == 'POST':
        resp = requests.post(f'{target_url}/{path}', json=request.json)
    elif request.method == 'PUT':
        resp = requests.put(f'{target_url}/{path}', json=request.json)
    elif request.method == 'DELETE':
        resp = requests.delete(f'{target_url}/{path}')

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)
