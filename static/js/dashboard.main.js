fetch("/api/dashboard")
  .then((res) => {
    if (!res.ok) {
      throw new Error(`HTTP error! Status: ${res.status}`);
    }
    return res.json();
  })
  .then((stat) => {
    initialStatData(stat);
    initialStatOverall(stat);
    initialStatDetail();
  })
  .catch((err) => {
    console.error("Fetch error:", err);
  });
