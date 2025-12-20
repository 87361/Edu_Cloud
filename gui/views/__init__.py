"""视图层"""
from .login_window import LoginWindow
from .main_window import MainWindow
from .assignment_list_interface import AssignmentListInterface
from .assignment_detail_interface import AssignmentDetailInterface

__all__ = [
    "LoginWindow",
    "MainWindow",
    "AssignmentListInterface",
    "AssignmentDetailInterface",
]
