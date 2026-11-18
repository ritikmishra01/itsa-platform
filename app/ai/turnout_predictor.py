import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import logging

logger = logging.getLogger(__name__)

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'ml_models')
MODEL_PATH = os.path.join(MODEL_DIR, 'event_turnout_model.joblib')

CATEGORIES = [
    'Technical', 'Workshop', 'Seminar', 'Cultural', 
    'Sports', 'Competition', 'Community Service', 'Other'
]

# Baseline historical collegiate data for model training
HISTORICAL_SAMPLES = [
    # category, day_of_week, hour, is_weekend, duration_hrs, venue_cap, hist_avg, lead_days, actual_registrations
    ['Technical', 5, 10, 1, 6.0, 500, 95.0, 14, 110],
    ['Technical', 4, 14, 0, 3.0, 150, 85.0, 10, 88],
    ['Technical', 2, 11, 0, 2.0, 100, 75.0, 7, 72],
    ['Workshop', 5, 9, 1, 4.0, 60, 55.0, 12, 58],
    ['Workshop', 6, 10, 1, 5.0, 60, 55.0, 10, 54],
    ['Workshop', 3, 14, 0, 3.0, 80, 50.0, 8, 48],
    ['Workshop', 1, 15, 0, 2.5, 60, 48.0, 5, 42],
    ['Seminar', 4, 11, 0, 2.0, 150, 65.0, 9, 62],
    ['Seminar', 2, 10, 0, 1.5, 40, 35.0, 6, 38],
    ['Seminar', 3, 14, 0, 2.0, 100, 55.0, 8, 52],
    ['Competition', 5, 9, 1, 8.0, 100, 80.0, 15, 85],
    ['Competition', 6, 10, 1, 6.0, 60, 58.0, 12, 60],
    ['Competition', 4, 13, 0, 4.0, 80, 65.0, 7, 63],
    ['Cultural', 5, 17, 1, 4.0, 500, 180.0, 20, 215],
    ['Cultural', 6, 18, 1, 3.5, 300, 150.0, 14, 168],
    ['Cultural', 4, 16, 0, 3.0, 200, 120.0, 10, 115],
    ['Sports', 6, 8, 1, 6.0, 300, 90.0, 14, 98],
    ['Sports', 5, 9, 1, 5.0, 200, 80.0, 10, 84],
    ['Sports', 0, 16, 0, 2.0, 100, 45.0, 5, 40],
    ['Community Service', 5, 8, 1, 4.0, 100, 40.0, 10, 45],
    ['Community Service', 6, 9, 1, 3.0, 80, 35.0, 7, 36],
    ['Other', 3, 15, 0, 2.0, 60, 30.0, 5, 28],
    ['Technical', 5, 10, 1, 7.0, 300, 90.0, 16, 105],
    ['Workshop', 5, 10, 1, 3.0, 60, 52.0, 9, 53],
    ['Competition', 5, 11, 1, 5.0, 150, 75.0, 11, 78],
    ['Seminar', 1, 14, 0, 2.0, 120, 60.0, 8, 58],
    ['Cultural', 5, 16, 1, 5.0, 500, 200.0, 21, 230],
    ['Workshop', 6, 13, 1, 4.0, 80, 55.0, 10, 56],
    ['Technical', 3, 10, 0, 3.0, 150, 78.0, 8, 74],
    ['Competition', 6, 9, 1, 6.0, 100, 70.0, 14, 76]
]


