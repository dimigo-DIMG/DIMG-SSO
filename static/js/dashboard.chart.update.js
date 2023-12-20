function getTranslatedUnit(unit) {
  let ret;
  switch (unit) {
    case "day":
      ret = "일";
      break;
    case "month":
      ret = "월";
      break;
    case "year":
      ret = "년";
      break;
    default:
      ret = "-";
  }
  return ret;
}

function changeChartRadio(radio, chart, para) {
  const radioButtons = document.getElementsByName(radio);

  radioButtons.forEach((radioButton) => {
    radioButton.addEventListener("change", function () {
      if (this.checked) {
        const val = this.value;
        const newPara = {
          ...para,
          x_label: `시간(${getTranslatedUnit(val)})`,
        };
        const chartPara = getParameterForChart(statistics[val], val, newPara);
        chart.updateChart(chartPara);
      }
    });
  });
}
