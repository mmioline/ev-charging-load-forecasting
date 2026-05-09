import time
import unittest
import HTMLTestRunner # 确保该文件在同一目录下

# 加载 testcases 目录下的所有测试用例
test_dir = './testcases'
discover = unittest.defaultTestLoader.discover(test_dir, pattern='test_*.py')

if __name__ == "__main__":
    # 生成带有时间戳的 HTML 报告文件
    now = time.strftime("%Y-%m-%d %H_%M_%S")
    filename = './report/' + now + '_EV_API_Report.html'
    
    with open(filename, 'wb') as fp:
        runner = HTMLTestRunner.HTMLTestRunner(
            stream=fp,
            title='EV 充电负荷微服务系统 - 接口测试报告',
            description='测试覆盖范围：用户服务鉴权、站点创建、负荷流水模拟。'
        )
        runner.run(discover)