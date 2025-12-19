"""
Unit tests for advanced metrics calculation
"""
import pytest
from src.analytics.metrics import (
    AdvancedMetricsCalculator,
    calculate_advanced_metrics
)
from tests.fixtures.sample_data import (
    get_sample_transformed_player_stat,
    get_sample_transformed_stat_without_ts
)


class TestAdvancedMetricsCalculator:
    """Test suite for AdvancedMetricsCalculator class methods"""
    
    def setup_method(self):
        """Setup before each test"""
        self.calculator = AdvancedMetricsCalculator()
    
    def test_calculate_true_shooting_pct_normal(self):
        """Test true shooting percentage with normal values"""
        result = self.calculator.calculate_true_shooting_pct(
            points=20,
            fga=15,
            fta=4
        )
        
        assert isinstance(result, float)
        assert result > 0
    
    def test_calculate_true_shooting_pct_zero_attempts(self):
        """Test true shooting percentage with zero attempts"""
        result = self.calculator.calculate_true_shooting_pct(
            points=0,
            fga=0,
            fta=0
        )
        
        assert result == 0.0
    
    def test_calculate_true_shooting_pct_perfect(self):
        """Test true shooting percentage with perfect shooting"""
        result = self.calculator.calculate_true_shooting_pct(
            points=30,
            fga=10,
            fta=10
        )
        
        assert result > 0
    
    def test_calculate_effective_fg_pct_normal(self):
        """Test effective field goal percentage with normal values"""
        result = self.calculator.calculate_effective_fg_pct(
            fgm=10,
            fg3m=3,
            fga=20
        )
        
        assert isinstance(result, float)
        assert 0 <= result <= 1
        assert result > 0
    
    def test_calculate_effective_fg_pct_zero_attempts(self):
        """Test effective field goal percentage with zero attempts"""
        result = self.calculator.calculate_effective_fg_pct(
            fgm=0,
            fg3m=0,
            fga=0
        )
        
        assert result == 0.0
    
    def test_calculate_effective_fg_pct_all_threes(self):
        """Test effective field goal percentage with all three-pointers"""
        result = self.calculator.calculate_effective_fg_pct(
            fgm=5,
            fg3m=5,
            fga=10
        )
        
        assert result == 0.75
    
    def test_calculate_usage_rate_normal(self):
        """Test usage rate with normal values"""
        result = self.calculator.calculate_usage_rate(
            fga=15,
            fta=4,
            tov=3,
            min_played=30.0,
            team_min=240.0,
            team_fga=80,
            team_fta=20,
            team_tov=12
        )
        
        assert isinstance(result, float)
        assert result >= 0
    
    def test_calculate_usage_rate_zero_minutes(self):
        """Test usage rate with zero minutes"""
        result = self.calculator.calculate_usage_rate(
            fga=0,
            fta=0,
            tov=0,
            min_played=0.0,
            team_min=240.0,
            team_fga=80,
            team_fta=20,
            team_tov=12
        )
        
        assert result == 0.0
    
    def test_calculate_per_normal(self):
        """Test PER calculation with normal values"""
        result = self.calculator.calculate_per(
            min_played=30.0,
            fg3m=3,
            ast=5,
            fgm=10,
            ftm=4,
            oreb=2,
            dreb=6,
            stl=2,
            blk=1,
            fga=20,
            fta=5,
            tov=3,
            pf=2
        )
        
        assert isinstance(result, float)
        assert result >= 0
    
    def test_calculate_per_zero_minutes(self):
        """Test PER with zero minutes"""
        result = self.calculator.calculate_per(
            min_played=0.0,
            fg3m=0,
            ast=0,
            fgm=0,
            ftm=0,
            oreb=0,
            dreb=0,
            stl=0,
            blk=0,
            fga=0,
            fta=0,
            tov=0,
            pf=0
        )
        
        assert result == 0.0
    
    def test_calculate_box_plus_minus_positive(self):
        """Test box plus minus with good stats"""
        result = self.calculator.calculate_box_plus_minus(
            points=30,
            reb=12,
            ast=8,
            stl=2,
            blk=2,
            tov=2,
            fga=20,
            fgm=12,
            fta=6,
            min_played=35.0
        )
        
        assert isinstance(result, float)
    
    def test_calculate_box_plus_minus_negative(self):
        """Test box plus minus with poor stats"""
        result = self.calculator.calculate_box_plus_minus(
            points=5,
            reb=2,
            ast=1,
            stl=0,
            blk=0,
            tov=5,
            fga=15,
            fgm=2,
            fta=2,
            min_played=20.0
        )
        
        assert isinstance(result, float)
    
    def test_calculate_box_plus_minus_zero_minutes(self):
        """Test box plus minus with zero minutes"""
        result = self.calculator.calculate_box_plus_minus(
            points=0,
            reb=0,
            ast=0,
            stl=0,
            blk=0,
            tov=0,
            fga=0,
            fgm=0,
            fta=0,
            min_played=0.0
        )
        
        assert result == 0.0
    
    def test_calculate_win_shares(self):
        """Test win shares calculation"""
        result = self.calculator.calculate_win_shares(
            points=25,
            fgm=10,
            fga=20,
            ftm=5,
            fta=6,
            oreb=2,
            dreb=8,
            ast=6,
            stl=2,
            blk=1,
            tov=3,
            min_played=35.0,
            team_wins=40,
            team_games=70
        )
        
        assert isinstance(result, dict)
        assert 'offensive_ws' in result
        assert 'defensive_ws' in result
        assert 'total_ws' in result
        assert isinstance(result['total_ws'], float)


