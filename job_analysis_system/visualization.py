import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def plot_skill_demand(top_skills_df, output_dir):
    ensure_dir(output_dir)
    data = top_skills_df.head(15)
    plt.figure(figsize=(10, 6))
    plt.barh(data["skill"][::-1], data["demand"][::-1], color="#4C72B0")
    plt.title("Top ky nang duoc yeu cau nhieu nhat")
    plt.xlabel("So tin tuyen dung")
    plt.tight_layout()
    path = os.path.join(output_dir, "skill_demand.png")
    plt.savefig(path)
    plt.close()
    return path


def plot_salary_box(jobs, output_dir):
    ensure_dir(output_dir)
    order = ["Entry", "Junior", "Middle", "Senior"]
    paid = jobs[jobs["salary_mid"] > 0]
    labels = [level for level in order if not paid[paid["level"] == level].empty]
    data = [paid[paid["level"] == level]["salary_mid"].tolist() for level in labels]
    plt.figure(figsize=(9, 6))
    plt.boxplot(data, tick_labels=labels)
    plt.title("Phan bo luong theo cap bac (trieu VND)")
    plt.ylabel("Luong (trieu VND)")
    plt.tight_layout()
    path = os.path.join(output_dir, "salary_box.png")
    plt.savefig(path)
    plt.close()
    return path


def plot_posting_trend(jobs, output_dir):
    ensure_dir(output_dir)
    data = jobs.copy()
    data["posted_date"] = pd.to_datetime(data["posted_date"], errors="coerce")
    data = data.dropna(subset=["posted_date"])
    weekly = data.groupby(data["posted_date"].dt.to_period("W")).size()
    labels = [str(period) for period in weekly.index]
    plt.figure(figsize=(11, 6))
    plt.plot(labels, weekly.values, marker="o", color="#55A868")
    plt.xticks(rotation=45, ha="right")
    plt.title("So tin tuyen dung theo tuan")
    plt.ylabel("So tin")
    plt.tight_layout()
    path = os.path.join(output_dir, "posting_trend.png")
    plt.savefig(path)
    plt.close()
    return path


def plot_location(location_df, output_dir):
    ensure_dir(output_dir)
    plt.figure(figsize=(8, 8))
    plt.pie(location_df["total"], labels=location_df["location"], autopct="%1.1f%%", startangle=90)
    plt.title("Phan bo viec lam theo dia diem")
    plt.tight_layout()
    path = os.path.join(output_dir, "location.png")
    plt.savefig(path)
    plt.close()
    return path
