function initialStatDetail() {
  /* 사용자 수 현황 chart */
  const user_para = {
    dataset_info_list: [
      {
        label: "재학생",
        rgb: "198, 131, 215",
        data_key: "enrolled_user_count",
      },
      {
        label: "졸업생",
        rgb: "237, 158, 214",
        data_key: "graduated_user_count",
      },
      { label: "일반", rgb: "255, 199, 199", data_key: "guest_count" },
    ],
    stack_bool: true,
    title: "사용자 수 현황",
    x_label: "시간(일)",
    y_label: "사용자 수(명)",
    type: "bar",
    beginAtZero: false,
  };

  const userChart = new CustomChart("user-stackedBar");
  const chartPara_user = getParameterForChart(statistics.day, "day", user_para);
  userChart.drawChart(chartPara_user);

  /* 로그인 시도 횟수 현황 chart */
  const login_para = {
    dataset_info_list: [
      {
        label: "성공",
        rgb: "75, 181, 67",
        data_key: "login_count",
      },
      {
        label: "실패",
        rgb: "252, 16, 13",
        data_key: "failed_login_count",
      },
    ],
    stack_bool: false,
    title: "일별 로그인 시도 횟수 현황",
    x_label: "시간(일)",
    y_label: "시도 횟수(번)",
    type: "bar",
    beginAtZero: false,
  };

  const loginChart = new CustomChart("login-stackedBar");
  const chartPara_login = getParameterForChart(
    statistics.day, "day", login_para
  );
  loginChart.drawChart(chartPara_login);

  /* 일월년 radio로 chart 변경 */
  changeChartRadio("dmy-user", userChart, user_para);
  changeChartRadio("dmy-login", loginChart, login_para);
}
