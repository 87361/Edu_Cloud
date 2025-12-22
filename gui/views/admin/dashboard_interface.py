"""管理员仪表盘界面"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QColor

from qfluentwidgets import (
    TitleLabel,
    BodyLabel,
    CaptionLabel,
    CardWidget,
    ElevatedCardWidget,
    ProgressBar,
    IconWidget,
    FluentIcon as FIF,
)

from ...services.async_service import AsyncService
from ...api_client import api_client, APIError
from ...services.auth_service import AuthService


class StatCard(ElevatedCardWidget):
    """
    后台首页的数据统计卡片
    显示：图标 + 数值 + 标题 + 增长率
    """

    def __init__(self, icon, title, value, growth, color="#0078D4", parent=None):
        """
        初始化统计卡片

        Args:
            icon: 图标
            title: 标题
            value: 数值
            growth: 增长率（字符串，如 "+12%"）
            color: 颜色
            parent: 父组件
        """
        super().__init__(parent)
        self.setFixedSize(220, 140)

        # 布局
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(20, 20, 20, 20)

        # 顶部：图标 + 增长率
        top_layout = QHBoxLayout()
        self.icon_widget = IconWidget(icon, self)
        self.icon_widget.setFixedSize(24, 24)

        self.growth_lbl = CaptionLabel(growth, self)
        if "+" in growth:
            self.growth_lbl.setTextColor(QColor("#107C10"), QColor("#107C10"))  # 绿色
        else:
            self.growth_lbl.setTextColor(QColor("#E81123"), QColor("#E81123"))  # 红色

        top_layout.addWidget(self.icon_widget)
        top_layout.addStretch(1)
        top_layout.addWidget(self.growth_lbl)

        # 中间：数值
        self.value_lbl = TitleLabel(value, self)
        self.value_lbl.setStyleSheet("font-size: 32px; font-weight: bold;")

        # 底部：标题
        self.title_lbl = BodyLabel(title, self)
        self.title_lbl.setTextColor(QColor(120, 120, 120), QColor(160, 160, 160))

        self.v_layout.addLayout(top_layout)
        self.v_layout.addWidget(self.value_lbl)
        self.v_layout.addWidget(self.title_lbl)


class DashboardInterface(QWidget):
    """后台仪表盘界面"""

    def __init__(self, parent=None):
        """
        初始化仪表盘界面

        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.async_service = AsyncService()
        self._setup_ui()
        self._load_stats()
    
    def refresh_stats(self) -> None:
        """刷新统计信息（公共方法，供外部调用）"""
        self._load_stats()

    def _setup_ui(self) -> None:
        """设置UI"""
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(30, 30, 30, 30)
        self.v_layout.setSpacing(20)

        self.lbl_title = TitleLabel("系统概览", self)

        # 1. 统计卡片区
        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(15)

        # 初始化卡片（数据将从API加载）
        self.stat_cards = []
        stats_config = [
            (FIF.PEOPLE, "总用户数", "0", "+0%"),
            (FIF.EDUCATION, "活跃课程", "0", "+0%"),
            (FIF.DOCUMENT, "今日作业", "0", "+0%"),
            (FIF.FEEDBACK, "未读通知", "0", "+0%"),
        ]

        for icon, title, val, growth in stats_config:
            card = StatCard(icon, title, val, growth)
            self.stat_cards.append(card)
            self.cards_layout.addWidget(card)
        self.cards_layout.addStretch(1)  # 左对齐

        # 2. 存储空间使用情况
        self.chart_card = CardWidget(self)
        self.chart_card.setFixedHeight(300)
        chart_layout = QVBoxLayout(self.chart_card)
        chart_layout.setContentsMargins(30, 30, 30, 30)

        chart_layout.addWidget(BodyLabel("存储空间使用情况", self.chart_card))
        chart_layout.addSpacing(20)

        # 存储进度条（将从API加载数据）
        self.db_progress_items = []
        items = [("数据库", 0)]  # 初始值，将从API更新
        for name, val in items:
            h_layout = QHBoxLayout()
            lbl = BodyLabel(name, self.chart_card)
            lbl.setFixedWidth(150)
            pb = ProgressBar(self.chart_card)
            pb.setValue(val)
            self.db_progress_items.append((lbl, pb))
            h_layout.addWidget(lbl)
            h_layout.addWidget(pb)
            chart_layout.addLayout(h_layout)
            chart_layout.addSpacing(10)

        chart_layout.addStretch(1)

        self.v_layout.addWidget(self.lbl_title)
        self.v_layout.addLayout(self.cards_layout)
        self.v_layout.addWidget(self.chart_card)
        self.v_layout.addStretch(1)

    def _load_stats(self) -> None:
        """加载统计信息"""
        def load_func():
            try:
                return api_client.get_admin_stats()
            except APIError as e:
                # 如果API调用失败，使用默认值
                return {}
            except Exception:
                return {}

        def on_success(stats: dict):
            # 更新统计卡片
            # 1. 总用户数
            users_stats = stats.get("users", {})
            if users_stats:
                total_users = users_stats.get("total", 0)
                active_users = users_stats.get("active", 0)
                self.stat_cards[0].value_lbl.setText(f"{total_users:,}")
                # 显示活跃用户占比
                if total_users > 0:
                    active_ratio = int((active_users / total_users) * 100)
                    self.stat_cards[0].growth_lbl.setText(f"{active_ratio}%活跃")
                else:
                    self.stat_cards[0].growth_lbl.setText("+0%")

            # 2. 活跃课程
            courses_stats = stats.get("courses", {})
            if courses_stats:
                active_courses = courses_stats.get("active", 0)
                total_courses = courses_stats.get("total", 0)
                self.stat_cards[1].value_lbl.setText(f"{active_courses:,}")
                if total_courses > 0:
                    self.stat_cards[1].growth_lbl.setText(f"共{total_courses}门")
                else:
                    self.stat_cards[1].growth_lbl.setText("+0%")

            # 3. 今日作业
            assignments_stats = stats.get("assignments", {})
            if assignments_stats:
                today_assignments = assignments_stats.get("today", 0)
                total_assignments = assignments_stats.get("total", 0)
                self.stat_cards[2].value_lbl.setText(f"{today_assignments:,}")
                if total_assignments > 0:
                    self.stat_cards[2].growth_lbl.setText(f"共{total_assignments}个")
                else:
                    self.stat_cards[2].growth_lbl.setText("+0%")

            # 4. 未读通知
            notifications_stats = stats.get("notifications", {})
            if notifications_stats:
                unread_notifications = notifications_stats.get("unread", 0)
                total_notifications = notifications_stats.get("total", 0)
                self.stat_cards[3].value_lbl.setText(f"{unread_notifications:,}")
                if total_notifications > 0:
                    read_ratio = int(((total_notifications - unread_notifications) / total_notifications) * 100)
                    self.stat_cards[3].growth_lbl.setText(f"{read_ratio}%已读")
                else:
                    self.stat_cards[3].growth_lbl.setText("+0%")

            # 更新数据库大小显示
            database_stats = stats.get("database", {})
            if database_stats and self.db_progress_items:
                size_mb = database_stats.get("size_mb", 0)
                # 假设最大100MB，超过100MB显示100%
                max_size = 100
                if size_mb > max_size:
                    progress = 100
                    size_text = f"数据库 ({size_mb:.2f} MB)"
                else:
                    progress = int((size_mb / max_size) * 100)
                    size_text = f"数据库 ({size_mb:.2f} MB)"
                
                lbl, pb = self.db_progress_items[0]
                lbl.setText(size_text)
                pb.setValue(progress)

        self.async_service.execute_async(load_func, on_success, lambda e: None)


