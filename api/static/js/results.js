// Update row count
function updateRowCount() {
  const table = document.querySelector("table");
  if (!table) return;

  const rows = Array.from(table.querySelectorAll("tbody tr"));
  const visibleRows = rows.filter((row) => row.style.display !== "none");
  const rowCountElement = document.getElementById("rowCount");

  if (rowCountElement) {
    rowCountElement.textContent = `Exibindo ${visibleRows.length} de ${rows.length} produtos`;
  }
}

// Filter table based on search input
function filterTable() {
  const input = document.getElementById("tableSearch");
  const filter = input.value.toUpperCase();
  const table = document.querySelector("table");

  if (!table) return;

  const rows = table.querySelectorAll("tbody tr");
  let hasVisibleRows = false;

  rows.forEach((row) => {
    const cells = row.querySelectorAll("td");
    let shouldShow = false;

    cells.forEach((cell) => {
      if (cell.textContent.toUpperCase().indexOf(filter) > -1) {
        shouldShow = true;
      }
    });

    if (shouldShow) {
      row.style.display = "";
      hasVisibleRows = true;
    } else {
      row.style.display = "none";
    }
  });

  updateRowCount();
}

// Initialize results page functionality
document.addEventListener("DOMContentLoaded", function () {
  updateRowCount();

  // Add event listener for search input
  const searchInput = document.getElementById("tableSearch");
  if (searchInput) {
    searchInput.addEventListener("input", filterTable);
  }
});

// Expose functions to global scope for HTML inline attributes
window.filterTable = filterTable;
