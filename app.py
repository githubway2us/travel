from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from extensions import db  # นำเข้า db ที่อยู่ใน extensions
from models import User, Province, TravelPlan, Activity, Comment, Like, PukTransaction  # นำเข้าโมเดล

# สร้างแอป Flask
app = Flask(__name__)

# กำหนดค่าต่าง ๆ สำหรับแอป
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# ตั้งค่าและเชื่อมต่อกับฐานข้อมูล
db.init_app(app)

@app.before_request
def create_tables():
    print("กำลังกระทำการสร้างตารางในฐานข้อมูล...")
    db.create_all()

print("เริ่มต้นแอป...")
print("SQLAlchemy initialized")


print("Models imported")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_plan_by_id(plan_id):
    plan = db.session.get(TravelPlan, plan_id)
    if not plan:
        abort(404, description="ไม่พบแผนการท่องเที่ยว")
    return plan

@app.context_processor
def inject_user():
    user = None
    puk_coins = 0
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])
        if user:
            puk_coins = user.puk_coins
        else:
            session.pop('user_id', None)
    return dict(current_user=user, puk_coins=puk_coins)
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/')
def index():
    provinces = Province.query.all()
    regions = {
        'ภาคเหนือ': [
            'เชียงใหม่', 'เชียงราย', 'ลำปาง', 'ลำพูน', 'แม่ฮ่องสอน', 'น่าน',
            'พะเยา', 'แพร่', 'อุตรดิตถ์'
        ],
        'ภาคตะวันออกเฉียงเหนือ': [
            'อำนาจเจริญ', 'บึงกาฬ', 'บุรีรัมย์', 'ชัยภูมิ', 'กาฬสินธุ์', 'ขอนแก่น',
            'เลย', 'มหาสารคาม', 'มุกดาหาร', 'นครพนม', 'นครราชสีมา', 'หนองบัวลำภู',
            'หนองคาย', 'ร้อยเอ็ด', 'สกลนคร', 'ศรีสะเกษ', 'สุรินทร์', 'อุบลราชธานี',
            'อุดรธานี', 'ยโสธร'
        ],
        'ภาคกลาง': [
            'อ่างทอง', 'พระนครศรีอยุธยา', 'ชัยนาท', 'กรุงเทพมหานคร', 'ลพบุรี',
            'นครปฐม', 'นนทบุรี', 'ปทุมธานี', 'สมุทรปราการ', 'สมุทรสาคร',
            'สมุทรสงคราม', 'สระบุรี', 'สิงห์บุรี', 'สุพรรณบุรี'
        ],
        'ภาคตะวันออก': [
            'ชลบุรี', 'จันทบุรี', 'ฉะเชิงเทรา', 'ปราจีนบุรี', 'ระยอง', 'สระแก้ว', 'ตราด'
        ],
        'ภาคตะวันตก': [
            'กาญจนบุรี', 'เพชรบุรี', 'ประจวบคีรีขันธ์', 'ราชบุรี', 'ตาก'
        ],
        'ภาคใต้': [
            'ชุมพร', 'กระบี่', 'นครศรีธรรมราช', 'นราธิวาส', 'ปัตตานี', 'พังงา',
            'พัทลุง', 'ภูเก็ต', 'ระนอง', 'สตูล', 'สงขลา', 'สุราษฎร์ธานี', 'ตรัง', 'ยะลา'
        ]
    }
    region_provinces = {region: [] for region in regions}
    for province in provinces:
        post_count = TravelPlan.query.filter_by(province_id=province.id).count()
        province_data = {
            'id': province.id,
            'name': province.name,
            'post_count': post_count
        }
        for region, province_names in regions.items():
            if province.name in province_names:
                region_provinces[region].append(province_data)
    return render_template('index.html', region_provinces=region_provinces)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, puk_coins=100)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('สมัครสมาชิกสำเร็จ! กรุณาล็อกอิน')
            return redirect(url_for('login'))
        except:
            flash('ชื่อผู้ใช้นี้มีอยู่แล้ว')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('ล็อกอินสำเร็จ!')
            return redirect(url_for('index'))
        flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('ล็อกเอาท์สำเร็จ!')
    return redirect(url_for('index'))

