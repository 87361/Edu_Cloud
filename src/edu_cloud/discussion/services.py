# 业务逻辑(sync_discussions)
import logging
from sqlalchemy.orm import Session
from . import models
from .scraper import DiscussionScraper
from ..course.models import Course  # 需要用来关联课程名

logger = logging.getLogger(__name__)

class DiscussionService:
    """
    讨论区业务逻辑
    """

    @staticmethod
    def sync_discussions(db: Session, cas_user: str, cas_pass: str):
        """
        同步流程：抓取 -> 打印日志 -> 存库
        注意：讨论区是公开的，不属于特定“用户”，而是属于“课程”。
        """
        print(f"--- [Service] 开始同步讨论区数据 ---")
        
        # 1. 调用爬虫
        scraper = DiscussionScraper(cas_user, cas_pass)
        topic_list = scraper.run()
        
        # 2. 【详细日志】打印抓取结果
        print(f"\n>>> 讨论区抓取清单 (共{len(topic_list)}个主题) <<<")
        print(f"{'课程ID':<20} | {'回复数':<6} | {'发帖人':<10} | {'标题'}")
        print("-" * 70)
        
        total_posts_count = 0
        for topic in topic_list:
            post_count = len(topic.posts)
            total_posts_count += post_count
            title_short = (topic.title[:20] + '..') if len(topic.title) > 20 else topic.title
            print(f"{topic.course_id:<20} | {post_count:<6} | {topic.author_name:<10} | {title_short}")
        print("-" * 70 + "\n")

        # 3. 存入数据库
        new_topic_count = 0
        new_post_count = 0
        
        for item in topic_list:
            # --- A. 处理主题 (Topic) ---
            db_topic = db.query(models.DiscussionTopic).filter(models.DiscussionTopic.id == item.id).first()
            
            if db_topic:
                # 更新动态数据
                db_topic.view_count = item.view_count
                db_topic.reply_count = item.reply_count
                db_topic.like_count = item.like_count
            else:
                # 新增
                new_topic = models.DiscussionTopic(
                    id=item.id,
                    course_id=item.course_id,
                    title=item.title,
                    author_name=item.author_name,
                    content=item.content,
                    view_count=item.view_count,
                    reply_count=item.reply_count,
                    like_count=item.like_count,
                    created_at=item.created_at
                )
                db.add(new_topic)
                new_topic_count += 1
            
            # --- B. 处理回复 (Posts) ---
            for post in item.posts:
                db_post = db.query(models.DiscussionPost).filter(models.DiscussionPost.id == post.id).first()
                if not db_post:
                    new_post = models.DiscussionPost(
                        id=post.id,
                        topic_id=item.id, # 关联外键
                        author_name=post.author_name,
                        content=post.content,
                        floor=post.floor,
                        created_at=post.created_at
                    )
                    db.add(new_post)
                    new_post_count += 1

        db.commit()
        
        return {
            "total_topics": len(topic_list),
            "new_topics": new_topic_count,
            "total_posts_found": total_posts_count,
            "new_posts_added": new_post_count
        }

    @staticmethod
    def get_course_topics(db: Session, course_id: str):
        """获取某门课的讨论列表"""
        return db.query(models.DiscussionTopic)\
            .filter(models.DiscussionTopic.course_id == course_id)\
            .order_by(models.DiscussionTopic.created_at.desc())\
            .all()

    @staticmethod
    def get_topic_detail(db: Session, topic_id: str):
        """获取单个帖子详情及其回复"""
        topic = db.query(models.DiscussionTopic).filter(models.DiscussionTopic.id == topic_id).first()
        if not topic:
            return None, []
            
        posts = db.query(models.DiscussionPost)\
            .filter(models.DiscussionPost.topic_id == topic_id)\
            .order_by(models.DiscussionPost.floor.asc())\
            .all()
            
        return topic, posts