class EventTurnoutPredictor:
    """
    Scikit-learn Machine Learning Regressor for Event Registration Turnout.
    Predicts student registration turnout based on event characteristics.
    """
    _instance = None
    _model = None
    _encoder = None
    _metrics = None

    FEATURE_NAMES = [
        'category_encoded',
        'day_of_week',
        'hour_of_start',
        'is_weekend',
        'duration_hours',
        'venue_capacity',
        'historical_avg_category',
        'days_until_event'
    ]

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = EventTurnoutPredictor()
        return cls._instance

    def __init__(self):
        self._ensure_model_loaded()

    @property
    def model(self):
        return self._model

    def _ensure_model_loaded(self):
        os.makedirs(MODEL_DIR, exist_ok=True)
        if os.path.exists(MODEL_PATH):
            try:
                bundle = joblib.load(MODEL_PATH)
                self._model = bundle['model']
                self._encoder = bundle['encoder']
                self._metrics = bundle.get('metrics', {})
                logger.info(f"Loaded ML Turnout model (version: {bundle.get('version', '1.0')})")
                return
            except Exception as e:
                logger.warning(f"Failed to load model from {MODEL_PATH}: {e}. Retraining...")

        self.train_and_save_model()

    def train_and_save_model(self, extra_db_events=None):
        """
        Trains Random Forest Regressor and persists it using joblib.
        """
        os.makedirs(MODEL_DIR, exist_ok=True)

        encoder = LabelEncoder()
        encoder.fit(CATEGORIES)

        records = list(HISTORICAL_SAMPLES)
        if extra_db_events:
            for ev in extra_db_events:
                if ev.get('current_registrations', 0) > 0:
                    records.append([
                        ev.get('category', 'Technical'),
                        ev.get('day_of_week', 5),
                        ev.get('hour_of_start', 10),
                        ev.get('is_weekend', 1),
                        ev.get('duration_hours', 3.0),
                        ev.get('venue_capacity', 100),
                        ev.get('historical_avg_category', 50.0),
                        ev.get('days_until_event', 10),
                        ev.get('current_registrations')
                    ])

        df = pd.DataFrame(records, columns=[
            'category', 'day_of_week', 'hour_of_start', 'is_weekend',
            'duration_hours', 'venue_capacity', 'historical_avg_category',
            'days_until_event', 'registrations'
        ])

        # Preprocessing
        df['category_encoded'] = encoder.transform(df['category'])
        X = df[self.FEATURE_NAMES]
        y = df['registrations'].values

        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=6,
            min_samples_split=2,
            random_state=42
        )
        model.fit(X, y)

        preds = model.predict(X)
        mae = float(mean_absolute_error(y, preds))
        r2 = float(r2_score(y, preds))

        metrics = {
            'mae': round(mae, 2),
            'r2_score': round(r2, 4),
            'samples_trained': len(df),
            'trained_at': datetime.utcnow().isoformat()
        }

        bundle = {
            'model': model,
            'encoder': encoder,
            'feature_names': self.FEATURE_NAMES,
            'version': 'RandomForestRegressor-v1.0',
            'metrics': metrics
        }

        joblib.dump(bundle, MODEL_PATH)
        self._model = model
        self._encoder = encoder
        self._metrics = metrics

        logger.info(f"Turnout ML Model trained and saved: R²={r2:.4f}, MAE={mae:.2f}")
        return metrics

    def predict(self, event, historical_avg=50.0):
        """
        Executes prediction pipeline on an Event instance or dict.
        """
        if self._model is None or self._encoder is None:
            self._ensure_model_loaded()

        cat_name = 'Technical'
        if hasattr(event, 'category') and event.category:
            cat_name = event.category.name
        elif isinstance(event, dict) and 'category_name' in event:
            cat_name = event['category_name']

        if cat_name not in CATEGORIES:
            cat_name = 'Other'

        cat_encoded = int(self._encoder.transform([cat_name])[0])

        start_dt = getattr(event, 'start_datetime', None)
        if isinstance(event, dict):
            start_dt = event.get('start_datetime')

        if isinstance(start_dt, str):
            try:
                start_dt = datetime.fromisoformat(start_dt)
            except Exception:
                start_dt = datetime.utcnow() + timedelta(days=7)
        elif not isinstance(start_dt, datetime):
            start_dt = datetime.utcnow() + timedelta(days=7)

        end_dt = getattr(event, 'end_datetime', None)
        if isinstance(event, dict):
            end_dt = event.get('end_datetime')
        if isinstance(end_dt, str):
            try:
                end_dt = datetime.fromisoformat(end_dt)
            except Exception:
                end_dt = start_dt + timedelta(hours=3)
        elif not isinstance(end_dt, datetime):
            end_dt = start_dt + timedelta(hours=3)

        duration = max(0.5, (end_dt - start_dt).total_seconds() / 3600.0)
        day_of_week = start_dt.weekday()
        hour_of_start = start_dt.hour
        is_weekend = 1 if day_of_week in [5, 6] else 0

        venue_cap = 100
        venue_name = "TBA"
        venue = getattr(event, 'venue', None)
        if venue and hasattr(venue, 'capacity') and venue.capacity:
            venue_cap = venue.capacity
            venue_name = venue.name
        elif isinstance(event, dict) and 'venue_capacity' in event:
            venue_cap = event['venue_capacity'] or 100

        now = datetime.utcnow()
        days_until = max(1, (start_dt - now).days) if start_dt > now else 1

        feature_df = pd.DataFrame([[
            cat_encoded,
            day_of_week,
            hour_of_start,
            is_weekend,
            duration,
            venue_cap,
            historical_avg,
            days_until
        ]], columns=self.FEATURE_NAMES)

        raw_prediction = float(self._model.predict(feature_df)[0])

        # Enforce realistic domain constraints
        predicted_count = max(5, int(round(raw_prediction)))

        max_participants = getattr(event, 'max_participants', None)
        if isinstance(event, dict):
            max_participants = event.get('max_participants')
        if max_participants and max_participants > 0:
            predicted_count = min(predicted_count, max_participants)

        # Confidence bounds based on tree predictions variance
        tree_preds = [tree.predict(feature_df.values)[0] for tree in self._model.estimators_]
        std_err = float(np.std(tree_preds))
        conf_low = max(5, int(round(predicted_count - 1.96 * std_err)))
        conf_high = int(round(predicted_count + 1.96 * std_err))
        if max_participants:
            conf_high = min(conf_high, max_participants)

        confidence_level = "HIGH" if std_err < 8 else ("MEDIUM" if std_err < 16 else "LOW")

        # Factors considered for frontend display
        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        factors = [
            f"Category: {cat_name} (Hist. Avg: {int(historical_avg)})",
            f"Venue: {venue_name} (Cap: {venue_cap})",
            f"Schedule: {weekday_names[day_of_week]} at {start_dt.strftime('%I:%M %p')}",
            f"Duration: {duration:.1f} hrs",
            f"Lead Time: {days_until} days until event"
        ]
        if is_weekend:
            factors.append("Weekend Session (Higher Turnout Factor)")

        return {
            'predicted_registrations': predicted_count,
            'predicted_count': predicted_count,  # backward compatibility
            'confidence': confidence_level,
            'confidence_range': [conf_low, conf_high],
            'confidence_interval': [conf_low, conf_high],
            'factors_considered': factors,
            'model_version': 'RandomForestRegressor-v1.0',
            'metrics': self._metrics
        }