@app.route('/post', methods=['GET', 'POST'])
def post():
    if 'user_id' not in session:
        flash('กรุณาล็อกอินก่อน')
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('เซสชันไม่ถูกต้อง กรุณาล็อกอินใหม่')
        return redirect(url_for('login'))
    provinces = Province.query.all()
    selected_province_id = request.args.get('province_id', type=int)
    if request.method == 'POST':
        print("Form data:", request.form.to_dict())
        print("Files:", request.files.to_dict())
        province_id = request.form['province_id']
        name = request.form['name']
        location = request.form['location']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        activity_count = max([int(key.split('[')[1].split(']')[0]) for key in request.form if key.startswith('activities[')] + [-1]) + 1
        max_activities = 50
        if activity_count > max_activities:
            flash(f'ไม่สามารถเพิ่มกิจกรรมเกิน {max_activities} รายการได้')
            return redirect(url_for('post', province_id=province_id))
        
        print(f"Received {activity_count} activities")
        new_plan = TravelPlan(
            user_id=session['user_id'],
            province_id=province_id,
            name=name,
            location=location,
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(new_plan)
        db.session.commit()
        total_budget = 0
        saved_activities = 0
        for index in range(activity_count):
            time = request.form.get(f'activities[{index}][time]', '')
            detail = request.form.get(f'activities[{index}][detail]', '')
            budget = request.form.get(f'activities[{index}][budget]', '')
            file = request.files.get(f'activities[{index}][image]')
            print(f"Activity {index}: time={time}, detail={detail}, budget={budget}, image={file.filename if file else None}")
            if time or detail or budget or (file and allowed_file(file.filename)):
                try:
                    budget_value = float(budget) if budget else 0
                except ValueError:
                    budget_value = 0
                activity = Activity(
                    travel_plan_id=new_plan.id,
                    time=time,
                    detail=detail,
                    budget=budget_value
                )
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    activity.image_path = filename
                db.session.add(activity)
                total_budget += budget_value
                saved_activities += 1
            else:
                print(f"Skipped activity {index}: no valid data")
        if saved_activities == 0:
            db.session.delete(new_plan)
            db.session.commit()
            flash('กรุณากรอกข้อมูลอย่างน้อยหนึ่งกิจกรรม')
            return redirect(url_for('post', province_id=province_id))
        new_plan.total_budget = total_budget
        user.puk_coins += 2  # เพิ่ม 2 เหรียญ PUK สำหรับการโพสต์
        db.session.commit()
        print(f"Saved plan {new_plan.id} with {saved_activities} activities, awarded 2 PUK coins to user {user.username}")
        flash(f'โพสต์แผนการท่องเที่ยวสำเร็จ! บันทึก {saved_activities} กิจกรรม และได้รับ 2 เหรียญ PUK')
        return redirect(url_for('province', province_id=province_id))
    return render_template('post.html', provinces=provinces, selected_province_id=selected_province_id)

@app.route('/add_plan', methods=['GET', 'POST'])
def add_plan():
    if 'user_id' not in session:
        flash('กรุณาล็อกอินก่อน')
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('เซสชันไม่ถูกต้อง กรุณาล็อกอินใหม่')
        return redirect(url_for('login'))
    provinces = Province.query.all()
    selected_province_id = request.args.get('province_id', type=int)
    if request.method == 'POST':
        print("Form data:", request.form.to_dict())
        print("Files:", request.files.to_dict())
        province_id = request.form['province_id']
        name = request.form['name']
        location = request.form['location']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        activity_count = max([int(key.split('[')[1].split(']')[0]) for key in request.form if key.startswith('activities[')] + [-1]) + 1
        max_activities = 50
        if activity_count > max_activities:
            flash(f'ไม่สามารถเพิ่มกิจกรรมเกิน {max_activities} รายการได้')
            return redirect(url_for('add_plan', province_id=province_id))
        
        print(f"Received {activity_count} activities")
        new_plan = TravelPlan(
            user_id=session['user_id'],
            province_id=province_id,
            name=name,
            location=location,
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(new_plan)
        db.session.commit()
        total_budget = 0
        saved_activities = 0
        for index in range(activity_count):
            time = request.form.get(f'activities[{index}][time]', '')
            detail = request.form.get(f'activities[{index}][detail]', '')
            budget = request.form.get(f'activities[{index}][budget]', '')
            file = request.files.get(f'activities[{index}][image]')
            print(f"Activity {index}: time={time}, detail={detail}, budget={budget}, image={file.filename if file else None}")
            if time or detail or budget or (file and allowed_file(file.filename)):
                try:
                    budget_value = float(budget) if budget else 0
                except ValueError:
                    budget_value = 0
                activity = Activity(
                    travel_plan_id=new_plan.id,
                    time=time,
                    detail=detail,
                    budget=budget_value
                )
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    activity.image_path = filename
                db.session.add(activity)
                total_budget += budget_value
                saved_activities += 1
            else:
                print(f"Skipped activity {index}: no valid data")
        if saved_activities == 0:
            db.session.delete(new_plan)
            db.session.commit()
            flash('กรุณากรอกข้อมูลอย่างน้อยหนึ่งกิจกรรม')
            return redirect(url_for('add_plan', province_id=province_id))
        new_plan.total_budget = total_budget
        user.puk_coins += 2  # เพิ่ม 2 เหรียญ PUK สำหรับการโพสต์
        db.session.commit()
        print(f"Saved plan {new_plan.id} with {saved_activities} activities, awarded 2 PUK coins to user {user.username}")
        flash(f'เพิ่มแผนการท่องเที่ยวสำเร็จ! บันทึก {saved_activities} กิจกรรม และได้รับ 2 เหรียญ PUK')
        return redirect(url_for('province', province_id=province_id))
    return render_template('add_plan.html', provinces=provinces, selected_province_id=selected_province_id)

@app.route('/edit_plan/<int:plan_id>', methods=['GET', 'POST'])
def edit_plan(plan_id):
    if 'user_id' not in session:
        flash('กรุณาล็อกอินก่อน')
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('เซสชันไม่ถูกต้อง กรุณาล็อกอินใหม่')
        return redirect(url_for('login'))
    plan = db.session.get(TravelPlan, plan_id)
    if not plan or plan.user_id != user.id:
        flash('คุณไม่มีสิทธิ์แก้ไขแผนนี้')
        return redirect(url_for('province', province_id=plan.province_id))
    provinces = Province.query.all()
    if request.method == 'POST':
        print("Form data:", request.form.to_dict())
        print("Files:", request.files.to_dict())
        plan.province_id = request.form['province_id']
        plan.name = request.form['name']
        plan.location = request.form['location']
        plan.start_date = request.form['start_date']
        plan.end_date = request.form['end_date']
        
        Activity.query.filter_by(travel_plan_id=plan_id).delete()
        activity_count = max([int(key.split('[')[1].split(']')[0]) for key in request.form if key.startswith('activities[')] + [-1]) + 1
        max_activities = 50
        if activity_count > max_activities:
            flash(f'ไม่สามารถเพิ่มกิจกรรมเกิน {max_activities} รายการได้')
            return redirect(url_for('edit_plan', plan_id=plan_id))
        
        print(f"Received {activity_count} activities for edit")
        total_budget = 0
        saved_activities = 0
        for index in range(activity_count):
            time = request.form.get(f'activities[{index}][time]', '')
            detail = request.form.get(f'activities[{index}][detail]', '')
            budget = request.form.get(f'activities[{index}][budget]', '')
            file = request.files.get(f'activities[{index}][image]')
            print(f"Activity {index}: time={time}, detail={detail}, budget={budget}, image={file.filename if file else None}")
            if time or detail or budget or (file and allowed_file(file.filename)):
                try:
                    budget_value = float(budget) if budget else 0
                except ValueError:
                    budget_value = 0
                activity = Activity(
                    travel_plan_id=plan_id,
                    time=time,
                    detail=detail,
                    budget=budget_value
                )
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    activity.image_path = filename
                db.session.add(activity)
                total_budget += budget_value
                saved_activities += 1
            else:
                print(f"Skipped activity {index}: no valid data")
        if saved_activities == 0:
            flash('กรุณากรอกข้อมูลอย่างน้อยหนึ่งกิจกรรม')
            return redirect(url_for('edit_plan', plan_id=plan_id))
        plan.total_budget = total_budget
        try:
            db.session.commit()
            print(f"Saved plan {plan.id} with {saved_activities} activities")
            flash(f'แก้ไขแผนการท่องเที่ยวสำเร็จ! บันทึก {saved_activities} กิจกรรม')
            return redirect(url_for('province', province_id=plan.province_id))
        except Exception as e:
            db.session.rollback()
            flash('เกิดข้อผิดพลาดในการบันทึกข้อมูล')
            print(f"Error: {str(e)}")
            return redirect(url_for('edit_plan', plan_id=plan_id))
    return render_template('edit_plan.html', plan=plan, provinces=provinces)

@app.route('/province/<int:province_id>')
def province(province_id):
    province = db.session.get(Province, province_id) or Province.query.get_or_404(province_id)
    page = request.args.get('page', 1, type=int)
    plans = TravelPlan.query.filter_by(province_id=province_id).options(db.joinedload(TravelPlan.activities)).paginate(page=page, per_page=10, error_out=False)
    for plan in plans.items:  # Use .items to access the plans on the current page
        print(f"Plan {plan.id} has {len(plan.activities)} activities")
        for activity in plan.activities:
            print(f"Activity: time={activity.time}, detail={activity.detail}, budget={activity.budget}")
    return render_template('province.html', province=province, plans=plans)

@app.route('/plan/<int:plan_id>')
def plan_detail(plan_id):
    plan = get_plan_by_id(plan_id)
    transactions = PukTransaction.query.filter_by(travel_plan_id=plan_id).all()
    return render_template('plan_detail.html', plan=plan, transactions=transactions)

@app.route('/plan/<int:plan_id>/delete', methods=['POST'])
def delete_plan(plan_id):
    if 'user_id' not in session:
        flash('กรุณาล็อกอินก่อน')
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('เซสชันไม่ถูกต้อง กรุณาล็อกอินใหม่')
        return redirect(url_for('login'))
    plan = get_plan_by_id(plan_id)
    if plan.user_id != user.id:
        flash('คุณไม่สามารถลบโพสต์นี้ได้')
        return redirect(url_for('province', province_id=plan.province_id))
    
    # ตรวจสอบว่าเหรียญ PUK เพียงพอหรือไม่
    if user.puk_coins < 10:
        flash('เหรียญ PUK ไม่เพียงพอสำหรับการลบโพสต์ (ต้องใช้ 10 เหรียญ)')
        return redirect(url_for('province', province_id=plan.province_id))
    
    # หัก 10 เหรียญ PUK
    user.puk_coins -= 10
    db.session.delete(plan)
    db.session.commit()
    
    print(f"Deleted plan {plan_id} by user {user.username}, deducted 10 PUK coins. Remaining: {user.puk_coins}")
    flash('โพสต์ถูกลบเรียบร้อย! ใช้ 10 เหรียญ PUK')
    return redirect(url_for('province', province_id=plan.province_id))

@app.route('/plan/<int:plan_id>/comment', methods=['POST'])
def comment(plan_id):
    if 'user_id' not in session:
        flash('กรุณาล็อกอินก่อน')
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('เซสชันไม่ถูกต้อง กรุณาล็อกอินใหม่')
        return redirect(url_for('login'))
    comment_text = request.form['comment']
    if comment_text:
        new_comment = Comment(
            travel_plan_id=plan_id,
            user_id=session['user_id'],
            comment=comment_text
        )
        db.session.add(new_comment)
        db.session.commit()
        flash('แสดงความคิดเห็นสำเร็จ!')
    plan = db.session.get(TravelPlan, plan_id) or TravelPlan.query.get_or_404(plan_id)
    return redirect(url_for('province', province_id=plan.province_id))

@app.route('/plan/<int:plan_id>/like', methods=['POST'])
def like(plan_id):
    if 'user_id' not in session:
        flash('กรุณาล็อกอินก่อน')
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('เซสชันไม่ถูกต้อง กรุณาล็อกอินใหม่')
        return redirect(url_for('login'))
    existing_like = Like.query.filter_by(travel_plan_id=plan_id, user_id=session['user_id']).first()
    if not existing_like:
        new_like = Like(travel_plan_id=plan_id, user_id=session['user_id'])
        db.session.add(new_like)
        db.session.commit()
        flash('กดไลก์สำเร็จ!')
    else:
        flash('คุณกดไลก์โพสต์นี้แล้ว')
    plan = db.session.get(TravelPlan, plan_id) or TravelPlan.query.get_or_404(plan_id)
    return redirect(url_for('province', province_id=plan.province_id))

@app.route('/plan/<int:plan_id>/send_puk', methods=['POST'])
def send_puk(plan_id):
    if 'user_id' not in session:
        flash('กรุณาล็อกอินก่อน')
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('เซสชันไม่ถูกต้อง กรุณาล็อกอินใหม่')
        return redirect(url_for('login'))
    amount = int(request.form['amount'])
    plan = db.session.get(TravelPlan, plan_id) or TravelPlan.query.get_or_404(plan_id)
    if user.puk_coins < amount:
        flash('เหรียญ PUK ไม่เพียงพอ')
        return redirect(url_for('province', province_id=plan.province_id))
    user.puk_coins -= amount
    receiver = db.session.get(User, plan.user_id)
    if not receiver:
        flash('ไม่พบผู้รับ กรุณาลองใหม่')
        return redirect(url_for('province', province_id=plan.province_id))
    receiver.puk_coins += amount
    transaction = PukTransaction(
        travel_plan_id=plan_id,
        sender_id=user.id,
        receiver_id=receiver.id,
        amount=amount
    )
    db.session.add(transaction)
    db.session.commit()
    flash(f'ส่ง {amount} PUK สำเร็จ!')
    return redirect(url_for('province', province_id=plan.province_id))

@app.route('/leaderboard')
def leaderboard():
    top_senders = db.session.query(
        User.username, db.func.sum(PukTransaction.amount).label('total_sent')
    ).join(PukTransaction, User.id == PukTransaction.sender_id)\
     .group_by(User.id)\
     .order_by(db.desc('total_sent'))\
     .limit(10).all()
    return render_template('leaderboard.html', top_senders=top_senders)

@app.route('/transactions')
def transactions():
    if 'user_id' not in session:
        flash('กรุณาล็อกอินก่อน')
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('เซสชันไม่ถูกต้อง กรุณาล็อกอินใหม่')
        return redirect(url_for('login'))
    transactions = PukTransaction.query.filter(
        (PukTransaction.sender_id == user.id) | (PukTransaction.receiver_id == user.id)
    ).order_by(PukTransaction.created_at.desc()).all()
    return render_template('transactions.html', transactions=transactions)

@app.template_filter('format_number')
def format_number(value, precision=2):
    try:
        formatted = f"{float(value):,.{precision}f}"
        return formatted
    except (ValueError, TypeError):
        return value

@app.template_filter('floatformat')
def floatformat(value, precision=2):
    try:
        return f"{float(value):.{precision}f}"
    except (ValueError, TypeError):
        return value

# ... (ส่วนบนเหมือนเดิม)

# ... (ส่วนบนของโค้ดเหมือนเดิม)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=2000)

# ไม่ต้องมีส่วน else สำหรับ Gunicorn เพราะการตั้งค่าฐานข้อมูลย้ายไป init_db.py แล้ว
