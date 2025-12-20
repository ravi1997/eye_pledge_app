"""
Dashboard Analytics Module
Provides optimized data aggregation and analytics functions for the dashboard.
"""

from datetime import datetime, timedelta
from sqlalchemy import func, extract, case
from models import EyeDonationPledge, db
from collections import defaultdict


class DashboardAnalytics:
    """Main analytics class for dashboard data"""
    
    @staticmethod
    def get_summary_stats(start_date=None, end_date=None, state_filter=None):
        """
        Get summary statistics for dashboard cards.
        
        Args:
            start_date: Optional filter start date
            end_date: Optional filter end date
            state_filter: Optional state name to filter by
            
        Returns:
            dict: Summary statistics including totals, today, month, year
        """
        # Base query
        query = EyeDonationPledge.query.filter_by(is_active=True)
        
        # Apply filters
        if start_date:
            query = query.filter(EyeDonationPledge.created_at >= start_date)
        if end_date:
            query = query.filter(EyeDonationPledge.created_at <= end_date)
        if state_filter:
            query = query.filter(EyeDonationPledge.state == state_filter)
        
        # Calculate various metrics
        total_pledges = query.count()
        
        # Today's pledges
        today = datetime.now().date()
        today_pledges = query.filter(
            func.date(EyeDonationPledge.created_at) == today
        ).count()
        
        # Yesterday's pledges (for % change)
        yesterday = today - timedelta(days=1)
        yesterday_pledges = query.filter(
            func.date(EyeDonationPledge.created_at) == yesterday
        ).count()
        
        # This month
        current_year = datetime.now().year
        current_month = datetime.now().month
        this_month_pledges = query.filter(
            extract('year', EyeDonationPledge.created_at) == current_year,
            extract('month', EyeDonationPledge.created_at) == current_month
        ).count()
        
        # Last month (for % change)
        if current_month == 1:
            last_month_year = current_year - 1
            last_month = 12
        else:
            last_month_year = current_year
            last_month = current_month - 1
            
        last_month_pledges = query.filter(
            extract('year', EyeDonationPledge.created_at) == last_month_year,
            extract('month', EyeDonationPledge.created_at) == last_month
        ).count()
        
        # This year
        this_year_pledges = query.filter(
            extract('year', EyeDonationPledge.created_at) == current_year
        ).count()
        
        # Last year (for % change)
        last_year_pledges = query.filter(
            extract('year', EyeDonationPledge.created_at) == current_year - 1
        ).count()
        
        # Average per day (last 30 days)
        thirty_days_ago = today - timedelta(days=30)
        last_30_days_pledges = query.filter(
            func.date(EyeDonationPledge.created_at) >= thirty_days_ago
        ).count()
        avg_per_day = round(last_30_days_pledges / 30, 1)
        
        # Calculate percentage changes
        def calc_percent_change(current, previous):
            if previous == 0:
                return 100 if current > 0 else 0
            return round(((current - previous) / previous) * 100, 1)
        
        return {
            'total_pledges': total_pledges,
            'today_pledges': today_pledges,
            'today_change_pct': calc_percent_change(today_pledges, yesterday_pledges),
            'this_month_pledges': this_month_pledges,
            'month_change_pct': calc_percent_change(this_month_pledges, last_month_pledges),
            'this_year_pledges': this_year_pledges,
            'year_change_pct': calc_percent_change(this_year_pledges, last_year_pledges),
            'avg_per_day': avg_per_day,
        }
    
    @staticmethod
    def get_temporal_trends(period='daily', limit=30, state_filter=None):
        """
        Get temporal trend data.
        
        Args:
            period: 'daily', 'weekly', 'monthly', or 'yearly'
            limit: Number of periods to return
            state_filter: Optional state filter
            
        Returns:
            dict: Labels and data arrays for charting
        """
        query = EyeDonationPledge.query.filter_by(is_active=True)
        
        if state_filter:
            query = query.filter(EyeDonationPledge.state == state_filter)
        
        if period == 'daily':
            # Last N days
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=limit - 1)
            
            daily_data = db.session.query(
                func.date(EyeDonationPledge.created_at).label('date'),
                func.count(EyeDonationPledge.id).label('count')
            ).filter(
                EyeDonationPledge.is_active == True,
                func.date(EyeDonationPledge.created_at) >= start_date
            ).group_by('date').order_by('date').all()
            
            # Fill gaps
            date_dict = {str(row.date): row.count for row in daily_data}
            labels = []
            data = []
            
            for i in range(limit):
                current_date = end_date - timedelta(days=limit - 1 - i)
                labels.append(current_date.strftime('%d %b'))
                data.append(date_dict.get(str(current_date), 0))
                
            return {'labels': labels, 'data': data}
        
        elif period == 'monthly':
            # Last N months
            current_year = datetime.now().year
            monthly_data = db.session.query(
                extract('year', EyeDonationPledge.created_at).label('year'),
                extract('month', EyeDonationPledge.created_at).label('month'),
                func.count(EyeDonationPledge.id).label('count')
            ).filter(
                EyeDonationPledge.is_active == True
            ).group_by('year', 'month').order_by('year', 'month').all()
            
            # Create a dictionary for easy lookup
            data_dict = {(int(row.year), int(row.month)): row.count for row in monthly_data}
            
            labels = []
            data = []
            
            # Get last N months
            end_date = datetime.now()
            for i in range(limit - 1, -1, -1):
                target_date = end_date - timedelta(days=i * 30)
                year, month = target_date.year, target_date.month
                labels.append(target_date.strftime('%b %Y'))
                data.append(data_dict.get((year, month), 0))
            
            return {'labels': labels, 'data': data}
        
        elif period == 'yearly':
            # Yearly trend
            yearly_data = db.session.query(
                extract('year', EyeDonationPledge.created_at).label('year'),
                func.count(EyeDonationPledge.id).label('count')
            ).filter(
                EyeDonationPledge.is_active == True
            ).group_by('year').order_by('year').all()
            
            labels = [str(int(row.year)) for row in yearly_data]
            data = [row.count for row in yearly_data]
            
            return {'labels': labels, 'data': data}
        
        return {'labels': [], 'data': []}
    
    @staticmethod
    def get_geographic_distribution(top_n=10):
        """
        Get geographic distribution of pledges.
        
        Args:
            top_n: Number of top states/cities to return
            
        Returns:
            dict: State-wise and city-wise breakdowns
        """
        # Top states
        top_states = db.session.query(
            EyeDonationPledge.state,
            func.count(EyeDonationPledge.id).label('count')
        ).filter_by(is_active=True).group_by(
            EyeDonationPledge.state
        ).order_by(func.count(EyeDonationPledge.id).desc()).limit(top_n).all()
        
        # Top cities
        top_cities = db.session.query(
            EyeDonationPledge.city,
            EyeDonationPledge.state,
            func.count(EyeDonationPledge.id).label('count')
        ).filter_by(is_active=True).group_by(
            EyeDonationPledge.city,
            EyeDonationPledge.state
        ).order_by(func.count(EyeDonationPledge.id).desc()).limit(top_n).all()
        
        # All states for map
        all_states = db.session.query(
            EyeDonationPledge.state,
            func.count(EyeDonationPledge.id).label('count')
        ).filter_by(is_active=True).group_by(
            EyeDonationPledge.state
        ).all()
        
        return {
            'top_states': [{'state': s.state, 'count': s.count} for s in top_states],
            'top_cities': [{'city': c.city, 'state': c.state, 'count': c.count} for c in top_cities],
            'all_states': {s.state: s.count for s in all_states}
        }
    
    @staticmethod
    def get_demographic_insights():
        """
        Get anonymized demographic insights.
        
        Returns:
            dict: Age group and gender distribution
        """
        # Age group distribution
        age_groups = db.session.query(
            case(
                (EyeDonationPledge.donor_age < 18, '< 18'),
                (EyeDonationPledge.donor_age.between(18, 25), '18-25'),
                (EyeDonationPledge.donor_age.between(26, 35), '26-35'),
                (EyeDonationPledge.donor_age.between(36, 45), '36-45'),
                (EyeDonationPledge.donor_age.between(46, 60), '46-60'),
                else_='60+'
            ).label('age_group'),
            func.count(EyeDonationPledge.id).label('count')
        ).filter_by(is_active=True).filter(
            EyeDonationPledge.donor_age.isnot(None)
        ).group_by('age_group').all()
        
        # Gender distribution
        gender_dist = db.session.query(
            EyeDonationPledge.donor_gender,
            func.count(EyeDonationPledge.id).label('count')
        ).filter_by(is_active=True).filter(
            EyeDonationPledge.donor_gender.isnot(None)
        ).group_by(EyeDonationPledge.donor_gender).all()
        
        return {
            'age_groups': [{'group': ag[0], 'count': ag[1]} for ag in age_groups],
            'gender': [{'gender': g.donor_gender, 'count': g.count} for g in gender_dist]
        }
    
    @staticmethod
    def get_growth_metrics():
        """
        Calculate growth metrics and rates.
        
        Returns:
            dict: Growth rates and cumulative trends
        """
        # Month-over-month growth for last 12 months
        current_date = datetime.now()
        monthly_counts = []
        
        for i in range(12, 0, -1):
            target_date = current_date - timedelta(days=i * 30)
            year, month = target_date.year, target_date.month
            
            count = EyeDonationPledge.query.filter_by(is_active=True).filter(
                extract('year', EyeDonationPledge.created_at) == year,
                extract('month', EyeDonationPledge.created_at) == month
            ).count()
            
            monthly_counts.append({
                'month': target_date.strftime('%b %Y'),
                'count': count
            })
        
        # Calculate growth rates
        growth_rates = []
        for i in range(1, len(monthly_counts)):
            prev_count = monthly_counts[i - 1]['count']
            curr_count = monthly_counts[i]['count']
            
            if prev_count > 0:
                growth_rate = ((curr_count - prev_count) / prev_count) * 100
            else:
                growth_rate = 100 if curr_count > 0 else 0
                
            growth_rates.append({
                'month': monthly_counts[i]['month'],
                'rate': round(growth_rate, 1)
            })
        
        return {
            'monthly_counts': monthly_counts,
            'growth_rates': growth_rates
        }
    
    @staticmethod
    def get_peak_activity_analysis():
        """
        Analyze peak activity patterns (hour of day, day of week).
        
        Returns:
            dict: Activity patterns by hour and day
        """
        # Hour of day distribution
        hourly_dist = db.session.query(
            extract('hour', EyeDonationPledge.created_at).label('hour'),
            func.count(EyeDonationPledge.id).label('count')
        ).filter_by(is_active=True).group_by('hour').order_by('hour').all()
        
        # Day of week distribution (0 = Monday, 6 = Sunday)
        daily_dist = db.session.query(
            extract('dow', EyeDonationPledge.created_at).label('day'),
            func.count(EyeDonationPledge.id).label('count')
        ).filter_by(is_active=True).group_by('day').order_by('day').all()
        
        # Day names
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Create 24-hour array
        hourly_data = [0] * 24
        for row in hourly_dist:
            hourly_data[int(row.hour)] = row.count
        
        # Create 7-day array
        daily_data_dict = {int(row.day): row.count for row in daily_dist}
        daily_data = []
        for i in range(7):
            # PostgreSQL: 0 = Sunday, 1 = Monday, ..., 6 = Saturday
            # Convert to: 0 = Monday, ..., 6 = Sunday
            pg_day = (i + 1) % 7
            daily_data.append(daily_data_dict.get(pg_day, 0))
        
        return {
            'hourly': {
                'labels': [f'{h:02d}:00' for h in range(24)],
                'data': hourly_data
            },
            'daily': {
                'labels': day_names,
                'data': daily_data
            }
        }
    
    @staticmethod
    def get_language_preference_distribution():
        """
        Get distribution of language preferences.
        
        Returns:
            dict: Language preference breakdown
        """
        lang_dist = db.session.query(
            EyeDonationPledge.language_preference,
            func.count(EyeDonationPledge.id).label('count')
        ).filter_by(is_active=True).filter(
            EyeDonationPledge.language_preference.isnot(None)
        ).group_by(EyeDonationPledge.language_preference).all()
        
        return {
            'languages': [{'language': l.language_preference, 'count': l.count} for l in lang_dist]
        }    @staticmethod
    def get_historical_comparison(years=5):
        """
        Get pledge comparisons for the last N years.
        
        Args:
            years: Number of years to compare
            
        Returns:
            dict: Year-wise labels and data
        """
        current_year = datetime.now().year
        data_by_year = {}
        
        # Calculate start year
        start_year = current_year - years + 1
        
        print(f"Adding historical comparison from {start_year}")
        
        # Query for yearly aggregation
        yearly_counts = db.session.query(
            extract('year', EyeDonationPledge.created_at).label('year'),
            func.count(EyeDonationPledge.id).label('count')
        ).filter(
            EyeDonationPledge.is_active == True,
            extract('year', EyeDonationPledge.created_at) >= start_year
        ).group_by('year').order_by('year').all()
        
        # Format response
        labels = []
        data = []
        
        for row in yearly_counts:
            labels.append(str(int(row.year)))
            data.append(row.count)
            
        return {
            'labels': labels,
            'data': data
        }

    @staticmethod
    def get_comparative_metrics():
        """
        Get comparative indicators (MoM, YoY).
        """
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        # Query total count function
        def get_count_for_period(year, month=None):
            q = EyeDonationPledge.query.filter_by(is_active=True).filter(
                extract('year', EyeDonationPledge.created_at) == year
            )
            if month:
                q = q.filter(extract('month', EyeDonationPledge.created_at) == month)
            return q.count()

        # Month over Month
        this_month_count = get_count_for_period(current_year, current_month)
        
        if current_month == 1:
            last_month_count = get_count_for_period(current_year - 1, 12)
        else:
            last_month_count = get_count_for_period(current_year, current_month - 1)
            
        mom_growth = 0
        if last_month_count > 0:
            mom_growth = round(((this_month_count - last_month_count) / last_month_count) * 100, 1)

        # Year over Year (YTD) to compare fair progress
        # Compare Jan-CurrentMonth of this year vs Jan-CurrentMonth of last year
        # This is more accurate than comparing a partial 2024 to a full 2023
        
        # Logic for YTD
        # Since standard SQL alchemy filtering for "month <= X" inside extract can be complex across DBs in YTD context, 
        # we will fetch full year counts for simplicity in this version, 
        # OR implement a rough YoY of total yearly volume.
        # Let's stick to Total Year comparison for "YoY" card generally.
        
        this_year_count = get_count_for_period(current_year)
        last_year_count = get_count_for_period(current_year - 1)
        
        yoy_growth = 0
        if last_year_count > 0:
            yoy_growth = round(((this_year_count - last_year_count) / last_year_count) * 100, 1)

        return {
            'mom': {'value': mom_growth, 'count': this_month_count, 'prev_count': last_month_count},
            'yoy': {'value': yoy_growth, 'count': this_year_count, 'prev_count': last_year_count}
        }

    @staticmethod
    def get_source_distribution():
        """Get breakdown of pledges by source."""
        results = db.session.query(
            EyeDonationPledge.source,
            func.count(EyeDonationPledge.id)
        ).filter_by(is_active=True).group_by(EyeDonationPledge.source).all()
        
        labels = [r[0] for r in results]
        data = [r[1] for r in results]
        
        return {'labels': labels, 'data': data}

    @staticmethod
    def get_medical_consent_stats():
        """Get stats on consent types (Cornea vs Whole Eye)."""
        results = db.session.query(
            EyeDonationPledge.organs_consented,
            func.count(EyeDonationPledge.id)
        ).filter_by(is_active=True).group_by(EyeDonationPledge.organs_consented).all()
        
        return [{'label': r[0], 'value': r[1]} for r in results]

    @staticmethod
    def get_district_wise_stats(state_name):
        """Get district-level stats for a specific state."""
        results = db.session.query(
            EyeDonationPledge.district,
            func.count(EyeDonationPledge.id)
        ).filter(
            EyeDonationPledge.is_active == True,
            EyeDonationPledge.state == state_name,
            EyeDonationPledge.district.isnot(None)
        ).group_by(EyeDonationPledge.district).order_by(func.count(EyeDonationPledge.id).desc()).all()
        
        return [{'district': r[0], 'count': r[1]} for r in results]
