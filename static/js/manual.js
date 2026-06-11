function submitManual() {
  var period = document.getElementById('period').value.trim();
  var drawDate = document.getElementById('drawDate').value;
  var prizeCount = document.getElementById('prizeCount').value.trim();
  var values = document.getElementById('numbersInput').value
    .split(',')
    .map(function(value) { return value.trim(); })
    .filter(function(value) { return value !== ''; });
  if (values.length !== 5) {
    showMessage(false, '請輸入 5 個以逗號分隔的號碼');
    return;
  }
  if (!prizeCount || isNaN(prizeCount) || parseInt(prizeCount) < 0) {
    showMessage(false, '請輸入有效的頭獎中獎注數');
    return;
  }
  values = values.map(function(value) { return value.padStart(2, '0'); });
  var numbers = values.join(',');

  fetch('/api/manual', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({period: period, draw_date: drawDate, numbers: numbers, prize_count: parseInt(prizeCount)})
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    if (data.success) {
      showMessage(true, '開獎記錄已儲存成功');
      document.getElementById('manualForm').reset();
      initDefaults();
    } else {
      showMessage(false, '儲存失敗：' + data.message);
    }
  });
}

function initDefaults() {
  loadNextPeriod();
  setDefaultDrawDate();
}

function setDefaultDrawDate() {
  var drawDateInput = document.getElementById('drawDate');
  if (drawDateInput.value) return;
  var today = new Date();
  var localToday = new Date(today.getTime() - today.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 10);
  drawDateInput.value = localToday;
}

function loadNextPeriod() {
  fetch('/api/next-period')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      var periodInput = document.getElementById('period');
      if (periodInput.value.trim()) return;
      periodInput.value = String(data.next_period);
    });
}

function showMessage(success, text) {
  var msg = document.getElementById('message');
  msg.style.backgroundColor = success ? '#eaf6ef' : '#fff0ee';
  msg.style.color = success ? '#126443' : '#9f2d22';
  msg.style.borderColor = success ? '#9ed4b6' : '#e7aea7';
  msg.textContent = text;
  msg.style.display = 'block';
  setTimeout(function() { msg.style.display = 'none'; }, 3000);
}

initDefaults();
