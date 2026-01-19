document.addEventListener("DOMContentLoaded", function () {
  const chartData = window.chartData;
  const filter = window.reqFilter || "all";

  if (!chartData || !chartData.labels || chartData.labels.length === 0) {
    console.error("表示するデータがありません。");
    return;
  }

  const canvas = document.getElementById("chart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  // --- データの準備とソート ---
  let labels = [...chartData.labels];
  let dataPoints = [...chartData.data];

  // 円グラフ（私の成績）の場合、点数が高い順にソート
  if (filter === "student") {
    const paired = labels.map((label, i) => ({ label, value: dataPoints[i] }));
    paired.sort((a, b) => b.value - a.value); // 降順ソート
    labels = paired.map((p) => p.label);
    dataPoints = paired.map((p) => p.value);
  }

  // --- グラフの設定 ---
  let chartType = "bar"; // デフォルトは棒グラフ
  let options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        max: filter === "predict" || filter === "all" ? 4.0 : 100,
      },
    },
  };

  if (filter === "student") {
    chartType = "doughnut";
    delete options.scales; // 円グラフに軸は不要
  } else if (filter === "predict") {
    chartType = "line"; // 成績予測を折れ線グラフに変更
    options.scales.y.suggestedMin = 0;
    options.scales.y.suggestedMax = 4.0;
  }

  // --- グラフの描画 ---
  new Chart(ctx, {
    type: chartType,
    data: {
      labels: labels,
      datasets: [
        {
          label: getLabelByFilter(filter),
          data: dataPoints,
          backgroundColor: getColorsByFilter(filter, dataPoints.length),
          borderColor: "#4e73df", // 折れ線の色
          borderWidth: 2,
          fill: filter === "predict" ? "origin" : false, // 予測グラフの下を塗りつぶす
          tension: 0.3, // 折れ線を少し滑らかにする
          pointRadius: 5,
          pointHoverRadius: 7,
        },
      ],
    },
    options: options,
  });

  // メッセージの更新
  const messageElement = document.getElementById("insight-message");
  if (messageElement && chartData.message) {
    messageElement.innerText = chartData.message;
  }
});

/**
 * フィルターに応じたラベルを返す（エラー解消のために必須）
 */
function getLabelByFilter(filter) {
  switch (filter) {
    case "all":
      return "学生数";
    case "student":
      return "自分の評点";
    case "subject":
      return "科目別平均点";
    case "predict":
      return "GPA予測";
    default:
      return "数値";
  }
}

/**
 * フィルターに応じた配色を返す（エラー解消のために必須）
 */
function getColorsByFilter(filter, count) {
  const baseColors = [
    "#4e73df",
    "#1cc88a",
    "#36b9cc",
    "#f6c23e",
    "#e74a3b",
    "#858796",
  ];
  if (filter === "student") {
    // 項目数分だけ色を繰り返して返す
    let colors = [];
    for (let i = 0; i < count; i++) {
      colors.push(baseColors[i % baseColors.length]);
    }
    return colors;
  }
  return "#4e73df"; // その他は単色
}
