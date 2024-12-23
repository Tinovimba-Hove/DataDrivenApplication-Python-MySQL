from flask import Flask
from pymysql.err import OperationalError
from flask import render_template
from flask import request,session, redirect,send_from_directory,make_response 
from flask_session import Session
from datetime import timedelta, datetime
from user import user
import time
from rooms import room
from reservations import reservation
from rewards_redeemed import rewards_redeemed

#create Flask app instance
app = Flask(__name__,static_url_path='')

#Configure serverside sessions 
app.config['SECRET_KEY'] = '56hdtryhRTg'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
sess = Session()
sess.init_app(app)

#Basic root route - show the word 'homepage'
@app.route('/')  #route name
def home(): #view function
    #return 'homepage'
    return render_template('homepage.html')   


@app.context_processor
def inject_user():
    return dict(me=session.get('user'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.form.get('name') is not None and request.form.get('password') is not None:
            u = user()
            # Try to log in and handle potential database connection errors
            if u.tryLogin(request.form.get('name'), request.form.get('password')):
                print("Login ok")
                session['user'] = u.data[0]
                session['active'] = time.time()
                return redirect('main')
            else:
                print("Login Failed")
                return render_template('login.html', title='Login', msg='Incorrect username or password.')
        else:   
            if 'msg' not in session.keys() or session['msg'] is None:
                m = 'Type your email and password to continue.'
            else:
                m = session['msg']
                session['msg'] = None
            return render_template('login.html', title='Login', msg=m)  
    except OperationalError as e:
        # Handle the database connection error
        error_message = "Please connect to the database via a secured connection first."
        print(f"Database connection error: {e}")  # Log the actual error for debugging
        return render_template('login.html', title='Login', msg=error_message)

    
@app.route('/logout',methods = ['GET','POST'])
def logout():
    if session.get('user') is not None:
        del session['user']
        del session['active']
    return render_template('login.html', title='Login', msg='You have logged out.')

@app.route('/main')
def main():
    if checkSession() == False: 
        return redirect('/login')
    if session['user']['role'] == 'admin':
        return render_template('main.html', title='Main menu') 
    else:
        user_id = session['user']['uid']
        u = user()
        u.getById(user_id)
        points_available = u.data[0]['points_available'] if u.data else 0
        return render_template('customer_main.html', title='Main menu', points_available=points_available) 
    
@app.route('/contact')  #route name
def contact(): #view function
    return render_template('contact.html')   

@app.route('/users/manage',methods=['GET','POST'])
def manage_user():
    if checkSession() == False or session['user']['role'] != 'admin': 
        return redirect('/login')
    o = user()
    action = request.args.get('action')
    pkval = request.args.get('pkval')
    if action is not None and action == 'delete': #action=delete&pkval=123
        o.deleteById(request.args.get('pkval'))
        return render_template('ok_dialog.html',msg= "Deleted.")
    if action is not None and action == 'insert':
        d = {}
        d['name'] = request.form.get('name')
        d['role'] = request.form.get('role')
        d['password'] = request.form.get('password')
        d['password2'] = request.form.get('password2')
        d['phone'] = request.form.get('phone')
        d['email'] = request.form.get('email')
        d['membership_type'] = request.form.get('membership_type')
        d['total_points_gained'] = int(request.form.get('total_points_gained', 0))
        d['total_points_used'] = int(request.form.get('total_points_used', 0))
        o.set(d)
        if o.verify_new():
            o.insert()
            return render_template('ok_dialog.html',msg= "User added.")
        else:
            return render_template('users/add.html',obj = o)
    if action is not None and action == 'update':
        o.getById(pkval)
        o.data[0]['name'] = request.form.get('name')
        o.data[0]['role'] = request.form.get('role')
        o.data[0]['password'] = request.form.get('password')
        o.data[0]['password2'] = request.form.get('password2')
        o.data[0]['phone'] = request.form.get('phone')
        o.data[0]['email'] = request.form.get('email')
        o.data[0]['membership_type'] = request.form.get('membership_type')
        o.data[0]['total_points_gained'] = int(request.form.get('total_points_gained', 0))
        o.data[0]['total_points_used'] = int(request.form.get('total_points_used', 0))
        if o.verify_update():
            o.update()
            return render_template('ok_dialog.html',msg= "User updated. <")
        else:
            return render_template('users/manage.html',obj = o)
        
    if pkval is None: #list all items
        o.getAll()
        return render_template('users/list.html',objs = o)
    if pkval == 'new':
        o.createBlank()
        return render_template('users/add.html',obj = o)
    else:
        print(pkval)
        o.getById(pkval)
        return render_template('users/manage.html',obj = o)

@app.route('/users/signup',methods=['GET','POST'])
def signup_user():
    try:
        o = user()
        if request.method == 'POST':
            d = {}
            d['name'] = request.form.get('name')
            d['password'] = request.form.get('password')
            d['password2'] = request.form.get('password2')
            d['phone'] = request.form.get('phone')
            d['email'] = request.form.get('email')
            d['membership_type'] = request.form.get('membership_type')
            d['role'] = 'customer'

            o.set(d)
            if o.verify_new():
                o.insert()
                return render_template('ok_dialog.html',msg= "User Created.")
            else:
                return render_template('users/signup.html',obj = o)
        o.createBlank()
        return render_template('users/signup.html',obj = o)
    except OperationalError as e:
        # Handle the database connection error
        error_message = "Please connect to the database via a secured connection first."
        print(f"Database connection error: {e}")  # Log the actual error for debugging
        return render_template('login.html', title='Login', msg=error_message)



@app.route('/rooms/manage', methods=['GET', 'POST'])
def manage_rooms():
    if checkSession() == False or session['user']['role'] != 'admin': 
        return redirect('/login')
    o = room()
    action = request.args.get('action')
    pkval = request.args.get('pkval')

    o.cur.execute("SELECT DISTINCT status FROM hotel_rooms;")
    dynamic_status = [{'value': row['status'], 'text': row['status']} for row in o.cur.fetchall()]
    o.status = dynamic_status 

    if action == 'delete' and pkval:
        o.deleteById(pkval)
        return render_template('ok_dialog.html', msg="Deleted.")

    if action == 'insert':
        d = {
            'room_num': request.form.get('room_num'),
            'price': request.form.get('price'),
            'status': request.form.get('status'),
            'room_type': request.form.get('room_type'),
            'description': request.form.get('description')
        }
        d['price'] = o.set_room_price(d['room_type'])
        o.set(d)
        if o.verify_new():
            o.insert()
            return render_template('ok_dialog.html', msg="Room added.")
        else:
            return render_template('rooms/add.html', obj=o)

    if action == 'update' and pkval:
        o.getById(pkval)
        o.data[0].update({
            'room_num': request.form.get('room_num'),
            'price': request.form.get('price'),
            'status': request.form.get('status'),
            'room_type': request.form.get('room_type'),
            'description': request.form.get('description')
        })
        o.data[0]['price'] = o.set_room_price(o.data[0]['room_type'])
        if o.verify_update():
            o.update()
            return render_template('ok_dialog.html', msg="Room updated.")
        else:
            return render_template('rooms/manage.html', obj=o)

    if not pkval:  # List all items
        o.getAll()
        return render_template('rooms/list.html', objs=o)

    if pkval == 'new':
        o.createBlank()
        return render_template('rooms/add.html', obj=o)

    o.getById(pkval)
    return render_template('rooms/manage.html', obj=o)

@app.route('/reservations/manage', methods=['GET', 'POST'])
def manage_reserve():
    if checkSession() == False or session['user']['role'] not in ['admin', 'customer']:
        return redirect('/login')
    
    o = reservation()
    action = request.args.get('action')
    pkval = request.args.get('pkval')
    logged_in_user = session['user']
    
    r = room()
    r.getAll()
    o.rooms = r

    u = user()
    if logged_in_user['role'] == 'admin':
        u.getAll()
    elif logged_in_user['role'] == 'customer':
        u.getByField('uid', logged_in_user['uid'])
    o.guests = u

    if action == 'delete' and pkval:
        o.getById(pkval)
        if o.data:
            o.deleteById(pkval)
            return render_template('ok_dialog.html', msg="Deleted.")
        return render_template('error.html', msg="Reservation not found.")

    if action == 'insert':
        d = {
            'uid': logged_in_user['uid'] if logged_in_user['role'] == 'customer' else request.form.get('uid'),
            'room_id': request.form.get('room_id'),
            'check_in_date': request.form.get('check_in_date'),
            'check_out_date': request.form.get('check_out_date'),
            'payment_method': request.form.get('payment_method'),
            'payment_date': request.form.get('payment_date')
        }
        o.set(d)
        if o.verify_new():
            o.calculate_points_and_amount()
            o.insert()
            return render_template('ok_dialog.html', msg=f"Reservation added. You earned {o.data[0]['points_gained']} points!")
        return render_template('reservations/add.html', obj=o)

    if action == 'update' and pkval:
        o.getById(pkval)
        previous_room_id = o.data[0]['room_id']

        o.data[0].update({
            'room_id': request.form.get('room_id'),
            'check_in_date': request.form.get('check_in_date'),
            'check_out_date': request.form.get('check_out_date'),
            'payment_method': request.form.get('payment_method'),
            'payment_date': request.form.get('payment_date')
        })

        if o.verify_update():
            if previous_room_id != o.data[0]['room_id']:
                r.free_room(previous_room_id)
            o.calculate_points_and_amount()
            o.update()
            return render_template('ok_dialog.html', msg="Reservation updated.")
        return render_template('reservations/manage.html', obj=o)

    if not pkval:
        if logged_in_user['role'] == 'admin':
            o.getAll()
        elif logged_in_user['role'] == 'customer':
            o.getByField('uid', logged_in_user['uid'])
        return render_template('reservations/list.html', objs=o)

    if pkval == 'new':
        o.createBlank()
        if logged_in_user['role'] == 'customer':
            o.data[0]['uid'] = logged_in_user['uid']
        return render_template('reservations/add.html', obj=o)

    o.getById(pkval)
    return render_template('reservations/manage.html', obj=o)

@app.template_filter('format_date')
def format_date(value, format='%Y-%m-%d'):
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            return value
    return value.strftime(format) if isinstance(value, datetime) else value

app.jinja_env.filters['format_date'] = format_date
   
   
@app.route('/rewards_redeemed/manage',methods=['GET','POST'])
def manage_rewards():
    if checkSession() == False or session['user']['role'] != 'customer': 
        return redirect('/login')
    o = rewards_redeemed()
    user_id = session['user']['uid']
    u = user()
    u.getById(user_id)
    points_available = u.data[0]['points_available'] if u.data else 0
    action = request.args.get('action')
    pkval = request.args.get('pkval')
    u = user()
    u.getAll() 
    o.guests = u

    if action is not None and action == 'delete': #action=delete&pkval=123
        o.deleteById(request.args.get('pkval'))
        return render_template('ok_dialog.html',msg= "Deleted.",points_available=points_available)
    
    if action is not None and action == 'insert':
        d = {}
        d['uid'] = request.form.get('uid')
        d['reward_code'] = request.form.get('reward_code')
        d['redeem_date'] = request.form.get('redeem_date')
        o.set(d)
        # Validate and redeem reward
        is_valid, description, points_used = o.verify_new(d['reward_code'])
        if is_valid:
            d['description'] = description
            d['points_used'] = points_used
            o.insert()  # Insert reward into rewards_redeemed table
            return render_template('ok_dialog.html', msg=f"Reward redeemed: {description}. You used {points_used} points!")
        else:
            return render_template('rewards_redeemed/add.html', obj=o, points_available=points_available)
        
    if action is not None and action == 'update':
        o.getById(pkval)
        d = {}
        d['uid'] = request.form.get('uid')
        d['reward_code'] = request.form.get('reward_code')
        d['redeem_date'] = request.form.get('redeem_date')
        is_valid, description, points_used = o.verify_update(d['reward_code'])
        if is_valid:
            d['description'] = description
            d['points_used'] = points_used
            #o.data[0].update(d)
            o.update() 
            return render_template('ok_dialog.html', msg=f"Reward redeemed: {description}. You used {points_used} points!")
        else:
            return render_template('rewards_redeemed/add.html', obj=o, points_available=points_available)
        
    if pkval is None: #list all items
        o.getByField('uid', user_id)
        return render_template('rewards_redeemed/list.html',objs = o)
    if pkval == 'new':
        o.createBlank()
        return render_template('rewards_redeemed/add.html',obj = o)
    else:
        print(pkval)
        o.getById(pkval)
        return render_template('rewards_redeemed/manage.html',obj = o)
    
@app.route('/roomAnalytics')
def room_analytics():
    if not checkSession():
        return redirect('/login')
    o = room()
    o.getRoomStats()
    return render_template('rooms/room_analytics.html', title='Room Analytics', obj=o)

@app.route('/userAnalytics')
def user_analytics():
    if not checkSession():
        return redirect('/login')
    o = user()
    o.analyzeCustomerStats()
    return render_template('users/user_analytics.html', title='User Analytics', obj=o)

@app.route('/reservationAnalytics')
def reservation_analytics():
    if not checkSession():
        return redirect('/login')
    o = reservation()
    o.getReservationStats()
    return render_template('reservations/reservation_analytics.html', title='Reservation Analytics', obj=o)

@app.route('/rewardAnalytics')
def rewards_analytics():
    if not checkSession():
        return redirect('/login')
    o = rewards_redeemed()
    o.getRewardStats()
    return render_template('rewards_redeemed/rewards_analytics.html', title='Reward Analytics', obj=o)

@app.route('/dashboard')  #route name
def dashboard(): #view function
    return render_template('dashboard.html') 

# endpoint route for static files
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

#standalone function to be called when we need to check if a user is logged in.
def checkSession():
    if 'active' in session.keys():
        timeSinceAct = time.time() - session['active']
        print(timeSinceAct)
        if timeSinceAct > 500:
            session['msg'] = 'Your session has timed out.'
            return False
        else:
            session['active'] = time.time()
            return True
    else:
        return False      
  
if __name__ == '__main__':
   app.run(host='127.0.0.1',debug=True)   