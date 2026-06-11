var selectedNumbers = new Set();
var numberCounts = {};

function two(n) {
  return n.toString().padStart(2, '0');
}

function buildPicker() {
  var picker = document.getElementById('numberPicker');
  picker.innerHTML = '';
  for (var i = 1; i <= 39; i++) {
    var num = two(i);
    var button = document.createElement('button');
    button.className = 'pick';
    button.type = 'button';
    button.textContent = num;
    button.setAttribute('data-num', num);
    button.onclick = function() { toggleNumber(this.getAttribute('data-num')); };
    picker.appendChild(button);
  }
}

function toggleNumber(num) {
  if (selectedNumbers.has(num)) {
    selectedNumbers.delete(num);
  } else if (selectedNumbers.size < 5) {
    selectedNumbers.add(num);
  }
  syncSelectedUI();
}

function syncSelectedUI() {
  document.querySelectorAll('.pick').forEach(function(button) {
    button.classList.toggle('selected', selectedNumbers.has(button.getAttribute('data-num')));
  });
  var list = document.getElementById('selectedList');
  var items = Array.from(selectedNumbers).sort();
  list.innerHTML = items.length
    ? items.map(function(num) { return '<span class="chip">' + num + '</span>'; }).join('')
    : '<span>尚未標記</span>';
}

function loadQuick(count) {
  document.getElementById('resultLabel').textContent = '載入最近 ' + count + ' 期';
  fetch('/api/history?limit=' + encodeURIComponent(count))
    .then(function(r) { return r.json(); })
    .then(function(data) { renderHistory(data, '最近 ' + count + ' 期'); });
}

function searchByPeriod() {
  var p1 = document.getElementById('p1').value.trim();
  var p2 = document.getElementById('p2').value.trim();
  var label = p1 && p2 ? p1 + ' - ' + p2 + ' 期' : '指定期次';
  fetch('/api/history?start=' + encodeURIComponent(p1) + '&end=' + encodeURIComponent(p2))
    .then(function(r) { return r.json(); })
    .then(function(data) { renderHistory(data, label); });
}

function renderHistory(data, label) {
  var head = document.getElementById('historyHead');
  var tbody = document.getElementById('historyBody');
  head.innerHTML = '<tr><th>期次</th><th>開獎日</th>' +
    Array.from({length: 39}, function(_, idx) { return '<th>' + two(idx + 1) + '</th>'; }).join('') +
    '</tr>';
  tbody.innerHTML = '';
  numberCounts = {};
  for (var i = 1; i <= 39; i++) numberCounts[i] = 0;

  if (!data.length) {
    tbody.innerHTML = '<tr><td class="empty" colspan="41">沒有符合條件的資料</td></tr>';
    document.getElementById('resultLabel').textContent = label + '，共 0 筆';
    renderRanking();
    renderSortedNumbers();
    return;
  }

  data.forEach(function(row) {
    var nums = row.numbers
      .split(/[\s,，]+/)
      .filter(function(n) { return n.trim().length > 0; })
      .map(function(n) { return n.trim().padStart(2, '0'); });
    nums.forEach(function(n) {
      var num = parseInt(n, 10);
      if (num >= 1 && num <= 39) numberCounts[num]++;
    });

    var tr = document.createElement('tr');
    tr.innerHTML = '<td>' + row.period + '</td><td>' + row.draw_date + '</td>';
    for (var i = 1; i <= 39; i++) {
      var num = two(i);
      tr.innerHTML += nums.indexOf(num) >= 0 ? '<td><span class="hit">' + num + '</span></td>' : '<td></td>';
    }
    tbody.appendChild(tr);
  });

  document.getElementById('resultLabel').textContent = label + '，共 ' + data.length + ' 筆';
  renderRanking();
  renderSortedNumbers();
}

function renderRanking() {
  var rankBody = document.getElementById('rankBody');
  rankBody.innerHTML = '';
  var counts = [];
  for (var i = 1; i <= 39; i++) counts.push({num: i, count: numberCounts[i] || 0});
  var maxCount = counts.reduce(function(max, item) { return Math.max(max, item.count); }, 0);

  rankBody.innerHTML = '<div class="stat-spacer stat-title">開出次數排序</div>';
  counts.forEach(function(item) {
    var height = maxCount > 0 && item.count > 0 ? Math.max(4, Math.round(item.count * 48 / maxCount)) : 0;
    var bar = item.count > 0 ? '<div class="bar" style="height:' + height + 'px"></div>' : '';
    var div = document.createElement('button');
    div.type = 'button';
    div.className = 'stat';
    div.onclick = function() { toggleNumber(two(item.num)); };
    div.innerHTML = '<strong>' + item.count + '</strong>' + bar;
    rankBody.appendChild(div);
  });
}

function renderSortedNumbers() {
  var sortedRankBody = document.getElementById('sortedRankBody');
  sortedRankBody.innerHTML = '';
  var sorted = [];
  for (var i = 1; i <= 39; i++) sorted.push({num: i, count: numberCounts[i] || 0});
  sorted.sort(function(a, b) { return b.count - a.count || a.num - b.num; });

  sortedRankBody.innerHTML = '<div class="stat-spacer stat-title">統計次數號碼</div>';
  sorted.forEach(function(item) {
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'rank-cell';
    button.onclick = function() { toggleNumber(two(item.num)); };
    button.innerHTML = '<strong>' + two(item.num) + '</strong><span>' + item.count + '</span>';
    sortedRankBody.appendChild(button);
  });
}

buildPicker();
syncSelectedUI();
loadQuick(30);
