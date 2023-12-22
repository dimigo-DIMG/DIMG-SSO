async function fetchUserServicesDataFromAPI(){
  const res = await fetch("/api/services");
  if (!res.ok) {
    throw new Error("Network response was not OK");
  }
  return await res.json();
}

/**
 * Applies filtering, sorting, and searching to a given array of data.
 *
 * @param {Array} data - The array of data to be processed.
 * @param {string} filterOption - The filtering option to determine how to filter the data.
 * @param {string} sortOption - The sorting option to determine how to sort the data.
 * @param {string} searchTerm - The search term to filter data based on name and description.
 * @param {Array} customValues - An optional array of custom values for specific filtering scenarios.
 * @returns {Array} - The processed data array after applying filtering, sorting, and searching.
 */
function applyFilterSortSearch(
  data,
  filterOption,
  sortOption,
  searchTerm,
  customValues = []
) {
  let filteredData = data;

  // Apply filtering based on the specified filterOption
  if (filterOption === "all") {
    filteredData = data;
  } else if (filterOption === "customValues") {
    filteredData = data.filter((item) => customValues.includes(item.status));
  } else if (filterOption === "official") {
    // Treat is_official as a boolean
    filteredData = data.filter((item) => item.is_official);
  } else if (filterOption === "unofficial") {
    // Treat is_official as a boolean
    filteredData = data.filter((item) => !item.is_official);
  } else {
    // Treat is_official as a string
    filteredData = data.filter((item) => item.is_official === filterOption);
  }

  // Apply sorting based on the specified sortOption
  if (sortOption === "join_date_asc") {
    filteredData.sort((a, b) => new Date(a.join_date) - new Date(b.join_date));
  } else if (sortOption === "join_date_desc") {
    filteredData.sort((a, b) => new Date(b.join_date) - new Date(a.join_date));
  } else if (sortOption === "name_asc") {
    filteredData.sort((a, b) => a.name.localeCompare(b.name));
  } else if (sortOption === "name_desc") {
    filteredData.sort((a, b) => b.name.localeCompare(a.name));
  }

  // Apply searching based on the specified searchTerm
  if (searchTerm) {
    const searchStr = searchTerm.toLowerCase();
    filteredData = filteredData.filter(
      (item) =>
        item.name.toLowerCase().includes(searchStr) ||
        item.description.toLowerCase().includes(searchStr)
    );
  }

  return filteredData; // Return the processed data after filtering, sorting, and searching
}

/**
 * Toggles the state of all checkboxes with the class "generated-checkbox"
 * based on the checked state of the "checkboxSelectAll" checkbox.
 *
 * This function is typically used in scenarios where there is a master checkbox
 * that can check or uncheck all other checkboxes at once.
 */
function toggleSelectAll() {
  // Retrieve all checkboxes with the class "generated-checkbox"
  const checkboxes = document.querySelectorAll(".generated-checkbox");

  // Iterate over each checkbox and set its checked state based on "checkboxSelectAll"
  checkboxes.forEach((checkbox) => {
    checkbox.checked = checkboxSelectAll.checked;
  });
}