import uuid
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.repositories.entry_repo import EntryRepository


def _minutes(entry) -> int:
    return max(0, int((entry.end_time - entry.start_time).total_seconds() / 60))


class InsightsService:
    def __init__(self, db: Session):
        self.repo = EntryRepository(db)

    def get_daily(self, user_id: uuid.UUID, filter_date: date) -> dict:
        entries = self.repo.list_for_user(user_id, filter_date)

        total_tracked = sum(_minutes(e) for e in entries)

        # Project breakdown — group by project name (or "Unassigned")
        project_map: dict[str, int] = {}
        for e in entries:
            name = e.project.name if e.project_id and e.project else "Unassigned"
            project_map[name] = project_map.get(name, 0) + _minutes(e)

        project_breakdown = sorted(
            [{"name": k, "minutes": v} for k, v in project_map.items()],
            key=lambda x: x["minutes"],
            reverse=True,
        )

        # Category breakdown
        cat_map = {"work": 0, "personal_care": 0, "breaks": 0, "others": 0}
        for e in entries:
            cat = e.category or ("work" if e.project_id else "others")
            if cat in cat_map:
                cat_map[cat] += _minutes(e)

        # Peak 3-hour window (scan each hour 0-21)
        peak_window: str | None = None
        if entries:
            best_start = 0
            best_min = 0
            for start_h in range(22):
                window_min = 0
                for e in entries:
                    # overlap between [start_h, start_h+3) and entry
                    e_start = e.start_time.hour + e.start_time.minute / 60
                    e_end = e.end_time.hour + e.end_time.minute / 60
                    overlap = max(0.0, min(e_end, start_h + 3) - max(e_start, start_h))
                    window_min += int(overlap * 60)
                if window_min > best_min:
                    best_min = window_min
                    best_start = start_h
            if best_min > 0:
                def fmt_h(h: int) -> str:
                    if h == 0: return "12 AM"
                    if h < 12: return f"{h} AM"
                    if h == 12: return "12 PM"
                    return f"{h - 12} PM"
                peak_window = f"{fmt_h(best_start)} – {fmt_h(best_start + 3)}"

        # Untracked vs 24h goal
        goal_minutes = 24 * 60
        untracked_minutes = max(0, goal_minutes - total_tracked)

        return {
            "total_tracked": total_tracked,
            "untracked_minutes": untracked_minutes,
            "peak_window": peak_window,
            "project_breakdown": project_breakdown,
            "category_breakdown": cat_map,
        }

    def get_weekly(self, user_id: uuid.UUID) -> dict:
        today = date.today()

        total_per_day = []
        all_entries = []

        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            entries = self.repo.list_for_user(user_id, d)
            day_minutes = sum(_minutes(e) for e in entries)
            total_per_day.append({"day": d.strftime("%a").upper()[:3], "minutes": day_minutes})
            all_entries.extend(entries)

        # Project totals across the week
        project_map: dict[str, int] = {}
        for e in all_entries:
            name = e.project.name if e.project_id and e.project else "Unassigned"
            project_map[name] = project_map.get(name, 0) + _minutes(e)

        project_totals = sorted(
            [{"name": k, "minutes": v} for k, v in project_map.items()],
            key=lambda x: x["minutes"],
            reverse=True,
        )

        top = project_totals[0] if project_totals else None
        top_project = {
            "name": top["name"] if top else "—",
            "total_minutes": top["minutes"] if top else 0,
            "change_percentage": 0,
        }

        return {
            "total_per_day": total_per_day,
            "top_project": top_project,
            "project_totals": project_totals,
        }
