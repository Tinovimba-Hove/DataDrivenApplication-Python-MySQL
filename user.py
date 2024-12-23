import hashlib
from baseObject import baseObject

class user(baseObject):

    def __init__(self):
        self.setup()
        self.roles = [{'value': 'admin', 'text': 'admin'}, {'value': 'customer', 'text': 'customer'}]
        self.membership_types = [
            {'type': 'Gold', 'discount_rate': 0.10, 'free_wifi': True, 'free_water': False},
            {'type': 'Platinum', 'discount_rate': 0.15, 'free_wifi': True, 'free_water': True}
        ]

    def hashPassword(self, pw):
        pw = pw + 'xyz'
        return hashlib.md5(pw.encode('utf-8')).hexdigest()

    def set_membership_benefits(self, membership_type):
        # Find the membership type from the list
        benefits = next((item for item in self.membership_types if item['type'] == membership_type), None)
        if benefits:
            # Set the benefits in the user's data
            self.data[0]['discount_rate'] = benefits.get('discount_rate', 0)
            self.data[0]['free_wifi'] = benefits.get('free_wifi', False)
            self.data[0]['free_water'] = benefits.get('free_water', False)
        else:
            # If no membership type is found, reset benefits to default
            self.data[0]['discount_rate'] = 0
            self.data[0]['free_wifi'] = False
            self.data[0]['free_water'] = False

    def calculate_points(self):
        total_points_gained = self.data[0].get('total_points_gained', 0)
        total_points_used = self.data[0].get('total_points_used', 0)
        self.data[0]['points_available'] = total_points_gained - total_points_used

    def insert(self, n=0):
        if 'total_points_gained' not in self.data[n]:
            self.data[n]['total_points_gained'] = 0
        if 'total_points_used' not in self.data[n]:
            self.data[n]['total_points_used'] = 0
        
        if 'points_available' in self.fields:
            self.fields.remove('points_available')
        super().insert(n)

    def update(self, n=0):
        if 'total_points_gained' not in self.data[n]:
            self.data[n]['total_points_gained'] = 0
        if 'total_points_used' not in self.data[n]:
            self.data[n]['total_points_used'] = 0

        if 'points_available' in self.fields:
            self.fields.remove('points_available')
        super().update(n)

    def verify_new(self, n=0):
        self.errors = []
        if self.data[n]['name'] == '':
            self.errors.append('Name cannot be blank.')
        else:
            u = user()
            u.getByField('name', self.data[n]['name'])
            if len(u.data) > 0:
                self.errors.append('Name already in use.')

        if self.data[n]['password'] != self.data[n]['password2']:
            self.errors.append('Retyped password must match.')
        if len(self.data[n]['password']) < 3:
            self.errors.append('Password needs to be more than 3 chars.')
        else:
            self.data[n]['password'] = self.hashPassword(self.data[n]['password'])

        rl = [role['value'] for role in self.roles]
        if self.data[n]['role'] not in rl:
            self.errors.append(f'Role must be one of {rl}')

        mt = [membership['type'] for membership in self.membership_types]
        if self.data[n]['membership_type'] not in mt:
            self.errors.append(f'Membership must be one of {mt}')

        phone_number = self.data[n].get('phone')
        if len(phone_number) != 10 or not phone_number.isdigit():
            self.errors.append("Enter a valid phone number (10 digits).")

        email = self.data[n].get('email')
        if '@' not in email:
            self.errors.append("Enter a valid email address.")
        
        if len(self.errors) > 0:
            return False
        else:
            # Set the membership benefits upon successful verification
            self.set_membership_benefits(self.data[n]['membership_type'])
            return True

    def verify_update(self, n=0):
        self.errors = []
        if self.data[n]['name'] == '':
            self.errors.append('Name cannot be blank.')
        else:
            u = user()
            u.getByField('name', self.data[n]['name'])
            if len(u.data) > 0 and u.data[0][u.pk] != self.data[n][self.pk]:
                self.errors.append('Name already in use.')

        rl = [role['value'] for role in self.roles]
        if self.data[n]['role'] not in rl:
            self.errors.append(f'Role must be one of {rl}')

        mt = [membership['type'] for membership in self.membership_types]
        if self.data[n]['membership_type'] not in mt:
            self.errors.append(f'Membership must be one of {mt}')

        if len(self.data[n]['password']) == 0:
            del self.data[n]['password']
        else:
            if 'password2' in self.data[n].keys():  # user intends to change pw
                if self.data[n]['password'] != self.data[n]['password2']:
                    self.errors.append('Retyped password must match.')
                if len(self.data[n]['password']) < 3:
                    self.errors.append('Password must be > 2 chars.')
                else:
                    self.data[n]['password'] = self.hashPassword(self.data[n]['password'])

        if 'membership_type' in self.data[n]:
            self.set_membership_benefits(self.data[n]['membership_type'])

        phone_number = self.data[n].get('phone')
        if len(phone_number) != 10 or not phone_number.isdigit():
            self.errors.append("Enter a valid phone number (10 digits).")

        email = self.data[n].get('email')
        if '@' not in email:
            self.errors.append("Enter a valid email address.")

        if len(self.errors) > 0:
            return False
        else:
            return True

    def tryLogin(self, name, password):
        pwd = self.hashPassword(password)
        sql = f"SELECT * FROM `{self.tn}` WHERE `name` = %s AND `password` = %s;" 
        self.cur.execute(sql, (name, pwd))
        self.data = [row for row in self.cur]
        return len(self.data) == 1


    def analyzeCustomerStats(self):
        # Fetch role counts - Compare the number of `admin` vs `customer`
        sql_role_counts = """
        SELECT role, COUNT(*) AS total_users
        FROM hotel_users
        GROUP BY role
        """
        self.cur.execute(sql_role_counts)
        self.role_counts = {'role': [], 'total_users': []}
        
        for row in self.cur:
            self.role_counts['role'].append(row['role'])
            self.role_counts['total_users'].append(int(row['total_users']))

        # Fetch membership type data
        sql_membership_counts = """
        SELECT membership_type, COUNT(*) AS members_count
        FROM hotel_users
        GROUP BY membership_type
        """
        self.cur.execute(sql_membership_counts)
        self.membership_counts = {'membership_type': [], 'members_count': []}
        
        for row in self.cur:
            self.membership_counts['membership_type'].append(row['membership_type'])
            self.membership_counts['members_count'].append(int(row['members_count']))

        # Analyze discount rates across memberships
        sql_discount_rates = """
        SELECT membership_type, AVG(discount_rate) AS avg_discount
        FROM hotel_users
        WHERE discount_rate IS NOT NULL
        GROUP BY membership_type
        """
        self.cur.execute(sql_discount_rates)
        self.discount_rates = {'membership_type': [], 'avg_discount': []}
        
        for row in self.cur:
            self.discount_rates['membership_type'].append(row['membership_type'])
            self.discount_rates['avg_discount'].append(float(row['avg_discount']))

        # Analyze points statistics
        sql_points_stats = """
        SELECT SUM(total_points_gained) AS total_gained,
            SUM(total_points_used) AS total_used,
            SUM(points_available) AS total_available
        FROM hotel_users
        WHERE total_points_gained IS NOT NULL AND total_points_used IS NOT NULL
        """
        self.cur.execute(sql_points_stats)
        row = self.cur.fetchone()
        self.points_summary = {
            'total_points_gained': int(row['total_gained']),
            'total_points_used': int(row['total_used']),
            'total_points_available': int(row['total_available'])
        }

        # Perks visualization
        sql_perks_count = """
        SELECT 
            SUM(CASE WHEN free_water IS NOT NULL THEN 1 ELSE 0 END) AS water_count,
            SUM(CASE WHEN free_wifi IS NOT NULL THEN 1 ELSE 0 END) AS wifi_count
        FROM hotel_users
        """
        self.cur.execute(sql_perks_count)
        row = self.cur.fetchone()
        self.perks_summary = {
            'free_water': int(row['water_count']),
            'free_wifi': int(row['wifi_count'])
        }

        # Debugging prints for review
        print("Role Counts:", self.role_counts)
        print("Membership Statistics:", self.membership_counts)
        print("Discount Rates:", self.discount_rates)
        print("Points Summary:", self.points_summary)
        print("Perks Data:", self.perks_summary)
