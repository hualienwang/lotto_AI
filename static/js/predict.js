function changePredictType() {
  return document.getElementById('predictType').value;
}

function generatePrediction() {
  var type = document.getElementById('predictType').value;
  fetch('/api/predict?type=' + encodeURIComponent(type))
    .then(function(response) {
      return response.json().then(function(data) {
        if (!response.ok || !data.success) throw new Error(data.message || '預測失敗');
        return data;
      });
    })
    .then(function(data) {
      var generatedAt = new Date(data.generated_at);
      document.getElementById('predictPeriod').textContent = data.period;
      document.getElementById('predictNumbers').innerHTML = data.numbers.map(function(n) {
        return '<span class="ball">' + n + '</span>';
      }).join('');
      document.getElementById('predictMethod').textContent = data.method;
      document.getElementById('predictTime').textContent = generatedAt.toLocaleString();
      document.getElementById('sampleSize').textContent = data.sample_size;
      document.getElementById('modelNote').textContent = data.description + ' 參考最近 ' + data.recent_window + ' 期與全部歷史資料。';
      document.getElementById('predictionResult').style.display = 'block';

      savePrediction(data.period, data.numbers, data.method, generatedAt);
    })
    .catch(function(error) {
      alert(error.message);
    });
}

function savePrediction(period, numbers, method, time) {
  var tbody = document.getElementById('predictionList');
  var tr = document.createElement('tr');
  var numberText = numbers.map(function(n) { return n.toString().padStart(2, '0'); }).join(',');
  tr.innerHTML = '<td>' + period + '</td>' +
                 '<td data-csv-value="' + numberText + '">' + numbers.map(function(n) { return '<span class="mini-ball">' + n.toString().padStart(2, '0') + '</span>'; }).join('') + '</td>' +
                 '<td>' + method + '</td>' +
                 '<td>' + time.toLocaleString() + '</td>';
  tbody.insertBefore(tr, tbody.firstChild);
}

function exportToCSV() {
  var rows = document.querySelectorAll('#predictionList tr');
  if (rows.length === 0) {
    alert('沒有資料可匯出');
    return;
  }
  var csvContent = '\uFEFF期次,預測號碼,方式,時間\n';
  rows.forEach(function(row) {
    var cols = row.querySelectorAll('td');
    var rowData = [];
    cols.forEach(function(col) {
      var value = col.getAttribute('data-csv-value') || col.textContent;
      rowData.push('"' + value.replace(/"/g, '""') + '"');
    });
    csvContent += rowData.join(',') + '\n';
  });

  var form = document.createElement('form');
  form.method = 'POST';
  form.action = '/api/export-csv';
  form.style.display = 'none';

  var input = document.createElement('textarea');
  input.name = 'csvContent';
  input.value = csvContent;
  form.appendChild(input);

  document.body.appendChild(form);
  form.submit();
  document.body.removeChild(form);
}
