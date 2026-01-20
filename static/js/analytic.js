
document.addEventListener("DOMContentLoaded", function () {
  const chartData = window.chartData;
  const urlParams = new URLSearchParams(window.location.search);
  let filter = window.reqFilter || urlParams.get('filter') || "all";
  if (window.userRole === 'student') {
    filter = 'student';
  }


  // ドロップダウン
  const select = document.getElementById('student-select');
  if (select) {
    select.addEventListener('change', function () {
      const studentId = select.value;
      const params = new URLSearchParams(window.location.search);
      params.set('filter', 'student'); // 選択時は強制的にstudentモード
      if (studentId) {
        params.set('student_id', studentId);
      } else {
        params.delete('student_id');
      }
      window.location.search = params.toString();
    });
  }

  // データ検証
  if (!chartData || !chartData.labels || chartData.labels.length === 0) {
    console.warn("表示するデータがありません。");
    const msgElem = document.getElementById("insight-message");
    if(msgElem) msgElem.innerText = "データがありません。";
    return;
  }

  const canvas = document.getElementById("chart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  // データの準備とソート
  let labels = [...chartData.labels];
  let dataPoints = [...chartData.data];

  // 円グラフ（学生別）の場合、点数が高い順にソートして見やすくする
  if (filter === "student") {
    const paired = labels.map((label, i) => ({ label, value: dataPoints[i] }));
    paired.sort((a, b) => b.value - a.value); // 降順ソート
    labels = paired.map((p) => p.label);
    dataPoints = paired.map((p) => p.value);
  }

  // 学生名の取得
  let chartStudentName = 'あなた';
  if (window.studentName && window.studentName.trim() !== '') {
    chartStudentName = window.studentName;
  }
  // ドロップダウンがある場合はそちらの表記を優先（(ID)を除く）
  if (select && select.options.length > 0 && select.selectedIndex > 0) {
    const selected = select.options[select.selectedIndex];
    chartStudentName = selected.text.replace(/\(.+\)/, '').trim();
  }

  // グラフの基本設定
  let chartType = "bar"; // デフォルト
  
  // グラフの共通オプション
  let options = {
    responsive: true,
    maintainAspectRatio: false, 
    resizeDelay: 5,
    layout: {
      padding: 10
    },
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          font: { size: 12 },
          padding: 20
        }
      },
      title: {
        display: true,
        text: getTitleByFilter(filter, chartStudentName),
        font: { size: 16, weight: 'bold' },
        padding: { top: 10, bottom: 20 }
      },
      tooltip: {
        bodyFont: { size: 14 },
        titleFont: { size: 14 }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        // 全体・予測は GPA(4.0)、それ以外は 100点満点
        max: (filter === "predict" || filter === "all" || isGpaMode(filter)) ? 4.0 : 100,
        ticks: { font: { size: 12 } }
      },
      x: {
        ticks: { autoSkip: true, maxRotation: 45, minRotation: 0, font: { size: 11 } }
      }
    }
  };

  // フィルター別の設定上書き
  if (filter === "student") {
    chartType = "doughnut";
    delete options.scales;
    // ドーナツグラフ用の凡例フォント調整
    options.plugins.legend.labels.font.size = 14; 

  } else if (filter === "predict") {
    chartType = "line"; 
    options.scales.y.suggestedMin = 0;
    options.scales.y.suggestedMax = 4.0;
  }

  // グラフの描画
  new Chart(ctx, {
    type: chartType,
    data: {
      labels: labels,
      datasets: [
        {
          label: getLabelByFilter(filter),
          data: dataPoints,
          backgroundColor: getColorsByFilter(filter, dataPoints.length),
          borderColor: filter === "predict" ? "#4e73df" : "#ffffff",
          borderWidth: 2,
          fill: filter === "predict" ? "origin" : false, 
          tension: 0.3,
          pointRadius: 5,
          pointHoverRadius: 7,
        },
      ],
    },
    options: options,
  });

  // メッセージの更新
  // サーバーからのメッセージがあればそれを優先、なければ自動生成
  const messageElement = document.getElementById("insight-message");
  if (messageElement) {
    if (chartData.message) {
      // サーバーからのメッセージを表示
      messageElement.innerText = chartData.message;
    } else if (filter === 'student' && dataPoints.length > 0) {
      // 得意・苦手を自動計算
      const maxIdx = dataPoints.indexOf(Math.max(...dataPoints));
      const minIdx = dataPoints.indexOf(Math.min(...dataPoints));
      const best = labels[maxIdx];
      const worst = labels[minIdx];
      messageElement.innerText = `${chartStudentName}は${best}が得意(${dataPoints[maxIdx]}点)、${worst}が苦手な傾向にあります(${dataPoints[minIdx]}点)。`;
    }
  }
});

/** フィルターに応じたデータセットラベル */
function getLabelByFilter(filter) {
  switch (filter) {
    case "all": return "学生数";
    case "student": return "評価点";
    case "subject": return "科目別平均点";
    case "predict": return "GPA予測";
    default: return "数値";
  }
}

/** グラフタイトルを生成 */
function getTitleByFilter(filter, studentName) {
    switch (filter) {
        case "student": return `${studentName}の成績分布`;
        case "subject": return "科目別 平均点分布";
        case "predict": return "GPA 推移と予測";
        default: return "全体成績分布";
    }
}

/** GPAモード判断 */
function isGpaMode(filter) {
    // 必要に応じてロジック追加
    return false; 
}

/** フィルターに応じた配色 */
function getColorsByFilter(filter, count) {
  // 基本的な色セット
  const baseColors = [
    '#36A2EB', '#FF6384', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF',
    "#4e73df", "#1cc88a", "#36b9cc", "#f6c23e", "#e74a3b", "#858796"
  ];

  if (filter === "student") {
    // 項目数分だけ色を繰り返して返す
    let colors = [];
    for (let i = 0; i < count; i++) {
      colors.push(baseColors[i % baseColors.length]);
    }
    return colors;
  }
  
  // 単色 (Bar/Line用)
  return "#4e73df"; 
}
