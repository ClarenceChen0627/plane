import time
import functools
import hashlib
from typing import Dict, Any

# ==========================================
# PART 1: THE CACHING INFRASTRUCTURE (模拟 NFR 实现)
# ==========================================

# 模拟 Redis 存储
MOCK_REDIS_CACHE: Dict[str, Any] = {}

def generate_cache_key(func_name, *args, **kwargs):
    # 简单的 Key 生成逻辑
    key_str = f"{func_name}:{str(args)}:{str(kwargs)}"
    return hashlib.md5(key_str.encode()).hexdigest()

def cache_response(timeout_seconds=60):
    """
    这是我们实现的装饰器 (NFR 核心代码的简化版)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 1. 生成缓存 Key
            cache_key = generate_cache_key(func.__name__, *args, **kwargs)
            
            # 2. 检查缓存 (模拟 Redis GET)
            cached_data = MOCK_REDIS_CACHE.get(cache_key)
            
            if cached_data:
                print(f"  [CACHE HIT] Found key {cache_key[:8]}... retrieving from Redis.")
                return cached_data
            
            # 3. 缓存未命中，执行原函数 (Slow DB Query)
            print(f"  [CACHE MISS] Key {cache_key[:8]} not found. Querying Database... (Slow)")
            result = func(*args, **kwargs)
            
            # 4. 写入缓存 (模拟 Redis SET)
            MOCK_REDIS_CACHE[cache_key] = result
            return result
        return wrapper
    return decorator

# ==========================================
# PART 2: THE BUSINESS LOGIC (模拟业务场景)
# ==========================================

class ProjectAnalyticsService:
    
    # 原始的慢查询函数 (模拟 DB 聚合操作)
    def check_stats_slow(self, project_id):
        # 模拟 200ms 的数据库查询延迟
        time.sleep(0.210) 
        return {
            "project_id": project_id,
            "total_issues": 1500,
            "completed": 1200,
            "pending": 300
        }

    # 应用了 NFR 优化的函数
    @cache_response(timeout_seconds=300)
    def check_stats_fast(self, project_id):
        # 逻辑完全一样，也有延迟，也是模拟 DB
        time.sleep(0.210)
        return {
            "project_id": project_id,
            "total_issues": 1500,
            "completed": 1200,
            "pending": 300
        }

# ==========================================
# PART 3: PERFORMANCE BENCHMARK (体验优化效果)
# ==========================================

def run_benchmark():
    service = ProjectAnalyticsService()
    project_id = "proj-123"

    print("\n" + "="*60)
    print(" NFR DEMO: APPLICATION-LEVEL CACHING PERFORMANCE")
    print("="*60 + "\n")

    # --- Scenario A: Without Caching ---
    print("--- Scenario A: Without Caching (Baseline) ---")
    total_time_a = 0
    for i in range(1, 4):
        start = time.time()
        service.check_stats_slow(project_id)
        duration = (time.time() - start) * 1000 # 转 ms
        total_time_a += duration
        print(f" Request {i}: {duration:.2f} ms")
    
    print(f" >> Average Latency: {total_time_a/3:.2f} ms\n")


    # --- Scenario B: With Caching (The NFR Improvement) ---
    print("--- Scenario B: With Caching (NFR optimized) ---")
    
    # Request 1: Cold Start
    start = time.time()
    service.check_stats_fast(project_id)
    duration_1 = (time.time() - start) * 1000
    print(f" Request 1 (Cold): {duration_1:.2f} ms")

    # Request 2-5: Hot Cache
    total_time_hot = 0
    for i in range(2, 6):
        start = time.time()
        service.check_stats_fast(project_id)
        duration = (time.time() - start) * 1000
        total_time_hot += duration
        print(f" Request {i} (Hot) : {duration:.2f} ms")
    
    avg_hot = total_time_hot / 4
    print(f" >> Average Latency (Hot): {avg_hot:.2f} ms")

    # --- Conclusion ---
    print("\n" + "-"*60)
    print(f" IMPACT ANALYSIS:")
    print(f" 1. First Load:  {duration_1:.2f} ms (Same as baseline, unavoidable)")
    print(f" 2. Subsequent:  {avg_hot:.2f} ms  (Instant!)")
    speedup = (total_time_a/3) / avg_hot if avg_hot > 0 else 999
    print(f" 3. Speedup:     {speedup:.1f}x Faster")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_benchmark()
