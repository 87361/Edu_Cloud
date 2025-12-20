import logging
from sqlalchemy.orm import Session
from . import models
from .scraper import NotificationScraper

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def sync_notifications(db: Session, user_id: int, cas_user: str, cas_pass: str):
        """同步公告"""
        print(f"--- [Service] 开始同步公告 ---")
        
        scraper = NotificationScraper(cas_user, cas_pass)
        data_list = scraper.run()
        
        # 详细日志
        print(f"\n>>> 公告抓取清单 (共{len(data_list)}条) <<<")
        print(f"{'类型':<10} | {'标题':<15} | {'内容摘要'}")
        print("-" * 60)
        for item in data_list:
            content_short = (item.content[:20] + '..') if item.content else ""
            # 去除 HTML 标签让日志更好看 (简单处理)
            content_clean = content_short.replace("<span>", "").replace("</span>", "")
            print(f"{item.msg_type:<10} | {item.title[:12]:<15} | {content_clean}")
        print("-" * 60 + "\n")

        # 入库
        new_count = 0
        update_count = 0
        
        for item in data_list:
            exists = db.query(models.Notification).filter(models.Notification.id == item.id).first()
            
            if exists:
                # 更新阅读状态
                if exists.is_read != item.is_read:
                    exists.is_read = item.is_read
                    update_count += 1
            else:
                new_msg = models.Notification(
                    id=item.id,
                    owner_id=user_id,
                    title=item.title,
                    content=item.content,
                    msg_type=item.msg_type,
                    is_read=item.is_read,
                    publish_time=item.publish_time
                )
                db.add(new_msg)
                new_count += 1
                
        db.commit()
        return new_count, update_count, len(data_list)

    @staticmethod
    def get_user_notifications(db: Session, user_id: int):
        """获取本地列表"""
        return db.query(models.Notification)\
            .filter(models.Notification.owner_id == user_id)\
            .order_by(models.Notification.publish_time.desc())\
            .all()