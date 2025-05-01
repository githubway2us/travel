import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from extensions import db  # นำเข้า db จาก extensions
from models import Province  # นำเข้าโมเดล Province

# สร้างแอป Flask สำหรับบริบท
app = Flask(__name__)

# กำหนดค่า config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # ป้องกัน warning

# เริ่มต้น SQLAlchemy
db.init_app(app)

# ฟังก์ชันสำหรับเริ่มต้นฐานข้อมูล
def init_database():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()  # สร้างตารางทั้งหมดตามโมเดล

        # ตรวจสอบว่ามีจังหวัดในฐานข้อมูลหรือไม่
        if not Province.query.first():
            print("Adding initial provinces...")
            provinces = [
                'กรุงเทพมหานคร', 'กระบี่', 'กาญจนบุรี', 'กาฬสินธุ์', 'กำแพงเพชร',
                'ขอนแก่น', 'จันทบุรี', 'ฉะเชิงเทรา', 'ชลบุรี', 'ชัยนาท',
                'ชัยภูมิ', 'ชุมพร', 'เชียงราย', 'เชียงใหม่', 'ตรัง',
                'ตราด', 'ตาก', 'นครนายก', 'นครปฐม', 'นครพนม',
                'นครราชสีมา', 'นครศรีธรรมราช', 'นครสวรรค์', 'นนทบุรี', 'นราธิวาส',
                'น่าน', 'บึงกาฬ', 'บุรีรัมย์', 'ปทุมธานี', 'ประจวบคีรีขันธ์',
                'ปราจีนบุรี', 'ปัตตานี', 'พระนครศรีอยุธยา', 'พังงา', 'พัทลุง',
                'พิจิตร', 'พิษณุโลก', 'เพชรบุรี', 'เพชรบูรณ์', 'แพร่',
                'พะเยา', 'ภูเก็ต', 'มหาสารคาม', 'มุกดาหาร', 'แม่ฮ่องสอน',
                'ยโสธร', 'ยะลา', 'ร้อยเอ็ด', 'ระนอง', 'ระยอง',
                'ราชบุรี', 'ลพบุรี', 'ลำปาง', 'ลำพูน', 'เลย',
                'ศรีสะเกษ', 'สกลนคร', 'สงขลา', 'สตูล', 'สมุทรปราการ',
                'สมุทรสาคร', 'สมุทรสงคราม', 'สระแก้ว', 'สระบุรี', 'สิงห์บุรี',
                'สุโขทัย', 'สุพรรณบุรี', 'สุราษฎร์ธานี', 'สุรินทร์', 'หนองคาย',
                'หนองบัวลำภู', 'อ่างทอง', 'อุดรธานี', 'อุตรดิตถ์', 'อุทัยธานี',
                'อุบลราชธานี', 'อำนาจเจริญ'
            ]
            for name in provinces:
                db.session.add(Province(name=name))
            db.session.commit()
            print(f"Added {len(provinces)} provinces to the database")
        else:
            print("Provinces already exist in the database.")

if __name__ == '__main__':
    init_database()