import hashlib
import pymysql
from baseObject import baseObject
class room(baseObject):
    
    def __init__(self):
        self.setup()
        self.room_types = [
            {'value': 'Standard', 'text': 'Standard', 'price': 100, 'description': 'Standard: Two Beds'},
            {'value': 'Exclusive', 'text': 'Exclusive', 'price': 175, 'description': 'Luxury Suite'}
        ]

    def verify_new(self, n=0):
        self.errors = []
        if len(self.errors) > 0:
            return False
        else:
            return True

    def verify_update(self, n=0):
        self.errors = []
        rt = [room['value'] for room in self.room_types]
        if self.data[n]['room_type'] not in rt:
            self.errors.append(f'Room Type must be one of {rt}')

        if len(self.errors) > 0:
            return False
        else:
            return True

    def set_room_price(self, room_type):
        for room in self.room_types:
            if room['value'] == room_type:
                return room['price']
        return 0

    def is_room_available(self, room_id, check_in_date, check_out_date):
        sql = """
        SELECT COUNT(*) 
        FROM hotel_reservations 
        WHERE room_id = %s AND %s <= check_out_date AND %s >= check_in_date;
        """
        self.cur.execute(sql, (room_id, check_in_date, check_out_date))
        result = self.cur.fetchone()
        if result is None or result.get('COUNT(*)', 0) == 0:
            return True  # No conflicts, room is available
        return False

    def update_status(self, room_id):
        sql = """
        SELECT COUNT(*) 
        FROM hotel_reservations 
        WHERE room_id = %s AND CURRENT_DATE BETWEEN check_in_date AND check_out_date;
        """
        self.cur.execute(sql, (room_id,))
        result = self.cur.fetchone()
        new_status = 'Unavailable' if result[0] > 0 else 'Available'

        sql_update = """
        UPDATE hotel_rooms 
        SET status = %s 
        WHERE id = %s;
        """
        self.cur.execute(sql_update, (new_status, room_id))
        self.conn.commit()

    def free_room(self, room_id):
        sql = """
        UPDATE hotel_rooms
        SET status = 'Available'
        WHERE room_id = %s;
        """
        self.cur.execute(sql, (room_id,))
        self.conn.commit()

    def get_available_rooms(self):
        sql = "SELECT * FROM hotel_rooms WHERE status = 'Available';"
        self.cur.execute(sql)
        return self.cur.fetchall()

    def is_room_available_for_update(self, room_id, check_in_date, check_out_date, res_id):
        sql = """
        SELECT COUNT(*) 
        FROM hotel_reservations 
        WHERE room_id = %s 
        AND %s <= check_out_date 
        AND %s >= check_in_date
        AND res_id != %s;
        """
        self.cur.execute(sql, (room_id, check_in_date, check_out_date, res_id))
        result = self.cur.fetchone()
        return result.get('COUNT(*)', 0) == 0 

    def reserve_room(self, room_id, check_in_date, check_out_date):
        if not self.is_room_available(room_id, check_in_date, check_out_date):
            return "Room is unavailable for the selected dates."

        sql = """
        INSERT INTO hotel_reservations (room_id, check_in_date, check_out_date)
        VALUES (%s, %s, %s);
        """
        self.cur.execute(sql, (room_id, check_in_date, check_out_date))
        self.conn.commit()

        # Update room status
        self.update_status(room_id)
        return "Reservation created successfully!"

    def cleanup_room_statuses(self):
        sql = """
        UPDATE hotel_rooms
        SET status = 'Available'
        WHERE id IN (
            SELECT room_id
            FROM reservations
            WHERE CURRENT_DATE > check_out_date
        );
        """
        self.cur.execute(sql)
        self.conn.commit()
        
    
    def getRoomStats(self):
        # Average Price by Room Type
        sql_avg_price = """
        SELECT room_type, AVG(price) AS avg_price, MIN(price) AS min_price, MAX(price) AS max_price
        FROM hotel_rooms
        WHERE status = 'available'
        GROUP BY room_type
        ORDER BY avg_price DESC
        """
        self.cur.execute(sql_avg_price)
        self.data_avg_price = []
        self.chart_avg_price = {'x': [], 'y': []}
        
        for row in self.cur:
            self.data_avg_price.append(row)
            self.chart_avg_price['x'].append(row['room_type'])
            self.chart_avg_price['y'].append(float(row['avg_price']))

        # Room Count by Status
        sql_room_status_count = """
        SELECT status, COUNT(*) AS count
        FROM hotel_rooms
        GROUP BY status
        """
        self.cur.execute(sql_room_status_count)
        self.room_status_counts = {'status': [], 'count': []}
        
        for row in self.cur:
            self.room_status_counts['status'].append(row['status'])
            self.room_status_counts['count'].append(int(row['count']))


        # Average occupancy rate trends (Available vs unavailable)
        sql_occupancy_rate = """
        SELECT room_type, 
            (SUM(CASE WHEN status='available' THEN 1 ELSE 0 END) / COUNT(*)) * 100 AS availability_rate
        FROM hotel_rooms
        GROUP BY room_type
        """
        self.cur.execute(sql_occupancy_rate)
        self.availability_rate_data = {'room_type': [], 'availability_rate': []}
        
        for row in self.cur:
            self.availability_rate_data['room_type'].append(row['room_type'])
            self.availability_rate_data['availability_rate'].append(float(row['availability_rate']))

        # Debugging
        print("Average Price Chart Data:", self.chart_avg_price)
        print("Room Status Counts:", self.room_status_counts)
        print("Availability Rate Data:", self.availability_rate_data)

