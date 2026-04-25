import sqlite3
from flask import Flask, request, redirect, jsonify, abort
from database import DB_PATH, init_db
from worker import IDWorker
from service import URLShortenerService

app = Flask(__name__)

init_db()
worker = IDWorker(DB_PATH, range_size=100)
service = URLShortenerService(DB_PATH, worker)

@app.route('/shorten', methods=['POST'])
def create_short_url():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "URL is required"}), 400
    short_code = service.shorten_url(data['url'])
    return jsonify({"short_url": f"http://localhost:5000/{short_code}"}), 201

@app.route('/<short_code>', methods=['GET'])
def redirect_to_long(short_code):
    # 1. Check Redis first
    long_url = service.redis.get(short_code)
    
    if long_url:
        print(f"[Cache Hit] Redirecting {short_code} via Redis")
        return redirect(long_url, code=302)

    # 2. Cache Miss - Check SQLite
    print(f"[Cache Miss] Querying Database for {short_code}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT long_url FROM url_mappings WHERE short_code = ?", (short_code,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        long_url = result[0]
        # 3. Write to Redis for future requests
        service.redis.set(short_code, long_url, ex=3600) # Cache for 1 hour
        return redirect(long_url, code=302)
    
    abort(404)

if __name__ == '__main__':
    app.run(debug=True, port=5000)