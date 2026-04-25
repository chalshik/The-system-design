import sqlite3

class IDWorker:
    def __init__(self, db_path, range_size=1000):
        self.db_path = db_path
        self.range_size = range_size
        self.current_id = 0
        self.max_id_in_range = 0

    def _fetch_new_range(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("BEGIN TRANSACTION")
        
        try:
            cursor.execute("SELECT last_id FROM global_counters WHERE counter_name = 'url_shortener'")
            last_id = cursor.fetchone()[0]
            
            new_max = last_id + self.range_size
            cursor.execute("UPDATE global_counters SET last_id = ? WHERE counter_name = 'url_shortener'", (new_max,))
            
            conn.commit()
            return last_id + 1, new_max
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_next_id(self):
        if self.current_id >= self.max_id_in_range:
            start, end = self._fetch_new_range()
            self.current_id = start
            self.max_id_in_range = end
        else:
            self.current_id += 1
            
        return self.current_id