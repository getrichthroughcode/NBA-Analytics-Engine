"""
Local Pipeline Testing Script
Test the NBA daily refresh pipeline without Airflow.

Usage:
    python scripts/test_pipeline.py
    python scripts/test_pipeline.py --date 2025-12-15
"""

import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from src.etl.extractors.nba_extractor import NBAExtractor
from src.etl.transformers.nba_transformer import NBATransformer
from src.etl.loaders.postgres_loader import PostgresLoader
from src.analytics.metrics import calculate_advanced_metrics
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_extraction(test_date="2024-12-15"):
    print("\n" + "=" * 80)
    print("STEP 1: EXTRACTION")
    print("=" * 80)
    
    extractor = NBAExtractor()
    
    try:
        games = extractor.get_games_by_date(test_date)
        print(f"Extracted {len(games)} games for {test_date}")
        
        if not games:
            print("WARNING: No games found for this date")
            return None, None
        
        game_id = games[0]["GAME_ID"]
        print(f"Testing with game: {game_id}")
        
        player_stats = extractor.get_player_game_stats(game_id)
        print(f"Extracted {len(player_stats)} player stat records")
        
        return games, player_stats
    
    except Exception as e:
        print(f"ERROR: Extraction failed: {str(e)}")
        raise


def test_transformation(player_stats):
    print("\n" + "=" * 80)
    print("STEP 2: TRANSFORMATION")
    print("=" * 80)
    
    if not player_stats:
        print("ERROR: No player stats to transform")
        return None
    
    transformer = NBATransformer()
    
    try:
        transformed = transformer.transform_player_stats(player_stats[:5])
        print(f"Transformed {len(transformed)} records")
        
        if transformed:
            sample = transformed[0]
            print(f"Sample transformed fields: {list(sample.keys())[:10]}")
            
            if 'PTS' in sample or 'FGM' in sample:
                print("WARNING: Raw API field names still present")
            else:
                print("Field names transformed correctly")
        
        return transformed
    
    except Exception as e:
        print(f"ERROR: Transformation failed: {str(e)}")
        raise


def test_advanced_metrics(transformed_stats):
    print("\n" + "=" * 80)
    print("STEP 3: ADVANCED METRICS CALCULATION")
    print("=" * 80)
    
    if not transformed_stats:
        print("ERROR: No transformed stats to enhance")
        return None
    
    try:
        enhanced = calculate_advanced_metrics(transformed_stats)
        print(f"Enhanced {len(enhanced)} records")
        
        if enhanced:
            sample = enhanced[0]
            
            errors = []
            
            if 'TS_PCT' in sample:
                errors.append("Found TS_PCT (should be true_shooting_pct)")
            
            if 'EFG_PCT' in sample:
                errors.append("Found EFG_PCT (should be effective_fg_pct)")
            
            if 'BPM' in sample:
                errors.append("Found BPM (should be box_plus_minus)")
            
            if 'box_plus_minus' in sample:
                errors.append("Found box_plus_minus (should NOT be in staging)")
            
            if errors:
                print("\nERROR: Field name issues detected:")
                for error in errors:
                    print(f"  - {error}")
                return None
            
            print("All field names correct")
            
            ts_pct = sample.get('true_shooting_pct')
            if ts_pct and ts_pct > 0:
                print(f"true_shooting_pct calculated: {ts_pct:.3f}")
        
        return enhanced
    
    except Exception as e:
        print(f"ERROR: Metrics calculation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


def test_schema_compatibility(enhanced_stats):
    print("\n" + "=" * 80)
    print("STEP 4: SCHEMA COMPATIBILITY CHECK")
    print("=" * 80)
    
    if not enhanced_stats:
        print("ERROR: No enhanced stats to check")
        return False
    
    import pandas as pd
    
    try:
        test_record = [enhanced_stats[0]]
        df = pd.DataFrame(test_record)
        
        print(f"DataFrame has {len(df.columns)} columns")
        
        schema_columns = [
            'game_id', 'team_id', 'player_id', 'player_name', 'position',
            'jersey_num', 'minutes_played', 'field_goals_made', 
            'field_goals_attempted', 'field_goal_pct', 'three_pointers_made',
            'three_pointers_attempted', 'three_point_pct', 'free_throws_made',
            'free_throws_attempted', 'free_throw_pct', 'offensive_rebounds',
            'defensive_rebounds', 'total_rebounds', 'assists', 'steals',
            'blocks', 'turnovers', 'personal_fouls', 'points', 'plus_minus',
            'offensive_rating', 'defensive_rating', 'net_rating',
            'true_shooting_pct', 'effective_fg_pct', 'usage_pct', 'pace',
            'pie', 'assist_percentage', 'assist_to_turnover', 'assist_ratio',
            'offensive_rebound_pct', 'defensive_rebound_pct',
            'rebound_percentage', 'turnover_ratio', 'raw_data'
        ]
        
        extra_cols = [col for col in df.columns if col not in schema_columns]
        
        if extra_cols:
            print("\nERROR: Extra columns not in schema:")
            for col in extra_cols:
                print(f"  - {col}")
            print("\nThese will cause database errors")
            return False
        
        print("All columns match schema")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Schema check failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_database_load(enhanced_stats):
    print("\n" + "=" * 80)
    print("STEP 5: DATABASE LOAD TEST")
    print("=" * 80)
    
    if not enhanced_stats:
        print("ERROR: No enhanced stats to load")
        return False
    
    try:
        loader = PostgresLoader()
        test_record = [enhanced_stats[0]]
        
        rows = loader.load_player_stats_staging(test_record)
        print(f"Successfully loaded {rows} test record to staging")
        return True
        
    except Exception as e:
        print(f"ERROR: Database load failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_full_pipeline_test(test_date="2024-12-15"):
    print("\n" + "=" * 80)
    print("NBA DAILY REFRESH PIPELINE TEST")
    print("=" * 80)
    print(f"Test Date: {test_date}")
    print("=" * 80)
    
    success = True
    
    try:
        games, player_stats = test_extraction(test_date)
        if not player_stats:
            print("\nWARNING: No data extracted - try a different date")
            return False
        
        transformed = test_transformation(player_stats)
        if not transformed:
            success = False
            return False
        
        enhanced = test_advanced_metrics(transformed)
        if not enhanced:
            success = False
            return False
        
        if not test_schema_compatibility(enhanced):
            success = False
            return False
        
        if not test_database_load(enhanced):
            success = False
            return False
        
        if success:
            print("\n" + "=" * 80)
            print("SUCCESS: ALL TESTS PASSED")
            print("=" * 80)
            print("\nPipeline is ready to deploy")
        
        return success
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("FAILURE: PIPELINE TEST FAILED")
        print("=" * 80)
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test NBA daily refresh pipeline locally')
    parser.add_argument('--date', default='2024-12-15', 
                       help='Test date in YYYY-MM-DD format')
    
    args = parser.parse_args()
    
    success = run_full_pipeline_test(args.date)
    sys.exit(0 if success else 1)
