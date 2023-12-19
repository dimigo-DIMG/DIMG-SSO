function changeChartRadio(radio) {
  const radioButtons = document.getElementsByName(radio);

  radioButtons.forEach((radioButton) => {
    radioButton.addEventListener('change', function () {
      if (this.checked) {
        const selectedValue = this.value;
        // console.log(selectedValue);
      }
    });
  });
}
