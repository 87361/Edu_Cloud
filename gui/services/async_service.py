"""统一异步处理服务"""
from typing import Any, Callable, Optional, TypeVar
from PyQt6.QtCore import QObject, QThread, pyqtSignal

T = TypeVar("T")


class AsyncWorker(QObject):
    """异步工作线程"""

    finished = pyqtSignal(object)  # 成功结果
    error = pyqtSignal(str)  # 错误信息

    def __init__(self, func: Callable[[], T], parent: Optional[QObject] = None):
        """
        初始化异步工作线程

        Args:
            func: 要执行的函数
            parent: 父对象
        """
        super().__init__(parent)
        self.func = func

    def run(self) -> None:
        """执行函数"""
        try:
            result = self.func()
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class AsyncService(QObject):
    """异步服务基类"""

    def __init__(self, parent: Optional[QObject] = None):
        """
        初始化异步服务

        Args:
            parent: 父对象
        """
        super().__init__(parent)
        self._thread: Optional[QThread] = None
        self._worker: Optional[AsyncWorker] = None

    def execute_async(
        self,
        func: Callable[[], T],
        on_success: Optional[Callable[[T], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        异步执行函数

        Args:
            func: 要执行的函数
            on_success: 成功回调
            on_error: 错误回调
        """
        # 清理之前的线程
        self._cleanup_thread()

        # 创建新线程
        self._thread = QThread()
        self._worker = AsyncWorker(func)

        # 移动worker到线程
        self._worker.moveToThread(self._thread)

        # 连接信号
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)

        if on_success:
            self._worker.finished.connect(on_success)
        if on_error:
            self._worker.error.connect(on_error)

        # 启动线程
        self._thread.start()

    def execute_service_method(
        self,
        service_method: Callable[[], T],
        success_signal,
        error_signal,
    ) -> None:
        """
        执行Service方法并发送信号

        Args:
            service_method: Service方法
            success_signal: 成功信号
            error_signal: 错误信号
        """
        def wrapper() -> T:
            try:
                return service_method()
            except Exception as e:
                error_signal.emit(str(e))
                raise

        def on_success(result: T) -> None:
            success_signal.emit(result)

        def on_error(error_msg: str) -> None:
            error_signal.emit(error_msg)

        self.execute_async(wrapper, on_success, on_error)

    def _on_finished(self, result: Any) -> None:
        """处理完成"""
        self._cleanup_thread()

    def _on_error(self, error_msg: str) -> None:
        """处理错误"""
        self._cleanup_thread()

    def _cleanup_thread(self) -> None:
        """清理线程资源"""
        if self._thread and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait()
        self._thread = None
        self._worker = None

    def __del__(self) -> None:
        """析构函数，确保线程被清理"""
        self._cleanup_thread()

