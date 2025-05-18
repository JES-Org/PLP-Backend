import numpy as np
from statistics import mode, StatisticsError
from assessments.models import Assessment, Submission

class AnalyticsService:
    @staticmethod
    def perform_class_analysis(assessment_id):
        submissions = Submission.objects.filter(assessment_id=assessment_id)
        scores = [s.score for s in submissions]
        if not scores:
            return None

        return {
            "meanScore": np.mean(scores),
            "medianScore": np.median(scores),
            "modeScore": AnalyticsService.get_mode(scores),
            "standardDeviation": np.std(scores),
            "variance": np.var(scores),
            "highestScore": max(scores),
            "lowestScore": min(scores),
            "range": max(scores) - min(scores),
            "totalSubmissions": len(scores),
        }

    @staticmethod
    def get_mode(scores):
        try:
            return mode(scores)
        except StatisticsError:
            return None

    @staticmethod
    def perform_cross_assessment(classroom_id):
        assessments = Assessment.objects.filter(classroom_id=classroom_id)
        return [
            {
                "assessmentId": a.id,
                "name": a.name,
                **AnalyticsService.perform_class_analysis(a.id)
            } for a in assessments
        ]
