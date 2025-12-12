from abc import ABC, abstractmethod
from typing import List, Any
from collections import defaultdict
import datetime

# ==========================================
# PART 1: MOCKING THE CORE SYSTEM (无需 Docker/DB)
# ==========================================

# 模拟 Django 的 Model 对象，防止 import 报错
class UserNotificationPreference:
    def __init__(self, mention=False, comment=False, state_change=False):
        self.mention = mention
        self.comment = comment
        self.state_change = state_change
        self.property_change = False
        self.issue_completed = False

# 模拟项目中的 Base Class (原本在 plane/utils/notification_providers.py)
class NotificationProvider(ABC):
    @property
    def provider_name(self):
        return "base"

    @abstractmethod
    def should_send(self, preference: UserNotificationPreference, activity: dict, project_id: str = None) -> bool:
        pass

    @abstractmethod
    def construct_payload(self, context: dict) -> Any:
        pass

    @abstractmethod
    def bulk_dispatch(self, payloads: List[Any]):
        pass

# 模拟项目中已有的 Email Provider
class EmailNotificationProvider(NotificationProvider):
    @property
    def provider_name(self):
        return "email"

    def should_send(self, preference, activity, project_id=None) -> bool:
        field = activity.get("field")
        if field == "mention" and preference.mention:
            return True
        if field == "comment" and preference.comment:
            return True
        return False

    def construct_payload(self, context: dict):
        return f"[Email Object] To: {context['receiver_id']}, Subject: You were mentioned in {context['issue_data']['identifier']}"

    def bulk_dispatch(self, payloads):
        print(f"  [EmailProvider] Saving {len(payloads)} logs to Database...")
        for p in payloads:
            print(f"    -> {p}")

# ==========================================
# PART 2: THE EXTENSION (新插件演示)
# ==========================================

# 这是一个新的 Slack 插件，完全解耦实现
class SlackNotificationProvider(NotificationProvider):
    @property
    def provider_name(self):
        return "slack"

    def should_send(self, preference, activity, project_id=None) -> bool:
        # 简单逻辑：只要是 mention 就发 Slack
        if activity.get("field") == "mention":
            return True
        return False

    def construct_payload(self, context: dict):
        # 模拟构造 Slack JSON Payload
        return {
            "channel": "#general",
            "text": f"Hey <@{context['receiver_id']}>! You were mentioned in {context['issue_data']['identifier']}.",
            "blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": "New Mention!"}}]
        }

    def bulk_dispatch(self, payloads):
        print(f"  [SlackProvider] Pushing {len(payloads)} requests to Slack API...")
        for p in payloads:
            print(f"    -> POST https://hooks.slack.com/... Body: {p['text']}")

# ==========================================
# PART 3: RUNNING THE SIMULATION (体验 NFR)
# ==========================================

def run_simulation():
    print("\n" + "="*60)
    print(" NFR DEMO: PLUGGABLE NOTIFICATION SYSTEM (STANDALONE)")
    print("="*60 + "\n")

    # 1. 模拟环境数据
    mock_preference_user_b = UserNotificationPreference(mention=True, comment=True)
    
    mock_activity = {
        "field": "mention",
        "verb": "created",
        "actor_id": "User-A",
        "new_value": "User-B"
    }

    mock_context = {
        "triggered_by_id": "User-A",
        "receiver_id": "User-B",
        "entity_identifier": "ISSUE-101",
        "issue_data": {"name": "Fix Login Bug", "identifier": "PROJ-1-105"}
    }

    # 2. 配置系统 (这里体现了 Extensibility)
    # 我们可以轻松地添加或移除 Provider，而不需要改动上面的核心逻辑
    active_providers = [
        EmailNotificationProvider(), # 现有
        SlackNotificationProvider()  # 新扩展
    ]

    print(f"System Configuration: Active Providers = {[p.provider_name for p in active_providers]}\n")
    
    # 3. 模拟核心任务循环 (Notification Task)
    print(f"--- Event Triggered: User-A mentioned User-B in Issue PROJ-1-105 ---")
    
    provider_payloads = defaultdict(list)

    for provider in active_providers:
        print(f"\n[Core System] Checking Provider: {provider.provider_name.upper()}...")
        
        should_trigger = provider.should_send(mock_preference_user_b, mock_activity)
        
        if should_trigger:
            print(f"  -> Check: PASSED. Constructing payload.")
            payload = provider.construct_payload(mock_context)
            provider_payloads[provider.provider_name].append(payload)
            
            # 模拟 Dispatch
            provider.bulk_dispatch([payload])
        else:
            print(f"  -> Check: FAILED. Skipping.")

    print("\n" + "="*60)
    print(" DEMO COMPLETE: Success! Both Email and Slack were triggered independently.")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_simulation()
