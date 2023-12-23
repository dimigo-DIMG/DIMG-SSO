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
        item.name.toLowerCase().includes(searchTermLowerCase) ||
        item.description.toLowerCase().includes(searchTermLowerCase)
    );
  }

  return filteredData;
}

// Module for filter, sort, and search
const FilterSortModule = (function () {
  const scriptElement = document.getElementById("listArrange");
  const apiSrc = scriptElement.getAttribute("api-src");

  const container = document.getElementById("item-container");
  const loadingCover = document.getElementById("loading-cover");
  const filterOptions = document.querySelectorAll(".filter-option");
  const sortOptions = document.querySelectorAll(".sort-option");
  const searchInput = document.getElementById("search-input");
  const selectAllCheckbox = document.getElementById("checkboxSelectAll");
  const filteredCount = document.getElementById("cnt-item-filtered");
  let fetchedData = null;

  async function fetchData() {
    try {
      selectAllCheckbox.checked = false;

      // Clear existing items
      container.innerHTML = "";

      // Show loading cover and text
      loadingCover.style.display = "block";

      const response = await fetch(apiSrc);
      if (!response.ok) {
        throw new Error("Network response was not OK");
      }
      const data = await response.json();
      console.log(data);

      // Hide loading cover
      loadingCover.style.display = "none";

      return Array.isArray(data) ? data : [];
    } catch (error) {
      console.error("Fetch error:", error);
      // Hide loading cover
      loadingCover.style.display = "none";
      return [];
    }
  }

  async function applyFilterSortSearchAndRender() {
    const data = fetchedData || (await fetchData());

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