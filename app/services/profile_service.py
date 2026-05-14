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
        since_30 = today - timedelta(days=29)

        # Single query for last 30 days (replaces 30 individual queries)
        all_30 = self.entry_repo.list_since(user.id, since_30)

        # Daily totals
        day_totals: dict[date, int] = {}
        for e in all_30:
            d = e.start_time.date()
            day_totals[d] = day_totals.get(d, 0) + _minutes(e)
        active_days = [m for m in day_totals.values() if m > 0]
        avg_daily = int(sum(active_days) / len(active_days)) if active_days else 0

        # Top category
        cat_map: dict[str, int] = {}
        for e in all_30:
            cat = e.category or ("work" if e.project_id else "others")
            cat_map[cat] = cat_map.get(cat, 0) + _minutes(e)
        top_cat_key = max(cat_map, key=lambda k: cat_map[k]) if cat_map else "work"
        top_category_labels = {
            "work": "Work", "personal_care": "Personal", "breaks": "Breaks", "others": "Others"
        }
        top_category = top_category_labels.get(top_cat_key, "Work")

        # Most used project
        proj_count: dict[str, int] = {}
        for e in all_30:
            if e.project:
                proj_count[e.project.name] = proj_count.get(e.project.name, 0) + 1
        most_used_project = max(proj_count, key=lambda k: proj_count[k]) if proj_count else "—"

        # Peak hour
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

        # Days logged in last 7 (derived from day_totals, no extra query)
        days_logged = sum(
            1 for i in range(7)
            if (today - timedelta(days=i)) in day_totals
        )
        consistency_insight = (
            f"You log consistently {days_logged} day{'s' if days_logged != 1 else ''} a week. "
            + ("Your flow state is stabilizing." if days_logged >= 4 else "Keep building the habit!")
        )

        # Single query for all distinct entry dates (replaces up to 365 queries)
        all_dates = self.entry_repo.get_distinct_dates(user.id)
        date_set = set(all_dates)

        # Current streak
        current_streak = 0
        for i in range(len(all_dates) + 1):
            if (today - timedelta(days=i)) in date_set:
                current_streak += 1
            else:
                break

        # Best streak
        best_streak = 0
        run = 0
        prev: date | None = None
        for d in all_dates:
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
