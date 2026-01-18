// Chart.jsで学生別成績ドーナツグラフを描画
// chartDataはwindow.chartDataとして渡される

console.log(window.chartData);
document.addEventListener('DOMContentLoaded', function () {
  // 学生選択時の挙動
  const select = document.getElementById('student-select');
  if (select) {
    select.addEventListener('change', function () {
      const studentId = select.value;
      const params = new URLSearchParams(window.location.search);
      params.set('filter', 'student');
      if (studentId) {
        params.set('student_id', studentId);
      } else {
        params.delete('student_id');
      }
      window.location.search = params.toString();
    });
  }

  if (!window.chartData || !window.chartData.labels || !window.chartData.scores) return;

  const ctx = document.getElementById('chart').getContext('2d');
  const data = {
    labels: window.chartData.labels,
    datasets: [{
      data: window.chartData.scores,
      backgroundColor: [
        '#36A2EB', '#FF6384', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF'
      ],
      borderWidth: 2
    }]
  };

  new Chart(ctx, {
    type: 'doughnut',
    data: data,
    options: {
      responsive: false,
      plugins: {
        legend: {
          position: 'bottom',
        },
        title: {
          display: true,
          text: window.chartData.message || '学生別成績分布'
        }
      }
    }
  });

  // 得意・苦手科目メッセージ
  const msgElem = document.getElementById('insight-message');
  if (msgElem && window.chartData.labels && window.chartData.scores && window.chartData.labels.length > 0) {
    const maxIdx = window.chartData.scores.indexOf(Math.max(...window.chartData.scores));
    const minIdx = window.chartData.scores.indexOf(Math.min(...window.chartData.scores));
    const best = window.chartData.labels[maxIdx];
    const worst = window.chartData.labels[minIdx];
    // 学生名はセレクトボックスから取得
    let studentName = '';
    const select = document.getElementById('student-select');
    if (select) {
      const selected = select.options[select.selectedIndex];
      studentName = selected.text.replace(/\(.+\)/, '').trim();
    }
    msgElem.textContent = `${studentName}は${best}が得意、${worst}が苦手です`;
  }
});
