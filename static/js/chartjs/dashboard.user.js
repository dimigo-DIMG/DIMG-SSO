var data = {
  labels: [
    "12/18",
    "19",
    "20",
    "21",
    "22",
    "23",
    "24",
    "25",
    "26",
    "27",
    "28",
    "29",
    "30",
    "31",
  ],
  datasets: [
    {
      label: "휴면계정",
      backgroundColor: "rgba(75, 192, 192, 0.5)",
      data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 20, 20, 20, 20],
    },
    {
      label: "졸업생",
      backgroundColor: "rgba(97, 0, 255, 0.5)",
      data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 182, 182, 182, 182],
    },
    {
      label: "재학생",
      backgroundColor: "rgba(255, 64, 105, 0.5)",
      data: [
        770, 770, 770, 770, 770, 770, 770, 770, 770, 760, 621, 621, 621, 621,
      ],
    },
    // Add more datasets if needed
  ],
};

// Configuration options
var options = {
  scales: {
    x: {
      stacked: true,
      title: {
        display: true,
        text: "시간(일)",
      },
      ticks: {
        font: {
          size: 14,
        },
      },
    },
    y: {
      stacked: true,
      title: {
        display: true,
        text: "유저 수(명)",
      },
      ticks: {
        font: {
          size: 14,
        },
        stepSize: 100,
      },
      beginAtZero: false,
    },
  },
  plugins: {
    title: {
      display: true,
      text: "일별 사용자 수",
      font: {
        size: 20,
      },
    },
  },
  responsive: true,
  maintainAspectRatio: false,
};

// Get the canvas element
var ctx = document.getElementById("user-stackedBar").getContext("2d");

// Create the stacked bar chart
var userStackedBar = new Chart(ctx, {
  type: "bar",
  data: data,
  options: options,
});

// Function to update the chart with new data
function updateChart() {
  // Update the chart labels
  myStackedBarChart.data.labels = ["New Label 1", "New Label 2", "New Label 3"];

  // Update the chart data
  myStackedBarChart.data.datasets[0].data = [50, 30, 80];
  myStackedBarChart.data.datasets[1].data = [20, 40, 60];

  // Update the chart title
  myStackedBarChart.options.plugins.title.text = "Updated Chart Title";

  // Update the chart
  myStackedBarChart.update();
}
