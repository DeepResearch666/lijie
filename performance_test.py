import http.client
import json
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

class APIPerformanceTester:
    def __init__(self):
        self.host = "unlocker-api.lunaproxy.com"
        self.payload = json.dumps({
            "url": "https://scholar.google.com/scholar?hl=en&as_sdt=0,5&q=Dual+Dependency-Awared+Collaborative+Service+Caching+and+Task+Offloading+in+Vehicular+Edge+Computing&btnG=",
            "type": "html",
            "country": "us",
            "js_render": "False",
            "block_resources": "image"
        })
        self.headers = {
            'Authorization': "Bearer gm963avxp3iepk03o1wc68bl13sms65j6sjg43wajxy8xfafe84125k6sqr84y19",
            'content-type': "application/json"
        }
        
        # 测试结果统计
        self.results = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': [],
            'errors': []
        }
        self.lock = threading.Lock()
    
    def single_request(self):
        """执行单个API请求并返回结果"""
        start_time = time.time()
        try:
            conn = http.client.HTTPSConnection(self.host, timeout=30)
            conn.request("POST", "/request", self.payload, self.headers)
            res = conn.getresponse()
            data = res.read()
            end_time = time.time()
            
            response_time = end_time - start_time
            status_code = res.status
            
            conn.close()
            
            return {
                'success':  status_code == 200,
                'status_code': status_code,
                'response_time': response_time,
                'data_size': len(data),
                'error': None
            }
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            return {
                'success': False,
                'status_code': None,
                'response_time': response_time,
                'data_size': 0,
                'error': str(e)
            }
    
    def update_results(self, result):
        """线程安全地更新测试结果"""
        with self.lock:
            self.results['total_requests'] += 1
            self.results['response_times'].append(result['response_time'])
            
            if result['success']:
                self.results['successful_requests'] += 1
            else:
                self.results['failed_requests'] += 1
                self.results['errors'].append({
                    'error': result['error'],
                    'status_code': result['status_code'],
                    'response_time': result['response_time']
                })
    
    def concurrent_test(self, num_requests=100, max_workers=10):
        """并发测试"""
        print(f"开始并发测试: {num_requests} 个请求，{max_workers} 个并发线程")
        print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            futures = [executor.submit(self.single_request) for _ in range(num_requests)]
            
            # 获取结果
            for i, future in enumerate(as_completed(futures), 1):
                result = future.result()
                self.update_results(result)
                
                # 实时显示进度
                if i % 10 == 0 or i == num_requests:
                    print(f"已完成: {i}/{num_requests} 请求")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        self.print_results(total_time)
    
    def sequential_test(self, num_requests=50):
        """顺序测试（用于对比）"""
        print(f"开始顺序测试: {num_requests} 个请求")
        print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        start_time = time.time()
        
        for i in range(num_requests):
            result = self.single_request()
            self.update_results(result)
            
            if (i + 1) % 10 == 0 or (i + 1) == num_requests:
                print(f"已完成: {i + 1}/{num_requests} 请求")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        self.print_results(total_time)
    
    def print_results(self, total_time):
        """打印测试结果"""
        results = self.results
        
        print("\n" + "="*60)
        print("测试结果统计")
        print("="*60)
        
        # 基本统计
        success_rate = (results['successful_requests'] / results['total_requests']) * 100 if results['total_requests'] > 0 else 0
        throughput = results['total_requests'] / total_time if total_time > 0 else 0
        
        print(f"总请求数: {results['total_requests']}")
        print(f"成功请求数: {results['successful_requests']}")
        print(f"失败请求数: {results['failed_requests']}")
        print(f"成功率: {success_rate:.2f}%")
        print(f"总测试时间: {total_time:.2f} 秒")
        print(f"吞吐量: {throughput:.2f} 请求/秒")
        
        # 响应时间统计
        if results['response_times']:
            response_times = results['response_times']
            print(f"\n响应时间统计:")
            print(f"  平均响应时间: {statistics.mean(response_times):.3f} 秒")
            print(f"  中位数响应时间: {statistics.median(response_times):.3f} 秒")
            print(f"  最小响应时间: {min(response_times):.3f} 秒")
            print(f"  最大响应时间: {max(response_times):.3f} 秒")
            
            if len(response_times) > 1:
                print(f"  响应时间标准差: {statistics.stdev(response_times):.3f} 秒")
            
            # 百分位数
            sorted_times = sorted(response_times)
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            p99 = sorted_times[int(len(sorted_times) * 0.99)]
            print(f"  95%响应时间: {p95:.3f} 秒")
            print(f"  99%响应时间: {p99:.3f} 秒")
        
        # 错误统计
        if results['errors']:
            print(f"\n错误统计:")
            error_types = {}
            for error in results['errors']:
                error_key = error['error'] or f"HTTP {error['status_code']}"
                error_types[error_key] = error_types.get(error_key, 0) + 1
            
            for error_type, count in error_types.items():
                print(f"  {error_type}: {count} 次")
        
        print("="*60)
    
    def reset_results(self):
        """重置测试结果"""
        self.results = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': [],
            'errors': []
        }

def main():
    tester = APIPerformanceTester()
    
    # 测试场景1: 低并发测试
    print("场景1: 低并发测试 (5个并发)")
    tester.reset_results()
    tester.concurrent_test(num_requests=50, max_workers=5)
    
    time.sleep(2)  # 间隔2秒
    
    # 测试场景2: 中等并发测试
    print("\n场景2: 中等并发测试 (10个并发)")
    tester.reset_results()
    tester.concurrent_test(num_requests=100, max_workers=10)
    
    time.sleep(2)  # 间隔2秒
    
    # 测试场景3: 高并发测试
    print("\n场景3: 高并发测试 (20个并发)")
    tester.reset_results()
    tester.concurrent_test(num_requests=200, max_workers=20)
    
    time.sleep(2)  # 间隔2秒
    
    # 测试场景4: 顺序测试（对比基准）
    print("\n场景4: 顺序测试（基准对比）")
    tester.reset_results()
    tester.sequential_test(num_requests=30)

if __name__ == "__main__":
    main() 