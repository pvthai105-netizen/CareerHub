import os
import sys
from datetime import date, datetime, timedelta, timezone

# Đảm bảo đường dẫn import backend/app hoạt động trơn tru
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app.models  # noqa: F401 (nạp toàn bộ model để Base.metadata nhận đủ bảng)
from app.database import Base, SessionLocal, engine
from app.models.applications import Application, ApplicationStatus
from app.models.chat_messages import ChatMessage
from app.models.cv_analyses import CvAnalysis
from app.models.employee_profiles import EmployerProfile
from app.models.job import Job, JobStatus, JobType
from app.models.notifications import Notification
from app.models.saved_jobs import SavedJob
from app.models.student_profiles import DesiredJobType, StudentProfile
from app.models.user import Role, User
from app.security import hash_password

# ==========================================================
# 1. DANH SÁCH TÀI KHOẢN MẪU (ADMIN - DOANH NGHIỆP - SINH VIÊN)
# ==========================================================
SAMPLE_USERS = [
    # --- Quản trị viên ---
    {"email": "admin@careerhub.vn", "password": "Admin@123", "role": Role.admin},

    # --- Doanh nghiệp (Thương hiệu lớn, email định danh rõ ràng) ---
    {"email": "employer@careerhub.vn", "password": "Employer@123", "role": Role.employer},       # FPT Software (Mặc định)
    {"email": "careers@vng.com.vn", "password": "Employer@123", "role": Role.employer},          # VNG Corporation
    {"email": "recruitment@viettel.com.vn", "password": "Employer@123", "role": Role.employer},  # Viettel Solutions
    {"email": "talent@momo.vn", "password": "Employer@123", "role": Role.employer},              # MoMo (M-Service)
    {"email": "hr@techcombank.com.vn", "password": "Employer@123", "role": Role.employer},       # Techcombank

    # --- Sinh viên (Tên thật, chuyên ngành đa dạng, trường top) ---
    {"email": "student@careerhub.vn", "password": "Student@123", "role": Role.student},          # Nguyễn Văn An - ĐH Bách Khoa
    {"email": "ngoc.tran@careerhub.vn", "password": "Student@123", "role": Role.student},        # Trần Thị Bích Ngọc - ĐH Kinh tế Quốc dân
    {"email": "long.le@careerhub.vn", "password": "Student@123", "role": Role.student},          # Lê Hoàng Long - ĐH Kiến trúc
    {"email": "tuan.pham@careerhub.vn", "password": "Student@123", "role": Role.student},        # Phạm Minh Tuấn - Học viện PTIT
    {"email": "trang.dang@careerhub.vn", "password": "Student@123", "role": Role.student},       # Đặng Thùy Trang - ĐH Ngoại Thương
    {"email": "huy.vu@careerhub.vn", "password": "Student@123", "role": Role.student},           # Vũ Quang Huy - ĐH FPT
]


def clean_database(db):
    """Xóa sạch dữ liệu cũ theo đúng thứ tự khóa ngoại để nạp dữ liệu demo tinh gọn."""
    print("--- 0. LÀM SẠCH DỮ LIỆU CŨ TRONG DATABASE ---")
    db.query(ChatMessage).delete()
    db.query(CvAnalysis).delete()
    db.query(Notification).delete()
    db.query(SavedJob).delete()
    db.query(Application).delete()
    db.query(Job).delete()
    db.query(StudentProfile).delete()
    db.query(EmployerProfile).delete()
    db.query(User).delete()
    db.commit()
    print("[CLEAN] Đã dọn sạch các bảng dữ liệu cũ.")


