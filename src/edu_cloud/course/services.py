 # 负责协调：调爬虫 -> 打印日志 -> 存入数据库
import logging
from sqlalchemy.orm import Session
from . import models
from .scraper import CourseScraper

logger = logging.getLogger(__name__)

class CourseService:
    """
    课程模块业务逻辑：协调爬虫与数据库
    """

    @staticmethod
    def sync_courses(db: Session, user_id: int, cas_user: str, cas_pass: str):
        """
        执行同步：抓取 -> 打印日志 -> 存库 (课程 + 资源)
        """
        print(f"--- [Service] 开始同步课程数据 (用户ID: {user_id}) ---")
        
        # 1. 调用爬虫
        scraper = CourseScraper(cas_user, cas_pass)
        course_data_list = scraper.run()
        
        # 2. 【详细日志】打印抓取结果表格
        print(f"\n>>> 课程抓取清单 (共{len(course_data_list)}门) <<<")
        print(f"{'ID':<20} | {'课程名称':<20} | {'资源数':<5} | {'教师'}")
        print("-" * 70)
        
        total_res_count = 0
        for course in course_data_list:
            res_count = len(course.resources)
            total_res_count += res_count
            # 截断过长的名称防止表格乱掉
            c_name = (course.name[:18] + '..') if len(course.name) > 18 else course.name
            print(f"{course.site_id:<20} | {c_name:<20} | {res_count:<5} | {course.teacher_name}")
        print("-" * 70 + "\n")

        # 3. 存入数据库
        new_course_count = 0
        updated_course_count = 0
        new_res_count = 0
        
        for item in course_data_list:
            # --- A. 处理课程本身 ---
            db_course = db.query(models.Course).filter(models.Course.id == item.site_id).first()
            
            if db_course:
                # 更新逻辑
                db_course.name = item.name
                db_course.teacher = item.teacher_name
                db_course.pic_url = item.pic_url
                db_course.description = item.description
                # 还可以更新其他字段...
                updated_course_count += 1
            else:
                # 新增逻辑
                new_course = models.Course(
                    id=item.site_id,
                    owner_id=user_id,
                    name=item.name,
                    course_code=item.course_code,
                    term_name=item.term_name,
                    teacher=item.teacher_name,
                    dept_name=item.dept_name,
                    pic_url=item.pic_url,
                    description=item.description
                )
                db.add(new_course)
                new_course_count += 1
            
            # --- B. 处理课程下的资源 (Link Table) ---
            # 简单策略：遍历抓到的资源，逐个 Upsert (更新或插入)
            for res in item.resources:
                db_res = db.query(models.CourseResource).filter(models.CourseResource.id == res.resource_id).first()
                
                if not db_res:
                    new_res = models.CourseResource(
                        id=res.resource_id,
                        course_id=item.site_id, # 关联外键
                        title=res.title,
                        file_type=res.file_type,
                        file_size=res.file_size,
                        download_url=res.download_url,
                        parent_section=res.parent_section,
                        created_at=res.upload_time
                    )
                    db.add(new_res)
                    new_res_count += 1
                else:
                    # 如果资源已存在，更新一下链接（防止过期）
                    db_res.download_url = res.download_url

        db.commit()
        
        return {
            "total_courses": len(course_data_list),
            "new_courses": new_course_count,
            "updated_courses": updated_course_count,
            "total_resources_found": total_res_count,
            "new_resources_added": new_res_count
        }

    @staticmethod
    def get_course_resources(db: Session, course_id: str):
        """获取某门课的所有资源"""
        return db.query(models.CourseResource)\
            .filter(models.CourseResource.course_id == course_id)\
            .all()