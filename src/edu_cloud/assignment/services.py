# src/edu_cloud/assignment/services.py
import logging
from sqlalchemy.orm import Session
from . import models
from .scraper import AssignmentScraper

# 配置日志
logger = logging.getLogger(__name__)

class AssignmentService:
    """
    业务逻辑层：负责协调 爬虫 和 数据库
    """
    
    @staticmethod
    def sync_assignments(db: Session, user_id: int, cas_user: str, cas_pass: str):
        """
        核心同步逻辑
        """
        # 1. 调用 Scraper 抓数据
        print(f"--- [Service] 开始为用户(ID:{user_id}) 同步作业 ---")
        scraper = AssignmentScraper(cas_user, cas_pass)
        data_list = scraper.run()
        
        # 2. 【详细日志】在这里打印抓取到的所有内容
        print(f"\n>>> 抓取结果清单 (共{len(data_list)}条) <<<")
        print(f"{'课程':<15} | {'状态':<8} | {'分数':<5} | {'作业标题'}")
        print("-" * 60)
        for item in data_list:
            status = "已交" if item.is_submitted else "未交"
            print(f"{item.course_name[:12]:<15} | {status:<8} | {item.score:<5} | {item.title}")
        print("-" * 60 + "\n")

        # 3. 存入数据库 (逻辑从 api.py 移过来)
        new_count = 0
        update_count = 0
        
        for item in data_list:
            # 查重
            exists = db.query(models.Assignment).filter(
                models.Assignment.owner_id == user_id,
                models.Assignment.course_name == item.course_name,
                models.Assignment.title == item.title
            ).first()
            
            if exists:
                # 更新
                if (exists.is_submitted != item.is_submitted or 
                    exists.score != item.score or 
                    exists.description != item.description): # 描述变了也更新
                    
                    exists.is_submitted = item.is_submitted
                    exists.score = item.score
                    exists.deadline = item.deadline
                    exists.description = item.description
                    update_count += 1
            else:
                # 新增
                new_assign = models.Assignment(
                    owner_id=user_id,
                    course_name=item.course_name,
                    title=item.title,
                    description=item.description, # 详情存这里
                    deadline=item.deadline,
                    is_submitted=item.is_submitted,
                    score=item.score
                )
                db.add(new_assign)
                new_count += 1
                
        db.commit()
        return new_count, update_count, len(data_list)

    @staticmethod
    def get_assignment_detail(db: Session, assignment_id: int, user_id: int):
        """
        获取单个作业的详情
        """
        return db.query(models.Assignment).filter(
            models.Assignment.id == assignment_id,
            models.Assignment.owner_id == user_id
        ).first()