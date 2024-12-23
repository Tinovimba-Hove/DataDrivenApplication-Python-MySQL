import hashlib
from baseObject import baseObject
from user import user

class rewards_redeemed(baseObject):
    
    def __init__(self):
        self.setup()
        self.rewards_claimed = [{'value':'fn1','text':'Free Night', 'points_used':1000},{'value':'ru1','text':'Room Upgrade', 'points_used':500}]

    def get_reward_description(self, reward_code):
        for reward in self.rewards_claimed:
            if reward['value'] == reward_code:
                return reward['text'], reward['points_used']
        return None, 0
        
    
    def verify_new(self, reward_code, n=0):
        self.errors = []
        description, points_used = self.get_reward_description(reward_code)

        # Check if the reward code is valid
        if description is None:
            self.errors.append("Invalid reward code.")
            return False, None, 0  # Return 0 points_used if invalid

        # Check if the user has enough points
        uid = self.data[n].get('uid')
        u = user()
        u.getById(uid)
        if not u.data:
            self.errors.append("User not found.")
            return False, None, 0

        user_data = u.data[0]
        points_available = user_data.get('points_available', 0)

        if points_available < points_used:
            self.errors.append("Not enough points available to redeem this reward.")

        if len(self.errors) > 0:
            return False, None, 0

        # Deduct points and update user details
        user_data['points_available'] -= points_used
        user_data['total_points_used'] = user_data.get('total_points_used', 0) + points_used
        u.update()  # Update user table with new points

        # Update rewards_redeemed record
        self.data[n]['points_used'] = points_used
        self.data[n]['description'] = description

        return True, description, points_used

        
    def verify_update(self, reward_code, n=0):
        self.errors = []
        description, points_used = self.get_reward_description(reward_code)

        # Check if the reward code is valid
        if description is None:
            self.errors.append("Invalid reward code.")
            return False, None, 0  # Return 0 points_used if invalid

        # Check if the user has enough points
        uid = self.data[n].get('uid')
        u = user()
        u.getById(uid)
        if not u.data:
            self.errors.append("User not found.")
            return False, None, 0

        user_data = u.data[0]
        points_available = user_data.get('points_available', 0)

        if points_available < points_used:
            self.errors.append("Not enough points available to redeem this reward.")

        if len(self.errors) > 0:
            return False, None, 0

        # Deduct points and update user details
        user_data['points_available'] -= points_used
        user_data['total_points_used'] = user_data.get('total_points_used', 0) + points_used
        u.update()  # Update user table with new points

        # Update rewards_redeemed record
        self.data[n]['points_used'] = points_used
        self.data[n]['description'] = description

        return True, description, points_used


    def getRewardStats(self):
        # Total Rewards Redeemed by Type
        sql_rewards_redeemed = """
        SELECT description, COUNT(*) AS redemption_count
        FROM hotel_rewards_redeemed
        GROUP BY description
        ORDER BY redemption_count DESC
        """
        self.cur.execute(sql_rewards_redeemed)
        self.data_rewards_redeemed = []
        self.chart_rewards_redeemed = {'x': [], 'y': []}

        for row in self.cur:
            self.data_rewards_redeemed.append(row)
            self.chart_rewards_redeemed['x'].append(row['description'])
            self.chart_rewards_redeemed['y'].append(row['redemption_count'])


        # Monthly Redemption Trends
        sql_monthly_redemption = """
        SELECT DATE_FORMAT(redeem_date, '%Y-%m') AS redemption_month, COUNT(*) AS total_redemptions
        FROM hotel_rewards_redeemed
        GROUP BY redemption_month
        ORDER BY redemption_month ASC
        """
        self.cur.execute(sql_monthly_redemption)
        self.monthly_redemption_trends = {'x': [], 'y': []}

        for row in self.cur:
            self.monthly_redemption_trends['x'].append(row['redemption_month'])
            self.monthly_redemption_trends['y'].append(row['total_redemptions'])

        # Redemption Distribution by User
        sql_user_redemption = """
        SELECT uid, COUNT(*) AS total_redemptions, SUM(points_used) AS total_points_used
        FROM hotel_rewards_redeemed
        GROUP BY uid
        ORDER BY total_redemptions DESC
        """
        self.cur.execute(sql_user_redemption)
        self.user_redemption_data = {'uid': [], 'total_redemptions': [], 'total_points_used': []}

        for row in self.cur:
            self.user_redemption_data['uid'].append(row['uid'])
            self.user_redemption_data['total_redemptions'].append(row['total_redemptions'])
            self.user_redemption_data['total_points_used'].append(row['total_points_used'])

        # Redemption Patterns for Top Rewards
        sql_top_reward_patterns = """
        SELECT description, 
            DATE_FORMAT(redeem_date, '%Y-%m') AS redemption_month, 
            COUNT(*) AS redemptions_in_month
        FROM hotel_rewards_redeemed
        GROUP BY description, redemption_month
        ORDER BY description, redemption_month
        """
        self.cur.execute(sql_top_reward_patterns)
        self.top_reward_patterns = {}

        for row in self.cur:
            if row['description'] not in self.top_reward_patterns:
                self.top_reward_patterns[row['description']] = {'x': [], 'y': []}
            self.top_reward_patterns[row['description']]['x'].append(row['redemption_month'])
            self.top_reward_patterns[row['description']]['y'].append(row['redemptions_in_month'])

        # Debugging
        print("Rewards Redeemed Chart Data:", self.chart_rewards_redeemed)
        print("Monthly Redemption Trends:", self.monthly_redemption_trends)
        print("User Redemption Data:", self.user_redemption_data)
        print("Top Reward Patterns:", self.top_reward_patterns)