class TestCalculateAdvancedMetrics:
    """Test suite for calculate_advanced_metrics function"""
    
    def test_no_box_plus_minus_in_output(self):
        """Test that box_plus_minus is NOT added to staging data"""
        sample_stats = [get_sample_transformed_stat_without_ts()]
        
        result = calculate_advanced_metrics(sample_stats)
        
        assert 'box_plus_minus' not in result[0], \
            "box_plus_minus should not be in staging data"
    
    def test_no_raw_api_field_names_in_output(self):
        """Test that output does not contain raw API field names"""
        sample_stats = [get_sample_transformed_stat_without_ts()]
        
        result = calculate_advanced_metrics(sample_stats)
        
        assert 'TS_PCT' not in result[0]
        assert 'EFG_PCT' not in result[0]
        assert 'BPM' not in result[0]
        assert 'PTS' not in result[0]
        assert 'FGM' not in result[0]
        assert 'FGA' not in result[0]
    
    def test_calculates_true_shooting_pct_when_missing(self):
        """Test that true_shooting_pct is calculated when None"""
        sample_stats = [get_sample_transformed_stat_without_ts()]
        
        result = calculate_advanced_metrics(sample_stats)
        
        assert result[0]['true_shooting_pct'] is not None
        assert isinstance(result[0]['true_shooting_pct'], float)
        assert 0 <= result[0]['true_shooting_pct'] <= 1
    
    def test_does_not_override_existing_true_shooting_pct(self):
        """Test that existing true_shooting_pct is preserved"""
        sample_stat = get_sample_transformed_player_stat()
        existing_ts_pct = 0.650
        sample_stat['true_shooting_pct'] = existing_ts_pct
        
        result = calculate_advanced_metrics([sample_stat])
        
        assert result[0]['true_shooting_pct'] == existing_ts_pct
    
    def test_calculates_effective_fg_pct_when_missing(self):
        """Test that effective_fg_pct is calculated when None"""
        sample_stats = [get_sample_transformed_stat_without_ts()]
        
        result = calculate_advanced_metrics(sample_stats)
        
        assert result[0]['effective_fg_pct'] is not None
        assert isinstance(result[0]['effective_fg_pct'], float)
        assert 0 <= result[0]['effective_fg_pct'] <= 1
    
    def test_does_not_override_existing_effective_fg_pct(self):
        """Test that existing effective_fg_pct is preserved"""
        sample_stat = get_sample_transformed_player_stat()
        existing_efg_pct = 0.550
        sample_stat['effective_fg_pct'] = existing_efg_pct
        
        result = calculate_advanced_metrics([sample_stat])
        
        assert result[0]['effective_fg_pct'] == existing_efg_pct
    
    def test_uses_transformed_field_names(self):
        """Test that function uses transformed field names not raw API names"""
        sample_stat = {
            'points': 20,
            'field_goals_made': 8,
            'field_goals_attempted': 15,
            'three_pointers_made': 2,
            'free_throws_made': 2,
            'free_throws_attempted': 2,
            'offensive_rebounds': 2,
            'defensive_rebounds': 6,
            'total_rebounds': 8,
            'assists': 5,
            'steals': 1,
            'blocks': 1,
            'turnovers': 2,
            'personal_fouls': 2,
            'minutes_played': 30.0,
            'true_shooting_pct': None,
            'effective_fg_pct': None,
        }
        
        result = calculate_advanced_metrics([sample_stat])
        
        assert result[0]['true_shooting_pct'] > 0
        assert result[0]['effective_fg_pct'] > 0
    
    def test_handles_zero_attempts(self):
        """Test that function handles zero attempts gracefully"""
        sample_stat = get_sample_transformed_stat_without_ts()
        sample_stat['field_goals_attempted'] = 0
        sample_stat['free_throws_attempted'] = 0
        sample_stat['points'] = 0
        
        result = calculate_advanced_metrics([sample_stat])
        
        assert 'true_shooting_pct' in result[0]
        assert 'effective_fg_pct' in result[0]
        assert result[0]['true_shooting_pct'] == 0.0
        assert result[0]['effective_fg_pct'] == 0.0
    
    def test_handles_multiple_records(self):
        """Test that function processes multiple records correctly"""
        sample_stats = [
            get_sample_transformed_stat_without_ts(),
            get_sample_transformed_stat_without_ts(),
            get_sample_transformed_stat_without_ts(),
        ]
        
        result = calculate_advanced_metrics(sample_stats)
        
        assert len(result) == 3
        for stat in result:
            assert 'box_plus_minus' not in stat
            assert 'true_shooting_pct' in stat
            assert 'effective_fg_pct' in stat
    
    def test_preserves_all_original_fields(self):
        """Test that all original fields are preserved"""
        sample_stat = get_sample_transformed_player_stat()
        original_keys = set(sample_stat.keys())
        
        result = calculate_advanced_metrics([sample_stat])
        result_keys = set(result[0].keys())
        
        assert original_keys.issubset(result_keys), \
            "Some original fields were lost"
    
    def test_handles_missing_optional_fields(self):
        """Test that function handles missing optional fields"""
        minimal_stat = {
            'points': 10,
            'field_goals_made': 4,
            'field_goals_attempted': 10,
            'three_pointers_made': 1,
            'free_throws_made': 1,
            'free_throws_attempted': 1,
            'true_shooting_pct': None,
            'effective_fg_pct': None,
        }
        
        result = calculate_advanced_metrics([minimal_stat])
        
        assert result[0]['true_shooting_pct'] is not None
        assert result[0]['effective_fg_pct'] is not None
    
    def test_returns_list(self):
        """Test that function returns a list"""
        sample_stats = [get_sample_transformed_stat_without_ts()]
        
        result = calculate_advanced_metrics(sample_stats)
        
        assert isinstance(result, list)
        assert len(result) == len(sample_stats)
    
    def test_empty_list_input(self):
        """Test that function handles empty list"""
        result = calculate_advanced_metrics([])
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_metrics_are_rounded(self):
        """Test that calculated metrics are properly rounded"""
        sample_stat = get_sample_transformed_stat_without_ts()
        
        result = calculate_advanced_metrics([sample_stat])
        
        ts_pct = result[0]['true_shooting_pct']
        efg_pct = result[0]['effective_fg_pct']
        
        assert len(str(ts_pct).split('.')[-1]) <= 3
        assert len(str(efg_pct).split('.')[-1]) <= 3
