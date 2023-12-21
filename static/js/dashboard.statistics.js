// Initialize an object to store statistics
const statistics = {
  day: [],
  month: [],
  year: [],
};

// Function to check and add dictionary for month
function checkAndAddMonthDictionary(year, month) {
  const existingMonth = statistics.month.find(
    (item) => item.date === `${year}-${month}`
  );
  if (!existingMonth) {
    statistics.month.push({
      date: `${year}-${month}`,
      count: 0,
      enrolled_user_count: 0,
      graduated_user_count: 0,
      guest_count: 0,
      login_count: 0,
      failed_login_count: 0,
    });
  }
}

// Function to check and add dictionary for year
function checkAndAddYearDictionary(year) {
  const existingYear = statistics.year.find((item) => item.date === year);
  if (!existingYear) {
    statistics.year.push({
      date: year,
      count: 0,
      enrolled_user_count: 0,
      graduated_user_count: 0,
      guest_count: 0,
      login_count: 0,
      failed_login_count: 0,
    });
  }
}

function initialStatData(stat) {
  // Statistical calculation
  stat.forEach((data) => {
    const date = data.date;
    const year = date.split("-")[0];
    const month = date.split("-")[1];
    const day = date.split("-")[2];

    // by date
    statistics.day.push({
      date: `${month}-${day}`,
      enrolled_user_count: data.enrolled_user_count,
      graduated_user_count: data.graduated_user_count,
      guest_count:
        data.user_count -
        (data.enrolled_user_count + data.graduated_user_count),
      login_count: data.login_count,
      failed_login_count: data.failed_login_count,
    });

    // by month
    checkAndAddMonthDictionary(year, month);
    const monthIndex = statistics.month.findIndex(
      (item) => item.date === `${year}-${month}`
    );
    // Update count and total for each statistic
    statistics.month[monthIndex].count += 1;

    statistics.month[monthIndex].enrolled_user_count +=
      data.enrolled_user_count;
    statistics.month[monthIndex].graduated_user_count +=
      data.graduated_user_count;
    statistics.month[monthIndex].guest_count +=
      data.user_count - (data.enrolled_user_count + data.graduated_user_count),
    statistics.month[monthIndex].login_count +=
      data.login_count;
    statistics.month[monthIndex].failed_login_count +=
      data.failed_login_count;
    
    // by year
    checkAndAddYearDictionary(year);
    const yearIndex = statistics.year.findIndex((item) => item.date === year);
    // Update count and total for each statistic
    statistics.year[yearIndex].count += 1;

    statistics.year[yearIndex].enrolled_user_count +=
      data.enrolled_user_count;
    statistics.year[yearIndex].graduated_user_count +=
      data.graduated_user_count;
    statistics.year[yearIndex].guest_count +=
      data.user_count - (data.enrolled_user_count + data.graduated_user_count),
    statistics.year[yearIndex].login_count +=
      data.login_count;
    statistics.year[yearIndex].failed_login_count +=
      data.failed_login_count;

  });

  // Calculate mean for each statistic
  statistics.month.forEach((monthData) => {
    monthData.enrolled_user_count = monthData.enrolled_user_count / monthData.count;
    monthData.graduated_user_count = monthData.graduated_user_count / monthData.count;
    monthData.guest_count = monthData.guest_count / monthData.count;
  });

  statistics.year.forEach((yearData) => {
    yearData.enrolled_user_count = yearData.enrolled_user_count / yearData.count;
    yearData.graduated_user_count = yearData.graduated_user_count / yearData.count;
    yearData.guest_count = yearData.guest_count / yearData.count;
  });
}

console.log(statistics)