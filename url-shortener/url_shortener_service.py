import sqlite3

class URLShortenerService:
    def __init__(self, db_path, worker):
        self.db_path = db_path
        self.worker = worker
        self.charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def _encode_base62(self, num):
        if num == 0: return self.charset[0]
        arr = []
        while num:
            num, rem = divmod(num, 62)
            arr.append(self.charset[rem])
        arr.reverse()
        return ''.join(arr)

    def shorten_url(self, long_url):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT short_code FROM url_mappings WHERE long_url = ?", (long_url,))
            result = cursor.fetchone()
            if result:
                return result[0]

            unique_id = self.worker.get_next_id()

            short_code = self._encode_base62(unique_id)

            cursor.execute(
                "INSERT INTO url_mappings (id, short_code, long_url) VALUES (?, ?, ?)",
                (unique_id, short_code, long_url)
            )
            conn.commit()
            return short_code

        except sqlite3.IntegrityError:
            conn.rollback()
            cursor.execute("SELECT short_code FROM url_mappings WHERE long_url = ?", (long_url,))
            return cursor.fetchone()[0]
        finally:
            conn.close()