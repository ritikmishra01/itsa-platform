from flask import Blueprint, request
from flask_login import login_required, current_user
from app.services.gamification_service import GamificationService
from app.services.ai_service import AIService
from app.utils.responses import success_response

gamification_bp = Blueprint('api_gamification', __name__, url_prefix='/api/v1')

@gamification_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    dept = request.args.get('department')
    year = request.args.get('year')
    year_int = int(year) if year else None
    leaderboard = GamificationService.get_leaderboard(limit=50, department=dept, year_of_study=year_int)
    return success_response(leaderboard)


@gamification_bp.route('/points/my', methods=['GET'])
@login_required
def get_my_points():
    history = GamificationService.get_user_points_history(current_user.id)
    score, breakdown = AIService.calculate_engagement_score(current_user)
    return success_response({
        'total_points': current_user.student_profile.total_points if current_user.student_profile else 0,
        'engagement_score': score,
        'engagement_breakdown': breakdown,
        'transactions': [tx.to_dict() for tx in history]
    })
