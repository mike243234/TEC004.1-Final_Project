def recommend_skills(skill_value_df, limit=10):
    records = skill_value_df.head(limit).to_dict("records")
    return list(map(lambda row: {
        "skill": row["skill"],
        "demand": int(row["demand"]),
        "avg_salary": round(row["avg_salary"], 1),
        "score": round(row["score"], 1),
    }, records))


def skill_gap(skill_value_df, student_skills, limit=10):
    owned = set(skill.strip().lower() for skill in student_skills)
    records = skill_value_df.to_dict("records")
    missing = filter(lambda row: row["skill"].lower() not in owned, records)
    ranked = sorted(missing, key=lambda row: row["score"], reverse=True)
    return list(map(lambda row: {
        "skill": row["skill"],
        "demand": int(row["demand"]),
        "avg_salary": round(row["avg_salary"], 1),
        "score": round(row["score"], 1),
    }, ranked[:limit]))
