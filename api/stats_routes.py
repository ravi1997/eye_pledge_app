from flask import Blueprint, jsonify
from dashboard_analytics import DashboardAnalytics

stats_bp = Blueprint('stats', __name__, url_prefix='/neb/api/stats')

@stats_bp.route('/summary')
def get_summary():
    """Get high-level summary statistics"""
    data = DashboardAnalytics.get_summary_stats()
    return jsonify(data)

@stats_bp.route('/monthly')
def get_monthly_trend():
    """Get monthly pledge trend for the current year"""
    data = DashboardAnalytics.get_temporal_trends(period='monthly', limit=12)
    # Ensure current year focus if needed by frontend, but standard monthly is fine
    return jsonify(data)

@stats_bp.route('/weekly')
def get_weekly_trend():
    """Get last 7 days pledge trend"""
    data = DashboardAnalytics.get_temporal_trends(period='daily', limit=7)
    return jsonify({
        'labels': data['labels'],
        'data': data['data']
    })

@stats_bp.route('/yearly')
def get_yearly_growth():
    """Get yearly cumulative growth"""
    data = DashboardAnalytics.get_temporal_trends(period='yearly')
    return jsonify(data)

@stats_bp.route('/historical')
def get_historical():
    """Get multi-year historical data"""
    data = DashboardAnalytics.get_historical_comparison(years=5)
    return jsonify(data)

@stats_bp.route('/comparative')
def get_comparative():
    """Get comparative growth metrics"""
    data = DashboardAnalytics.get_comparative_metrics()
    return jsonify(data)

@stats_bp.route('/sources')
def get_sources():
    """Get pledge source distribution"""
    data = DashboardAnalytics.get_source_distribution()
    return jsonify(data)

@stats_bp.route('/consent')
def get_consent():
    """Get medical consent breakdown"""
    data = DashboardAnalytics.get_medical_consent_stats()
    return jsonify(data)

@stats_bp.route('/districts/<path:state_name>')
def get_districts(state_name):
    """Get district stats for a state"""
    data = DashboardAnalytics.get_district_wise_stats(state_name)
    return jsonify(data)

@stats_bp.route('/states')
def get_top_states():
    """Get top contributing states"""
    # Assuming frontend wants simple list or detailed map data
    data = DashboardAnalytics.get_geographic_distribution(top_n=5)
    
    # Format for the list view in stats.html
    # The existing template expects a list of [state, count] tuples or objects
    formatted_states = [[s['state'], s['count']] for s in data['top_states']]
    return jsonify(formatted_states)

@stats_bp.route('/demographics')
def get_demographics():
    """Get age and gender distribution"""
    data = DashboardAnalytics.get_demographic_insights()
    
    # Age chart data formatting
    age_labels = [item['group'] for item in data['age_groups']]
    age_counts = [item['count'] for item in data['age_groups']]
    
    # Gender chart data formatting
    gender_labels = [item['gender'] for item in data['gender']]
    gender_counts = [item['count'] for item in data['gender']]
    
    return jsonify({
        'age': {'labels': age_labels, 'data': age_counts},
        'gender': {'labels': gender_labels, 'data': gender_counts}
    })

@stats_bp.route('/hourly')
def get_hourly_activity():
    """Get hourly activity pattern"""
    data = DashboardAnalytics.get_peak_activity_analysis()
    return jsonify(data['hourly'])
