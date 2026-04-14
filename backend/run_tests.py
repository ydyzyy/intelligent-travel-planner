"""测试运行脚本"""

import subprocess
import sys
import os


def run_tests(test_path: str = "tests", verbose: bool = True, coverage: bool = False):
    """
    运行测试
    
    Args:
        test_path: 测试路径
        verbose: 是否显示详细输出
        coverage: 是否生成覆盖率报告
    """
    cmd = [sys.executable, "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend([
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])
    
    cmd.append(test_path)
    
    print(f"🚀 运行测试: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    return result.returncode == 0


def run_specific_test(test_file: str):
    """
    运行特定测试文件
    
    Args:
        test_file: 测试文件路径
    """
    cmd = [sys.executable, "-m", "pytest", test_file, "-v"]
    print(f"🚀 运行测试: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    return result.returncode == 0


if __name__ == "__main__":
    # 切换到backend目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("="*60)
    print("🧪 智能旅行规划系统 - 测试套件")
    print("="*60)
    print()
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "coverage":
            success = run_tests(coverage=True)
        elif sys.argv[1].endswith(".py"):
            success = run_specific_test(sys.argv[1])
        else:
            success = run_tests(sys.argv[1])
    else:
        # 默认运行所有测试
        success = run_tests()
    
    print()
    if success:
        print("✅ 所有测试通过!")
        sys.exit(0)
    else:
        print("❌ 部分测试失败!")
        sys.exit(1)
