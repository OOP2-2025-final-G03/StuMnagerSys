// Chart.jsで学生別成績ドーナツグラフを描画
// chartDataはwindow.chartDataとして渡される

console.log(window.chartData);

document.addEventListener("DOMContentLoaded", function () {
  const chartData = window.chartData;
  const filter = window.reqFilter || "all";

  if (!chartData || !chartData.labels || chartData.labels.length === 0) {
    console.error("表示するデータがありません。");
    return;
  }

  /* ===============================
     学生選択時の挙動
  =============================== */
  const select = document.getElementById("student-select");
  if (select) {
    select.addEventListener("change", function () {
      const studentId = select.value;
      const params = new URLSearchParams(window.location.search);
      params.set("filter", "student");
      if (studentId) {
        params.set("student_id", studentId);
      } else {
        params.delete("student_id");
      }
      window.location.search = params.toString();
    });
  }

  const canvas = document.getElementById("chart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  // --- データの準備とソート ---
  let labels = [...chartData.labels];

  // scores / data 両対応（元コード互換）
  let dataPoints =
    chartData.data ??
    chartData.scores ??
    [];

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

  // --- 学生名取得（元コードのロジック保持） ---
  let chartStudentName = "";
  if (window.studentName && window.studentName.trim() !== "") {
    chartStudentName = window.studentName;
  } else {
    chartStudentName = "あなた";
  }
  if (select && select.options.length > 0 && select.selectedIndex > 0) {
    const selected = select.options[select.selectedIndex];
    chartStudentName = selected.text.replace(/\(.+\)/, "").trim();
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
    options: {
      ...options,
      plugins: {
        legend: {
          position: filter === "student" ? "bottom" : "top",
        },
        title:
          filter === "student"
            ? {
                display: true,
                text: `${chartStudentName}の成績分布`,
              }
            : undefined,
      },
    },
  });

  // メッセージの更新
  const messageElement = document.getElementById("insight-message");

  // 得意・苦手科目メッセージ
  if (
    messageElement &&
    filter === "student" &&
    labels.length > 0
  ) {
    const maxIdx = dataPoints.indexOf(Math.max(...dataPoints));
    const minIdx = dataPoints.indexOf(Math.min(...dataPoints));
    const best = labels[maxIdx];
    const worst = labels[minIdx];
    messageElement.textContent = `${chartStudentName}は${best}が得意、${worst}が苦手です`;
  } else if (messageElement && chartData.message) {
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
