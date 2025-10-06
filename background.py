import asyncio
from typing import Callable, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

class BackgroundTaskManager:
    def __init__(self, max_workers: int = 10):
        self.tasks: List[asyncio.Task] = []
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
    
    def add_task(self, coro: Callable, *args, **kwargs):
        """Add a background task"""
        task = asyncio.create_task(coro(*args, **kwargs))
        self.tasks.append(task)
        return task
    
    def run_in_thread(self, func: Callable, *args, **kwargs):
        """Run a function in thread pool"""
        return asyncio.get_event_loop().run_in_executor(
            self.thread_pool, func, *args, **kwargs
        )
    
    async def wait_all(self):
        """Wait for all tasks to complete"""
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
    
    def cleanup(self):
        """Cancel all tasks and shutdown thread pool"""
        for task in self.tasks:
            if not task.done():
                task.cancel()
        self.thread_pool.shutdown(wait=True)

def background_task(func: Callable):
    """Decorator to run function as background task"""
    def wrapper(*args, **kwargs):
        app = kwargs.get('app')
        if app and hasattr(app, 'background_tasks'):
            return app.background_tasks.add_task(func, *args, **kwargs)
        else:
            return asyncio.create_task(func(*args, **kwargs))
    return wrapper