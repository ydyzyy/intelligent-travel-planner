"""
智能旅行规划系统 - 一键启动脚本

功能：
1. 自动启动后端服务（FastAPI）
2. 自动启动前端服务（Vite）
3. 等待服务就绪
4. 自动打开浏览器
5. 确保终端退出时所有子进程都被清理
6. 恢复终端状态,防止出现退格符异常

使用方法：
    python start.py

或者直接双击运行（Windows）
"""

import subprocess
import sys
import os
import time
import webbrowser
import signal
import threading
import atexit
from pathlib import Path
from typing import Optional, Tuple


class TerminalRestorer:
    """终端状态恢复器(Windows专用)"""
    
    @staticmethod
    def restore_terminal():
        """恢复Windows终端状态,清除异常字符"""
        if sys.platform == "win32":
            try:
                # 方法1: 使用ctypes恢复控制台模式
                import ctypes
                import msvcrt
                
                # 清空输入缓冲区
                while msvcrt.kbhit():
                    msvcrt.getch()
                
                # 方法2: 发送一个回车符刷新命令行
                # 这可以清除残留的控制序列
                print("\n", end="", flush=True)
                
                # 方法3: 使用Windows API重置控制台
                kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                stdin_handle = kernel32.GetStdHandle(-10)  # STD_INPUT_HANDLE
                
                if stdin_handle and stdin_handle != -1:
                    # 刷新输入缓冲区
                    kernel32.FlushConsoleInputBuffer(stdin_handle)
                    
            except Exception as e:
                # 如果恢复失败,至少打印一个干净的换行
                print("\n", end="", flush=True)


