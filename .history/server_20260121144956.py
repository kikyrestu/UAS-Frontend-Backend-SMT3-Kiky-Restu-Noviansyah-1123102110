
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

    # Users table (Customers)
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  phone TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Seed a demo user if empty
    c.execute("SELECT count(*) FROM users")
    if c.fetchone()[0] == 0:
        import hashlib
        demo_pass = hashlib.sha256('demo123'.encode()).hexdigest()
        c.execute("INSERT INTO users (name, email, password_hash, phone) VALUES (?, ?, ?, ?)",
                  ('Demo User', 'demo@ottobus.com', demo_pass, '08123456789'))
        conn.commit()

    # Schedules table (specific departure dates/times)
    c.execute('''CREATE TABLE IF NOT EXISTS schedules
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  route_id INTEGER NOT NULL,
                  bus_id INTEGER NOT NULL,
                  departure_date TEXT NOT NULL,
                  departure_time TEXT NOT NULL,
                  price INTEGER DEFAULT 0,
                  available_seats INTEGER DEFAULT 40,
                  booked_seats TEXT DEFAULT '',
                  status TEXT DEFAULT 'active',
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (route_id) REFERENCES routes(id),
                  FOREIGN KEY (bus_id) REFERENCES buses(id))''')
    
    # Seed schedules for next 7 days if empty
    c.execute("SELECT count(*) FROM schedules")
    if c.fetchone()[0] == 0:
        from datetime import datetime, timedelta
        today = datetime.now()
        for i in range(7):
            date_str = (today + timedelta(days=i)).strftime('%Y-%m-%d')
            # Route 1: Jakarta-Bandung with Bus 1
            c.execute("INSERT INTO schedules (route_id, bus_id, departure_date, departure_time, price, available_seats) VALUES (?, ?, ?, ?, ?, ?)",
                      (1, 1, date_str, '08:00', 100000, 40))
            c.execute("INSERT INTO schedules (route_id, bus_id, departure_date, departure_time, price, available_seats) VALUES (?, ?, ?, ?, ?, ?)",
                      (1, 1, date_str, '14:00', 100000, 40))
            # Route 2: Jakarta-Surabaya with Bus 2
            c.execute("INSERT INTO schedules (route_id, bus_id, departure_date, departure_time, price, available_seats) VALUES (?, ?, ?, ?, ?, ?)",
                      (2, 2, date_str, '19:00', 350000, 20))
            # Route 3: Bandung-Yogyakarta with Bus 3
            c.execute("INSERT INTO schedules (route_id, bus_id, departure_date, departure_time, price, available_seats) VALUES (?, ?, ?, ?, ?, ?)",
                      (3, 3, date_str, '07:00', 200000, 30))
        conn.commit()

    # Migration: Add origin, destination, duration to schedules if not exists (Phase Refactor)
    try:
        c.execute("ALTER TABLE schedules ADD COLUMN origin TEXT")
        c.execute("ALTER TABLE schedules ADD COLUMN destination TEXT")
        c.execute("ALTER TABLE schedules ADD COLUMN duration TEXT")
    except sqlite3.OperationalError:
        pass

    # REPAIR DATA: Fix null origin/destination for legacy schedules
    c.execute("SELECT count(*) FROM schedules WHERE origin IS NULL OR origin = ''")
    if c.fetchone()[0] > 0:
        print("PERBAIKAN DATA: Mengisi data jadwal yang kosong...")
        c.execute("UPDATE schedules SET origin='Jakarta', destination='Bandung', duration='3 Jam 30 Menit' WHERE (origin IS NULL OR origin = '') AND id % 3 = 0")
        c.execute("UPDATE schedules SET origin='Surabaya', destination='Bali (Denpasar)', duration='12 Jam' WHERE (origin IS NULL OR origin = '') AND id % 3 = 1")
        c.execute("UPDATE schedules SET origin='Yogyakarta', destination='Semarang', duration='3 Jam' WHERE (origin IS NULL OR origin = '') AND id % 3 = 2")
        conn.commit()

    # Bookings table
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  schedule_id INTEGER NOT NULL,
                  seat_numbers TEXT NOT NULL,
                  total_price INTEGER DEFAULT 0,
                  status TEXT DEFAULT 'pending',
                  booking_code TEXT UNIQUE,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users(id),
                  FOREIGN KEY (schedule_id) REFERENCES schedules(id))''')

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
                # Still support finding "route" by ID - but now it maps to a schedule group
                # For compatibility, try to return one representative schedule or keep old logic if table exists
                # BUT user wants to remove routes table logic.
                # Let's return a synthetic route object based on available schedules
                c.execute('''SELECT s.id, s.origin, s.destination, s.duration, s.price, s.departure_time as time,
                                    b.seat_capacity, b.facilities, b.image_url, b.bus_type as category
                             FROM schedules s 
                             JOIN buses b ON s.bus_id = b.id
                             WHERE s.id = ?''', (route_id,)) # treating route_id as schedule_id for detail view?
                             # Wait, bus-detail used ?id={route_id}.
                             # Now it should be schedule-detail. 
                             # The landing page cards link to bus-detail?id={schedule_id} maybe?
                             # Or we aggregate by Origin-Dest.
                
                # Let's look at the old logic: routes table had ID.
                # If we aggregate, we don't have a stable ID for "Jakarta-Bandung".
                # Unless we generate one or use a composite key?
                # Simplest: bus-detail takes a SCHEDULE ID now. 
                # Landing page cards should represent specific departure options or a group.
                
                # User asked to "remove dependency on routes".
                # Let's say we still return data from `routes` table IF it exists, but `schedules` is the source of truth for NEW stuff.
                # BUT the user wants to DELETE the "Kelola Rute" menu.
                # So we should serve /api/routes from distinct schedules.
                
                # If ID is passed, it is likely a SCHEDULE ID in the new paradigm.
                c.execute('''SELECT s.id, s.origin, s.destination, s.departure_time as time, s.price, s.duration,
                                    b.seat_capacity, b.facilities, b.image_url, b.bus_type as category,
                                    co.name as company_name, co.logo_url as company_logo
                             FROM schedules s
                             JOIN buses b ON s.bus_id = b.id
                             LEFT JOIN companies co ON b.company_id = co.id
                             WHERE s.id=?''', (route_id,))
                row = c.fetchone()
                if row:
                    result = dict(row)
                    # Add description if missing from DB or just dynamic
                    result['description'] = f"Perjalanan {result['origin']} ke {result['destination']} dengan {result['company_name'] or 'Bus'}"
                else:
                    result = {}

            else:
                # Aggregate schedules to show unique routes (Origin -> Dest)
                # Actually, landing page cards usually show specific times? 
                # Or just generic "Jakarta -> All" options?
                # The existing index.html shows individual cards for each route.
                # So we can just list ALL active schedules as "cards".
                c.execute('''SELECT s.id, s.origin, s.destination, s.departure_time as time, s.price, s.duration,
                                    b.seat_capacity, b.facilities, b.image_url, b.bus_type as category,
                                    co.name as company_name, co.logo_url as company_logo
                             FROM schedules s
                             JOIN buses b ON s.bus_id = b.id
                             LEFT JOIN companies co ON b.company_id = co.id
                             WHERE s.status = 'active'
                             ORDER BY s.departure_date, s.departure_time''')
                rows = c.fetchall()
                result = [dict(row) for row in rows]
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
                c.execute('''SELECT c.*, count(b.id) as bus_count 
                             FROM companies c 
                             LEFT JOIN buses b ON c.id = b.company_id 
                             WHERE c.id=?
                             GROUP BY c.id''', (company_id,))
                row = c.fetchone()
                result = dict(row) if row else {}
            else:
                c.execute('''SELECT c.*, count(b.id) as bus_count 
                             FROM companies c 
                             LEFT JOIN buses b ON c.id = b.company_id 
                             GROUP BY c.id 
                             ORDER BY c.name''')
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

            # Count distinct routes from schedules (Origin -> Dest)
            c.execute("SELECT count(DISTINCT origin || destination) FROM schedules")
            total_routes = c.fetchone()[0]

            conn.close()
            self.wfile.write(json.dumps({
                'tickets_today': tickets_today,
                'revenue_today': revenue_today,
                'total_routes': total_routes or 0
            }).encode())
        elif parsed_path.path == '/api/schedules':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            query = urllib.parse.parse_qs(parsed_path.query)
            schedule_id = query.get('id', [None])[0]
            route_id = query.get('route_id', [None])[0]
            date_filter = query.get('date', [None])[0]

            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            if schedule_id:
                c.execute('''SELECT s.*, 
                                    r.origin as legacy_origin, r.destination as legacy_destination, r.category, r.duration as legacy_duration,
                                    b.plate_number, b.bus_type, b.seat_capacity, b.seat_layout, b.facilities,
                                    co.name as company_name
                             FROM schedules s
                             LEFT JOIN routes r ON s.route_id = r.id
                             JOIN buses b ON s.bus_id = b.id
                             LEFT JOIN companies co ON b.company_id = co.id
                             WHERE s.id=?''', (schedule_id,))
                row = c.fetchone()
                if row:
                    r = dict(row)
                    # Fallback for origin/dest if missing in schedule but present in route (legacy)
                    if not r.get('origin') and r.get('legacy_origin'):
                        r['origin'] = r['legacy_origin']
                        r['destination'] = r['legacy_destination']
                        r['duration'] = r['legacy_duration']
                    result = r
                else: 
                     result = {}
            else:
                # LIST schedules
                # Use LEFT JOIN for routes because new schedules might not have route_id
                sql = '''SELECT s.*, 
                                r.origin as legacy_origin, r.destination as legacy_destination, r.category, r.duration as legacy_duration,
                                b.plate_number, b.bus_type, b.seat_capacity, b.seat_layout,
                                co.name as company_name
                         FROM schedules s
                         LEFT JOIN routes r ON s.route_id = r.id
                         JOIN buses b ON s.bus_id = b.id
                         LEFT JOIN companies co ON b.company_id = co.id
                         WHERE s.status = 'active' '''
                params = []
                if route_id:
                    # Deprecated filter, but kept for compatibility or specific schedule ID lookup if mislabeled
                    sql += ' AND s.id = ?' # Assuming route_id passed here might be schedule_id in new context? 
                    params.append(route_id)
                if date_filter:
                    sql += ' AND s.departure_date = ?'
                    params.append(date_filter)
                sql += ' ORDER BY s.departure_date, s.departure_time'
                c.execute(sql, params)
                rows = c.fetchall()
                print(f"DEBUG: Found {len(rows)} schedules")
                # Process result to fill origin/dest from routes if missing (migration fallback)
                result = []
                for row in rows:
                    r = dict(row)
                    print(f"DEBUG: Processing ID {r.get('id')} -> Origin: {r.get('origin')}, Legacy: {r.get('legacy_origin')}")
                    # If origin is NULL in schedules, try to use legacy_origin from JOIN
                    if not r.get('origin') and r.get('legacy_origin'):
                         print(f"DEBUG: APPLYING FALLBACK for ID {r.get('id')}")
                         r['origin'] = r['legacy_origin']
                         r['destination'] = r['legacy_destination']
                         r['duration'] = r['legacy_duration']
                    result.append(r)
            
            conn.close()
            self.wfile.write(json.dumps(result).encode())
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
                self.wfile.write(json.dumps({'status': 'success', 'token': 'fake-jwt-token', 'role': 'admin'}).encode())
            else:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid credentials'}).encode())
        
        elif parsed_path.path == '/api/register':
            import hashlib
            name = data.get('name', '')
            email = data.get('email', '')
            password = data.get('password', '')
            phone = data.get('phone', '')
            
            if not name or not email or not password:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Name, email, and password are required'}).encode())
                return
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (name, email, password_hash, phone) VALUES (?, ?, ?, ?)",
                          (name, email, password_hash, phone))
                user_id = c.lastrowid
                conn.commit()
                conn.close()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success', 'user_id': user_id, 'token': f'user-token-{user_id}'}).encode())
            except sqlite3.IntegrityError:
                conn.close()
                self.send_response(409)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Email already registered'}).encode())
        
        elif parsed_path.path == '/api/user/login':
            import hashlib
            email = data.get('email', '')
            password = data.get('password', '')
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email=? AND password_hash=?", (email, password_hash))
            user = c.fetchone()
            conn.close()
            
            if user:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'status': 'success',
                    'token': f'user-token-{user["id"]}',
                    'user': {
                        'id': user['id'],
                        'name': user['name'],
                        'email': user['email'],
                        'phone': user['phone']
                    }
                }).encode())
            else:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid email or password'}).encode())
        
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

        elif parsed_path.path == '/api/companies':
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            name = data.get('name', '')
            logo_url = data.get('logo_url', '')
            description = data.get('description', '')
            phone = data.get('phone', '')
            email = data.get('email', '')
            
            # Handle Base64 Image Upload for logo
            if data.get('logo_file'):
                saved_path = save_image_from_base64(data['logo_file'])
                if saved_path:
                    logo_url = saved_path
            
            c.execute("INSERT INTO companies (name, logo_url, description, phone, email) VALUES (?, ?, ?, ?, ?)",
                      (name, logo_url, description, phone, email))
            new_id = c.lastrowid
            conn.commit()
            conn.close()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success', 'id': new_id}).encode())

        elif parsed_path.path == '/api/buses':
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            company_id = data.get('company_id')
            plate_number = data.get('plate_number', '')
            bus_type = data.get('bus_type', 'Executive')
            seat_capacity = data.get('seat_capacity', 40)
            seat_layout = data.get('seat_layout', '2-2')
            facilities = data.get('facilities', '')
            image_url = data.get('image_url', '')
            
            # Handle Base64 Image Upload
            if data.get('image_file'):
                saved_path = save_image_from_base64(data['image_file'])
                if saved_path:
                    image_url = saved_path
            
            c.execute("INSERT INTO buses (company_id, plate_number, bus_type, seat_capacity, seat_layout, facilities, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (company_id, plate_number, bus_type, seat_capacity, seat_layout, facilities, image_url))
            new_id = c.lastrowid
            conn.commit()
            conn.close()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success', 'id': new_id}).encode())

        elif parsed_path.path == '/api/routes':
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            category = data.get('category', 'Executive') 
            image_url = data.get('image_url', '')
            description = data.get('description', '')
            facilities = data.get('facilities', '')
            seat_capacity = data.get('seat_capacity', 30)
            duration = data.get('duration', '4 Jam')
            company_id = data.get('company_id')  # New field

            # Handle Base64 Image Upload
            if data.get('image_file'):
                saved_path = save_image_from_base64(data['image_file'])
                if saved_path:
                    image_url = saved_path
            
            c.execute("INSERT INTO routes (origin, destination, time, price, category, image_url, description, facilities, seat_capacity, duration, company_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                      (data['origin'], data['destination'], data['time'], data['price'], category, image_url, description, facilities, seat_capacity, duration, company_id))
            conn.commit()
            conn.close()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success'}).encode())
        
        elif parsed_path.path == '/api/schedules':
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            # route_id is deprecated/optional
            bus_id = data.get('bus_id')
            origin = data.get('origin')
            destination = data.get('destination')
            duration = data.get('duration', '4 Jam')
            departure_date = data.get('departure_date')
            departure_time = data.get('departure_time')
            price = data.get('price', 0)
            available_seats = data.get('available_seats', 40)
            
            c.execute("INSERT INTO schedules (bus_id, origin, destination, duration, departure_date, departure_time, price, available_seats) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (bus_id, origin, destination, duration, departure_date, departure_time, price, available_seats))
            new_id = c.lastrowid
            conn.commit()
            conn.close()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success', 'id': new_id}).encode())

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
                
                category = data.get('category', 'Executive')
                image_url = data.get('image_url', '')
                description = data.get('description', '')
                facilities = data.get('facilities', '')
                seat_capacity = data.get('seat_capacity', 30)
                duration = data.get('duration', '4 Jam')
                company_id = data.get('company_id')  # New field

                # Handle Base64 Image Upload
                if data.get('image_file'):
                    saved_path = save_image_from_base64(data['image_file'])
                    if saved_path:
                        image_url = saved_path
                
                c.execute("""UPDATE routes 
                             SET origin=?, destination=?, time=?, price=?, category=?, image_url=?, description=?, facilities=?, seat_capacity=?, duration=?, company_id=?
                             WHERE id=?""", 
                          (data['origin'], data['destination'], data['time'], data['price'], category, image_url, description, facilities, seat_capacity, duration, company_id, route_id))
                conn.commit()
                conn.close()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success'}).encode())
            else:
                self.send_response(400)
                self.end_headers()
        
        elif parsed_path.path == '/api/companies':
            query = urllib.parse.parse_qs(parsed_path.query)
            company_id = query.get('id', [None])[0]
            
            if company_id:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                
                name = data.get('name', '')
                logo_url = data.get('logo_url', '')
                description = data.get('description', '')
                phone = data.get('phone', '')
                email = data.get('email', '')
                
                if data.get('logo_file'):
                    saved_path = save_image_from_base64(data['logo_file'])
                    if saved_path:
                        logo_url = saved_path
                
                c.execute("""UPDATE companies 
                             SET name=?, logo_url=?, description=?, phone=?, email=?
                             WHERE id=?""", 
                          (name, logo_url, description, phone, email, company_id))
                conn.commit()
                conn.close()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success'}).encode())
            else:
                self.send_response(400)
                self.end_headers()
        
        elif parsed_path.path == '/api/buses':
            query = urllib.parse.parse_qs(parsed_path.query)
            bus_id = query.get('id', [None])[0]
            
            if bus_id:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                
                company_id = data.get('company_id')
                plate_number = data.get('plate_number', '')
                bus_type = data.get('bus_type', 'Executive')
                seat_capacity = data.get('seat_capacity', 40)
                seat_layout = data.get('seat_layout', '2-2')
                facilities = data.get('facilities', '')
                image_url = data.get('image_url', '')
                
                if data.get('image_file'):
                    saved_path = save_image_from_base64(data['image_file'])
                    if saved_path:
                        image_url = saved_path
                
                c.execute("""UPDATE buses 
                             SET company_id=?, plate_number=?, bus_type=?, seat_capacity=?, seat_layout=?, facilities=?, image_url=?
                             WHERE id=?""", 
                          (company_id, plate_number, bus_type, seat_capacity, seat_layout, facilities, image_url, bus_id))
                conn.commit()
                conn.close()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success'}).encode())
            else:
                self.send_response(400)
                self.end_headers()
        
        elif parsed_path.path == '/api/schedules':
            query = urllib.parse.parse_qs(parsed_path.query)
            schedule_id = query.get('id', [None])[0]
            
            if schedule_id:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                
                # route_id is deprecated
                bus_id = data.get('bus_id')
                origin = data.get('origin')
                destination = data.get('destination')
                duration = data.get('duration')
                departure_date = data.get('departure_date')
                departure_time = data.get('departure_time')
                price = data.get('price', 0)
                available_seats = data.get('available_seats')
                
                c.execute("""UPDATE schedules 
                             SET bus_id=?, origin=?, destination=?, duration=?, departure_date=?, departure_time=?, price=?, available_seats=?
                             WHERE id=?""", 
                          (bus_id, origin, destination, duration, departure_date, departure_time, price, available_seats, schedule_id))
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
        query = urllib.parse.parse_qs(parsed_path.query)
        
        if parsed_path.path == '/api/routes':
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
        
        elif parsed_path.path == '/api/companies':
            company_id = query.get('id', [None])[0]
            if company_id:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                # Also delete related buses
                c.execute("DELETE FROM buses WHERE company_id=?", (company_id,))
                c.execute("DELETE FROM companies WHERE id=?", (company_id,))
                conn.commit()
                conn.close()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success'}).encode())
            else:
                self.send_response(400)
                self.end_headers()
        
        elif parsed_path.path == '/api/buses':
            bus_id = query.get('id', [None])[0]
            if bus_id:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("DELETE FROM buses WHERE id=?", (bus_id,))
                conn.commit()
                conn.close()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success'}).encode())
            else:
                self.send_response(400)
                self.end_headers()
        
        elif parsed_path.path == '/api/schedules':
            schedule_id = query.get('id', [None])[0]
            if schedule_id:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("DELETE FROM schedules WHERE id=?", (schedule_id,))
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
