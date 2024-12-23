from datetime import datetime
import hashlib
from baseObject import baseObject
from user import user
from rooms import room
from rewards_redeemed import rewards_redeemed

class reservation(baseObject):
    
    def __init__(self):
        self.setup()
        self.payment_methods = [{'value':'Credit/Debit Card','text':'Credit/Debit Card'},{'value':'Cash','text':'Cash'}]
        self.deleteById

    def verify_new(self, n=0):
        self.errors = []

        # Validate room availability
        r = room()
        room_id = self.data[n].get('room_id')
        check_in_date = self.data[n].get('check_in_date')
        check_out_date = self.data[n].get('check_out_date')

        if not r.is_room_available(room_id, check_in_date, check_out_date):
            self.errors.append('Selected room is unavailable.')

        # Validate dates
        self._validate_dates(n)

        # Validate payment method
        valid_payment_methods = [method['value'] for method in self.payment_methods]
        if self.data[n].get('payment_method') not in valid_payment_methods:
            self.errors.append(f"Payment method must be one of {valid_payment_methods}.")

        return len(self.errors) == 0

    def verify_update(self, n=0):
        self.errors = []

        r = room()
        room_id = self.data[n].get('room_id')
        check_in_date = self.data[n].get('check_in_date')
        check_out_date = self.data[n].get('check_out_date')
        res_id = self.data[n].get('res_id')  

        if not r.is_room_available_for_update(room_id, check_in_date, check_out_date, res_id):
            self.errors.append('Selected room is unavailable for the updated dates.')

        # Validate dates
        self._validate_dates(n)

        # Validate payment method
        valid_payment_methods = [method['value'] for method in self.payment_methods]
        if self.data[n].get('payment_method') not in valid_payment_methods:
            self.errors.append(f"Payment method must be one of {valid_payment_methods}.")

        return len(self.errors) == 0

    def _validate_dates(self, n):
        try:
            check_in_date = datetime.strptime(self.data[n].get('check_in_date'), '%Y-%m-%d')
            check_out_date = datetime.strptime(self.data[n].get('check_out_date'), '%Y-%m-%d')
            payment_date = datetime.strptime(self.data[n].get('payment_date'), '%Y-%m-%d')

            if check_out_date <= check_in_date:
                self.errors.append('Check-out date must be after check-in date.')

            if payment_date > check_in_date:
                self.errors.append('Payment date cannot be after check-in date.')
        except (ValueError, TypeError):
            self.errors.append('Invalid date format. Dates must be in YYYY-MM-DD format.')

    def calculate_points_and_amount(self, n=0):
        room_id = self.data[n].get('room_id')
        r = room()
        r.getById(room_id)
        room_price = r.data[0].get('price', 0)

        uid = self.data[n].get('uid')
        u = user()
        u.getById(uid)
        membership_type = u.data[0].get('membership_type', '') if u.data else ''

        discount_rate = {'gold': 0.10, 'platinum': 0.15}.get(membership_type, 0)

        check_in_date = datetime.strptime(self.data[n].get('check_in_date'), '%Y-%m-%d')
        check_out_date = datetime.strptime(self.data[n].get('check_out_date'), '%Y-%m-%d')
        stay_duration = (check_out_date - check_in_date).days

        amount = room_price * stay_duration * (1 - discount_rate)
        points_gained = 50 * stay_duration if stay_duration <= 2 else 100 * stay_duration

        # Update user's total points
        if u.data:
            u.data[0]['total_points_gained'] += points_gained
            u.update()

        self.data[n]['amount'] = amount
        self.data[n]['points_gained'] = points_gained

    def deleteById(self, id):
        # Retrieve the reservation details before deletion
        r = room()
        if not self.data:
            print(f"No data found for id: {id}")
            return False 
        
        room_id = self.data[0].get('room_id')
        print("Room ID to free:", room_id)
        r.free_room(room_id)  # Change the room status back to Available

        super().deleteById(id)  # Now actually delete the reservation

    def getReservationStats(self):
        # Count reservations by payment method
        sql_payment_method = """
        SELECT payment_method, COUNT(*) AS reservation_count
        FROM hotel_reservations
        GROUP BY payment_method
        ORDER BY reservation_count DESC
        """
        self.cur.execute(sql_payment_method)
        self.chart_payment_method = {"x": [], "y": []}
        for row in self.cur:
            self.chart_payment_method["x"].append(row['payment_method'])
            self.chart_payment_method["y"].append(row['reservation_count'])

        # Total reservations grouped by amount ranges
        sql_amount_ranges = """
        SELECT 
            CASE 
                WHEN amount <= 1000 THEN '0-1000'
                WHEN amount BETWEEN 1000 AND 2000 THEN '1000-2000'
                ELSE '2000+'
            END AS amount_range,
            COUNT(*) AS total_reservations
        FROM hotel_reservations
        GROUP BY amount_range
        """
        self.cur.execute(sql_amount_ranges)
        self.chart_amount_ranges = {"x": [], "y": []}
        for row in self.cur:
            self.chart_amount_ranges["x"].append(row['amount_range'])
            self.chart_amount_ranges["y"].append(row['total_reservations'])

        # Daily reservation trends over time
        sql_daily_trends = """
        SELECT check_in_date, COUNT(*) AS total_reservations
        FROM hotel_reservations
        GROUP BY check_in_date
        ORDER BY check_in_date
        """
        self.cur.execute(sql_daily_trends)
        self.chart_daily_trends = {"x": [], "y": []}
        for row in self.cur:
            self.chart_daily_trends["x"].append(row['check_in_date'])
            self.chart_daily_trends["y"].append(row['total_reservations'])

        # Total points gained by users
        sql_points_gained = """
        SELECT uid, SUM(points_gained) AS total_points
        FROM hotel_reservations
        GROUP BY uid
        ORDER BY total_points DESC
        """
        self.cur.execute(sql_points_gained)
        self.chart_user_points_gained = {"x": [], "y": []}
        for row in self.cur:
            self.chart_user_points_gained["x"].append(row['uid'])
            self.chart_user_points_gained["y"].append(row['total_points'])

        # Count of unique room reservations by room_id
        sql_room_reservations = """
        SELECT room_id, COUNT(*) AS total_reservations
        FROM hotel_reservations
        GROUP BY room_id
        """
        self.cur.execute(sql_room_reservations)
        self.chart_room_reservations = {"x": [], "y": []}
        for row in self.cur:
            self.chart_room_reservations["x"].append(row['room_id'])
            self.chart_room_reservations["y"].append(row['total_reservations'])

        # Average spending per reservation by payment method
        sql_avg_spending = """
        SELECT payment_method, AVG(amount) AS average_amount
        FROM hotel_reservations
        GROUP BY payment_method
        """
        self.cur.execute(sql_avg_spending)
        self.chart_avg_spending = {"x": [], "y": []}
        for row in self.cur:
            self.chart_avg_spending["x"].append(row['payment_method'])
            self.chart_avg_spending["y"].append(float(row['average_amount']))

        

        # Debugging printout
        print("Payment Method Stats:", self.chart_payment_method)
        print("Amount Ranges Stats:", self.chart_amount_ranges)
        print("Daily Reservation Trends:", self.chart_daily_trends)
        print("Points Gained Stats:", self.chart_user_points_gained)
        print("Room Reservation Stats:", self.chart_room_reservations)
        print("Average Spending Stats:", self.chart_avg_spending)

        
        
        
       