document.addEventListener("DOMContentLoaded", function () {
  // chartData はテンプレで文字列として渡されるので parse する
  let chartData = window.chartData;
  if (typeof chartData === "string") {
    try {
      chartData = JSON.parse(chartData);
    } catch (e) {
      chartData = null;
    }
  }

  const urlParams = new URLSearchParams(window.location.search);

  // テンプレは window.chartFilter を渡している
  let filter = window.chartFilter || urlParams.get("filter") || "all";

  // 生徒はデフォルト student だが、predict を潰さない
  if (window.userRole === "student") {
    if (!urlParams.get("filter") && !window.chartFilter) {
      filter = "student";
    }
  }

  // ドロップダウン
  const select = document.getElementById("student-select");
  if (select) {
    select.addEventListener("change", function () {
      const studentId = select.value;
      const params = new URLSearchParams(window.location.search);
      params.set("filter", "student"); // 選択時はstudentモード
      if (studentId) {
        params.set("student_id", studentId);
      } else {
        params.delete("student_id");
      }
      window.location.search = params.toString();
    });
  }

  // データ検証
  if (!chartData || !chartData.labels || chartData.labels.length === 0) {
    console.warn("表示するデータがありません。");
    const msgElem = document.getElementById("insight-message");
    if (msgElem) msgElem.innerText = "データがありません。";
    return;
  }

  const canvas = document.getElementById("chart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  // データの準備
  let labels = [...chartData.labels];
  let dataPoints = [...chartData.data].map((v) => Number(v));

  // 学生別（ドーナツ）の場合、点数が高い順にソート
  if (filter === "student") {
    const paired = labels.map((label, i) => ({ label, value: dataPoints[i] }));
    paired.sort((a, b) => b.value - a.value);
    labels = paired.map((p) => p.label);
    dataPoints = paired.map((p) => p.value);
  }

  // 学生名の取得
  let chartStudentName = "あなた";
  if (window.studentName && window.studentName.trim() !== "") {
    chartStudentName = window.studentName;
  }
  if (select && select.options.length > 0 && select.selectedIndex > 0) {
    const selected = select.options[select.selectedIndex];
    chartStudentName = selected.text.replace(/\(.+\)/, "").trim();
  }

  // グラフの基本設定
  let chartType = "bar"; // デフォルト

  // Y軸の範囲（predict用に値の周辺だけ表示）
  function calcPredictBounds(values) {
    if (!values || values.length === 0) return { min: 0, max: 4 };
    const vmin = Math.min(...values);
    const vmax = Math.max(...values);
    let min = Math.floor((vmin - 0.15) * 100) / 100;
    let max = Math.ceil((vmax + 0.15) * 100) / 100;
    min = Math.max(0, min);
    max = Math.min(4, max);
    if (max - min < 0.4) {
      min = Math.max(0, min - 0.2);
      max = Math.min(4, max + 0.2);
    }
    return { min, max };
  }

  let options = {
    responsive: true,
    maintainAspectRatio: false,
    resizeDelay: 5,
    layout: { padding: 10 },
    plugins: {
      legend: {
        position: "bottom",
        labels: { font: { size: 12 }, padding: 20 },
      },
      title: {
        display: true,
        text: getTitleByFilter(filter, chartStudentName),
        font: { size: 16, weight: "bold" },
        padding: { top: 10, bottom: 20 },
      },
      tooltip: {
        bodyFont: { size: 14 },
        titleFont: { size: 14 },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: filter === "all" ? undefined : (filter === "predict" ? 4.0 : 100),
        ticks: { font: { size: 12 } },
      },
      x: {
        ticks: { autoSkip: true, maxRotation: 45, minRotation: 0, font: { size: 11 } },
      },
    },
  };

  // フィルター別設定
  if (filter === "all") {
    chartType = "bar";
    options.scales.y.ticks.stepSize = 1;
    options.plugins.title.text = "全体成績分布（GPA範囲別学生数）";
  } else if (filter === "student") {
    chartType = "doughnut";
    delete options.scales;
    options.plugins.legend.labels.font.size = 14;
  } else if (filter === "predict") {
    // ★chart_pre.pngのように「3本の棒」で比較
    chartType = "bar";
    const b = calcPredictBounds(dataPoints);
    options.scales.y.beginAtZero = false;
    options.scales.y.min = b.min;
    options.scales.y.max = b.max;
    options.scales.y.ticks.stepSize = 0.05;
    options.plugins.title.text = "GPA比較（全体平均 / 現在 / 予測）";
  }

  // 描画
  new Chart(ctx, {
    type: chartType,
    data: {
      labels: labels,
      datasets: [
        {
          label: getLabelByFilter(filter),
          data: dataPoints,
          backgroundColor:
            filter === "all"
              ? [
                  "#dc212164",
                  "#e1626263",
                  "#f58a6083",
                  "#acaf3c6d",
                  "#bcc53c7a",
                  "#c6f43c77",
                  "#d7ff0d82",
                  "#48ff008c",
                ]
              : getColorsByFilter(filter, dataPoints.length),
          borderColor: "#4e73df",
          borderWidth: 2,
        },
      ],
    },
    options: options,
  });

  // メッセージ更新
  const messageElement = document.getElementById("insight-message");
  if (messageElement) {
    if (chartData.message) {
      messageElement.innerText = chartData.message;
    }
  }
});

/** フィルターに応じたデータセットラベル */
function getLabelByFilter(filter) {
  switch (filter) {
    case "all":
      return "学生数";
    case "student":
      return "評価点";
    case "subject":
      return "科目別平均点";
    case "predict":
      return "GPA";
    default:
      return "数値";
  }
}

/** グラフタイトルを生成 */
function getTitleByFilter(filter, studentName) {
  switch (filter) {
    case "student":
      return `${studentName}の成績分布`;
    case "subject":
      return "科目別 平均点分布";
    case "predict":
      return "GPA比較（全体平均 / 現在 / 予測）";
    default:
      return "全体成績分布";
  }
}

/** フィルターに応じた配色 */
function getColorsByFilter(filter, count) {
  const baseColors = [
    "#36A2EB",
    "#FF6384",
    "#FFCE56",
    "#4BC0C0",
    "#9966FF",
    "#FF9F40",
    "#C9CBCF",
    "#4e73df",
    "#1cc88a",
    "#36b9cc",
    "#f6c23e",
    "#e74a3b",
    "#858796",
  ];

  if (filter === "student") {
    const colors = [];
    for (let i = 0; i < count; i++) colors.push(baseColors[i % baseColors.length]);
    return colors;
  }

  // predict / subject は単色でOK（chart_pre.pngのイメージ）
  return "#4e73df";
}
