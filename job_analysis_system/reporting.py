import pandas as pd


def df_to_md(df, columns, headers):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return "\n".join(lines)


def records_to_md(records, columns, headers):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in records:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return "\n".join(lines)


def generate_report(jobs, top_skills_df, salary_role_df, location_df, experience_df, recommendations, gap, charts, output_path):
    parts = []
    parts.append("# Bao cao phan tich thi truong viec lam IT")
    parts.append("")
    parts.append("Tong so tin tuyen dung: {}".format(len(jobs)))
    parts.append("")
    parts.append("## Top ky nang duoc yeu cau")
    parts.append(df_to_md(top_skills_df.head(15), ["skill", "demand"], ["Ky nang", "So tin"]))
    parts.append("")
    parts.append("## Luong trung vi theo vi tri (trieu VND)")
    parts.append(df_to_md(salary_role_df, ["title", "median_salary"], ["Vi tri", "Luong trung vi"]))
    parts.append("")
    parts.append("## Phan bo theo cap bac")
    parts.append(df_to_md(experience_df, ["level", "total"], ["Cap bac", "So tin"]))
    parts.append("")
    parts.append("## Phan bo theo dia diem")
    parts.append(df_to_md(location_df, ["location", "total"], ["Dia diem", "So tin"]))
    parts.append("")
    parts.append("## Goi y ky nang nen hoc")
    parts.append(records_to_md(recommendations, ["skill", "demand", "avg_salary", "score"], ["Ky nang", "Nhu cau", "Luong TB", "Diem"]))
    parts.append("")
    parts.append("## Khoang cach ky nang (nen bo sung)")
    parts.append(records_to_md(gap, ["skill", "demand", "avg_salary", "score"], ["Ky nang", "Nhu cau", "Luong TB", "Diem"]))
    parts.append("")
    parts.append("## Bieu do")
    for name, path in charts.items():
        parts.append("- {}: {}".format(name, path))
    text = "\n".join(parts)
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return output_path


def generate_weekly_report(jobs, reference_date, output_path):
    data = jobs.copy()
    data["posted_date"] = pd.to_datetime(data["posted_date"], errors="coerce")
    start = pd.Timestamp(reference_date) - pd.Timedelta(days=7)
    end = pd.Timestamp(reference_date)
    recent = data[(data["posted_date"] >= start) & (data["posted_date"] <= end)]
    parts = []
    parts.append("# Bao cao tuan ({} den {})".format(start.date(), end.date()))
    parts.append("")
    parts.append("So tin moi trong tuan: {}".format(len(recent)))
    parts.append("")
    if len(recent) > 0:
        by_location = recent.groupby("location").size().reset_index(name="total").sort_values("total", ascending=False)
        parts.append("## Tin moi theo dia diem")
        parts.append(df_to_md(by_location, ["location", "total"], ["Dia diem", "So tin"]))
    text = "\n".join(parts)
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return output_path
