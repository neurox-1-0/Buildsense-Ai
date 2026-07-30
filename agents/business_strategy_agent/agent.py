"""Generate business strategies grounded in analyzed market evidence."""

import json
from tools.openai_client import OpenAIClient
from prompts.strategy_prompts import STRATEGY_SYSTEM_PROMPT
from schemas.strategy_schema import Recommendation
from agents.business_strategy_agent.strategy_generator import generate_local_strategies
from agents.business_strategy_agent.strategy_comparator import rank_strategies
from agents.business_strategy_agent.recommendation_builder import build_recommendation


class BusinessStrategyAgent:
    def __init__(self) -> None:
        self.openai = OpenAIClient()

    def run(self, objective: dict, report: dict, constraints: dict | None = None) -> dict:
        constraints = constraints or {}
        ai_result = self.openai.json_response(
            STRATEGY_SYSTEM_PROMPT,
            json.dumps(
                {"objective": objective, "intelligence": report, "human_constraints": constraints},
                ensure_ascii=False,
            ),
        )
        if ai_result:
            try:
                recommendation = Recommendation.model_validate(ai_result).model_dump()
                self._validate_grounding(recommendation, report, constraints, objective=objective)
                self._validate_decision_quality(recommendation, objective, report)
                recommendation["strategy_engine"] = "openai"
                return recommendation
            except Exception:
                pass
        strategies = rank_strategies(generate_local_strategies(objective, report))
        required = constraints.get("required_constraints", [])
        if required:
            requirement_text = "; ".join(required)
            for strategy in strategies:
                strategy["description"] += f" Required management conditions: {requirement_text}."
        recommendation = Recommendation.model_validate(
            build_recommendation(strategies, report, objective)
        ).model_dump()
        self._validate_grounding(
            recommendation,
            report,
            constraints,
            enforce_constraints=False,
            objective=objective,
        )
        self._validate_decision_quality(recommendation, objective, report)
        recommendation["strategy_engine"] = "local_rules"
        return recommendation

    @staticmethod
    def _validate_grounding(
        recommendation: dict,
        report: dict,
        constraints: dict,
        enforce_constraints: bool = True,
        objective: dict | None = None,
    ) -> None:
        valid_ids = {
            evidence_id
            for item in report.get("items", [])
            for evidence_id in item.get("evidence_ids", [])
        }
        strategies = [
            recommendation["recommended_strategy"],
            *recommendation.get("alternatives", []),
        ]
        if valid_ids:
            for strategy in strategies:
                cited = set(strategy.get("evidence_ids", []))
                if not cited or not cited.issubset(valid_ids):
                    raise ValueError("Every strategy must cite valid evidence IDs")
            final_report = recommendation.get("final_business_report", {})
            for answer in final_report.get("requirement_answers", []):
                cited = set(answer.get("evidence_ids", []))
                if cited and not cited.issubset(valid_ids):
                    raise ValueError("Requirement answer cited an unknown evidence ID")
            for section in final_report.get("dynamic_sections", []):
                cited = set(section.get("evidence_ids", []))
                if cited and not cited.issubset(valid_ids):
                    raise ValueError("Dynamic report section cited an unknown evidence ID")
        if enforce_constraints:
            combined = " ".join(
                f"{item['title']} {item['description']} {item['justification']}"
                for item in strategies
            ).lower()
            for prohibited in constraints.get("prohibited_constraints", []):
                phrase = prohibited.lower()
                for marker in ("do not", "don't", "avoid", "exclude", "must not"):
                    phrase = phrase.replace(marker, "")
                phrase = phrase.strip(" :,-")
                if phrase and phrase in combined:
                    raise ValueError(f"Strategy violated prohibited constraint: {prohibited}")
            for required in constraints.get("required_constraints", []):
                if required.lower() not in combined:
                    raise ValueError(f"Strategy omitted required constraint: {required}")

    @staticmethod
    def _validate_decision_quality(
        recommendation: dict,
        objective: dict,
        intelligence: dict | None = None,
    ) -> None:
        """Reject outputs that hand the requested decision back to the user."""
        report = recommendation.get("final_business_report", {})
        prohibited_deferrals = (
            "conduct market research",
            "do more research",
            "investigate areas",
            "investigate locations",
            "gather localized",
            "identify a suitable location",
            "find a suitable location",
            "determine the best location",
            "invest in inventory",
        )
        decision_texts = [
            report.get("overall_recommendation", ""),
            *report.get("operational_improvements", []),
            *[
                answer.get("recommendation", "")
                for answer in report.get("requirement_answers", [])
            ],
        ]
        combined = " ".join(decision_texts).lower()
        for phrase in prohibited_deferrals:
            if phrase in combined:
                raise ValueError(f"Recommendation deferred the requested decision: {phrase}")

        objective_text = " ".join(
            str(objective.get(key, ""))
            for key in ("title", "description")
        ).lower()
        location_requested = any(
            term in objective_text
            for term in ("location", "where", "area", "city", "suitable place")
        )
        if location_requested:
            location_answers = [
                answer
                for answer in report.get("requirement_answers", [])
                if any(
                    term in answer.get("requirement", "").lower()
                    for term in ("location", "where", "area", "city", "place")
                )
            ]
            if not location_answers:
                raise ValueError("Location requirement did not receive a direct answer")
            if any(
                len(answer.get("recommendation", "").strip()) < 45
                for answer in location_answers
            ):
                raise ValueError("Location recommendation was not specific enough")
            supported_location_terms = [
                candidate.get("name", "")
                for candidate in (intelligence or {}).get("location_candidates", [])
            ] + [
                candidate.get("address", "")
                for candidate in (intelligence or {}).get("location_candidates", [])
            ] + [objective.get("target_market", "")]
            supported_location_terms = [
                term.lower() for term in supported_location_terms
                if term and len(term.strip()) >= 4
            ]
            if supported_location_terms and not any(
                any(term in answer.get("recommendation", "").lower() for term in supported_location_terms)
                for answer in location_answers
            ):
                raise ValueError("Location recommendation was not grounded in a supported candidate or target market")

        overall = report.get("overall_recommendation", "").strip()
        if len(overall) < 60:
            raise ValueError("Overall recommendation is too generic")
