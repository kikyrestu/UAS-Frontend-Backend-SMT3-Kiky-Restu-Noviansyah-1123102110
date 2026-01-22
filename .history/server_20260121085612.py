
import http.server
import socketserver
import json
import sqlite3
import os
import urllib.parse

PORT = 8000
DB_FILE = 'ottobus.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Content table for dynamic text (Hero title, About, etc.)
    c.execute('''CREATE TABLE IF NOT EXISTS content
                 (key TEXT PRIMARY KEY, value TEXT)''')
    
    # Check if content exists, if not seed it
    c.execute("SELECT count(*) FROM content")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO content (key, value) VALUES ('hero_title', 'Perjalanan Nyaman Bersama Ottobus')")
        c.execute("INSERT INTO content (key, value) VALUES ('hero_subtitle', 'Antar kota antar provinsi dengan armada terbaik.')")
        c.execute("INSERT INTO content (key, value) VALUES ('about_text', 'Ottobus adalah penyedia layanan transportasi terpercaya sejak 2024.')")
        # Initialize stats
        c.execute("INSERT INTO content (key, value) VALUES ('tickets_today', '5')")
        c.execute("INSERT INTO content (key, value) VALUES ('revenue_today', '750000')")
        conn.commit()

    # Routes table
    c.execute('''CREATE TABLE IF NOT EXISTS routes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  origin TEXT, 
                  destination TEXT, 
                  time TEXT, 
                  price TEXT,
                  category TEXT,
                  image_url TEXT)''')
    
    # Migration: Add columns if they don't exist
    try:
        c.execute("ALTER TABLE routes ADD COLUMN category TEXT")
    except sqlite3.OperationalError:
        pass 
        
    try:
        c.execute("ALTER TABLE routes ADD COLUMN image_url TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE routes ADD COLUMN description TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE routes ADD COLUMN facilities TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE routes ADD COLUMN seat_capacity INTEGER")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE routes ADD COLUMN duration TEXT")
    except sqlite3.OperationalError:
        pass

    # Seed routes if empty
    c.execute("SELECT count(*) FROM routes")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO routes (origin, destination, time, price, category, image_url, description, facilities, seat_capacity, duration) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                  ('Jakarta', 'Bandung', '08:00', 'Rp 100.000', 'Executive', 'https://images.unsplash.com/photo-1570125909232-eb263c188f7e?w=800&q=80', 'Perjalanan nyaman dengan pemandangan indah.', 'AC,WiFi,USB', 30, '3 - 4 Jam'))
        c.execute("INSERT INTO routes (origin, destination, time, price, category, image_url, description, facilities, seat_capacity, duration) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                  ('Jakarta', 'Surabaya', '19:00', 'Rp 350.000', 'Sleeper Class', 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=800&q=80', 'Tidur nyenyak sepanjang perjalanan dengan fasilitas premium.', 'AC,WiFi,Toilet,Reclining,Blanket', 20, '10 - 12 Jam'))
        c.execute("INSERT INTO routes (origin, destination, time, price, category, image_url, description, facilities, seat_capacity, duration) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                  ('Bandung', 'Yogyakarta', '07:00', 'Rp 200.000', 'Royal Class', 'https://images.unsplash.com/photo-1494515843206-f3117d3f51b7?w=800&q=80', 'Layanan kelas kerajaan dengan kenyamanan maksimal.', 'AC,WiFi,USB,Meal', 24, '6 - 7 Jam'))
        conn.commit()

    # Companies table (PO Bus)
    c.execute('''CREATE TABLE IF NOT EXISTS companies
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  logo_url TEXT,
                  description TEXT,
                  phone TEXT,
                  email TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Seed companies if empty
    c.execute("SELECT count(*) FROM companies")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO companies (name, logo_url, description, phone, email) VALUES (?, ?, ?, ?, ?)",
                  ('Sinar Jaya', 'https://via.placeholder.com/100x100?text=SJ', 'PO Bus Sinar Jaya - Melayani rute Jawa sejak 1990', '021-5551234', 'info@sinarjaya.co.id'))
        c.execute("INSERT INTO companies (name, logo_url, description, phone, email) VALUES (?, ?, ?, ?, ?)",
                  ('Harapan Jaya', 'https://via.placeholder.com/100x100?text=HJ', 'PO Bus Harapan Jaya - Armada modern dan nyaman', '021-5555678', 'cs@harapanjaya.com'))
        c.execute("INSERT INTO companies (name, logo_url, description, phone, email) VALUES (?, ?, ?, ?, ?)",
                  ('Lorena', 'https://via.placeholder.com/100x100?text=LR', 'PO Lorena - Kenyamanan adalah prioritas kami', '021-5559012', 'hello@lorena.co.id'))
        conn.commit()

    # Buses table (Armada)
    c.execute('''CREATE TABLE IF NOT EXISTS buses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  company_id INTEGER,
                  plate_number TEXT NOT NULL,
                  bus_type TEXT,
                  seat_capacity INTEGER DEFAULT 40,
                  seat_layout TEXT DEFAULT '2-2',
                  facilities TEXT,
                  image_url TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (company_id) REFERENCES companies(id))''')
    
    # Seed buses if empty
    c.execute("SELECT count(*) FROM buses")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO buses (company_id, plate_number, bus_type, seat_capacity, seat_layout, facilities, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (1, 'B 1234 SJ', 'Executive', 40, '2-2', 'AC,WiFi,USB,Toilet', 'https://images.unsplash.com/photo-1570125909232-eb263c188f7e?w=800&q=80'))
        c.execute("INSERT INTO buses (company_id, plate_number, bus_type, seat_capacity, seat_layout, facilities, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (1, 'B 5678 SJ', 'Sleeper', 20, '2-1', 'AC,WiFi,USB,Toilet,Blanket,Meal', 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=800&q=80'))
        c.execute("INSERT INTO buses (company_id, plate_number, bus_type, seat_capacity, seat_layout, facilities, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (2, 'B 9012 HJ', 'Royal Class', 30, '2-2', 'AC,WiFi,USB,Reclining,Meal', 'https://images.unsplash.com/photo-1494515843206-f3117d3f51b7?w=800&q=80'))
        conn.commit()

    # Migration: Add company_id to routes if not exists
    try:
        c.execute("ALTER TABLE routes ADD COLUMN company_id INTEGER")
    except sqlite3.OperationalError:
        pass

    conn.close()

def save_image_from_base64(data_url):
    try:
        header, encoded = data_url.split(",", 1)
        import base64
        import time
        
        # Ensure uploads directory exists
        if not os.path.exists('uploads'):
            os.makedirs('uploads')
            
        # Generate unique filename
        ext = 'png'
        if 'jpeg' in header or 'jpg' in header:
            ext = 'jpg'
        
        filename = f"bus_{int(time.time())}.{ext}"
        filepath = os.path.join('uploads', filename)
        
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(encoded))
            
        return f"/uploads/{filename}"
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

class OttobusHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/api/content':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM content")
            rows = c.fetchall()
            content = {row['key']: row['value'] for row in rows}
            conn.close()
            self.wfile.write(json.dumps(content).encode())
        elif parsed_path.path == '/api/routes':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            query = urllib.parse.parse_qs(parsed_path.query)
            route_id = query.get('id', [None])[0]

            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            if route_id:
                c.execute("SELECT * FROM routes WHERE id=?", (route_id,))
                row = c.fetchone()
                if row:
                    result = dict(row)
                else:
                    result = {}
            else:
                c.execute("SELECT * FROM routes")
                rows = c.fetchall()
                result = [dict(row) for row in rows]
            
            conn.close()
            self.wfile.write(json.dumps(result).encode())
        elif parsed_path.path == '/api/companies':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            query = urllib.parse.parse_qs(parsed_path.query)
            company_id = query.get('id', [None])[0]

            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            if company_id:
                c.execute("SELECT * FROM companies WHERE id=?", (company_id,))
                row = c.fetchone()
                result = dict(row) if row else {}
            else:
                c.execute("SELECT * FROM companies ORDER BY name")
                rows = c.fetchall()
                result = [dict(row) for row in rows]
            
            conn.close()
            self.wfile.write(json.dumps(result).encode())
        elif parsed_path.path == '/api/buses':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            query = urllib.parse.parse_qs(parsed_path.query)
            bus_id = query.get('id', [None])[0]
            company_id = query.get('company_id', [None])[0]

            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            if bus_id:
                c.execute('''SELECT b.*, c.name as company_name 
                             FROM buses b LEFT JOIN companies c ON b.company_id = c.id 
                             WHERE b.id=?''', (bus_id,))
                row = c.fetchone()
                result = dict(row) if row else {}
            elif company_id:
                c.execute('''SELECT b.*, c.name as company_name 
                             FROM buses b LEFT JOIN companies c ON b.company_id = c.id 
                             WHERE b.company_id=?''', (company_id,))
                rows = c.fetchall()
                result = [dict(row) for row in rows]
            else:
                c.execute('''SELECT b.*, c.name as company_name 
                             FROM buses b LEFT JOIN companies c ON b.company_id = c.id 
                             ORDER BY c.name, b.plate_number''')
                rows = c.fetchall()
                result = [dict(row) for row in rows]
            
            conn.close()
            self.wfile.write(json.dumps(result).encode())
        elif parsed_path.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            c.execute("SELECT value FROM content WHERE key='tickets_today'")
            row_tickets = c.fetchone()
            tickets_today = int(row_tickets['value']) if row_tickets else 0
            
            c.execute("SELECT value FROM content WHERE key='revenue_today'")
            row_revenue = c.fetchone()
            revenue_today = int(row_revenue['value']) if row_revenue else 0

            c.execute("SELECT count(*) FROM routes")
            total_routes = c.fetchone()[0]

            conn.close()
            self.wfile.write(json.dumps({
                'tickets_today': tickets_today,
                'revenue_today': revenue_today,
                'total_routes': total_routes
            }).encode())
        else:
            # Clean up path to serve files correctly particularly for /admin
            if self.path == '/admin' or self.path == '/admin/':
                self.path = '/admin/index.html'
            super().do_GET()

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(length)
        data = json.loads(post_data.decode())
        
        parsed_path = urllib.parse.urlparse(self.path)

        if parsed_path.path == '/api/login':
            # Simple hardcoded admin login
            if data.get('username') == 'admin' and data.get('password') == 'admin123':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success', 'token': 'fake-jwt-token'}).encode())
            else:
                self.send_response(401)
                self.end_headers()
        
        elif parsed_path.path == '/api/content':
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            for key, value in data.items():
                c.execute("INSERT OR REPLACE INTO content (key, value) VALUES (?, ?)", (key, value))
            conn.commit()
            conn.close()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success'}).encode())

        elif parsed_path.path == '/api/stats/increment':
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            type_ = data.get('type')
            
            if type_ == 'ticket':
                # Increment Count
                c.execute("SELECT value FROM content WHERE key='tickets_today'")
                row = c.fetchone()
                val = int(row[0]) if row else 0
                c.execute("INSERT OR REPLACE INTO content (key, value) VALUES ('tickets_today', ?)", (str(val + 1),))
                
                # Increment Revenue
                price_str = str(data.get('price', '0'))
                # Clean price string (remove Rp, dots, etc)
                import re
                price_clean = re.sub(r'[^\d]', '', price_str)
                price_val = int(price_clean) if price_clean else 0
                
                c.execute("SELECT value FROM content WHERE key='revenue_today'")
                row_rev = c.fetchone()
                current_rev = int(row_rev[0]) if row_rev else 0
                c.execute("INSERT OR REPLACE INTO content (key, value) VALUES ('revenue_today', ?)", (str(current_rev + price_val),))
                
            conn.commit()
            conn.close()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success'}).encode())

        elif parsed_path.path == '/api/routes':
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            category = data.get('category', 'Executive') 
            image_url = data.get('image_url', '')
            description = data.get('description', '')
            facilities = data.get('facilities', '') # Expecting comma separated string
            seat_capacity = data.get('seat_capacity', 30)
            duration = data.get('duration', '4 Jam')

            # Handle Base64 Image Upload
            if data.get('image_file'):
                saved_path = save_image_from_base64(data['image_file'])
                if saved_path:
                    image_url = saved_path
            
            c.execute("INSERT INTO routes (origin, destination, time, price, category, image_url, description, facilities, seat_capacity, duration) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                      (data['origin'], data['destination'], data['time'], data['price'], category, image_url, description, facilities, seat_capacity, duration))
            conn.commit()
            conn.close()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success'}).encode())

    def do_PUT(self):
        length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(length)
        data = json.loads(post_data.decode())
        
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/api/routes':
            query = urllib.parse.parse_qs(parsed_path.query)
            route_id = query.get('id', [None])[0]
            
            if route_id:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                
                # Check for existing fields to allow partial updates if needed, though form sends all
                category = data.get('category', 'Executive')
                image_url = data.get('image_url', '')
                description = data.get('description', '')
                facilities = data.get('facilities', '')
                seat_capacity = data.get('seat_capacity', 30)
                duration = data.get('duration', '4 Jam')

                # Handle Base64 Image Upload
                if data.get('image_file'):
                    saved_path = save_image_from_base64(data['image_file'])
                    if saved_path:
                        image_url = saved_path
                
                c.execute("""UPDATE routes 
                             SET origin=?, destination=?, time=?, price=?, category=?, image_url=?, description=?, facilities=?, seat_capacity=?, duration=?
                             WHERE id=?""", 
                          (data['origin'], data['destination'], data['time'], data['price'], category, image_url, description, facilities, seat_capacity, duration, route_id))
                conn.commit()
                conn.close()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success'}).encode())
            else:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
            


    def do_DELETE(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/api/routes':
            query = urllib.parse.parse_qs(parsed_path.query)
            route_id = query.get('id', [None])[0]
            if route_id:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("DELETE FROM routes WHERE id=?", (route_id,))
                conn.commit()
                conn.close()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success'}).encode())
            else:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    init_db()
    with socketserver.TCPServer(("", PORT), OttobusHandler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()
