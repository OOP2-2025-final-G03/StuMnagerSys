// Chart.jsで成績分析グラフを描画
// chartDataはwindow.chartDataとして渡される
// chartFilterで表示する図表の種類を判定

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
  const reqFilter = window.chartFilter || 'all';
  
  // 全体タブ：棒グラフでGPA分布を表示
  if (reqFilter === 'all') {
    const colors = [
      '#FF6B6B', '#FF8E8E', '#FFA8A8', '#FFB3B3',
      '#99FF99', '#66FF66', '#33FF33', '#00DD00'
    ];
    
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: window.chartData.labels,
        datasets: [{
          label: '学生数',
          data: window.chartData.scores,
          backgroundColor: colors,
          borderColor: '#333',
          borderWidth: 1
        }]
      },
      options: {
        responsive: false,
        indexAxis: 'x',
        plugins: {
          legend: {
            position: 'bottom',
          },
          title: {
            display: true,
            text: 'GPA分布'
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: '学生数'
            }
          }
        }
      }
    });
  } 
  // 学生別・科目別：ドーナツグラフ
  else {
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

    let chartTitle = '成績分布';
    if (window.studentName && window.studentName.trim() !== '') {
      chartTitle = `${window.studentName}の成績分布`;
    } else if (select && select.options.length > 0 && select.selectedIndex > 0) {
      const selected = select.options[select.selectedIndex];
      chartTitle = `${selected.text.replace(/\(.+\)/, '').trim()}の成績分布`;
    }

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
            text: chartTitle
          }
        }
      }
    });
  }

  // メッセージを表示
  const msgElem = document.getElementById('insight-message');
  if (msgElem && window.chartData.message) {
    msgElem.textContent = window.chartData.message;
  } 
  // メッセージがない場合、得意・苦手科目メッセージを表示（学生別・科目別用）
  else if (msgElem && reqFilter !== 'all' && window.chartData.labels && window.chartData.scores && window.chartData.labels.length > 0) {
    const maxIdx = window.chartData.scores.indexOf(Math.max(...window.chartData.scores));
    const minIdx = window.chartData.scores.indexOf(Math.min(...window.chartData.scores));
    const best = window.chartData.labels[maxIdx];
    const worst = window.chartData.labels[minIdx];
    let chartName = 'あなた';
    if (window.studentName && window.studentName.trim() !== '') {
      chartName = window.studentName;
    } else if (select && select.options.length > 0 && select.selectedIndex > 0) {
      chartName = select.options[select.selectedIndex].text.replace(/\(.+\)/, '').trim();
    }
    msgElem.textContent = `${chartName}は${best}が得意、${worst}が苦手です`;
  }
});