def seed(clean: bool = True):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if clean:
            clean_database(db)

        print("\n--- 1. TẠO TÀI KHOẢN USERS ---")
        users_map = {}
        for data in SAMPLE_USERS:
            user = db.query(User).filter(User.email == data["email"]).first()
            if not user:
                user = User(
                    email=data["email"],
                    hashed_password=hash_password(data["password"]),
                    role=data["role"],
                    is_locked=False,
                )
                db.add(user)
                db.flush()
                print(f"[ADD] User: {data['email']} ({data['role'].value})")
            else:
                print(f"[EXISTS] User: {data['email']}")
            users_map[data["email"]] = user

        db.commit()

        # ==========================================================
        # 2. TẠO HỒ SƠ DOANH NGHIỆP (EMPLOYER PROFILES)
        # ==========================================================
        print("\n--- 2. TẠO HỒ SƠ DOANH NGHIỆP ---")
        employers_data = [
            {
                "email": "employer@careerhub.vn",
                "company_name": "Công ty Cổ phần Phần mềm FPT (FPT Software)",
                "contact_name": "Nguyễn Văn Tuyển",
                "phone": "02473007300",
                "company_website": "https://fptsoftware.com",
                "address": "Khu Công Nghệ Cao Hòa Lạc, Thạch Thất, Hà Nội",
                "description": "Tập đoàn công nghệ và chuyển đổi số hàng đầu Việt Nam, cung cấp giải pháp phần mềm toàn cầu trên 30 quốc gia.",
                "logo_url": "https://images.unsplash.com/photo-1549923746-c502d488b3ea?w=200",
                "tax_code": "0101234567",
                "is_verified": True,
            },
            {
                "email": "careers@vng.com.vn",
                "company_name": "Công ty Cổ phần VNG (VNG Corporation)",
                "contact_name": "Lê Thị Hồng",
                "phone": "02839623888",
                "company_website": "https://vng.com.vn",
                "address": "VNG Campus, Đường số 19, KCX Tân Thuận, Quận 7, TP. Hồ Chí Minh",
                "description": "Kỳ lân công nghệ đầu tiên tại Việt Nam, tiên phong trong mảng Trò chơi trực tuyến, Zalo, ZaloPay và AI Cloud.",
                "logo_url": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=200",
                "tax_code": "0303456789",
                "is_verified": True,
            },
            {
                "email": "recruitment@viettel.com.vn",
                "company_name": "Tổng Công ty Giải pháp Doanh nghiệp Viettel (Viettel Solutions)",
                "contact_name": "Trần Quốc Toản",
                "phone": "02462778899",
                "company_website": "https://viettelsolutions.vn",
                "address": "Số 1 Trần Hữu Dực, KĐT Mỹ Đình 2, Nam Từ Liêm, Hà Nội",
                "description": "Thành viên của Tập đoàn Viettel, tiên phong kiến tạo xã hội số với các giải pháp Cloud, IoT, Big Data, AI và Smart City.",
                "logo_url": "https://images.unsplash.com/photo-1560179707-f14e90ef3623?w=200",
                "tax_code": "0100109106",
                "is_verified": True,
            },
            {
                "email": "talent@momo.vn",
                "company_name": "Công ty Cổ phần Dịch vụ Di động Trực tuyến (Ví MoMo)",
                "contact_name": "Phạm Hoàng Nam",
                "phone": "02854147667",
                "company_website": "https://momo.vn",
                "address": "Lầu 6, Tòa nhà Phú Mỹ Hưng, 8 Hoàng Văn Thái, Quận 7, TP. Hồ Chí Minh",
                "description": "Kỳ lân FinTech hàng đầu Việt Nam cung cấp nền tảng siêu ứng dụng thanh toán, dịch vụ tài chính cho hơn 30 triệu người dùng.",
                "logo_url": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=200",
                "tax_code": "0305141933",
                "is_verified": True,
            },
            {
                "email": "hr@techcombank.com.vn",
                "company_name": "Ngân hàng TMCP Kỹ Thương Việt Nam (Techcombank)",
                "contact_name": "Đỗ Thu Hương",
                "phone": "02439446368",
                "company_website": "https://techcombank.com",
                "address": "Số 6 Quang Trung, P. Trần Hưng Đạo, Q. Hoàn Kiếm, Hà Nội",
                "description": "Ngân hàng số tiên phong chuyển đổi số với nền tảng công nghệ tài chính hiện đại hàng đầu khu vực Đông Nam Á.",
                "logo_url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=200",
                "tax_code": "0100230800",
                "is_verified": True,
            },
        ]

        for item in employers_data:
            user = users_map.get(item["email"])
            if user and not db.query(EmployerProfile).filter(EmployerProfile.user_id == user.id).first():
                profile = EmployerProfile(
                    user_id=user.id,
                    company_name=item["company_name"],
                    contact_name=item["contact_name"],
                    phone=item["phone"],
                    company_website=item["company_website"],
                    address=item["address"],
                    description=item["description"],
                    logo_url=item["logo_url"],
                    tax_code=item["tax_code"],
                    is_verified=item["is_verified"],
                )
                db.add(profile)
                print(f"[ADD] EmployerProfile: {item['company_name']}")

        db.commit()

        # ==========================================================
        # 3. TẠO HỒ SƠ SINH VIÊN (STUDENT PROFILES)
        # ==========================================================
        print("\n--- 3. TẠO HỒ SƠ SINH VIÊN ---")
        students_data = [
            {
                "email": "student@careerhub.vn",
                "full_name": "Nguyễn Văn An",
                "phone": "0901112233",
                "university": "Đại học Bách Khoa Hà Nội",
                "major": "Công nghệ thông tin (Khoa học Máy tính)",
                "bio": "Sinh viên năm cuối đam mê lập trình Backend và kiến trúc Microservices. Đã có 1 năm kinh nghiệm làm dự án thực tế với Python, FastAPI và Docker.",
                "skills": "Python, FastAPI, MySQL, Redis, Docker, Git, RESTful API",
                "desired_job_type": DesiredJobType.INTERNSHIP,
                "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200",
            },
            {
                "email": "ngoc.tran@careerhub.vn",
                "full_name": "Trần Thị Bích Ngọc",
                "phone": "0902223344",
                "university": "Đại học Kinh tế Quốc dân (NEU)",
                "major": "Digital Marketing & Truyền thông",
                "bio": "Năng động, sáng tạo, có tư duy số liệu tốt. Từng quản trị fanpage đạt 50k followers, thành thạo viết bài chuẩn SEO và xây dựng kế hoạch truyền thông.",
                "skills": "Content Marketing, SEO, Social Media, Google Analytics, Canva, Copywriting",
                "desired_job_type": DesiredJobType.PART_TIME,
                "avatar_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200",
            },
            {
                "email": "long.le@careerhub.vn",
                "full_name": "Lê Hoàng Long",
                "phone": "0903334455",
                "university": "Đại học Kiến trúc Hà Nội",
                "major": "Thiết kế Đồ họa & Đa phương tiện",
                "bio": "Đam mê thiết kế giao diện ứng dụng và trải nghiệm người dùng (UI/UX). Sở hữu tư duy thẩm mỹ cao và Portfolio trên Behance với hơn 10 dự án thiết kế.",
                "skills": "Figma, Adobe Photoshop, Illustrator, UI/UX Wireframing, Prototyping, Design Systems",
                "desired_job_type": DesiredJobType.BOTH,
                "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200",
            },
            {
                "email": "tuan.pham@careerhub.vn",
                "full_name": "Phạm Minh Tuấn",
                "phone": "0904445566",
                "university": "Học viện Công nghệ Bưu chính Viễn thông (PTIT)",
                "major": "Khoa học Dữ liệu & Trí tuệ nhân tạo",
                "bio": "Định hướng trở thành Data Analyst / Data Engineer. Nắm vững phân tích dữ liệu với SQL, thư viện Pandas và xây dựng Dashboard trực quan trên PowerBI.",
                "skills": "SQL, Python, Pandas, PowerBI, Tableau, Machine Learning Cơ bản, ETL",
                "desired_job_type": DesiredJobType.INTERNSHIP,
                "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200",
            },
            {
                "email": "trang.dang@careerhub.vn",
                "full_name": "Đặng Thùy Trang",
                "phone": "0905556677",
                "university": "Đại học Ngoại Thương (FTU)",
                "major": "Quản trị Kinh doanh & Nhân sự",
                "bio": "Kỹ năng giao tiếp và đàm phán xuất sắc. Mong muốn phát triển sự nghiệp trong mảng Tuyển dụng công nghệ (Tech Recruiter) và Quản trị nhân sự doanh nghiệp.",
                "skills": "Lọc CV, Phỏng vấn sơ bộ, Quản lý hồ sơ nhân sự, Tổ chức sự kiện tuyển dụng, Tiếng Anh IELTS 7.5",
                "desired_job_type": DesiredJobType.INTERNSHIP,
                "avatar_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200",
            },
            {
                "email": "huy.vu@careerhub.vn",
                "full_name": "Vũ Quang Huy",
                "phone": "0906667788",
                "university": "Đại học FPT Hà Nội",
                "major": "An toàn Thông tin (Cyber Security)",
                "bio": "Đam mê phân tích mã độc và giám sát an ninh mạng. Đạt chứng chỉ CEH và tích cực tham gia các giải đấu CTF sinh viên toàn quốc.",
                "skills": "Wireshark, Linux, Network Security, SOC Tier 1, Web Penetration Testing, Python Security",
                "desired_job_type": DesiredJobType.INTERNSHIP,
                "avatar_url": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=200",
            },
        ]

        for item in students_data:
            user = users_map.get(item["email"])
            if user and not db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first():
                profile = StudentProfile(
                    user_id=user.id,
                    full_name=item["full_name"],
                    phone=item["phone"],
                    university=item["university"],
                    major=item["major"],
                    bio=item["bio"],
                    skills=item["skills"],
                    desired_job_type=item["desired_job_type"],
                    avatar_url=item["avatar_url"],
                )
                db.add(profile)
                print(f"[ADD] StudentProfile: {item['full_name']}")

        db.commit()

        # ==========================================================
        # 4. TẠO 25 TIN TUYỂN DỤNG MẪU (20 ACTIVE, 3 DRAFT, 1 CLOSED, 1 EXPIRED)
        # ==========================================================
        print("\n--- 4. TẠO 25 TIN TUYỂN DỤNG (JOBS) ---")
        emp_fpt = users_map["employer@careerhub.vn"]
        emp_vng = users_map["careers@vng.com.vn"]
        emp_vtt = users_map["recruitment@viettel.com.vn"]
        emp_momo = users_map["talent@momo.vn"]
        emp_tcb = users_map["hr@techcombank.com.vn"]

        today = date.today()
        d_future_short = today + timedelta(days=20)
        d_future_med = today + timedelta(days=45)
        d_future_long = today + timedelta(days=60)
        d_past = today - timedelta(days=15)

        raw_jobs = [
            # --- 1. FPT Software (5 tin: 4 ACTIVE, 1 DRAFT) ---
            (emp_fpt.id, "Thực tập sinh Python/FastAPI Backend", "Tham gia phát triển hệ thống quản lý nhân sự và API Gateway cho khách hàng Nhật Bản. Được đào tạo chuyên sâu về Clean Architecture và Docker.", "Công nghệ thông tin", "Hà Nội", 4000000, 7000000, "INTERNSHIP", d_future_long, JobStatus.ACTIVE.value),
            (emp_fpt.id, "Thực tập sinh Frontend ReactJS", "Hỗ trợ xây dựng giao diện người dùng hiện đại, tối ưu tốc độ tải trang, ghép API và quản lý State với Redux Toolkit.", "Công nghệ thông tin", "Hà Nội", 3500000, 6500000, "INTERNSHIP", d_future_med, JobStatus.ACTIVE.value),
            (emp_fpt.id, "Thực tập sinh Kiểm thử phần mềm (Tester/QA)", "Viết testcase, thực hiện manual testing và phối hợp với đội ngũ lập trình viên ghi nhận lỗi qua Jira.", "Công nghệ thông tin", "Hà Nội", 3000000, 5500000, "INTERNSHIP", d_future_short, JobStatus.ACTIVE.value),
            (emp_fpt.id, "Kỹ sư Hệ thống Nhúng C++/Linux", "Nghiên cứu và phát triển phần mềm điều khiển nhúng trên nền tảng Linux cho các dự án ô tô thông minh (Automotive).", "Công nghệ thông tin", "Hà Nội", 5000000, 8000000, "INTERNSHIP", d_future_long, JobStatus.ACTIVE.value),
            (emp_fpt.id, "[Tin mới] Thực tập sinh Cloud & DevOps (AWS/Docker)", "Tham gia vận hành hạ tầng CI/CD pipeline, làm quen với dịch vụ AWS ECS/EC2 và tối ưu hóa hệ thống container.", "Công nghệ thông tin", "Hà Nội", 5000000, 8500000, "INTERNSHIP", d_future_long, JobStatus.DRAFT.value),

            # --- 2. VNG Corporation (5 tin: 4 ACTIVE, 1 DRAFT) ---
            (emp_vng.id, "Thực tập sinh Game Developer (Unity/C#)", "Phát triển các module gameplay 2D/3D trên nền tảng Unity, tối ưu hiệu năng đồ họa trên thiết bị di động iOS/Android.", "Công nghệ thông tin", "TP. Hồ Chí Minh", 5000000, 8000000, "INTERNSHIP", d_future_long, JobStatus.ACTIVE.value),
            (emp_vng.id, "Thực tập sinh UI/UX Mobile Product", "Nghiên cứu hành vi người dùng, thiết kế wireframe và prototype cho các tính năng mới của ứng dụng giải trí.", "Thiết kế", "TP. Hồ Chí Minh", 4000000, 7000000, "INTERNSHIP", d_future_med, JobStatus.ACTIVE.value),
            (emp_vng.id, "Nhân viên Content Marketing (Part-time)", "Lên ý tưởng kịch bản video ngắn TikTok, viết nội dung bài đăng trên Facebook Fanpage bắt trend giới trẻ.", "Marketing", "TP. Hồ Chí Minh", 3500000, 6000000, "PART_TIME", d_future_short, JobStatus.ACTIVE.value),
            (emp_vng.id, "Thực tập sinh Phân tích dữ liệu người dùng", "Truy vấn dữ liệu hành vi game thủ bằng SQL và Python, trực quan hóa các chỉ số tương tác và retention.", "Phân tích dữ liệu", "TP. Hồ Chí Minh", 4500000, 7500000, "INTERNSHIP", d_future_long, JobStatus.ACTIVE.value),
            (emp_vng.id, "[Tin mới] Thực tập sinh 3D Game Artist", "Vẽ texture, dựng model nhân vật và bối cảnh hoạt hình cho các dự án game mobile chuẩn bị ra mắt.", "Thiết kế", "TP. Hồ Chí Minh", 4000000, 6500000, "INTERNSHIP", d_future_med, JobStatus.DRAFT.value),

            # --- 3. Viettel Solutions (5 tin: 4 ACTIVE/CLOSED, 0 DRAFT) ---
            (emp_vtt.id, "Thực tập sinh An toàn thông tin (SOC Tier 1)", "Giám sát hệ thống cảnh báo bảo mật SIEM, điều tra log mạng và ứng phó các sự cố an ninh mạng cấp độ 1.", "An toàn thông tin", "Hà Nội", 5000000, 9000000, "INTERNSHIP", d_future_long, JobStatus.ACTIVE.value),
            (emp_vtt.id, "Thực tập sinh AI & Xử lý ngôn ngữ tự nhiên (NLP)", "Nghiên cứu các mô hình ngôn ngữ lớn (LLM), fine-tune trợ lý ảo phục vụ giải pháp chính phủ số.", "Trí tuệ nhân tạo", "Hà Nội", 6000000, 10000000, "INTERNSHIP", d_future_long, JobStatus.ACTIVE.value),
            (emp_vtt.id, "Thực tập sinh Kỹ sư Dữ liệu lớn (Big Data)", "Xây dựng các luồng thu thập và xử lý dữ liệu thời gian thực sử dụng Apache Spark, Kafka và Hadoop.", "Dữ liệu lớn", "Hà Nội", 5500000, 9000000, "INTERNSHIP", d_future_med, JobStatus.ACTIVE.value),
            (emp_vtt.id, "Nhân viên Kinh doanh Giải pháp số (Part-time)", "Tư vấn và giới thiệu giải pháp chữ ký số, hóa đơn điện tử và dịch vụ lưu trữ đám mây cho doanh nghiệp vừa và nhỏ.", "Kinh doanh / Bán hàng", "Hà Nội", 3000000, 6000000, "PART_TIME", d_future_short, JobStatus.ACTIVE.value),
            (emp_vtt.id, "Kỹ sư Mạng viễn thông 5G", "Tham gia cấu hình và thử nghiệm trạm phát sóng 5G băng thông rộng. Đã hoàn thành đợt tuyển dụng.", "Viễn thông", "Hà Nội", 6000000, 9000000, "INTERNSHIP", d_past, JobStatus.CLOSED.value),

            # --- 4. MoMo (M-Service) (5 tin: 4 ACTIVE, 1 DRAFT) ---
            (emp_momo.id, "Thực tập sinh Lập trình Di động (Flutter/iOS)", "Phát triển các tính năng thanh toán tiện ích và dịch vụ Mini-App trên hệ sinh thái siêu ứng dụng MoMo.", "Công nghệ thông tin", "TP. Hồ Chí Minh", 4500000, 7500000, "INTERNSHIP", d_future_long, JobStatus.ACTIVE.value),
            (emp_momo.id, "Thực tập sinh Backend Golang / Microservices", "Xây dựng API xử lý giao dịch tài chính tốc độ cao, đảm bảo tính nhất quán (ACID) và khả năng chịu tải hàng triệu request/ngày.", "Công nghệ thông tin", "TP. Hồ Chí Minh", 5000000, 8500000, "INTERNSHIP", d_future_long, JobStatus.ACTIVE.value),
            (emp_momo.id, "Nhân viên Hỗ trợ Thanh toán Ví điện tử (Part-time)", "Hỗ trợ tiếp nhận thắc mắc và giải đáp các vấn đề liên quan đến giao dịch ví của khách hàng.", "Dịch vụ khách hàng", "TP. Hồ Chí Minh", 3500000, 5500000, "PART_TIME", d_future_short, JobStatus.ACTIVE.value),
            (emp_momo.id, "Thực tập sinh Phân tích nghiệp vụ (BA Intern)", "Khảo sát yêu cầu người dùng, viết tài liệu đặc tả chức năng (SRS/BRD) cho tính năng thanh toán QR mới.", "Quản lý dự án", "TP. Hồ Chí Minh", 4000000, 6500000, "INTERNSHIP", d_future_med, JobStatus.ACTIVE.value),
            (emp_momo.id, "[Tin mới] Thực tập sinh Chống gian lận tài chính (Fraud)", "Phân tích các mẫu giao dịch bất thường, xây dựng bộ quy tắc cảnh báo phòng chống gian lận ví điện tử.", "An toàn thông tin", "TP. Hồ Chí Minh", 5000000, 8000000, "INTERNSHIP", d_future_med, JobStatus.DRAFT.value),

            # --- 5. Techcombank (5 tin: 4 ACTIVE/EXPIRED, 0 DRAFT) ---
            (emp_tcb.id, "Thực tập sinh Java Spring Boot (Ngân hàng số)", "Tham gia phát triển các dịch vụ Core Banking thế hệ mới trên nền tảng Java 17 và kiến trúc Cloud-native.", "Công nghệ thông tin", "Hà Nội", 5000000, 8000000, "INTERNSHIP", d_future_long, JobStatus.ACTIVE.value),
            (emp_tcb.id, "Thực tập sinh Quản trị rủi ro dữ liệu", "Phân tích dữ liệu tín dụng khách hàng cá nhân, hỗ trợ xây dựng mô hình xếp hạng rủi ro tự động.", "Kế toán / Tài chính", "Hà Nội", 4500000, 7500000, "INTERNSHIP", d_future_med, JobStatus.ACTIVE.value),
            (emp_tcb.id, "Chuyên viên CSKH Ngân hàng số (Part-time)", "Tư vấn mở tài khoản thanh toán và hỗ trợ hướng dẫn sử dụng ứng dụng Techcombank Mobile.", "Dịch vụ khách hàng", "Hà Nội", 4000000, 6000000, "PART_TIME", d_future_short, JobStatus.ACTIVE.value),
            (emp_tcb.id, "Thực tập sinh Tuyển dụng & Đào tạo (HR)", "Hỗ trợ đăng tin tuyển dụng, sàng lọc hồ sơ ứng viên và điều phối các lớp đào tạo nhân sự mới.", "Nhân sự", "Hà Nội", 3000000, 5000000, "INTERNSHIP", d_future_med, JobStatus.ACTIVE.value),
            (emp_tcb.id, "Thực tập sinh Tài chính doanh nghiệp", "Tham gia phân tích báo cáo tài chính của các doanh nghiệp đối tác. Đã hết hạn nộp hồ sơ.", "Kế toán / Tài chính", "Hà Nội", 3500000, 5500000, "INTERNSHIP", d_past, JobStatus.EXPIRED.value),
        ]

        jobs_list = []
        for emp_id, title, desc, ind, loc, s_min, s_max, j_type, d_line, st in raw_jobs:
            job = db.query(Job).filter(Job.title == title, Job.employer_id == emp_id).first()
            if not job:
                job = Job(
                    title=title,
                    description=desc,
                    industry=ind,
                    location=loc,
                    salary_min=s_min,
                    salary_max=s_max,
                    job_type=j_type,
                    deadline=d_line,
                    status=st,
                    employer_id=emp_id,
                )
                db.add(job)
                db.flush()
                print(f"[ADD] Job: {title} ({st})")
            jobs_list.append(job)

        db.commit()

        # ==========================================================
        # 5. TẠO 30 ĐƠN ỨNG TUYỂN (APPLICATIONS)
        # ==========================================================
        print("\n--- 5. TẠO 30 ĐƠN ỨNG TUYỂN (APPLICATIONS) ---")
        students = [
            users_map["student@careerhub.vn"],
            users_map["ngoc.tran@careerhub.vn"],
            users_map["long.le@careerhub.vn"],
            users_map["tuan.pham@careerhub.vn"],
            users_map["trang.dang@careerhub.vn"],
            users_map["huy.vu@careerhub.vn"],
        ]

        # Phân bổ trạng thái phong phú
        statuses_cycle = [
            ApplicationStatus.pending,
            ApplicationStatus.reviewed,
            ApplicationStatus.interview,
            ApplicationStatus.accepted,
            ApplicationStatus.pending,
            ApplicationStatus.rejected,
            ApplicationStatus.pending,
            ApplicationStatus.withdrawn,
            ApplicationStatus.interview,
            ApplicationStatus.reviewed,
        ]

        cover_letters = [
            "Em rất quan tâm đến vị trí này của công ty và tự tin kỹ năng bản thân sẽ đáp ứng tốt yêu cầu công việc.",
            "Với nền tảng học tập vững chắc và các dự án cá nhân thực tế, em hy vọng có cơ hội được học hỏi và cống hiến.",
            "Em xin gửi hồ sơ ứng tuyển kèm CV chi tiết, rất mong có cơ hội trao đổi trong buổi phỏng vấn sắp tới.",
            "Em đã tìm hiểu kỹ về văn hóa công ty và rất ấn tượng với môi trường chuyên nghiệp, mong muốn được gia nhập đội ngũ.",
        ]

        active_jobs = [j for j in jobs_list if j.status == JobStatus.ACTIVE.value]
        app_count = 0
        now_utc = datetime.now(timezone.utc)

        # Tạo 30 đơn ứng tuyển không trùng lặp (student_id, job_id)
        for i in range(30):
            job = active_jobs[i % len(active_jobs)]
            student = students[(i + (i // len(active_jobs))) % len(students)]
            status = statuses_cycle[i % len(statuses_cycle)]
            applied_time = now_utc - timedelta(days=(30 - i))

            exists = db.query(Application).filter(
                Application.job_id == job.job_id,
                Application.student_id == student.id,
            ).first()

            if not exists:
                app = Application(
                    job_id=job.job_id,
                    student_id=student.id,
                    status=status,
                    applied_at=applied_time,
                    cv_file_path=f"cv_{student.email.split('@')[0]}.pdf",
                    cover_letter=cover_letters[i % len(cover_letters)],
                )
                db.add(app)
                app_count += 1
                print(f"[ADD] Application #{app_count}: {student.email} -> Job #{job.job_id} ({status.value})")

        db.commit()

        # ==========================================================
        # 6. TẠO TIN ĐÃ LƯU (SAVED JOBS)
        # ==========================================================
        print("\n--- 6. TẠO TIN ĐÃ LƯU (SAVED JOBS) ---")
        saved_samples = [
            (students[0].id, active_jobs[0].job_id),
            (students[0].id, active_jobs[1].job_id),
            (students[0].id, active_jobs[11].job_id),
            (students[1].id, active_jobs[2].job_id),
            (students[1].id, active_jobs[7].job_id),
            (students[2].id, active_jobs[6].job_id),
            (students[2].id, active_jobs[1].job_id),
            (students[3].id, active_jobs[8].job_id),
            (students[3].id, active_jobs[12].job_id),
            (students[4].id, active_jobs[13].job_id),
            (students[5].id, active_jobs[10].job_id),
            (students[5].id, active_jobs[14].job_id),
        ]

        for stu_id, j_id in saved_samples:
            if not db.query(SavedJob).filter(SavedJob.user_id == stu_id, SavedJob.job_id == j_id).first():
                db.add(SavedJob(user_id=stu_id, job_id=j_id))
                print(f"[ADD] SavedJob: User #{stu_id} saved Job #{j_id}")

        db.commit()

        # ==========================================================
        # 7. TẠO LỊCH SỬ CHAT VỚI BOT TƯ VẤN (CHAT MESSAGES)
        # ==========================================================
        print("\n--- 7. TẠO LỊCH SỬ CHAT BOT ---")
        student_main = students[0]  # Nguyễn Văn An
        chat_samples = [
            ("user", "Chào bạn, mình là sinh viên năm cuối Bách Khoa ngành CNTT, mình muốn xin tư vấn chuẩn bị hồ sơ ứng tuyển vị trí Backend Python/FastAPI."),
            ("bot", "Chào bạn An! Với mục tiêu trở thành Backend Developer chuyên nghiệp, bạn nên tập trung vào 3 điểm cốt lõi trong CV:\n1. Nắm chắc kiến trúc RESTful API, ORM (SQLAlchemy) và tối ưu hóa câu truy vấn CSDL (đánh Index, tránh N+1 Query).\n2. Đưa vào CV các dự án cá nhân có sử dụng Docker, Redis Cache và viết Unit Test.\n3. Nêu rõ các số liệu định lượng về hiệu năng API bạn từng tối ưu (ví dụ: giảm thời gian phản hồi từ 200ms xuống 30ms)."),
            ("user", "Khi phỏng vấn vị trí Backend, nhà tuyển dụng thường hỏi những câu hỏi nào về Database vậy bạn?"),
            ("bot", "Các câu hỏi phỏng vấn CSDL rất phổ biến gồm có:\n1. Giải thích tính chất ACID trong giao dịch (Transaction).\n2. Phân biệt Index B-Tree và Hash Index; khi nào một câu truy vấn không tận dụng được Index?\n3. Cách giải quyết bài toán N+1 Query trong ORM (Eager Loading vs Lazy Loading).\n4. Sự khác biệt giữa NoSQL (Redis, MongoDB) và RDBMS (MySQL, PostgreSQL)."),
            ("user", "Cảm ơn bot nhiều nhé, thông tin rất hữu ích!"),
            ("bot", "Chúc bạn An tự tin và đạt kết quả xuất sắc trong buổi phỏng vấn sắp tới! Đừng quên theo dõi các tin tuyển dụng mới nhất từ FPT Software và MoMo trên CareerHub nhé."),
        ]

        for sender, msg in chat_samples:
            db.add(ChatMessage(user_id=student_main.id, sender=sender, message=msg))
            print(f"[ADD] ChatMessage ({sender}): {msg[:45]}...")

        db.commit()

        # ==========================================================
        # 8. TẠO LỊCH SỬ CHẤM ĐIỂM CV BẰNG AI (CV ANALYSES)
        # ==========================================================
        print("\n--- 8. TẠO ĐÁNH GIÁ CV (CV ANALYSES) ---")
        cv_samples = [
            (
                students[0].id,
                "https://careerhub.vn/uploads/cv/nguyen_van_an_backend.pdf",
                88.5,
                "Điểm mạnh: Cấu trúc hồ sơ chuẩn quốc tế, làm nổi bật kỹ năng lập trình Python/FastAPI và Docker. Dự án thực tế rõ ràng. Cần cải thiện: Hãy bổ sung các chỉ số đo lường hiệu năng (metrics) cho dự án cá nhân để tăng sức thuyết phục với nhà tuyển dụng.",
            ),
            (
                students[1].id,
                "https://careerhub.vn/uploads/cv/tran_thi_bich_ngoc_marketing.pdf",
                82.0,
                "Điểm mạnh: Kỹ năng viết Content và quản trị kênh truyền thông phong phú. Cần cải thiện: Nên đính kèm liên kết Portfolio tổng hợp các bài viết nổi bật và chiến dịch đã từng triển khai để nhà tuyển dụng đánh giá trực tiếp.",
            ),
            (
                students[2].id,
                "https://careerhub.vn/uploads/cv/le_hoang_long_designer.pdf",
                94.0,
                "Hồ sơ xuất sắc! Bố cục thẩm mỹ, link dự án Behance/Figma rất chi tiết, thể hiện tư duy thiết kế lấy người dùng làm trung tâm (User-Centered Design) đúng chuẩn UI/UX quốc tế.",
            ),
            (
                students[3].id,
                "https://careerhub.vn/uploads/cv/pham_minh_tuan_data.pdf",
                85.0,
                "Điểm mạnh: Nền tảng SQL và thư viện phân tích dữ liệu Pandas rất vững chắc. Cần cải thiện: Nên bổ sung thêm các chứng chỉ trực tuyến về Data Visualization (PowerBI / Tableau) để làm hồ sơ nổi bật hơn.",
            ),
            (
                students[4].id,
                "https://careerhub.vn/uploads/cv/dang_thuy_trang_hr.pdf",
                80.5,
                "Điểm mạnh: Kỹ năng giao tiếp và tiếng Anh tốt (IELTS 7.5). Cần cải thiện: Hãy nêu rõ hơn các hoạt động tổ chức sự kiện hoặc câu lạc bộ mà bạn từng tham gia điều phối.",
            ),
            (
                students[5].id,
                "https://careerhub.vn/uploads/cv/vu_quang_huy_security.pdf",
                87.0,
                "Điểm mạnh: Sở hữu chứng chỉ an ninh mạng quốc tế và có trải nghiệm thực chiến tại các cuộc thi CTF. Rất phù hợp với vị trí SOC Tier 1.",
            ),
        ]

        for s_id, url, score, fb in cv_samples:
            db.add(CvAnalysis(student_id=s_id, cv_file_url=url, score=score, feedback=fb))
            print(f"[ADD] CvAnalysis: Student #{s_id} - Score: {score}")

        db.commit()

        # ==========================================================
        # 9. TẠO THÔNG BÁO (NOTIFICATIONS)
        # ==========================================================
        print("\n--- 9. TẠO THÔNG BÁO (NOTIFICATIONS) ---")
        notif_samples = [
            (students[0].id, "Ứng tuyển thành công", "Bạn đã nộp đơn vào vị trí 'Thực tập sinh Python/FastAPI Backend' tại FPT Software."),
            (students[0].id, "Hồ sơ đã được xem", "Nhà tuyển dụng FPT Software đã mở xem hồ sơ ứng tuyển của bạn."),
            (students[0].id, "Mời phỏng vấn", "MoMo đã gửi lời mời bạn tham gia vòng phỏng vấn kỹ thuật trực tuyến."),
            (students[1].id, "Cập nhật trạng thái đơn", "Đơn ứng tuyển 'Content Marketing' của bạn tại VNG đã chuyển sang trạng thái: Đã xem xét."),
            (students[2].id, "Chúc mừng trúng tuyển", "VNG Corporation chúc mừng bạn đã xuất sắc trúng tuyển vị trí 'Thực tập sinh UI/UX Mobile Product'!"),
            (students[5].id, "Lịch phỏng vấn an ninh mạng", "Viettel Solutions trân trọng mời bạn tham gia phỏng vấn vị trí SOC Tier 1 vào sáng thứ Sáu."),
            (emp_fpt.id, "Có ứng viên mới", "Ứng viên Nguyễn Văn An vừa nộp đơn vào vị trí Thực tập sinh Python/FastAPI Backend."),
            (emp_vng.id, "Có ứng viên mới", "Ứng viên Lê Hoàng Long vừa nộp hồ sơ ứng tuyển vị trí Thực tập sinh UI/UX Mobile Product."),
            (emp_momo.id, "Có ứng viên mới", "Ứng viên Nguyễn Văn An vừa ứng tuyển vị trí Backend Golang / Microservices."),
            (emp_tcb.id, "Có ứng viên mới", "Ứng viên Đặng Thùy Trang vừa nộp đơn vào vị trí Thực tập sinh Tuyển dụng & Đào tạo."),
        ]

        for u_id, title, message in notif_samples:
            db.add(Notification(user_id=u_id, title=title, message=message, is_read=False))
            print(f"[ADD] Notification: User #{u_id} - {title}")

        db.commit()
        print("\n=== TẤT CẢ DỮ LIỆU SEED ĐÃ HOÀN TẤT THÀNH CÔNG ===")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed(clean=True)
