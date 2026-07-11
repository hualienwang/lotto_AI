import unittest

from src.predictor import LottoPredictor


def make_draws(count=45):
    draws = []
    for index in range(count):
        start = (index * 3) % 39
        numbers = [((start + offset * 7) % 39) + 1 for offset in range(5)]
        draws.append({
            'period': str(115000000 + count - index),
            'numbers': numbers,
            'draw_date': f'2026-06-{(index % 28) + 1:02d}',
        })
    return draws


class LottoPredictorTest(unittest.TestCase):
    def test_prediction_returns_multiple_ranked_sets(self):
        predictor = LottoPredictor(make_draws())

        result = predictor.predict('ensemble')

        self.assertTrue(result['success'])
        self.assertEqual(5, len(result['numbers']))
        self.assertEqual(5, len(result['prediction_sets']))
        self.assertEqual(
            ['推薦組合', '穩健組合', '熱度組合', '冷門組合', '探索組合'],
            [item['label'] for item in result['prediction_sets']],
        )
        for item in result['prediction_sets']:
            self.assertEqual(5, len(item['numbers']))
            self.assertEqual(sorted(item['numbers']), item['numbers'])
            self.assertGreaterEqual(item['confidence'], 0)
            self.assertLessEqual(item['confidence'], 100)

    def test_backtest_summary_reports_recent_performance(self):
        predictor = LottoPredictor(make_draws(60))

        result = predictor.predict('ensemble')
        backtest = result['backtest']

        self.assertEqual(25, backtest['rounds'])
        self.assertIn('average_hits', backtest)
        self.assertIn('hit_distribution', backtest)
        self.assertIn('best_result', backtest)
        self.assertEqual(25, sum(backtest['hit_distribution'].values()))
        self.assertIn('baseline_average_hits', backtest)


if __name__ == '__main__':
    unittest.main()
