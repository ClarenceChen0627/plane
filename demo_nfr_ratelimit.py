import time
import math
from collections import defaultdict

# ==========================================
# PART 1: THE RATE LIMITER CORE (模拟 NFR 实现)
# ==========================================

class RateLimitMiddleware:
    def __init__(self, limit=100, window=60):
        self.limit = limit        # 最大请求数 (e.g. 100 requests)
        self.window = window      # 时间窗口 (e.g. per 60 seconds)
        # 模拟 Redis: 存储结构为 { "IP_ADDRESS": { "count": 10, "reset_at": TIMESTAMP } }
        self.redis_mock = defaultdict(dict)

    def process_request(self, ip_address):
        """
        核心逻辑：检查是否允许请求通过
        return: True (Allowed) / False (Blocked)
        """
        current_time = time.time()
        record = self.redis_mock[ip_address]

        # 1. 检查窗口是否过期 (Reset if expired)
        reset_at = record.get("reset_at", 0)
        if current_time > reset_at:
            # 新窗口：重置计数器
            record["count"] = 0
            record["reset_at"] = current_time + self.window
            print(f"  [Redis] New window started for {ip_address}. Reset count to 0.")

        # 2. 检查计数器
        if record["count"] >= self.limit:
            # 超过限制：拒绝
            return False, record["reset_at"] - current_time

        # 3. 允许通过：计数器 +1
        record["count"] += 1
        return True, 0

# ==========================================
# PART 2: THE API SERVER (模拟后端视图)
# ==========================================

class MockAPIServer:
    def __init__(self):
        # 我们的 NFR 组件：限制每分钟 50 个请求 (为了演示不用等太久，设小一点)
        self.rate_limiter = RateLimitMiddleware(limit=50, window=60)

    def handle_request(self, user_ip, req_id):
        # 1. 过中间件
        is_allowed, wait_time = self.rate_limiter.process_request(user_ip)

        if not is_allowed:
            return 429, f"Too Many Requests. Retry in {wait_time:.1f}s"
        
        # 2. 正常业务逻辑
        # time.sleep(0.01) # 假装在查询数据库
        return 200, "OK: Data Payload"

# ==========================================
# PART 3: THE ATTACK SIMULATION (体验防护效果)
# ==========================================

def run_attack_simulation():
    server = MockAPIServer()
    attacker_ip = "192.168.1.100"
    
    print("\n" + "="*60)
    print(f" NFR DEMO: API RATE LIMITING PROTECTION")
    print(f" Policy: Max 50 requests / 60 seconds")
    print("="*60 + "\n")

    # --- Phase 1: Normal Traffic ---
    print("--- Phase 1: Normal User Behavior (10 requests) ---")
    for i in range(1, 11):
        status, msg = server.handle_request(attacker_ip, i)
        print(f" Req {i:02d}: {status} | {msg}")
    print(" >> Result: All normal requests passed.\n")

    # --- Phase 2: Burst Attack ---
    print("--- Phase 2: DOS Attack Simulation (Sender goes crazy) ---")
    print("Sending 50 more requests rapidly... (Limit is 50)")
    
    # 把它填满
    for i in range(11, 51):
        server.handle_request(attacker_ip, i)
    print("... (40 requests sent successfully, quota is now full) ...\n")

    print("Now trying to exceed the limit:")
    blocked_count = 0
    
    # 尝试再次发送 20 个请求 (应该全部被杀)
    for i in range(51, 71):
        status, msg = server.handle_request(attacker_ip, i)
        if status == 429:
            print(f" Req {i:02d}: {status} [BLOCKED!] | {msg}")
            blocked_count += 1
        else:
            print(f" Req {i:02d}: {status} [PASSED]  | {msg}")

    # --- Conclusion ---
    print("\n" + "-"*60)
    print(f" SECURITY REPORT:")
    print(f" Total Requests Sent: 70")
    print(f" Allowed:             50 (Max Capacity)")
    print(f" Blocked:             {blocked_count} (Malicious Traffic Dropped)")
    
    if blocked_count > 0:
        print(f" STATUS: SYSTEM PROTECTED. DOS ATTACK NEUTRALIZED.")
    else:
        print(f" STATUS: FAILED. SYSTEM VULNERABLE.")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_attack_simulation()
