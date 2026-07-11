import random
from datetime import datetime

from .utils import normalize_scores, next_period_from_draws


class LottoPredictor:
    METHODS = {
        'ai': {
            'name': 'AI智能預測',
            'description': '綜合全期頻率、近30期熱度與遺漏期數的加權模型。',
            'weights': {'total': 0.35, 'recent': 0.25, 'missing': 0.2, 'momentum': 0.1, 'markov': 0.1},
        },
        'frequency': {
            'name': '頻率分析',
            'description': '偏重歷史開出次數，並少量參考近期表現。',
            'weights': {'total': 0.75, 'recent': 0.2, 'momentum': 0.05},
        },
        'cold': {
            'name': '冷熱分析',
            'description': '偏向近期較少出現、遺漏期數較長的號碼。',
            'weights': {'inverse_recent': 0.42, 'missing': 0.42, 'inverse_total': 0.16},
        },
        'trend': {
            'name': '走勢分析',
            'description': '偏重近10期相對前20期升溫的號碼。',
            'weights': {'recent': 0.35, 'momentum': 0.5, 'total': 0.15},
        },
        'markov': {
            'name': '馬可夫預測',
            'description': '依最新一期號碼，推估歷史上相似轉移後下一期較常出現的號碼。',
            'weights': {'markov': 0.62, 'recent': 0.23, 'total': 0.15},
        },
        'cooccurrence': {
            'name': '共現矩陣預測',
            'description': '依最新一期號碼，挑選歷史上與這組號碼常共同出現的搭配號碼。',
            'weights': {'cooccurrence': 0.58, 'recent': 0.25, 'total': 0.17},
        },
        'pattern': {
            'name': '版路分析預測',
            'description': '結合尾數分佈、連號走勢與近期熱度的進階分析。',
            'weights': {'tail': 0.28, 'consecutive': 0.24, 'recent': 0.28, 'total': 0.12, 'momentum': 0.08},
        },
        'balanced': {
            'name': '均衡分佈預測',
            'description': '考慮奇偶與大小數值的平衡，避免選號過於集中。',
            'weights': {'recent': 0.28, 'odd_even_balance': 0.28, 'big_small_balance': 0.28, 'total': 0.16},
        },
        'ensemble': {
            'name': '整合策略預測',
            'description': '結合頻率、近期走勢、遺漏期數、馬可夫與共現矩陣的綜合策略。',
            'weights': {'total': 0.18, 'recent': 0.2, 'missing': 0.14, 'momentum': 0.12, 'markov': 0.18, 'cooccurrence': 0.18},
        },
    }

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

        normalized_total = normalize_scores(total_counts)
        normalized_recent = normalize_scores(recent_counts)
        self.features = {
            'total': normalized_total,
            'recent': normalized_recent,
            'missing': normalize_scores(missing_spans),
            'inverse_total': {n: 1 - v for n, v in normalized_total.items()},
            'inverse_recent': {n: 1 - v for n, v in normalized_recent.items()},
        }

        hot_rate = {n: hot_counts[n] / hot_window if hot_window else 0 for n in range(1, 40)}
        prior_rate = {n: prior_counts[n] / prior_window if prior_window else 0 for n in range(1, 40)}
        self.features['momentum'] = normalize_scores({
            n: hot_rate[n] - prior_rate[n] for n in range(1, 40)
        })

        chronological_draws = list(reversed(self.draws))
        transition_counts = {s: {t: 0 for t in range(1, 40)} for s in range(1, 40)}
        transition_totals = {n: 0 for n in range(1, 40)}
        for index in range(1, len(chronological_draws)):
            prev_nums = chronological_draws[index - 1]['numbers']
            next_nums = chronological_draws[index]['numbers']
            for source in prev_nums:
                for target in next_nums:
                    transition_counts[source][target] += 1
                    transition_totals[source] += 1

        self.features['markov'] = normalize_scores({
            target: sum(
                transition_counts[source][target] / transition_totals[source]
                for source in self.latest_numbers
                if transition_totals[source] > 0
            )
            for target in range(1, 40)
        })

        co_counts = {s: {t: 0 for t in range(1, 40)} for s in range(1, 40)}
        for draw in self.draws:
            for source in draw['numbers']:
                for target in draw['numbers']:
                    if source != target:
                        co_counts[source][target] += 1

        self.features['cooccurrence'] = normalize_scores({
            target: sum(co_counts[source][target] for source in self.latest_numbers)
            for target in range(1, 40)
        })

        odd_denominator = max(1, min(10, self.total_draws) * 5)
        recent_odd_count = sum(1 for draw in self.draws[:10] for n in draw['numbers'] if n % 2 != 0)
        odd_ratio = recent_odd_count / odd_denominator
        self.features['odd_even_balance'] = {
            n: (1 - odd_ratio if n % 2 != 0 else odd_ratio) for n in range(1, 40)
        }

        recent_big_count = sum(1 for draw in self.draws[:10] for n in draw['numbers'] if n >= 20)
        big_ratio = recent_big_count / odd_denominator
        self.features['big_small_balance'] = {
            n: (1 - big_ratio if n >= 20 else big_ratio) for n in range(1, 40)
        }

        tail_counts = {tail: 0 for tail in range(10)}
        for draw in self.draws:
            for number in draw['numbers']:
                tail_counts[number % 10] += 1
        normalized_tails = normalize_scores(tail_counts)
        self.features['tail'] = {n: normalized_tails[n % 10] for n in range(1, 40)}

        consecutive_counts = {n: 0 for n in range(1, 40)}
        for draw in self.draws:
            nums = sorted(draw['numbers'])
            for index in range(len(nums) - 1):
                if nums[index + 1] - nums[index] == 1:
                    consecutive_counts[nums[index]] += 1
                    consecutive_counts[nums[index + 1]] += 1
        self.features['consecutive'] = normalize_scores(consecutive_counts)

    def predict(self, prediction_type):
        method = self.METHODS.get(prediction_type, self.METHODS['ai'])
        scores = self._score_numbers(method['weights'])
        prediction_sets = self._build_prediction_sets(prediction_type, scores)
        top_candidates = sorted(
            [{'number': f'{number:02d}', 'score': round(scores[number], 4)} for number in scores],
            key=lambda item: item['score'],
            reverse=True,
        )[:10]

        return {
            'success': True,
            'period': next_period_from_draws(self.draws),
            'numbers': prediction_sets[0]['numbers'],
            'method': method['name'],
            'description': method['description'],
            'generated_at': datetime.now().isoformat(timespec='seconds'),
            'sample_size': self.total_draws,
            'recent_window': min(30, self.total_draws),
            'top_candidates': top_candidates,
            'prediction_sets': prediction_sets,
            'backtest': self.backtest(prediction_type),
        }

    def backtest(self, prediction_type, rounds=25, min_history=10):
        chronological_draws = list(reversed(self.draws))
        if len(chronological_draws) <= min_history:
            return {
                'rounds': 0,
                'average_hits': 0,
                'baseline_average_hits': 0,
                'hit_distribution': {hits: 0 for hits in range(6)},
                'best_result': None,
            }

        start_index = max(min_history, len(chronological_draws) - rounds)
        results = []
        baseline_hits = []
        for target_index in range(start_index, len(chronological_draws)):
            history = list(reversed(chronological_draws[:target_index]))
            actual = set(chronological_draws[target_index]['numbers'])
            predictor = LottoPredictor(history)
            method = predictor.METHODS.get(prediction_type, predictor.METHODS['ai'])
            scores = predictor._score_numbers(method['weights'])
            predicted = predictor._select_numbers(scores, style='balanced')
            hits = len(set(predicted) & actual)
            results.append({
                'period': chronological_draws[target_index]['period'],
                'predicted': [f'{number:02d}' for number in predicted],
                'actual': [f'{number:02d}' for number in sorted(actual)],
                'hits': hits,
            })

            rng = random.Random(539000 + target_index)
            baseline = set(rng.sample(range(1, 40), 5))
            baseline_hits.append(len(baseline & actual))

        distribution = {hits: 0 for hits in range(6)}
        for item in results:
            distribution[item['hits']] += 1

        best_result = max(results, key=lambda item: (item['hits'], item['period'])) if results else None
        return {
            'rounds': len(results),
            'average_hits': round(sum(item['hits'] for item in results) / len(results), 3) if results else 0,
            'baseline_average_hits': round(sum(baseline_hits) / len(baseline_hits), 3) if baseline_hits else 0,
            'hit_distribution': distribution,
            'best_result': best_result,
        }

    def _score_numbers(self, weights):
        scores = {number: 0 for number in range(1, 40)}
        for feature, weight in weights.items():
            feature_scores = self.features.get(feature, {})
            for number in range(1, 40):
                scores[number] += feature_scores.get(number, 0) * weight
        return normalize_scores(scores)

    def _build_prediction_sets(self, prediction_type, scores):
        hot_scores = self._score_numbers({'recent': 0.55, 'momentum': 0.25, 'total': 0.2})
        cold_scores = self._score_numbers({'inverse_recent': 0.45, 'missing': 0.4, 'inverse_total': 0.15})
        exploratory_scores = self._score_numbers({'markov': 0.32, 'cooccurrence': 0.28, 'missing': 0.2, 'tail': 0.1, 'consecutive': 0.1})
        definitions = [
            ('推薦組合', scores, 'balanced'),
            ('穩健組合', scores, 'top'),
            ('熱度組合', hot_scores, 'balanced'),
            ('冷門組合', cold_scores, 'balanced'),
            ('探索組合', exploratory_scores, 'explore'),
        ]

        used = set()
        prediction_sets = []
        for label, set_scores, style in definitions:
            numbers = self._select_numbers(set_scores, style=style, used_sets=used, salt=f'{prediction_type}:{label}')
            used.add(tuple(numbers))
            prediction_sets.append({
                'label': label,
                'numbers': [f'{number:02d}' for number in numbers],
                'confidence': self._confidence(numbers, set_scores),
                'profile': self._profile(numbers),
            })
        return prediction_sets

    def _select_numbers(self, scores, style='balanced', used_sets=None, salt=''):
        used_sets = used_sets or set()
        if style == 'top':
            ranked = sorted(scores, key=lambda number: (scores[number], -number), reverse=True)
            return self._first_reasonable_combo(ranked)

        seed = self._seed_for(salt or style)
        rng = random.Random(seed)
        best = None
        best_value = -1
        attempts = 80 if style == 'explore' else 50
        temperature = 0.65 if style == 'explore' else 1.0
        for _ in range(attempts):
            candidate = self._weighted_sample(scores, rng, temperature=temperature)
            combo = tuple(candidate)
            if combo in used_sets:
                continue
            value = sum(scores[number] for number in candidate)
            if self._is_reasonable(candidate):
                return candidate
            if value > best_value:
                best = candidate
                best_value = value
        return best or self._first_reasonable_combo(sorted(scores, key=scores.get, reverse=True))

    def _weighted_sample(self, scores, rng, temperature=1.0):
        available = list(scores.keys())
        picked = []
        while available and len(picked) < 5:
            weights = [(max(scores[number], 0) + 0.05) ** temperature for number in available]
            selected = rng.choices(available, weights=weights, k=1)[0]
            picked.append(selected)
            available.remove(selected)
        return sorted(picked)

    def _first_reasonable_combo(self, ranked_numbers):
        chosen = []
        for number in ranked_numbers:
            trial = sorted(chosen + [number])
            if len(trial) < 5 or self._is_reasonable(trial, partial=True):
                chosen.append(number)
            if len(chosen) == 5:
                break
        chosen = sorted(chosen[:5])
        if len(chosen) == 5 and self._is_reasonable(chosen):
            return chosen
        return sorted(ranked_numbers[:5])

    def _confidence(self, numbers, scores):
        if not numbers:
            return 0
        average_score = sum(scores[number] for number in numbers) / len(numbers)
        spread_bonus = 0.06 if self._is_reasonable(numbers) else 0
        return max(0, min(100, round((average_score + spread_bonus) * 100)))

    def _profile(self, numbers):
        total_sum = sum(numbers)
        odds = sum(1 for number in numbers if number % 2 != 0)
        bigs = sum(1 for number in numbers if number >= 20)
        return {
            'sum': total_sum,
            'odd_even': f'{odds}:{5 - odds}',
            'big_small': f'{bigs}:{5 - bigs}',
        }

    def _seed_for(self, salt):
        basis = '|'.join(draw.get('period', '') for draw in self.draws[:12]) + '|' + salt
        return sum((index + 1) * ord(char) for index, char in enumerate(basis))

    def _is_reasonable(self, numbers, partial=False):
        if not numbers:
            return False
        if partial and len(numbers) < 5:
            return True

        total_sum = sum(numbers)
        if not (70 <= total_sum <= 130):
            return False

        odds = sum(1 for number in numbers if number % 2 != 0)
        if odds == 0 or odds == 5:
            return False

        bigs = sum(1 for number in numbers if number >= 20)
        if bigs == 0 or bigs == 5:
            return False

        return True