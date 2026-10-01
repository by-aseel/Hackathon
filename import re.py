import re
import json
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from pypdf import PdfReader
`
# ============================================================
# 1. JOB DESCRIPTION
# ============================================================

JOB_DESCRIPTION = {
    "title": "AI / Data Analyst",

    "required_skills": [
        "python",
        "machine learning",
        "data analysis",
        "sql"
    ],

    "preferred_skills": [
        "tensorflow",
        "pytorch",
        "scikit-learn",
        "pandas",
        "numpy"
    ],

    "minimum_experience_years": 1,

    "education": [
        "computer science",
        "electrical engineering",
        "data science",
        "artificial intelligence",
        "engineering"
    ]
}


# ============================================================
# 2. SKILL NORMALIZATION
# ============================================================

SKILL_ALIASES = {

    "python": [
        "python",
        "python3"
    ],

    "machine learning": [
        "machine learning",
        "ml"
    ],

    "deep learning": [
        "deep learning",
        "dl"
    ],

    "data analysis": [
        "data analysis",
        "data analytics",
        "data analyst"
    ],

    "sql": [
        "sql",
        "mysql",
        "postgresql",
        "postgres"
    ],

    "tensorflow": [
        "tensorflow",
        "tf"
    ],

    "pytorch": [
        "pytorch",
        "torch"
    ],

    "scikit-learn": [
        "scikit-learn",
        "sklearn"
    ],

    "pandas": [
        "pandas"
    ],

    "numpy": [
        "numpy"
    ],

    "power bi": [
        "power bi",
        "powerbi"
    ],

    "excel": [
        "excel",
        "microsoft excel"
    ]
}


# ============================================================
# 3. RESUME EXTRACTION AGENT
# ============================================================

class ResumeExtractionAgent:

    """
    Agent responsible only for extracting factual information
    from a resume.

    It does NOT make hiring decisions.
    """

    def extract_text(self, pdf_path: str) -> str:

        reader = PdfReader(pdf_path)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    def extract_skills(self, text: str) -> List[str]:

        text_lower = text.lower()

        detected = []

        for normalized_skill, aliases in SKILL_ALIASES.items():

            for alias in aliases:

                if alias.lower() in text_lower:

                    detected.append(normalized_skill)
                    break

        return sorted(set(detected))

    def extract_experience(self, text: str) -> float:

        """
        Simple rule-based extraction of years of experience.

        Examples detected:
        '3 years of experience'
        '5+ years experience'
        """

        patterns = [
            r"(\d+)\+?\s+years?\s+of\s+experience",
            r"(\d+)\+?\s+years?\s+experience"
        ]

        years = []

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text.lower()
            )

            for value in matches:
                years.append(float(value))

        if not years:
            return 0.0

        return max(years)

    def extract_education(self, text: str) -> List[str]:

        education_keywords = [
            "computer science",
            "electrical engineering",
            "data science",
            "artificial intelligence",
            "engineering"
        ]

        text_lower = text.lower()

        found = []

        for education in education_keywords:

            if education in text_lower:
                found.append(education)

        return sorted(set(found))

    def run(self, pdf_path: str) -> Dict[str, Any]:

        text = self.extract_text(pdf_path)

        result = {
            "skills": self.extract_skills(text),
            "experience_years": self.extract_experience(text),
            "education": self.extract_education(text)
        }

        return result


# ============================================================
# 4. MATCHING AGENT
# ============================================================

class MatchingAgent:

    """
    This agent performs deterministic scoring.

    The AI does NOT decide the score.
    """

    REQUIRED_WEIGHT = 70
    PREFERRED_WEIGHT = 20
    EXPERIENCE_WEIGHT = 10

    def calculate_required_skill_score(
        self,
        resume_skills: List[str]
    ):

        required = JOB_DESCRIPTION["required_skills"]

        matched = [
            skill
            for skill in required
            if skill in resume_skills
        ]

        score = (
            len(matched) /
            len(required)
        ) * 100

        return score, matched

    def calculate_preferred_skill_score(
        self,
        resume_skills: List[str]
    ):

        preferred = JOB_DESCRIPTION["preferred_skills"]

        matched = [
            skill
            for skill in preferred
            if skill in resume_skills
        ]

        if not preferred:
            return 0, matched

        score = (
            len(matched) /
            len(preferred)
        ) * 100

        return score, matched

    def calculate_experience_score(
        self,
        experience_years: float
    ):

        required = JOB_DESCRIPTION[
            "minimum_experience_years"
        ]

        if experience_years >= required:
            return 100

        return (
            experience_years /
            required
        ) * 100

    def run(
        self,
        extracted_resume: Dict[str, Any]
    ):

        skills = extracted_resume["skills"]

        required_score, required_matched = (
            self.calculate_required_skill_score(skills)
        )

        preferred_score, preferred_matched = (
            self.calculate_preferred_skill_score(skills)
        )

        experience_score = (
            self.calculate_experience_score(
                extracted_resume["experience_years"]
            )
        )

        final_score = (

            required_score *
            (self.REQUIRED_WEIGHT / 100)

            +

            preferred_score *
            (self.PREFERRED_WEIGHT / 100)

            +

            experience_score *
            (self.EXPERIENCE_WEIGHT / 100)
        )

        return {

            "final_score": round(final_score, 2),

            "required_skill_score":
                round(required_score, 2),

            "preferred_skill_score":
                round(preferred_score, 2),

            "experience_score":
                round(experience_score, 2),

            "matched_required_skills":
                required_matched,

            "matched_preferred_skills":
                preferred_matched,

            "missing_required_skills": [
                skill
                for skill in JOB_DESCRIPTION["required_skills"]
                if skill not in skills
            ]
        }


# ============================================================
# 5. EXPLANATION AGENT
# ============================================================

class ExplanationAgent:

    """
    Generates a transparent explanation from the
    structured evidence.

    It does not invent evidence.
    """

    def run(
        self,
        extracted: Dict[str, Any],
        matching: Dict[str, Any]
    ):

        explanation = []

        # Required skills

        matched_required = matching[
            "matched_required_skills"
        ]

        missing_required = matching[
            "missing_required_skills"
        ]

        if matched_required:

            explanation.append(
                "Required skills matched: "
                + ", ".join(matched_required)
                + "."
            )

        if missing_required:

            explanation.append(
                "Required skills not found in the "
                "resume: "
                + ", ".join(missing_required)
                + "."
            )

        # Preferred skills

        preferred = matching[
            "matched_preferred_skills"
        ]

        if preferred:

            explanation.append(
                "Preferred skills found: "
                + ", ".join(preferred)
                + "."
            )

        # Experience

        experience = extracted[
            "experience_years"
        ]

        required_experience = JOB_DESCRIPTION[
            "minimum_experience_years"
        ]

        if experience >= required_experience:

            explanation.append(
                f"The resume reports {experience:g} "
                f"years of experience, meeting the "
                f"minimum requirement of "
                f"{required_experience} year."
            )

        else:

            explanation.append(
                f"The resume reports {experience:g} "
                f"years of experience, below the "
                f"minimum requirement of "
                f"{required_experience} year."
            )

        # Education

        education = extracted["education"]

        if education:

            explanation.append(
                "Relevant educational background found: "
                + ", ".join(education)
                + "."
            )

        return explanation


# ============================================================
# 6. FAIRNESS / CONSISTENCY AGENT
# ============================================================

class FairnessAgent:

    """
    Checks whether the scoring process relies on
    protected or irrelevant personal attributes.

    These attributes are intentionally ignored.
    """

    IGNORED_ATTRIBUTES = [
        "name",
        "gender",
        "age",
        "nationality",
        "religion",
        "marital status",
        "photo",
        "address"
    ]

    def run(self, resume_text: str):

        text_lower = resume_text.lower()

        detected_ignored = []

        for attribute in self.IGNORED_ATTRIBUTES:

            if attribute in text_lower:

                detected_ignored.append(attribute)

        return {

            "protected_attributes_detected":
                detected_ignored,

            "protected_attributes_used_for_score":
                False,

            "fairness_note":
                "Scoring is based on job-related "
                "skills and experience only."
        }


# ============================================================
# 7. CONSISTENCY AGENT
# ============================================================

class ConsistencyAgent:

    """
    Checks whether the same structured resume data
    produces the same score.

    This is important for reproducibility.
    """

    def run(
        self,
        extracted_resume: Dict[str, Any]
    ):

        matcher = MatchingAgent()

        result_1 = matcher.run(
            extracted_resume
        )

        result_2 = matcher.run(
            extracted_resume
        )

        consistent = (
            result_1["final_score"]
            ==
            result_2["final_score"]
        )

        return {

            "consistent": consistent,

            "score_1":
                result_1["final_score"],

            "score_2":
                result_2["final_score"]
        }


# ============================================================
# 8. MAIN AGENTIC PIPELINE
# ============================================================

class ResumeScreeningSystem:

    def __init__(self):

        self.extractor = ResumeExtractionAgent()

        self.matcher = MatchingAgent()

        self.explainer = ExplanationAgent()

        self.fairness = FairnessAgent()

        self.consistency = ConsistencyAgent()

    def run(self, pdf_path: str):

        # ---------------------------------------
        # Agent 1: Extract information
        # ---------------------------------------

        extracted = self.extractor.run(
            pdf_path
        )

        # ---------------------------------------
        # Agent 2: Match against job
        # ---------------------------------------

        matching = self.matcher.run(
            extracted
        )

        # ---------------------------------------
        # Agent 3: Generate explanation
        # ---------------------------------------

        explanation = self.explainer.run(
            extracted,
            matching
        )

        # ---------------------------------------
        # Agent 4: Fairness check
        # ---------------------------------------

        resume_text = self.extractor.extract_text(
            pdf_path
        )

        fairness = self.fairness.run(
            resume_text
        )

        # ---------------------------------------
        # Agent 5: Consistency check
        # ---------------------------------------

        consistency = self.consistency.run(
            extracted
        )

        # ---------------------------------------
        # Final result
        # ---------------------------------------

        return {

            "resume": extracted,

            "matching": matching,

            "explanation": explanation,

            "fairness": fairness,

            "consistency": consistency
        }


# ============================================================
# 9. FASTAPI
# ============================================================

app = FastAPI(
    title="Fair & Transparent CV Screener"
)

screening_system = ResumeScreeningSystem()


@app.post("/screen")
async def screen_resume(
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF resumes are supported."
        )

    temp_dir = Path("temp_resumes")

    temp_dir.mkdir(
        exist_ok=True
    )

    file_path = (
        temp_dir /
        file.filename
    )

    content = await file.read()

    with open(file_path, "wb") as f:

        f.write(content)

    try:

        result = screening_system.run(
            str(file_path)
        )

        return result

    finally:

        if file_path.exists():

            file_path.unlink()


# ============================================================
# 10. RUN SERVER
# ============================================================

# Run with:
#
# uvicorn main:app --reload
#
# Then open:
#
# http://127.0.0.1:8000/docs