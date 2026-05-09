import os
import time
import unittest
# 核心修改点：从 HTMLTestRunner 模块中导入 HTMLTestRunner 类
try:
    from HTMLTestRunner import HTMLTestRunner
except ImportError:
    # 兼容性处理：如果上面的导入失败，尝试直接导入模块
    import HTMLTestRunner

# 动态获取当前脚本所在的绝对路径
current_path = os.path.dirname(os.path.abspath(__file__))
test_dir = os.path.join(current_path, 'testcases')

# 自动发现测试用例
discover = unittest.defaultTestLoader.discover(
    start_dir=test_dir, 
    pattern='test_*.py',
    top_level_dir=os.path.dirname(current_path)
)

if __name__ == "__main__":
    # 确保 report 文件夹存在
    report_dir = os.path.join(current_path, 'report')
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    now = time.strftime("%Y-%m-%d %H_%M_%S")
    filename = os.path.join(report_dir, now + '_EV_API_Report.html')
    
    with open(filename, 'wb') as fp:
        # 实例化 runner
        # 注意：此处要确保导入的是类。如果报错，请使用 HTMLTestRunner.HTMLTestRunner
        runner = HTMLTestRunner(
            stream=fp,
            title='EV 充电负荷微服务系统 - 接口测试报告',
            description='运行环境：FastAPI, Docker, PyTorch'
        )
        
        # 核心修改点：传入该版本要求的额外参数
        # rerun=0 表示不重跑，save_last_run=True 表示保存记录
        runner.run(discover, rerun=0, save_last_run=True)

    print(f"测试完成！报告已生成：{filename}")