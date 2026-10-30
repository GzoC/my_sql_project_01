from datetime import datetime, timedelta
from random import Random


def generate(seed=42):
    """Invented 12-asset, 90-day scenario. No measured plant data or statistical realism claim."""
    rng = Random(seed)
    data = {
        k: []
        for k in (
            "assets",
            "work_orders",
            "failures",
            "downtime",
            "shifts",
            "parts",
            "part_usage",
        )
    }
    base = datetime(2025, 1, 1)

    def fmt(t):
        return t.strftime("%Y-%m-%d %H:%M:%S")

    for part_id, name in enumerate(
        ("Rodamiento", "Sello", "Contactor", "Sensor", "Correa", "Variador"), 1
    ):
        data["parts"].append((part_id, name))
    order_id = failure_id = event_id = usage_id = shift_id = 0
    for asset in range(1, 13):
        data["assets"].append(
            (
                asset,
                f"Equipo {asset:02d}",
                "Línea A" if asset <= 6 else "Línea B",
                1 + asset % 3,
            )
        )
        for day in range(90):
            shift = base + timedelta(days=day, hours=8)
            shift_id += 1
            data["shifts"].append(
                (shift_id, asset, fmt(shift), fmt(shift + timedelta(hours=8)))
            )
            if rng.random() < (0.30 if asset <= 3 else 0.12):
                opened = shift + timedelta(minutes=rng.randrange(-180, 480))
                duration = rng.choice((30, 60, 90, 180, 360, 720))
                repaired = opened + timedelta(minutes=duration)
                unclosed = day > 70 and rng.random() < 0.35
                order_id += 1
                data["work_orders"].append(
                    (
                        order_id,
                        asset,
                        "corrective",
                        rng.randint(1, 3),
                        fmt(opened),
                        fmt(opened + timedelta(days=2)),
                        None if unclosed else fmt(repaired + timedelta(hours=1)),
                        None,
                    )
                )
                failure_id += 1
                data["failures"].append(
                    (
                        failure_id,
                        asset,
                        order_id,
                        fmt(opened),
                        None if unclosed else fmt(repaired),
                        rng.choice(("mecánica", "eléctrica", "instrumentación")),
                    )
                )
                event_id += 1
                data["downtime"].append(
                    (
                        event_id,
                        asset,
                        fmt(opened),
                        None if unclosed else fmt(repaired),
                        "failure",
                    )
                )
                # Duplicate/nested reports intentionally exercise interval union.
                if duration >= 180 and not unclosed:
                    event_id += 1
                    data["downtime"].append(
                        (
                            event_id,
                            asset,
                            fmt(opened + timedelta(minutes=15)),
                            fmt(opened + timedelta(minutes=45)),
                            "utility",
                        )
                    )
                for part in rng.sample(range(1, 7), rng.randint(1, 3)):
                    usage_id += 1
                    unit = (12000, 2500, 18000, 8500, 4000, 220000)[part - 1]
                    data["part_usage"].append(
                        (
                            usage_id,
                            order_id,
                            part,
                            fmt(opened + timedelta(minutes=10)),
                            rng.randint(1, 3),
                            unit,
                        )
                    )
            if day % 14 == asset % 14:
                order_id += 1
                cancelled = day % 3 == 0
                end = shift + timedelta(hours=1)
                data["work_orders"].append(
                    (
                        order_id,
                        asset,
                        "preventive",
                        3,
                        fmt(shift),
                        fmt(end),
                        None if cancelled else fmt(end),
                        fmt(shift) if cancelled else None,
                    )
                )
                if not cancelled:
                    event_id += 1
                    data["downtime"].append(
                        (event_id, asset, fmt(shift), fmt(end), "planned")
                    )
    return data
