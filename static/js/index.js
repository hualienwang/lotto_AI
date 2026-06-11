const fetchBtn = document.getElementById('fetch-history-btn');
const statusText = document.getElementById('fetch-status');

fetchBtn.addEventListener('click', async () => {
  fetchBtn.disabled = true;
  statusText.textContent = '正在抓取歷史資料，請稍候...';

  try {
    const response = await fetch('/api/fetch-history', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    const result = await response.json();

    if (result.success) {
      statusText.textContent = result.message;
    } else {
      statusText.textContent = '抓取失敗：' + result.message;
    }
  } catch (error) {
    statusText.textContent = '伺服器連線失敗，請稍後再試。';
  } finally {
    fetchBtn.disabled = false;
  }
});
