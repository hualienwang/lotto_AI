import random
from datetime import datetime
from .utils import normalize_scores, weighted_pick, next_period_from_draws

class LottoPredictor:
    def __init__(self, draws):
        self.draws = draws
        self.total_draws = len(draws)
        self.latest_numbers = draws[0]['numbers'] if draws else []
        self._calculate_features()

    def _calculate_features(self):
        recent_window = min(30, self.total_draws)
        hot_window = min(10, self.total_draws)
        prior_window = min(20, max(self.total_draws - hot_window, 0))

        total_counts = {number: 0 for number in range(1, 40)}
        recent_counts = {number: 0 for number in range(1, 40)}
        hot_counts = {number: 0 for number in range(1, 40)}
        prior_counts = {number: 0 for number in range(1, 40)}
        missing_spans = {number: self.total_draws + 1 for number in range(1, 40)}

        for index, draw in enumerate(self.draws):
            for number in draw['numbers']:
                total_counts[number] += 1
                if index < recent_window:
                    recent_counts[number] += 1
                if index < hot_window:
                    hot_counts[number] += 1
                elif index < hot_window + prior_window:
                    prior_counts[number] += 1
                if missing_spans[number] == self.total_draws + 1:
                    missing_spans[number] = index

        self.features = {
            'total': normalize_scores(total_counts),
            'recent': normalize_scores(recent_counts),
            'missing': normalize_scores(missing_spans),
            'inverse_total': {n: 1 - v for n, v in normalize_scores(total_counts).items()},
            'inverse_recent': {n: 1 - v for n, v in normalize_scores(recent_counts).items()},
        }

        hot_rate = {n: hot_counts[n] / hot_window if hot_window else 0 for n in range(1, 40)}
        prior_rate = {n: prior_counts[n] / prior_window if prior_window else 0 for n in range(1, 40)}
        self.features['momentum'] = normalize_scores({
            n: hot_rate[n] - prior_rate[n] for n in range(1, 40)
        })

        # Markov
        chronological_draws = list(reversed(self.draws))
        transition_counts = {s: {t: 0 for t in range(1, 40)} for s in range(1, 40)}
        transition_totals = {n: 0 for n in range(1, 40)}
        for i in range(1, len(chronological_draws)):
            prev_nums = chronological_draws[i-1]['numbers']
            next_nums = chronological_draws[i]['numbers']
            for s in prev_nums:
                for t in next_nums:
                    transition_counts[s][t] += 1
                    transition_totals[s] += 1
        
        self.features['markov'] = normalize_scores({
            t: sum(transition_counts[s][t] / transition_totals[s] for s in self.latest_numbers if transition_totals[s] > 0)
            for t in range(1, 40)
        })

        # Co-occurrence
        co_counts = {s: {t: 0 for t in range(1, 40)} for s in range(1, 40)}
        for draw in self.draws:
            for s in draw['numbers']:
                for t in draw['numbers']:
                    if s != t: co_counts[s][t] += 1
        
        self.features['cooccurrence'] = normalize_scores({
            t: sum(co_counts[s][t] for s in self.latest_numbers)
            for t in range(1, 40)
        })

        # --- New Features ---
        
        # 1. Odd/Even Balance
        # If the last few draws were mostly odd, even might be "due" (or vice versa, depending on strategy)
        # Here we just provide the ratio as a feature.
        recent_odd_count = sum(1 for d in self.draws[:10] for n in d['numbers'] if n % 2 != 0)
        odd_ratio = recent_odd_count / 50.0 # 10 draws * 5 numbers
        self.features['odd_even_balance'] = {n: (1 - odd_ratio if n % 2 != 0 else odd_ratio) for n in range(1, 40)}

        # 2. Big/Small Balance (Small: 1-19, Big: 20-39)
        recent_big_count = sum(1 for d in self.draws[:10] for n in d['numbers'] if n >= 20)
        big_ratio = recent_big_count / 50.0
        self.features['big_small_balance'] = {n: (1 - big_ratio if n >= 20 else big_ratio) for n in range(1, 40)}

        # 3. Tail Frequency (尾數頻率)
        tail_counts = {t: 0 for t in range(10)}
        for draw in self.draws:
            for n in draw['numbers']:
                tail_counts[n % 10] += 1
        normalized_tails = normalize_scores(tail_counts)
        self.features['tail'] = {n: normalized_tails[n % 10] for n in range(1, 40)}

        # 4. Consecutive Frequency (連號頻率)
        consecutive_counts = {n: 0 for n in range(1, 40)}
        for draw in self.draws:
            nums = sorted(draw['numbers'])
            for i in range(len(nums) - 1):
                if nums[i+1] - nums[i] == 1:
                    consecutive_counts[nums[i]] += 1
                    consecutive_counts[nums[i+1]] += 1
        self.features['consecutive'] = normalize_scores(consecutive_counts)

    def predict(self, prediction_type):
        methods = {
            'ai': {
                'name': 'AI智能預測',
                'description': '綜合全期頻率、近30期熱度與遺漏期數的加權模型。',
                'weights': {'total': 0.4, 'recent': 0.35, 'missing': 0.25}
            },
            'frequency': {
                'name': '頻率分析',
                'description': '偏重歷史開出次數，並少量參考近期表現。',
                'weights': {'total': 0.8, 'recent': 0.2}
            },
            'cold': {
                'name': '冷熱分析',
                'description': '偏向近期較少出現、遺漏期數較長的號碼。',
                'weights': {'inverse_recent': 0.45, 'missing': 0.4, 'inverse_total': 0.15}
            },
            'trend': {
                'name': '走勢分析',
                'description': '偏重近10期相對前20期升溫的號碼。',
                'weights': {'recent': 0.45, 'momentum': 0.45, 'total': 0.1}
            },
            'markov': {
                'name': '馬可夫預測',
                'description': '依最新一期號碼，推估歷史上相似轉移後下一期較常出現的號碼。',
                'weights': {'markov': 0.7, 'recent': 0.2, 'total': 0.1}
            },
            'cooccurrence': {
                'name': '共現矩陣預測',
                'description': '依最新一期號碼，挑選歷史上與這組號碼常共同出現的搭配號碼。',
                'weights': {'cooccurrence': 0.65, 'recent': 0.25, 'total': 0.1}
            },
            # --- New Methods ---
            'pattern': {
                'name': '版路分析預測',
                'description': '結合尾數分佈與連號走勢的進階分析。',
                'weights': {'tail': 0.4, 'consecutive': 0.3, 'recent': 0.2, 'total': 0.1}
            },
            'balanced': {
                'name': '均衡分佈預測',
                'description': '考慮奇偶與大小數值的平衡，避免選號過於集中。',
                'weights': {'recent': 0.3, 'odd_even_balance': 0.35, 'big_small_balance': 0.35}
            },
            'ensemble': {
                'name': '整合策略預測',
                'description': '結合 AI、馬可夫與共現矩陣的綜合策略。',
                'weights': {'total': 0.2, 'recent': 0.2, 'markov': 0.3, 'cooccurrence': 0.3}
            }
        }
        
        method = methods.get(prediction_type, methods['ai'])
        scores = {n: 0 for n in range(1, 40)}
        for feature, weight in method['weights'].items():
            for n in range(1, 40):
                scores[n] += self.features[feature][n] * weight

        numbers = self._get_filtered_pick(scores)
        top_candidates = sorted(
            [{'number': f'{n:02d}', 'score': round(scores[n], 4)} for n in scores],
            key=lambda item: item['score'],
            reverse=True
        )[:10]

        return {
            'success': True,
            'period': next_period_from_draws(self.draws),
            'numbers': [f'{n:02d}' for n in numbers],
            'method': method['name'],
            'description': method['description'],
            'generated_at': datetime.now().isoformat(timespec='seconds'),
            'sample_size': self.total_draws,
            'recent_window': 30,
            'top_candidates': top_candidates
        }

    def _get_filtered_pick(self, scores, max_attempts=50):
        for _ in range(max_attempts):
            numbers = weighted_pick(scores)
            if self._is_reasonable(numbers):
                return numbers
        return weighted_pick(scores) # Fallback

    def _is_reasonable(self, numbers):
        # 1. Sum Range (70-130 is common for 539)
        total_sum = sum(numbers)
        if not (70 <= total_sum <= 130):
            return False
            
        # 2. Odd/Even Balance (avoid 5:0 or 0:5)
        odds = sum(1 for n in numbers if n % 2 != 0)
        if odds == 0 or odds == 5:
            return False
            
        # 3. Big/Small Balance (avoid 5:0 or 0:5)
        bigs = sum(1 for n in numbers if n >= 20)
        if bigs == 0 or bigs == 5:
            return False
            
        return True
