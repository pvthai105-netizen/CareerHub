import app.models  # noqa: F401  (nạp mọi model để Base.metadata nhận đủ bảng)
from datetime import date, datetime, timedelta, timezone

from app.database import Base, SessionLocal, engine
from app.models.applications import Application, ApplicationStatus
from app.models.chat_messages import ChatMessage
from app.models.cv_analyses import CvAnalysis
from app.models.employee_profiles import EmployerProfile
from app.models.jobs import Job
from app.models.notifications import Notification
from app.models.save_jobs import SavedJob
from app.models.student_profiles import DesiredJobType, StudentProfile
from app.models.user import Role, User
from app.security import hash_password

# ==========================================================
# 1. TÀI KHOẢN MẪU (Bao gồm 3 user gốc + mở rộng)
# ==========================================================
SAMPLE_USERS = [
    {"email": "admin@careerhub.vn", "password": "Admin@123", "role": Role.admin},
    {"email": "employer@careerhub.vn", "password": "Employer@123", "role": Role.employer},
    {"email": "student@careerhub.vn", "password": "Student@123", "role": Role.student},
    # Tài khoản mở rộng để test dữ liệu đa dạng
    {"email": "vng@careerhub.vn", "password": "Employer@123", "role": Role.employer},
    {"email": "viettel@careerhub.vn", "password": "Employer@123", "role": Role.employer},
    {"email": "student2@careerhub.vn", "password": "Student@123", "role": Role.student},
    {"email": "student3@careerhub.vn", "password": "Student@123", "role": Role.student},
    {"email": "student4@careerhub.vn", "password": "Student@123", "role": Role.student},
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("--- 1. TẠO TÀI KHOẢN USERS ---")
        users_map = {}
        for data in SAMPLE_USERS:
            user = db.query(User).filter(User.email == data["email"]).first()
            if not user:
                user = User(
                    email=data["email"],
                    password_hash=hash_password(data["password"]),
                    role=data["role"],
                    is_locked=False,
                )
                db.add(user)
                db.flush()
                print(f"[ADD] User: {data['email']} ({data['role'].value})")
            else:
                print(f"[SKIP] User: {data['email']} đã tồn tại")
            users_map[data["email"]] = user

        db.commit()

        # ==========================================================
        # 2. TẠO HỒ SƠ DOANH NGHIỆP (EMPLOYER PROFILES)
        # ==========================================================
        print("\n--- 2. TẠO HỒ SƠ DOANH NGHIỆP ---")
        employers_data = [
            {
                "email": "employer@careerhub.vn",
                "company_name": "FPT Software",
                "contact_name": "Nguyễn Văn Tuyển",
                "phone": "0987654321",
                "company_website": "https://fptsoftware.com",
                "address": "Khu Công Nghệ Cao Hòa Lạc, Hà Nội",
                "description": "Tập đoàn công nghệ hàng đầu Việt Nam cung cấp giải pháp chuyển đổi số toàn cầu.",
                "logo_url": "https://images.unsplash.com/photo-1549923746-c502d488b3ea?w=150",
                "tax_code": "0101234567",
                "is_verified": True,
            },
            {
                "email": "vng@careerhub.vn",
                "company_name": "VNG Corporation",
                "contact_name": "Lê Thị Hồng",
                "phone": "0912345678",
                "company_website": "https://vng.com.vn",
                "address": "VNG Campus, Quận 7, TP. Hồ Chí Minh",
                "description": "Kỳ lân công nghệ đầu tiên tại Việt Nam với các sản phẩm Zalo, ZaloPay, Game.",
                "logo_url": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=150",
                "tax_code": "0303456789",
                "is_verified": True,
            },
            {
                "email": "viettel@careerhub.vn",
                "company_name": "Viettel Solutions",
                "contact_name": "Trần Quốc Toản",
                "phone": "0977889900",
                "company_website": "https://viettelsolutions.vn",
                "address": "Số 1 Trần Hữu Dực, Nam Từ Liêm, Hà Nội",
                "description": "Tổng Công ty Giải pháp Doanh nghiệp Viettel - tiên phong kiến tạo xã hội số.",
                "logo_url": "https://images.unsplash.com/photo-1560179707-f14e90ef3623?w=150",
                "tax_code": "0100109106",
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
                "phone": "0901112223",
                "university": "Đại học Bách Khoa Hà Nội",
                "major": "Công nghệ thông tin",
                "bio": "Sinh viên năm 3 đam mê lập trình Backend, ham học hỏi và có khả năng làm việc nhóm tốt.",
                "skills": "Python, FastAPI, MySQL, Docker, Git",
                "desired_job_type": DesiredJobType.INTERNSHIP,
                "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150",
            },
            {
                "email": "student2@careerhub.vn",
                "full_name": "Trần Thị Bích",
                "phone": "0902223334",
                "university": "Đại học Kinh tế Quốc dân",
                "major": "Marketing",
                "bio": "Năng động, sáng tạo, có kinh nghiệm quản trị Fanpage và viết Content chuẩn SEO.",
                "skills": "Content Writing, SEO, Canva, Social Media Management",
                "desired_job_type": DesiredJobType.PART_TIME,
                "avatar_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150",
            },
            {
                "email": "student3@careerhub.vn",
                "full_name": "Lê Hoàng Long",
                "phone": "0903334445",
                "university": "Đại học Kiến trúc Hà Nội",
                "major": "Thiết kế đồ họa",
                "bio": "Yêu thích UI/UX Design, có tư duy thẩm mỹ hiện đại và làm chủ bộ công cụ Adobe, Figma.",
                "skills": "Figma, Adobe Photoshop, Illustrator, UI/UX Wireframing",
                "desired_job_type": DesiredJobType.BOTH,
                "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150",
            },
            {
                "email": "student4@careerhub.vn",
                "full_name": "Phạm Minh Tuấn",
                "phone": "0904445556",
                "university": "Học viện Công nghệ Bưu chính Viễn thông",
                "major": "Khoa học máy tính",
                "bio": "Sinh viên năm cuối định hướng Data Analyst, nắm vững SQL và phân tích dữ liệu với Python.",
                "skills": "SQL, Python, Pandas, PowerBI, Machine Learning Cơ bản",
                "desired_job_type": DesiredJobType.INTERNSHIP,
                "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150",
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
        # 4. TẠO 22 TIN TUYỂN DỤNG MẪU (JOBS)
        # ==========================================================
        print("\n--- 4. TẠO TIN TUYỂN DỤNG (>= 20 JOBS) ---")
        emp1 = users_map["employer@careerhub.vn"]
        emp2 = users_map["vng@careerhub.vn"]
        emp3 = users_map["viettel@careerhub.vn"]

        raw_jobs = [
            (emp1.id, "Thực tập sinh Python/FastAPI", "Tham gia phát triển hệ thống backend, xây dựng RESTful API.", "Công nghệ thông tin", "Hà Nội", 4000000, 7000000, "Thực tập", date(2026, 12, 31)),
            (emp1.id, "Thực tập sinh Frontend ReactJS", "Hỗ trợ cắt giao diện, ghép API, tối ưu trải nghiệm người dùng.", "Công nghệ thông tin", "Hà Nội", 3500000, 6000000, "Thực tập", date(2026, 12, 15)),
            (emp1.id, "Thực tập sinh Kiểm thử phần mềm (Tester)", "Viết testcase, thực hiện manual test và báo cáo bug trên Jira.", "Công nghệ thông tin", "Hà Nội", 3000000, 5000000, "Thực tập", date(2026, 12, 20)),
            (emp1.id, "Thực tập sinh DevOps / Cloud", "Làm quen với Docker, CI/CD pipeline và hạ tầng đám mây AWS.", "Công nghệ thông tin", "Hà Nội", 5000000, 8000000, "Thực tập", date(2026, 12, 30)),
            (emp1.id, "Thực tập sinh Lập trình C++/Embedded", "Nghiên cứu và phát triển phần mềm nhúng trên hệ điều hành Linux.", "Công nghệ thông tin", "Hà Nội", 4500000, 7500000, "Thực tập", date(2026, 12, 25)),
            (emp1.id, "Thực tập sinh Tuyển dụng Nhân sự (HR Intern)", "Hỗ trợ lọc CV, liên hệ ứng viên và sắp xếp lịch phỏng vấn.", "Nhân sự", "Hà Nội", 2500000, 4000000, "Thực tập", date(2026, 12, 18)),
            (emp1.id, "Thực tập sinh Quản trị mạng (Network Admin)", "Cấu hình router/switch, hỗ trợ người dùng mạng nội bộ doanh nghiệp.", "Công nghệ thông tin", "Hà Nội", 3500000, 5500000, "Thực tập", date(2026, 12, 28)),

            (emp2.id, "Thực tập sinh Game Developer (Unity)", "Phát triển logic game 2D/3D cho di động trên nền tảng Unity/C#.", "Công nghệ thông tin", "TP. Hồ Chí Minh", 5000000, 8000000, "Thực tập", date(2026, 12, 30)),
            (emp2.id, "Thực tập sinh UI/UX Designer", "Thiết kế wireframe, prototype cho ứng dụng mobile bằng Figma.", "Thiết kế", "TP. Hồ Chí Minh", 4000000, 6500000, "Thực tập", date(2026, 12, 22)),
            (emp2.id, "Nhân viên Content Marketing (Part-time)", "Viết bài social media, kịch bản video ngắn cho sản phẩm công nghệ.", "Marketing", "TP. Hồ Chí Minh", 3000000, 5000000, "Bán thời gian", date(2026, 12, 10)),
            (emp2.id, "Thực tập sinh Data Analyst", "Xử lý dữ liệu hành vi người dùng bằng SQL, Python và vẽ dashboard.", "Phân tích dữ liệu", "TP. Hồ Chí Minh", 4500000, 7000000, "Thực tập", date(2026, 12, 31)),
            (emp2.id, "Nhân viên Chăm sóc khách hàng Game (Part-time)", "Giải đáp thắc mắc và hỗ trợ khiếu nại của game thủ qua ticket/livechat.", "Dịch vụ khách hàng", "TP. Hồ Chí Minh", 3500000, 5500000, "Bán thời gian", date(2026, 12, 15)),
            (emp2.id, "Thực tập sinh Thiết kế đồ họa 2D", "Thiết kế banner sự kiện, hình ảnh quảng cáo cho game và mạng xã hội.", "Thiết kế", "TP. Hồ Chí Minh", 3500000, 6000000, "Thực tập", date(2026, 12, 24)),
            (emp2.id, "Thực tập sinh Video Editor (TikTok/Reels)", "Cắt ghép video ngắn, hiệu ứng âm thanh và phụ đề bắt trend.", "Truyền thông", "TP. Hồ Chí Minh", 3000000, 5000000, "Bán thời gian", date(2026, 12, 25)),

            (emp3.id, "Thực tập sinh An toàn thông tin (SOC Tier 1)", "Giám sát cảnh báo an ninh mạng, phân tích log và nhận diện tấn công.", "An toàn thông tin", "Hà Nội", 5000000, 8500000, "Thực tập", date(2026, 12, 31)),
            (emp3.id, "Thực tập sinh Trí tuệ nhân tạo (AI/NLP)", "Nghiên cứu xử lý ngôn ngữ tự nhiên tiếng Việt cho chatbot thông minh.", "Trí tuệ nhân tạo", "Hà Nội", 6000000, 9000000, "Thực tập", date(2026, 12, 30)),
            (emp3.id, "Thực tập sinh Lập trình viên Java Backend", "Tham gia dự án giải pháp chính phủ điện tử sử dụng Spring Boot.", "Công nghệ thông tin", "Hà Nội", 4000000, 7000000, "Thực tập", date(2026, 12, 20)),
            (emp3.id, "Thực tập sinh Kế toán nội bộ", "Hỗ trợ sắp xếp hóa đơn, kiểm tra chứng từ và nhập liệu phần mềm kế toán.", "Kế toán / Tài chính", "Hà Nội", 2500000, 4500000, "Thực tập", date(2026, 12, 18)),
            (emp3.id, "Nhân viên Telesales Giải pháp số (Part-time)", "Gọi điện giới thiệu gói dịch vụ hóa đơn điện tử và chữ ký số cho doanh nghiệp.", "Kinh doanh / Bán hàng", "Hà Nội", 3000000, 6000000, "Bán thời gian", date(2026, 12, 15)),
            (emp3.id, "Thực tập sinh Kỹ sư Dữ liệu (Data Engineer)", "Xây dựng ETL pipeline vận chuyển dữ liệu lớn từ Kafka vào Data Lake.", "Dữ liệu lớn", "Hà Nội", 5500000, 8500000, "Thực tập", date(2026, 12, 31)),
            (emp3.id, "Thực tập sinh Digital Marketing (Google Ads)", "Hỗ trợ lên chiến dịch quảng cáo tìm kiếm và đo lường tỷ lệ chuyển đổi.", "Marketing", "Hà Nội", 3000000, 5500000, "Thực tập", date(2026, 12, 22)),
            (emp3.id, "Thực tập sinh Quản lý dự án (PMO Intern)", "Theo dõi tiến độ sprint, cập nhật tài liệu dự án và hỗ trợ Scrum Master.", "Quản lý dự án", "Hà Nội", 3500000, 6000000, "Thực tập", date(2026, 12, 25)),
        ]

        jobs_list = []
        for emp_id, title, desc, ind, loc, s_min, s_max, j_type, d_line in raw_jobs:
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
                    status="Đang tuyển",
                    employer_id=emp_id,
                )
                db.add(job)
                db.flush()
                print(f"[ADD] Job: {title}")
            jobs_list.append(job)

        db.commit()

        # ==========================================================
        # 5. TẠO ĐƠN ỨNG TUYỂN (>= 20 APPLICATIONS)
        # ==========================================================
        print("\n--- 5. TẠO ĐƠN ỨNG TUYỂN (>= 20 APPLICATIONS) ---")
        students = [
            users_map["student@careerhub.vn"],
            users_map["student2@careerhub.vn"],
            users_map["student3@careerhub.vn"],
            users_map["student4@careerhub.vn"],
        ]

        statuses = [
            ApplicationStatus.pending,
            ApplicationStatus.reviewed,
            ApplicationStatus.accepted,
            ApplicationStatus.rejected,
        ]

        app_count = 0
        for i, job in enumerate(jobs_list[:20]):
            # Phân bổ sinh viên xoay vòng để không bị trùng (job_id, student_id)
            student = students[i % len(students)]
            status = statuses[i % len(statuses)]
            
            exists = db.query(Application).filter(
                Application.job_id == job.job_id,
                Application.student_id == student.id,
            ).first()

            if not exists:
                app = Application(
                    job_id=job.job_id,
                    student_id=student.id,
                    status=status,
                    applied_at=datetime.now(timezone.utc) - timedelta(days=i),
                )
                db.add(app)
                app_count += 1
                print(f"[ADD] Application: Student {student.email} -> Job #{job.job_id} ({status.value})")

        # Thêm 2 đơn nữa cho đủ 22 đơn
        for j in range(20, min(22, len(jobs_list))):
            student = students[(j + 1) % len(students)]
            if not db.query(Application).filter(Application.job_id == jobs_list[j].job_id, Application.student_id == student.id).first():
                db.add(Application(
                    job_id=jobs_list[j].job_id,
                    student_id=student.id,
                    status=ApplicationStatus.pending,
                ))
                app_count += 1
                print(f"[ADD] Application: Student {student.email} -> Job #{jobs_list[j].job_id}")

        db.commit()

        # ==========================================================
        # 6. TẠO TIN ĐÃ LƯU (SAVED JOBS)
        # ==========================================================
        print("\n--- 6. TẠO TIN ĐÃ LƯU (SAVED JOBS) ---")
        saved_samples = [
            (students[0].id, jobs_list[0].job_id),
            (students[0].id, jobs_list[1].job_id),
            (students[0].id, jobs_list[3].job_id),
            (students[1].id, jobs_list[9].job_id),
            (students[1].id, jobs_list[13].job_id),
            (students[2].id, jobs_list[8].job_id),
            (students[2].id, jobs_list[12].job_id),
            (students[3].id, jobs_list[6].job_id),
            (students[3].id, jobs_list[10].job_id),
            (students[3].id, jobs_list[19].job_id),
        ]

        for stu_id, j_id in saved_samples:
            if not db.query(SavedJob).filter(SavedJob.student_id == stu_id, SavedJob.job_id == j_id).first():
                db.add(SavedJob(student_id=stu_id, job_id=j_id))
                print(f"[ADD] SavedJob: Student #{stu_id} saved Job #{j_id}")

        db.commit()

        # ==========================================================
        # 7. TẠO LỊCH SỬ CHAT VỚI BOT (CHAT MESSAGES)
        # ==========================================================
        print("\n--- 7. TẠO LỊCH SỬ CHAT BOT ---")
        student_main = students[0]
        chat_samples = [
            ("user", "Chào bạn, mình là sinh viên năm 3 ngành CNTT, mình muốn xin tư vấn chuẩn bị hồ sơ thực tập Backend."),
            ("bot", "Chào bạn! Với vị trí Thực tập sinh Backend, bạn cần chuẩn bị: 1. Nắm chắc một ngôn ngữ (như Python/Java/NodeJS); 2. Hiểu biết về RESTful API và cơ sở dữ liệu (MySQL); 3. Chuẩn bị 1-2 đồ án thực tế đưa lên GitHub."),
            ("user", "Nhà tuyển dụng thường hỏi những câu hỏi phỏng vấn SQL nào vậy bạn?"),
            ("bot", "Một số câu hỏi SQL rất hay gặp: 1. Phân biệt INNER JOIN và LEFT JOIN; 2. Chỉ mục (Index) là gì và khi nào nên đánh Index; 3. Sự khác nhau giữa WHERE và HAVING; 4. Cách tối ưu câu truy vấn khi dữ liệu lớn."),
            ("user", "Cảm ơn bot nhé!"),
            ("bot", "Chúc bạn sớm tìm được công việc thực tập như ý! Đừng quên nộp CV trực tiếp tại các tin tuyển dụng trên CareerHub nhé."),
        ]

        if not db.query(ChatMessage).filter(ChatMessage.user_id == student_main.id).first():
            for sender, msg in chat_samples:
                db.add(ChatMessage(user_id=student_main.id, sender=sender, message=msg))
                print(f"[ADD] ChatMessage ({sender}): {msg[:40]}...")

        db.commit()

        # ==========================================================
        # 8. TẠO LỊCH SỬ CHẤM ĐIỂM CV (CV ANALYSES)
        # ==========================================================
        print("\n--- 8. TẠO ĐÁNH GIÁ CV (CV ANALYSES) ---")
        cv_samples = [
            (
                students[0].id,
                "https://careerhub.vn/uploads/cv/nguyen_van_an_backend.pdf",
                85.0,
                "Điểm mạnh: Cấu trúc rõ ràng, kỹ năng Python/FastAPI tốt. Cần cải thiện: Hãy bổ sung các số liệu định lượng (metrics) cho đồ án cá nhân để tăng sức thuyết phục.",
            ),
            (
                students[1].id,
                "https://careerhub.vn/uploads/cv/tran_thi_bich_marketing.pdf",
                78.5,
                "Điểm mạnh: Kinh nghiệm viết Content phong phú. Cần cải thiện: Nên đính kèm link Portfolio các bài viết nổi bật để nhà tuyển dụng dễ tham khảo.",
            ),
            (
                students[2].id,
                "https://careerhub.vn/uploads/cv/le_hoang_long_designer.pdf",
                92.0,
                "Hồ sơ xuất sắc! Bố cục thẩm mỹ, link dự án Behance/Figma rất chi tiết và đúng chuẩn UI/UX quốc tế.",
            ),
            (
                students[3].id,
                "https://careerhub.vn/uploads/cv/pham_minh_tuan_data.pdf",
                82.0,
                "Nền tảng SQL và Python phân tích dữ liệu rất vững. Nên bổ sung thêm kỹ năng trực quan hóa dữ liệu qua Tableau hoặc PowerBI.",
            ),
        ]

        for s_id, url, score, fb in cv_samples:
            if not db.query(CvAnalysis).filter(CvAnalysis.student_id == s_id).first():
                db.add(CvAnalysis(student_id=s_id, cv_file_url=url, score=score, feedback=fb))
                print(f"[ADD] CvAnalysis: Student #{s_id} - Score: {score}")

        db.commit()

        # ==========================================================
        # 9. TẠO THÔNG BÁO (NOTIFICATIONS)
        # ==========================================================
        print("\n--- 9. TẠO THÔNG BÁO (NOTIFICATIONS) ---")
        notif_samples = [
            (students[0].id, "Ứng tuyển thành công", "Bạn đã nộp đơn vào vị trí 'Thực tập sinh Python/FastAPI' tại FPT Software."),
            (students[0].id, "Hồ sơ đã được xem", "Nhà tuyển dụng FPT Software đã mở xem hồ sơ của bạn."),
            (students[1].id, "Cập nhật trạng thái đơn", "Đơn ứng tuyển 'Content Marketing' của bạn đã chuyển sang trạng thái: Đã xem xét."),
            (emp1.id, "Có ứng viên mới", "Ứng viên Nguyễn Văn An vừa nộp đơn vào vị trí Thực tập sinh Python/FastAPI."),
            (emp2.id, "Có ứng viên mới", "Ứng viên Trần Thị Bích vừa nộp đơn vào vị trí Content Marketing."),
        ]

        for u_id, title, message in notif_samples:
            if not db.query(Notification).filter(Notification.user_id == u_id, Notification.title == title).first():
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
    seed()