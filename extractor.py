import re

SKILL_ALIASES = {
    "reactjs": "React",
    "react.js": "React",
    "react": "React",
    "nodejs": "Node.js",
    "node js": "Node.js",
    "node.js": "Node.js",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "sql": "SQL",
    "aws": "AWS",
    "html": "HTML",
    "css": "CSS",   
    "ci/cd": "CI/CD",
    "power bi": "Power BI",
    "machine learning": "Machine Learning",
    "manual testing": "Manual Testing",
    "api testing": "API Testing",
    "ai": "AI",
    "devops": "DevOps",
    "nlp": "NLP",
    "ui/ux": "UI/UX",
    "ui ux": "UI/UX",
    "qa qc": "QA QC",
    "golang": "Go",
    "go": "Go",
    ".net": ".NET",
    "c#": "C#",
    "c++": "C++",
}

SKILL_KEYWORDS = [
    ("javascript", "JavaScript"),
    ("typescript", "TypeScript"),
    ("reactjs", "React"),
    ("react native", "React Native"),
    ("react", "React"),
    ("angular", "Angular"),
    ("vue", "Vue.js"),
    ("next.js", "Next.js"),
    ("nextjs", "Next.js"),
    ("node.js", "Node.js"),
    ("nodejs", "Node.js"),
    ("express", "Express"),
    ("python", "Python"),
    ("django", "Django"),
    ("flask", "Flask"),
    ("fastapi", "FastAPI"),
    ("java", "Java"),
    ("spring", "Spring"),
    ("kotlin", "Kotlin"),
    ("php", "PHP"),
    ("laravel", "Laravel"),
    ("golang", "Go"),
    ("ruby", "Ruby"),
    ("rust", "Rust"),
    ("scala", "Scala"),
    ("swift", "Swift"),
    ("objective-c", "Objective-C"),
    ("flutter", "Flutter"),
    ("dart", "Dart"),
    (".net", ".NET"),
    ("asp.net", ".NET"),
    ("c#", "C#"),
    ("c++", "C++"),
    ("html", "HTML"),
    ("css", "CSS"),
    ("tailwind", "Tailwind"),
    ("bootstrap", "Bootstrap"),
    ("sql server", "SQL Server"),
    ("mysql", "MySQL"),
    ("postgresql", "PostgreSQL"),
    ("postgres", "PostgreSQL"),
    ("mongodb", "MongoDB"),
    ("redis", "Redis"),
    ("oracle", "Oracle"),
    ("elasticsearch", "Elasticsearch"),
    ("sql", "SQL"),
    ("aws", "AWS"),
    ("azure", "Azure"),
    ("gcp", "GCP"),
    ("google cloud", "GCP"),
    ("docker", "Docker"),
    ("kubernetes", "Kubernetes"),
    ("terraform", "Terraform"),
    ("jenkins", "Jenkins"),
    ("ci/cd", "CI/CD"),
    ("devops", "DevOps"),
    ("linux", "Linux"),
    ("git", "Git"),
    ("graphql", "GraphQL"),
    ("rest api", "REST API"),
    ("microservices", "Microservices"),
    ("machine learning", "Machine Learning"),
    ("deep learning", "Deep Learning"),
    ("data science", "Data Science"),
    ("data engineer", "Data Engineering"),
    ("data analyst", "Data Analysis"),
    ("big data", "Big Data"),
    ("spark", "Spark"),
    ("hadoop", "Hadoop"),
    ("airflow", "Airflow"),
    ("power bi", "Power BI"),
    ("tableau", "Tableau"),
    ("pandas", "Pandas"),
    ("tensorflow", "TensorFlow"),
    ("pytorch", "PyTorch"),
    ("nlp", "NLP"),
    ("computer vision", "Computer Vision"),
    ("ai", "AI"),
    ("manual testing", "Manual Testing"),
    ("automation test", "Automation Testing"),
    ("automation testing", "Automation Testing"),
    ("api testing", "API Testing"),
    ("tester", "Testing"),
    ("qa qc", "QA QC"),
    ("figma", "Figma"),
    ("ui/ux", "UI/UX"),
    ("ux/ui", "UI/UX"),
    ("agile", "Agile"),
    ("scrum", "Scrum"),
    ("english", "English"),
    ("japanese", "Japanese"),
    ("korean", "Korean"),
]

SPECIAL_TOKENS = {".net", "c#", "c++", "ci/cd", "ui/ux", "ux/ui", "node.js", "next.js", "react.js", "asp.net", "objective-c"}


def clean_skill(name):
    key = name.strip().lower()
    if key in SKILL_ALIASES:
        return SKILL_ALIASES[key]
    return name.strip().title()


def extract_skills(text):
    if not text:
        return []
    lowered = " " + text.lower() + " "
    found = []
    for token, canonical in SKILL_KEYWORDS:
        if token in SPECIAL_TOKENS:
            matched = token in lowered
        else:
            matched = re.search(r"(?<![a-z0-9])" + re.escape(token) + r"(?![a-z0-9])", lowered) is not None
        if matched and canonical not in found:
            found.append(canonical)
    return found


def parse_salary(text):
    lowered = text.lower().strip()
    if any(word in lowered for word in ["th\u1ecfa thu\u1eadn", "th\u01b0\u01a1ng l\u01b0\u1ee3ng", "c\u1ea1nh tranh", "nego"]):
        return (0.0, 0.0)
    if "usd" in lowered or "$" in lowered:
        cleaned = lowered.replace(",", "")
        numbers = [int(item) for item in re.findall(r"\d+", cleaned)]
        values = [round(number / 40.0, 1) for number in numbers]
    elif "tri\u1ec7u" in lowered:
        numbers = [int(item) for item in re.findall(r"\d+", lowered)]
        values = [float(number) for number in numbers]
    elif "vnd" in lowered or "\u0111\u1ed3ng" in lowered:
        cleaned = lowered.replace(".", "").replace(",", "")
        numbers = [int(item) for item in re.findall(r"\d+", cleaned)]
        values = [round(number / 1000000.0, 1) for number in numbers]
    else:
        numbers = [int(item) for item in re.findall(r"\d+", lowered)]
        values = [float(number) for number in numbers]
    if not values:
        return (0.0, 0.0)
    if len(values) == 1:
        if "up to" in lowered or "\u0111\u1ebfn" in lowered:
            return (0.0, values[0])
        if "from" in lowered or "tr\u00ean" in lowered or "t\u1eeb" in lowered:
            return (values[0], 0.0)
        return (values[0], values[0])
    return (min(values), max(values))


def parse_experience(text):
    lowered = text.lower()
    if "kh\u00f4ng y\u00eau c\u1ea7u" in lowered or "d\u01b0\u1edbi 1" in lowered or "kh\u00f4ng c\u1ea7n" in lowered:
        return 0
    numbers = [int(item) for item in re.findall(r"\d+", lowered)]
    if not numbers:
        return 0
    return min(numbers)


def experience_level(years):
    if years <= 0:
        return "Entry"
    if years <= 2:
        return "Junior"
    if years <= 4:
        return "Middle"
    return "Senior"