class ServiceManager:
    """服务管理器"""
    
    def __init__(self):
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
        self.project_root = Path(__file__).parent
        self._cleanup_done = False
        self._terminal_restored = False
        
        # 注册退出处理函数
        atexit.register(self._cleanup_on_exit)
        
    def check_dependencies(self) -> bool:
        """检查依赖是否已安装"""
        print("🔍 检查依赖...")
        
        # 检查Python依赖
        backend_dir = self.project_root / "backend"
        if not (backend_dir / "app").exists():
            print("❌ 后端目录不存在")
            return False
        
        # 检查并安装后端Python依赖
        requirements_file = backend_dir / "requirements.txt"
        if requirements_file.exists():
            print("   检查后端Python依赖...")
            try:
                # 尝试导入关键模块来检查依赖是否已安装
                import uvicorn
                import fastapi
                import hello_agents
                print("   ✅ 后端依赖已安装")
            except ImportError as e:
                print(f"   ⚠️  后端依赖未完全安装，正在安装...")
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                        cwd=backend_dir,
                        check=True,
                        capture_output=False
                    )
                    print("   ✅ 后端依赖安装成功")
                except Exception as e:
                    print(f"   ❌ 后端依赖安装失败: {e}")
                    return False
        
        # 检查Node.js依赖
        frontend_dir = self.project_root / "frontend"
        if not (frontend_dir / "node_modules").exists():
            print("⚠️  前端依赖未安装，正在安装...")
            try:
                # Windows使用npm.cmd，其他系统使用npm
                npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
                
                subprocess.run(
                    [npm_cmd, "install"],
                    cwd=frontend_dir,
                    check=True,
                    capture_output=True
                )
                print("✅ 前端依赖安装成功")
            except Exception as e:
                print(f"❌ 前端依赖安装失败: {e}")
                return False
        
        print("✅ 依赖检查通过")
        return True
    
    def _read_output(self, process: subprocess.Popen, service_name: str):
        """读取进程输出的辅助方法"""
        for line in iter(process.stdout.readline, ''):
            if line:
                print(f"[{service_name}] {line.rstrip()}")
            else:
                break
    
    def start_backend(self) -> bool:
        """启动后端服务"""
        print("\n🚀 启动后端服务...")
        
        backend_dir = self.project_root / "backend"
        
        try:
            # Windows使用不同的命令
            if sys.platform == "win32":
                cmd = [
                    sys.executable, "-m", "uvicorn",
                    "app.api.main:app",
                    "--host", "0.0.0.0",
                    "--port", "8000"
                    # 移除--reload以加快启动速度
                ]
            else:
                cmd = [
                    sys.executable, "-m", "uvicorn",
                    "app.api.main:app",
                    "--host", "0.0.0.0",
                    "--port", "8000"
                    # 移除--reload以加快启动速度
                ]
            
            # 在Windows下使用CREATE_NEW_PROCESS_GROUP标志,确保进程可以独立终止
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
            
            self.backend_process = subprocess.Popen(
                cmd,
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=creationflags
            )
            
            # 启动线程读取输出,避免缓冲区阻塞
            output_thread = threading.Thread(
                target=self._read_output,
                args=(self.backend_process, "后端"),
                daemon=True
            )
            output_thread.start()
            
            print(f"✅ 后端进程已启动 (PID: {self.backend_process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ 后端启动失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def start_frontend(self) -> bool:
        """启动前端服务"""
        print("\n🎨 启动前端服务...")
        
        frontend_dir = self.project_root / "frontend"
        
        try:
            # Windows使用npm.cmd，其他系统使用npm
            npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
            
            # 在Windows下使用CREATE_NEW_PROCESS_GROUP标志,确保进程可以独立终止
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
            
            self.frontend_process = subprocess.Popen(
                [npm_cmd, "run", "dev"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=creationflags
            )
            
            # 启动线程读取输出,避免缓冲区阻塞
            output_thread = threading.Thread(
                target=self._read_output,
                args=(self.frontend_process, "前端"),
                daemon=True
            )
            output_thread.start()
            
            print(f"✅ 前端进程已启动 (PID: {self.frontend_process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ 前端启动失败: {e}")
            return False
    
    def wait_for_service(self, url: str, service_name: str, timeout: int = 60) -> bool:
        """等待服务就绪"""
        print(f"\n⏳ 等待{service_name}就绪...")
        
        import urllib.request
        import urllib.error
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = urllib.request.urlopen(url, timeout=2)
                if response.status == 200:
                    print(f"✅ {service_name}已就绪 ({url})")
                    return True
            except (urllib.error.URLError, ConnectionRefusedError, OSError):
                pass
            
            time.sleep(1)
            elapsed = int(time.time() - start_time)
            if elapsed % 5 == 0:
                print(f"   等待中... ({elapsed}秒)")
        
        print(f"❌ {service_name}启动超时")
        return False
    
    def health_check(self) -> bool:
        """健康检查"""
        print("\n🏥 执行健康检查...")
        
        # 检查后端
        backend_ready = self.wait_for_service(
            "http://localhost:8000/health",
            "后端服务",
            timeout=30
        )
        
        if not backend_ready:
            return False
        
        # 检查前端（Vite启动较快，通常5-10秒）
        frontend_ready = self.wait_for_service(
            "http://localhost:5173",
            "前端服务",
            timeout=30
        )
        
        return frontend_ready
    
    def open_browser(self):
        """打开浏览器"""
        print("\n🌐 打开浏览器...")
        webbrowser.open("http://localhost:5173")
    
    def print_banner(self):
        """打印欢迎信息"""
        print("\n" + "="*70)
        print("🌍 智能旅行规划助手 - 一键启动")
        print("="*70)
        print("💡 提示:")
        print("   - 后端服务: http://localhost:8000")
        print("   - 前端界面: http://localhost:5173")
        print("   - API文档:  http://localhost:8000/docs")
        print("   - 按 Ctrl+C 停止所有服务")
        print("="*70 + "\n")
    
    def _terminate_process(self, process: subprocess.Popen, service_name: str):
        """终止单个进程及其子进程"""
        if not process:
            return
        
        try:
            pid = process.pid
            
            # Windows下特殊处理
            if sys.platform == "win32":
                # 首先尝试优雅终止
                process.terminate()
                
                # 等待进程结束
                try:
                    process.wait(timeout=5)
                    print(f"✅ {service_name}已停止 (PID: {pid})")
                    return
                except subprocess.TimeoutExpired:
                    pass
                
                # 如果超时,强制终止整个进程树
                print(f"⚠️  {service_name}未响应,强制终止...")
                try:
                    # 使用taskkill命令终止进程树
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(pid)],
                        capture_output=True,
                        timeout=5
                    )
                    print(f"✅ {service_name}已强制停止 (PID: {pid})")
                except Exception as e:
                    print(f"⚠️  强制终止{service_name}失败: {e}")
                    process.kill()
            else:
                # Unix/Linux/macOS系统
                import signal
                
                # 首先尝试优雅终止
                process.terminate()
                
                try:
                    process.wait(timeout=5)
                    print(f"✅ {service_name}已停止 (PID: {pid})")
                    return
                except subprocess.TimeoutExpired:
                    pass
                
                # 如果超时,强制终止
                print(f"⚠️  {service_name}未响应,强制终止...")
                process.kill()
                process.wait(timeout=3)
                print(f"✅ {service_name}已强制停止 (PID: {pid})")
                
        except Exception as e:
            print(f"⚠️  停止{service_name}时出错: {e}")
            try:
                process.kill()
            except:
                pass
    
    def stop_services(self):
        """停止所有服务"""
        # 防止重复清理
        if self._cleanup_done:
            return
        
        self._cleanup_done = True
        
        print("\n\n🛑 正在停止服务...")
        
        # 先停止前端,再停止后端
        if self.frontend_process:
            self._terminate_process(self.frontend_process, "前端服务")
            self.frontend_process = None
        
        if self.backend_process:
            self._terminate_process(self.backend_process, "后端服务")
            self.backend_process = None
        
        print("👋 感谢使用智能旅行规划助手！\n")
        
        # 恢复终端状态(Windows专用)
        if sys.platform == "win32" and not self._terminal_restored:
            self._terminal_restored = True
            TerminalRestorer.restore_terminal()
    
    def _cleanup_on_exit(self):
        """退出时清理资源(由atexit调用)"""
        if not self._cleanup_done:
            print("\n检测到程序退出,清理子进程...")
            self.stop_services()
        elif sys.platform == "win32" and not self._terminal_restored:
            # 即使已经清理,也要恢复终端状态
            self._terminal_restored = True
            TerminalRestorer.restore_terminal()
    
    def run(self):
        """主运行流程"""
        # 注册信号处理器(仅在Unix系统有效,Windows下主要依赖atexit)
        if sys.platform != "win32":
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            # 1. 打印欢迎信息
            self.print_banner()
            
            # 2. 检查依赖
            if not self.check_dependencies():
                print("\n❌ 依赖检查失败，请手动安装依赖后重试")
                sys.exit(1)
            
            # 3. 启动后端
            if not self.start_backend():
                print("\n❌ 后端启动失败")
                sys.exit(1)
            
            # 4. 启动前端
            if not self.start_frontend():
                print("\n❌ 前端启动失败")
                self.stop_services()
                sys.exit(1)
            
            # 5. 等待服务就绪
            if not self.health_check():
                print("\n❌ 服务启动失败")
                self.stop_services()
                sys.exit(1)
            
            # 6. 打开浏览器
            self.open_browser()
            
            # 7. 保持运行
            print("\n✨ 系统已就绪，正在运行中...")
            print("   提示: 按 Ctrl+C 停止服务\n")
            
            # 监控进程状态
            while True:
                time.sleep(1)
                
                # 检查进程是否还在运行
                if self.backend_process and self.backend_process.poll() is not None:
                    print("\n⚠️  后端服务意外退出")
                    break
                
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("\n⚠️  前端服务意外退出")
                    break
        
        except KeyboardInterrupt:
            print("\n\n⚠️  收到中断信号")
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # 确保无论如何都会清理资源
            self.stop_services()
            # 最后再次恢复终端状态
            if sys.platform == "win32" and not self._terminal_restored:
                self._terminal_restored = True
                TerminalRestorer.restore_terminal()
    
    def _signal_handler(self, signum, frame):
        """信号处理器(Unix系统使用)"""
        print("\n\n⚠️  收到停止信号")
        self.stop_services()
        sys.exit(0)


def main():
    """主函数"""
    manager = ServiceManager()
    manager.run()


if __name__ == "__main__":
    main()
