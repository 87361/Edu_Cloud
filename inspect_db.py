import sys
import os

# 确保能导入 src 模块
sys.path.append(os.getcwd())

from sqlalchemy import text
from src.edu_cloud.common.database import SessionLocal
from src.edu_cloud.user.models import User
from src.edu_cloud.assignment.models import Assignment
from src.edu_cloud.course.models import Course, CourseResource
from src.edu_cloud.discussion.models import DiscussionTopic
from src.edu_cloud.notification.models import Notification

def print_header(title):
    print("\n" + "="*60)
    print(f"  📂 {title}")
    print("="*60)

def print_row(cols, widths):
    row_str = " | ".join([str(c).ljust(w) for c, w in zip(cols, widths)])
    print(row_str)

def inspect_all():
    db = SessionLocal()
    try:
        # 1. 用户表
        print_header("Users (本地用户)")
        users = db.query(User).all()
        print(f"总数: {len(users)}")
        if users:
            print_row(["ID", "用户名", "Role"], [5, 15, 10])
            print("-" * 40)
            for u in users:
                print_row([u.id, u.username, u.role], [5, 15, 10])

        # 2. 作业表
        print_header("Assignments (作业)")
        assigns = db.query(Assignment).all()
        print(f"总数: {len(assigns)}")
        if assigns:
            print_row(["课程名", "作业标题", "状态", "分数"], [20, 30, 8, 5])
            print("-" * 75)
            for a in assigns[:10]: # 只打印前10条防止刷屏
                title = (a.title[:28] + "..") if len(a.title) > 28 else a.title
                cname = (a.course_name[:18] + "..") if a.course_name and len(a.course_name) > 18 else str(a.course_name)
                status = "已交" if a.is_submitted else "未交"
                print_row([cname, title, status, a.score or "-"], [20, 30, 8, 5])
            if len(assigns) > 10: print(f"... 还有 {len(assigns)-10} 条 ...")

        # 3. 课程表
        print_header("Courses (课程)")
        courses = db.query(Course).all()
        print(f"总数: {len(courses)}")
        if courses:
            print_row(["ID", "课程名称", "教师"], [20, 25, 10])
            print("-" * 65)
            for c in courses:
                print_row([c.id, c.name[:23], c.teacher], [20, 25, 10])

        # 4. 课程资源表
        print_header("Course Resources (课件/PPT)")
        res = db.query(CourseResource).all()
        print(f"总数: {len(res)}")
        if res:
            print_row(["类型", "大小", "文件名"], [6, 10, 40])
            print("-" * 65)
            for r in res[:10]:
                print_row([r.file_type, r.file_size, r.title[:38]], [6, 10, 40])

        # 5. 讨论区
        print_header("Discussions (讨论帖)")
        topics = db.query(DiscussionTopic).all()
        print(f"总数: {len(topics)}")
        if topics:
            print_row(["回复数", "发帖人", "标题"], [8, 15, 30])
            print("-" * 60)
            for t in topics[:10]:
                print_row([t.reply_count, t.author_name, t.title[:28]], [8, 15, 30])

        # 6. 公告表 (新增)
        print_header("Notifications (系统公告)")
        notifs = db.query(Notification).all()
        print(f"总数: {len(notifs)}")
        if notifs:
            print_row(["类型", "已读", "时间", "标题"], [15, 6, 18, 20])
            print("-" * 70)
            for n in notifs[:10]: # 只看前10条
                time_str = n.publish_time.strftime("%m-%d %H:%M") if n.publish_time else "-"
                read_status = "是" if n.is_read else "否"
                print_row([n.msg_type, read_status, time_str, n.title[:18]], [15, 6, 18, 20])
            if len(notifs) > 10: print(f"... 还有 {len(notifs)-10} 条 ...")

    except Exception as e:
        print(f"\n❌ 查询出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    inspect_all()