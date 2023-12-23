function applyFilterSortSearch(
  data,
  filterOption,
  sortOption,
  searchTerm
) {
  let filteredData = [...data]; // Convert data to an array

  // Filter based on filterOption
  if (filterOption === "official") {
    filteredData = filteredData.filter((item) => item.is_official);
  } else if (filterOption === "unofficial") {
    filteredData = filteredData.filter((item) => !item.is_official);
  } else if (filterOption === "enrolled") {
    filteredData = filteredData.filter((item) => item.tag === "enrol");
  } else if (filterOption === "graduated") {
    filteredData = filteredData.filter((item) => item.tag === "grad");
  } else if (filterOption === "guest") {
    filteredData = filteredData.filter((item) => item.tag === "guest");
  }

  // Sort based on sortOption
  if (sortOption === "join_date_asc") {
    filteredData.sort(
      (a, b) => new Date(a.join_date) - new Date(b.join_date)
    );
  } else if (sortOption === "join_date_desc") {
    filteredData.sort(
      (a, b) => new Date(b.join_date) - new Date(a.join_date)
    );
  } else if (sortOption === "name_asc") {
    filteredData.sort((a, b) => a.name.localeCompare(b.name));
  } else if (sortOption === "name_desc") {
    filteredData.sort((a, b) => b.name.localeCompare(a.name));
  }

  // Search based on searchTerm
  if (searchTerm) {
    const searchTermLowerCase = searchTerm.toLowerCase();
    filteredData = filteredData.filter(
      (item) =>
        (item.name && item.name.toLowerCase().includes(searchTermLowerCase)) ||
        (item.description && item.description.toLowerCase().includes(searchTermLowerCase))
    );
  }

  return filteredData;
}

// Module for filter, sort, and search
const FilterSortModule = (function () {
  const userEmailFromURL = window.location.pathname
    .split("/")
    .filter(Boolean)
    .pop();

  const scriptElement = document.getElementById("listArrange");
  const apiSrc = scriptElement.getAttribute("api-src");

  const container = document.getElementById("item-container");
  const loadingCover = document.getElementById("loading-cover");
  const filterOptions = document.querySelectorAll(".filter-option");
  const sortOptions = document.querySelectorAll(".sort-option");
  const searchInput = document.getElementById("search-input");
  const selectAllCheckbox = document.getElementById("checkboxSelectAll");
  const filteredCount = document.getElementById("cnt-item-filtered");
  let fetchedDataPromise = null;

  async function fetchData() {
    if (!fetchedDataPromise) {
      fetchedDataPromise = new Promise(async (resolve, reject) => {
        try {
          selectAllCheckbox.checked = false;

          // Clear existing items
          container.innerHTML = "";

          // Show loading cover and text
          loadingCover.style.display = "block";

          let apiSrcRes = apiSrc;
          const match = apiSrc.match(/\{([^}]+)\}/);
          if (match){
            const parameterName = match[1];
            if (parameterName === "email"){
              apiSrcRes = apiSrc.replace("{email}", userEmailFromURL);
            }
          }

          const response = await fetch(apiSrcRes);
          if (!response.ok) {
            throw new Error("Network response was not OK");
          }
          const data = await response.json();

          // Hide loading cover
          loadingCover.style.display = "none";

          resolve(Array.isArray(data) ? data : []);
        } catch (error) {
          console.error("Fetch error:", error);
          // Hide loading cover
          loadingCover.style.display = "none";
          reject(error);
        }
      });
    }
    return fetchedDataPromise;
  }

  async function applyFilterSortSearchAndRender() {
    const data = await fetchData();

    const filterOption = document.querySelector(".filter-option.active")
      .dataset.option;
    const sortOption = document.querySelector(".sort-option.active")
      .dataset.option;
    const searchTerm = searchInput.value;

    const filteredSortedSearchData = applyFilterSortSearch(
      data,
      filterOption,
      sortOption,
      searchTerm
    );

    // Update the filtered nodes
    appendFilteredNodes(filterOption, filteredSortedSearchData.length);

    // Clear existing items
    container.innerHTML = "";

    // Append the updated items to the container
    for (let i = 0; i < filteredSortedSearchData.length; i++) {
      const containerItem = getList2DOM(filteredSortedSearchData[i]);
      container.appendChild(containerItem);
    }
  }

  function updateDropdownItemClass(dropdownItems, selectedOption) {
    dropdownItems.forEach((option) => option.classList.remove("active"));
    selectedOption.classList.add("active");
  }

  function updateCheckboxes(checked) {
    const checkboxes = document.querySelectorAll(".form-check-input");
    checkboxes.forEach((checkbox) => (checkbox.checked = checked));
  }

  function appendFilteredNodes(filterOption, count) {
    // Clear existing content
    filteredCount.innerHTML = "";

    // Append nodes based on filterOption
    if (filterOption === "all") {
      // Append "전체" text node
      const allTextNode = document.createTextNode("전체");
      filteredCount.appendChild(allTextNode);
    } else if (filterOption === "official") {
      // Append nodes for "official" filter
      const allTextNode = document.createTextNode("공식");
      filteredCount.appendChild(allTextNode);
    } else if (filterOption === "unofficial") {
      // Append nodes for "unofficial" filter
      const allTextNode = document.createTextNode("비공식");
      filteredCount.appendChild(allTextNode);
    } else if (filterOption === "enrolled") {
      // Append nodes for "enrolled" filter
      const allTextNode = document.createTextNode("재학생");
      filteredCount.appendChild(allTextNode);
    } else if (filterOption === "graduated") {
      // Append nodes for "graduated" filter
      const allTextNode = document.createTextNode("졸업생");
      filteredCount.appendChild(allTextNode);
    } else if (filterOption === "guest") {
      // Append nodes for "guest" filter
      const allTextNode = document.createTextNode("일반");
      filteredCount.appendChild(allTextNode);
    }

    // Append span tag with the count
    const countSpan = document.createElement("span");
    countSpan.textContent = count;
    filteredCount.append(" ", countSpan);
  }

  function init() {
    filterOptions.forEach((option) =>
      option.addEventListener("click", function () {
        updateDropdownItemClass(filterOptions, this);
        applyFilterSortSearchAndRender();
      })
    );

    sortOptions.forEach((option) =>
      option.addEventListener("click", function () {
        updateDropdownItemClass(sortOptions, this);
        applyFilterSortSearchAndRender();
      })
    );

    searchInput.addEventListener("input", applyFilterSortSearchAndRender);

    selectAllCheckbox.addEventListener("change", function () {
      updateCheckboxes(this.checked);
    });

    // Initial fetch and render
    applyFilterSortSearchAndRender();
  }

  // Expose only necessary methods/properties
  return {
    init: init,
  };
})();

// Initialize the module
FilterSortModule.init();