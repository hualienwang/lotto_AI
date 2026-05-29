from flask import Blueprint, jsonify, request, Response, redirect, render_template
from datetime import datetime
from .database import get_db, load_draws
from .predictor import LottoPredictor

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/history')
def get_history():
    db = get_db()
    limit = request.args.get('limit', type=int)
    start = request.args.get('start')
    end = request.args.get('end')
    
    query = 'SELECT "期別" AS period, "大小順序" AS numbers, "開獎日" AS draw_date FROM history'
    params = []
    
    if start and end:
        query += ' WHERE "期別" >= ? AND "期別" <= ?'
        params = [start, end]
    
    query += ' ORDER BY "期別" DESC'
    
    if limit:
        query += f' LIMIT {limit}'
    
    results = db.execute(query, params).fetchall()
    return jsonify([dict(row) for row in results])

@api_bp.route('/api/manual', methods=['POST'])
def add_manual():
    db = get_db()
    data = request.get_json()
    
    try:
        db.execute(
            'INSERT OR REPLACE INTO history ("期別", "大小順序", "開獎日", "頭獎中獎注數") VALUES (?, ?, ?, ?)',
            (data['period'], data['numbers'], data['draw_date'], data.get('prize_count', 0))
        )
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@api_bp.route('/api/next-period')
def get_next_period():
    db = get_db()
    result = db.execute('SELECT MAX("期別") as max_period FROM history').fetchone()
    next_period = int(result['max_period']) + 1 if result['max_period'] else 1
    return jsonify({'next_period': next_period})

@api_bp.route('/api/predict')
def predict_numbers():
    prediction_type = request.args.get('type', 'ai')
    draws = load_draws()
    if len(draws) < 5:
        return jsonify({
            'success': False,
            'message': '歷史資料不足，至少需要 5 期開獎資料才能建立預測模型。'
        }), 400
    
    predictor = LottoPredictor(draws)
    return jsonify(predictor.predict(prediction_type))

@api_bp.route('/api/export-csv', methods=['POST'])
def export_csv():
    if request.is_json:
        data = request.get_json(silent=True) or {}
        csv_content = data.get('csvContent', '')
    else:
        csv_content = request.form.get('csvContent', '')
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'prediction_history_{timestamp}.csv'
    
    return Response(
        csv_content,
        content_type='text/csv; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )

@api_bp.route('/')
def index():
    return render_template('index.html')

@api_bp.route('/history.html')
def history_page():
    return render_template('history.html')

@api_bp.route('/predict.html')
def predict_page():
    return render_template('predict.html')

@api_bp.route('/manual.html')
def manual_page():
    return render_template('manual.html')

@api_bp.route('/pridict.html')
def predict_typo():
    return redirect('/predict.html', code=302)
