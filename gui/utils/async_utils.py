"""
异步工具模块
使用线程池执行耗时操作，避免阻塞GUI主线程
"""
import threading
from typing import Callable, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import queue

class AsyncExecutor:
    """异步执行器，使用线程池执行耗时操作"""
    
    def __init__(self, max_workers: int = 3):
        """
        初始化异步执行器
        
        Args:
            max_workers: 最大工作线程数
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._running_tasks = set()
    
    def submit(
        self,
        func: Callable,
        *args,
        on_success: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        **kwargs
    ):
        """
        提交异步任务
        
        Args:
            func: 要执行的函数
            *args: 函数位置参数
            on_success: 成功回调函数，接收函数返回值
            on_error: 错误回调函数，接收异常对象
            **kwargs: 函数关键字参数
        
        Returns:
            Future对象
        """
        def task_wrapper():
            try:
                result = func(*args, **kwargs)
                if on_success:
                    # 在主线程中执行回调
                    self._schedule_callback(on_success, result)
                return result
            except Exception as e:
                if on_error:
                    self._schedule_callback(on_error, e)
                else:
                    print(f"异步任务执行失败: {e}")
                raise
        
        future = self.executor.submit(task_wrapper)
        self._running_tasks.add(future)
        future.add_done_callback(lambda f: self._running_tasks.discard(f))
        return future
    
    def _schedule_callback(self, callback: Callable, arg: Any):
        """在主线程中调度回调（需要GUI框架支持）"""
        # 这个方法需要在GUI主循环中调用
        # 对于tkinter/customtkinter，需要使用after()方法
        # 这里只提供接口，具体实现由调用者处理
        callback(arg)
    
    def shutdown(self, wait: bool = True):
        """关闭执行器"""
        self.executor.shutdown(wait=wait)

# 全局异步执行器实例
async_executor = AsyncExecutor(max_workers=3)

