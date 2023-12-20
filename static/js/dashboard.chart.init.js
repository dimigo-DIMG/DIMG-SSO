class CustomChart {
  constructor(nodeID) {
    this.nodeID = nodeID;
  }

  drawChart(para) {
    const {
      label_list,
      dataset_list,
      stack_bool,
      title,
      x_label,
      y_label,
      type,
      beginAtZero,
    } = para;

    const data = {
      labels: label_list || [],
      datasets: dataset_list || [],
    };

    const options = {
      scales: {
        x: {
          stacked: stack_bool || false,
          title: {
            display: x_label ? true : false,
            text: x_label ? x_label : "",
          },
          ticks: {
            font: {
              size: 14,
            },
          },
        },
        y: {
          stacked: stack_bool || false,
          title: {
            display: y_label ? true : false,
            text: y_label ? y_label : "",
          },
          ticks: {
            font: {
              size: 14,
            },
            stepSize: 100,
          },
          beginAtZero: beginAtZero || true,
        },
      },
      plugins: {
        title: {
          display: title ? true : false,
          text: title || "untitled",
          font: {
            size: 20,
          },
        },
      },
      responsive: true,
      maintainAspectRatio: false,
    };

    const ctx = document.getElementById(this.nodeID).getContext("2d");
    this.userChart = new Chart(ctx, {
      type: type || "bar",
      data: data,
      options: options,
    });
  }

  updateChart(para) {
    const {
      label_list,
      dataset_list,
      stack_bool,
      title,
      x_label,
      y_label,
      type,
      beginAtZero,
    } = para;

    this.userChart.data.labels = label_list || [];
    this.userChart.data.datasets = dataset_list || [];

    this.userChart.options.scales.x.stacked = stack_bool || false;
    this.userChart.options.scales.y.stacked = stack_bool || false;

    this.userChart.options.plugins.title.text = title || "untitled";

    this.userChart.options.scales.x.title.display = x_label ? true : false;
    this.userChart.options.scales.x.title.text = x_label ? x_label : "";

    this.userChart.options.scales.y.title.display = y_label ? true : false;
    this.userChart.options.scales.y.title.text = y_label ? y_label : "";

    this.userChart.options.scales.y.beginAtZero = beginAtZero || false;

    this.userChart.config.type = type || "bar";

    this.userChart.update();
  }
}
