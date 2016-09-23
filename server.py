import json
from flask import Flask, request

from guess import manager

app = Flask(__name__)

@app.route('/')
def main():
    with open('plug.html', 'r') as f:
        return f.read()

@app.route('/magic.jpg')
def img():
    with open('magic.jpg', 'rb') as f:
        return f.read()

@app.route("/search")
def search():
    
    query = request.args.get('query')
    print 'Query: %s' % str(query)
    
    try:
        answer = manager(query)
        return json.dumps(answer)
    except Exception, e:
        print 'Error: ' + str(e)
        return json.dumps({'error': str(e)})

if __name__ == "__main__":
    app.run()
