// DOM Elements
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const fileList = document.getElementById("fileList");
const submitButton = document.getElementById("submitButton");
const resultsContainer = document.getElementById("results-container");
const fileCount = document.getElementById("fileCount");
const totalSize = document.getElementById("totalSize");
const progressBar = document.getElementById("progress-bar");
const progressBar2 = document.getElementById("progress-bar-2");
const processStep = document.getElementById("process-step");
const processText = document.getElementById("process-text");
const resultsStep = document.getElementById("results-step");
const resultsText = document.getElementById("results-text");

// Utility Functions
function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

function copyTableData() {
  const table = document.querySelector("table");
  if (!table) return;

  const rows = Array.from(table.querySelectorAll("tr"));
  const data = rows
    .map((row) =>
      Array.from(row.querySelectorAll("th,td"))
        .map((cell) => cell.textContent.trim())
        .join("\t")
    )
    .join("\n");

  navigator.clipboard
    .writeText(data)
    .then(() => {
      const copyBtn = document.querySelector(
        "button[onclick='copyTableData()']"
      );
      const originalText = copyBtn.innerHTML;
      copyBtn.innerHTML = '<i class="fas fa-check"></i><span>Copiado!</span>';
      copyBtn.classList.replace("bg-green-600", "bg-green-700");

      setTimeout(() => {
        copyBtn.innerHTML = originalText;
        copyBtn.classList.replace("bg-green-700", "bg-green-600");
      }, 2000);
    })
    .catch((err) => {
      console.error("Erro ao copiar dados:", err);
      alert("Erro ao copiar dados. Por favor, tente novamente.");
    });
}

// Export to CSV
function exportTableToCSV() {
  const table = document.querySelector("table");
  if (!table) return;

  const rows = Array.from(table.querySelectorAll("tr"));
  const csvContent = rows
    .map((row) =>
      Array.from(row.querySelectorAll("th,td"))
        .map((cell) => `"${cell.textContent.trim()}"`)
        .join(",")
    )
    .join("\n");

  const blob = new Blob([csvContent], {
    type: "text/csv;charset=utf-8;",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  const date = new Date().toISOString().split("T")[0];

  link.setAttribute("href", url);
  link.setAttribute("download", `produtos-nota-fiscal-${date}.csv`);
  link.style.visibility = "hidden";

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// File Upload Handling
function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

function highlight(e) {
  dropZone.classList.add("dragover");
}

function unhighlight(e) {
  dropZone.classList.remove("dragover");
}

function handleDrop(e) {
  const dt = e.dataTransfer;
  const files = dt.files;
  handleFiles({ target: { files: files } });
}

function handleFiles(e) {
  const files = [...e.target.files];
  updateFileList(files);
  fileInput.files = e.target.files;
  submitButton.disabled = files.length === 0;

  // Update file count and size
  fileCount.textContent = `${files.length} arquivo${
    files.length !== 1 ? "s" : ""
  } selecionado${files.length !== 1 ? "s" : ""}`;

  const totalBytes = files.reduce((acc, file) => acc + file.size, 0);
  totalSize.textContent = formatFileSize(totalBytes);

  // Update progress bar
  progressBar.style.width = "100%";
}

function updateFileList(files) {
  fileList.innerHTML = files
    .map(
      (file) => `
      <div class="flex items-center space-x-2 text-sm text-gray-600 py-1.5 px-2 rounded hover:bg-gray-50">
        <i class="fas fa-file-pdf text-violet-500"></i>
        <span class="flex-1 truncate" title="${file.name}">${file.name}</span>
        <span class="text-gray-400 text-xs">${formatFileSize(file.size)}</span>
      </div>
    `
    )
    .join("");
}

// Event Listeners
document.addEventListener("DOMContentLoaded", () => {
  // Drag and drop events
  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, preventDefaults, false);
  });

  ["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(eventName, highlight, false);
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, unhighlight, false);
  });

  dropZone.addEventListener("drop", handleDrop, false);
  dropZone.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", handleFiles);

  // HTMX event handlers
  document.body.addEventListener("htmx:beforeRequest", function () {
    document.getElementById("loading").style.display = "flex";

    // Update progress indicators
    processStep.classList.replace("bg-gray-100", "bg-violet-100");
    processStep.classList.replace("text-gray-400", "text-violet-600");
    processText.classList.replace("text-gray-400", "text-gray-700");
    progressBar.style.width = "100%";
    progressBar2.style.width = "50%";
  });

  document.body.addEventListener("htmx:afterRequest", function (event) {
    document.getElementById("loading").style.display = "none";

    // Update progress indicators
    resultsStep.classList.replace("bg-gray-100", "bg-violet-100");
    resultsStep.classList.replace("text-gray-400", "text-violet-600");
    resultsText.classList.replace("text-gray-400", "text-gray-700");
    progressBar2.style.width = "100%";

    // Scroll to results
    const resultsElement = document.getElementById("results-container");
    if (resultsElement) {
      resultsElement.scrollIntoView({ behavior: "smooth" });
    }
  });
});

// Expose functions to global scope for HTML onclick attributes
window.copyTableData = copyTableData;
window.exportTableToCSV = exportTableToCSV;
