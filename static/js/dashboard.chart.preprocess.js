function getDataset(label, bgColor, data) {
  return {
    label,
    backgroundColor: `rgba(${bgColor}, 0.5)`,
    data,
  };
}

function getParameterForChart(data, unit, para) {
  // data: List
  // unit: "day" | "month" | "year"
  // para: as below
  const {
    dataset_info_list,
    stack_bool,
    title,
    x_label,
    y_label,
    type,
    beginAtZero,
  } = para;
  // dataset_info_list: [{label, rgb, data_key}, {}, {}]
  // stack_bool: Boolean
  // title: String
  // x_label: String
  // y_label: String
  // type: String
  // beginAtZero: boolean

  const label_list = [];
  const dataset_list = [];
  const stat_list = [];

  for (let i = 0; i < data.length; i++) {
    const date = data[i]["date"];
    /* label_list */
    if (unit === "year") {
      // year
      label_list.push(date);
    } else {
      // month, day
      if (i === 0 || date.split("-")[1] == 1) {
        label_list.push(`${date.split("-")[0]}/${date.split("-")[1]}`);
      } else {
        label_list.push(`${date.split("-")[1]}`);
      }
    }

    /* stat_list */
    for (let j = 0; j < dataset_info_list.length; j++) {
      stat_list[j] = stat_list[j] || [];
      
      const item = data[i][dataset_info_list[j]["data_key"]] || 0;
      stat_list[j].push(item);
    }
  }

  /* dataset_list */
  for (let i = 0; i < dataset_info_list.length; i++) {
    dataset_list.push(
      getDataset(
        dataset_info_list[i]["label"],
        dataset_info_list[i]["rgb"],
        stat_list[i]
      )
    );
  }

  return {
    label_list,
    dataset_list,
    stack_bool,
    title,
    x_label,
    y_label,
    type,
    beginAtZero,
  };
}