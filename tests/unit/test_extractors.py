"""
Unit Tests for NBA Extractor
=============================
"""

import pytest
from unittest.mock import Mock, patch
from src.etl.extractors.nba_extractor import NBAExtractor


class TestNBAExtractor:
    """Test suite for NBAExtractor class"""
    
    @pytest.fixture
    def extractor(self):
        """Create an NBAExtractor instance for testing"""
        return NBAExtractor()
    
    def test_initialization(self, extractor):
        """Test that extractor initializes correctly"""
        assert extractor is not None
        assert extractor.rate_limit == 600
        assert extractor.request_count == 0
    
    def test_rate_limit_check(self, extractor):
        """Test rate limiting logic"""
        # Should not sleep if under limit
        extractor.request_count = 100
        extractor._rate_limit_check()
        assert extractor.request_count == 101
    
    def test_get_all_teams(self, extractor):
        """Test fetching all teams"""
        teams = extractor.get_all_teams()
        assert isinstance(teams, list)
        assert len(teams) == 30  # NBA has 30 teams
        assert 'id' in teams[0]
        assert 'full_name' in teams[0]
    
    def test_season_date_range(self, extractor):
        """Test season date range calculation"""
        start, end = extractor.get_season_date_range('2024-25')
        assert start == '2024-10-01'
        assert end == '2025-06-30'
    
    @patch('src.etl.extractors.nba_extractor.leaguegamefinder.LeagueGameFinder')
    def test_get_games_by_date(self, mock_finder, extractor):
        """Test fetching games by date"""
        # Mock the API response
        mock_instance = Mock()
        mock_instance.get_data_frames.return_value = [Mock(to_dict=lambda x: [])]
        mock_finder.return_value = mock_instance
        
        games = extractor.get_games_by_date('2024-12-13')
        
        assert isinstance(games, list)
        mock_finder.assert_called_once()


class TestNBAExtractorEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.fixture
    def extractor(self):
        return NBAExtractor()
    
    def test_empty_date_handling(self, extractor):
        """Test handling of empty date string"""
        start, end = extractor.get_season_date_range('')
        # Should handle gracefully
    
    def test_invalid_season_format(self, extractor):
        """Test handling of invalid season format"""
        with pytest.raises(Exception):
            extractor.get_season_date_range('invalid')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
