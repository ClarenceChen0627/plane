from abc import ABC, abstractmethod
from typing import List, Any
# Django imports
from plane.db.models import EmailNotificationLog, UserNotificationPreference, Notification, State

# Base Observer Interface
class NotificationProvider(ABC):
    @property
    def provider_name(self):
        return "base"

    @abstractmethod
    def should_send(self, preference: UserNotificationPreference, activity: dict, project_id: str = None) -> bool:
        """
        Determine if this provider should trigger based on user preferences.
        """
        pass

    @abstractmethod
    def construct_payload(self, context: dict) -> Any:
        """
        Create the object to be sent/saved.
        """
        pass

    @abstractmethod
    def bulk_dispatch(self, payloads: List[Any]):
        """
        Send all payloads in a batch.
        """
        pass

# Concrete Observer for Email
class EmailNotificationProvider(NotificationProvider):
    @property
    def provider_name(self):
        return "email"

    def should_send(self, preference: UserNotificationPreference, activity: dict, project_id: str = None) -> bool:
        field = activity.get("field")
        
        # State change logic
        if field == "state":
            if preference.state_change:
                return True
            # Check completed logic
            if preference.issue_completed and project_id:
                # We need to check if the NEW state is a completed state
                # Note: This query inside a loop might be N+1 if not careful, but the original code did it too.
                # Ideally this state lookup happens once outside, but we follow original structure for safety.
                is_completed = State.objects.filter(
                    project_id=project_id,
                    pk=activity.get("new_identifier"),
                    group="completed",
                ).exists()
                if is_completed:
                    return True
                    
        if field == "comment" and preference.comment:
            return True
        if field == "mention" and preference.mention:
            return True
        if preference.property_change and field not in ["state", "comment", "mention"]:
            return True
            
        return False

    def construct_payload(self, context: dict) -> EmailNotificationLog:
        # Context expects: triggered_by_id, receiver_id, issue, issue_activity, etc.
        return EmailNotificationLog(
            triggered_by_id=context['triggered_by_id'],
            receiver_id=context['receiver_id'],
            entity_identifier=context['entity_identifier'],
            entity_name="issue",
            data={
                "issue": context['issue_data'],
                "issue_activity": context['activity_data']
            }
        )

    def bulk_dispatch(self, payloads: List[EmailNotificationLog]):
        if payloads:
            EmailNotificationLog.objects.bulk_create(payloads, batch_size=100, ignore_conflicts=True)
