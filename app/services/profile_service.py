import uuid
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.entry_repo import EntryRepository
from app.repositories.goal_repo import GoalRepository
from app.repositories.reflection_repo import ReflectionRepository
from app.repositories.user_repo import UserRepository


def _minutes(entry) -> int:
    return max(0, int((entry.end_time - entry.start_time).total_seconds() / 60))


class ProfileService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.entry_repo = EntryRepository(db)
        self.goal_repo = GoalRepository(db)
        self.reflection_repo = ReflectionRepository(db)

    def get_profile(self, user: User) -> dict:
        today = date.today()

        # --- Collect last 30 days of entries ---
        all_30: list = []
        daily_totals: list[int] = []
        for i in range(30):
            d = today - timedelta(days=i)
            day_entries = self.entry_repo.list_for_user(user.id, d)
            mins = sum(_minutes(e) for e in day_entries)
            if mins > 0:
                daily_totals.append(mins)
            all_30.extend(day_entries)

        avg_daily = int(sum(daily_totals) / len(daily_totals)) if daily_totals else 0

        # --- Top category (last 30 days) ---
        cat_map = {"work": 0, "personal_care": 0, "breaks": 0, "others": 0}
        for e in all_30:
            cat = e.category or ("work" if e.project_id else "others")
            cat_map[cat] = cat_map.get(cat, 0) + _minutes(e)
        top_cat_key = max(cat_map, key=lambda k: cat_map[k])
        top_category_labels = {
            "work": "Work", "personal_care": "Personal", "breaks": "Breaks", "others": "Others"
        }
        top_category = top_category_labels.get(top_cat_key, "Work")

        # --- Most used project (last 30 days) ---
        proj_count: dict[str, int] = {}
        for e in all_30:
            if e.project:
                proj_count[e.project.name] = proj_count.get(e.project.name, 0) + 1
        most_used_project = max(proj_count, key=lambda k: proj_count[k]) if proj_count else "—"

        # --- Peak hour (last 30 days) ---
        hour_map: dict[int, int] = {}
        for e in all_30:
            h = e.start_time.hour
            hour_map[h] = hour_map.get(h, 0) + _minutes(e)
        peak_hour = max(hour_map, key=lambda k: hour_map[k]) if hour_map else None

        def fmt_hour(h: int) -> str:
            if h == 0: return "12 AM"
            if h < 12: return f"{h} AM"
            if h == 12: return "12 PM"
            return f"{h - 12} PM"

        productivity_insight = (
            f"You're most productive at {fmt_hour(peak_hour)}. "
            f"Deep work sessions peak around that time."
            if peak_hour is not None
            else "Start logging your day to discover your peak productivity hours."
        )

        # --- Days logged in last 7 ---
        days_logged = sum(
            1 for i in range(7)
            if any(
                (today - timedelta(days=i)).isoformat() in e.start_time.date().isoformat()
                for e in all_30
            )
        )
        consistency_insight = (
            f"You log consistently {days_logged} day{'s' if days_logged != 1 else ''} a week. "
            + ("Your flow state is stabilizing." if days_logged >= 4 else "Keep building the habit!")
        )

        # --- Current streak (consecutive days back from today) ---
        current_streak = 0
        for i in range(365):
            d = today - timedelta(days=i)
            day_entries = self.entry_repo.list_for_user(user.id, d)
            if day_entries:
                current_streak += 1
            else:
                break

        # --- Best streak (all time) ---
        all_entries = self.entry_repo.list_for_user(user.id)
        entry_dates = sorted({e.start_time.date() for e in all_entries})
        best_streak = 0
        run = 0
        prev: date | None = None
        for d in entry_dates:
            if prev is None or (d - prev).days == 1:
                run += 1
            else:
                run = 1
            best_streak = max(best_streak, run)
            prev = d

        goals = self.goal_repo.list_for_user(user.id)
        recent_reflections = self.reflection_repo.list_recent(user.id, limit=5)

        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "avg_daily_minutes": avg_daily,
            "top_category": top_category,
            "most_used_project": most_used_project,
            "current_streak": current_streak,
            "best_streak": best_streak,
            "productivity_insight": productivity_insight,
            "consistency_insight": consistency_insight,
            "goals": goals,
            "recent_reflections": recent_reflections,
        }

    def update_profile(self, user: User, name: str | None, avatar_url: str | None) -> User:
        return self.user_repo.update_profile(user, name=name, avatar_url=avatar_url)

    def delete_account(self, user: User) -> None:
        self.user_repo.delete(user)
