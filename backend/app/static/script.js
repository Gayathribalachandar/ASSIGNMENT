let resumeFiles = [];
let structuredFiles = [];

const resumeInput = document.getElementById("resumeInput");
const structuredInput = document.getElementById("structuredInput");

const resumeList = document.getElementById("resumeFileList");
const structuredList = document.getElementById("structuredFileList");

const analyzeButton = document.getElementById("analyzeButton");

const loadingSection = document.getElementById("loadingSection");
const resultSection = document.getElementById("resultSection");

const trustScore = document.getElementById("trustScore");
const trustLabel = document.getElementById("trustLabel");
const progressFill = document.getElementById("progressFill");
const processingTime = document.getElementById("processingTime");

const jsonViewer = document.getElementById("jsonViewer");
const explanationViewer = document.getElementById("explanationViewer");

const copyButton = document.getElementById("copyJson");
const downloadButton = document.getElementById("downloadJson");

let latestResult = null;

/* ------------------------------------------------------- */
/* Resume Upload */
/* ------------------------------------------------------- */

resumeInput.addEventListener("change", () => {

    [...resumeInput.files].forEach(file => {

        if (
            file.type !== "application/pdf"
        ) {
            alert(file.name + " is not a PDF.");
            return;
        }

        const exists = resumeFiles.some(
            f => f.name === file.name &&
                 f.size === file.size
        );

        if (!exists)
            resumeFiles.push(file);

    });

    renderResumeFiles();

});


/* ------------------------------------------------------- */
/* Structured Upload */
/* ------------------------------------------------------- */

structuredInput.addEventListener("change", () => {

    [...structuredInput.files].forEach(file => {

        const valid =
            file.name.endsWith(".csv") ||
            file.name.endsWith(".json");

        if (!valid) {

            alert(file.name + " is not CSV/JSON.");

            return;

        }

        const exists = structuredFiles.some(
            f => f.name === file.name &&
                 f.size === file.size
        );

        if (!exists)
            structuredFiles.push(file);

    });

    renderStructuredFiles();

});


/* ------------------------------------------------------- */
/* Resume List */
/* ------------------------------------------------------- */

function renderResumeFiles() {

    resumeList.innerHTML = "";

    resumeFiles.forEach((file, index) => {

        const li = document.createElement("li");

        li.innerHTML = `
            ${file.name}
            <span class="remove-file" data-index="${index}">
                ✕
            </span>
        `;

        resumeList.appendChild(li);

    });

    document.querySelectorAll("#resumeFileList .remove-file")
        .forEach(btn => {

            btn.onclick = () => {

                resumeFiles.splice(btn.dataset.index, 1);

                renderResumeFiles();

            };

        });

}


/* ------------------------------------------------------- */
/* Structured List */
/* ------------------------------------------------------- */

function renderStructuredFiles() {

    structuredList.innerHTML = "";

    structuredFiles.forEach((file, index) => {

        const li = document.createElement("li");

        li.innerHTML = `
            ${file.name}
            <span class="remove-file" data-index="${index}">
                ✕
            </span>
        `;

        structuredList.appendChild(li);

    });

    document.querySelectorAll("#structuredFileList .remove-file")
        .forEach(btn => {

            btn.onclick = () => {

                structuredFiles.splice(btn.dataset.index, 1);

                renderStructuredFiles();

            };

        });

}


/* ------------------------------------------------------- */
/* Analyze */
/* ------------------------------------------------------- */

/* ------------------------------------------------------- */
/* Analyze */
/* ------------------------------------------------------- */

analyzeButton.addEventListener("click", async () => {

    if (resumeFiles.length !== 1) {
        alert("Please upload exactly one Resume PDF.");
        return;
    }

    if (structuredFiles.length !== 1) {
        alert("Please upload exactly one CSV or ATS JSON.");
        return;
    }

    analyzeButton.disabled = true;

    loadingSection.classList.remove("hidden");
    resultSection.classList.add("hidden");

    const formData = new FormData();

    // Single Resume
    formData.append("resume", resumeFiles[0]);

    // Single Structured File
    formData.append("structured_file", structuredFiles[0]);

    try {

        const response = await fetch("/process", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        console.log("========== BACKEND RESPONSE ==========");
        console.log(result);
        console.log("======================================");

        loadingSection.classList.add("hidden");
        analyzeButton.disabled = false;

        if (!response.ok) {
            alert(result.detail || "Processing Failed");
            return;
        }

        latestResult = result;

        showResult(result);

    }
    catch (err) {

        loadingSection.classList.add("hidden");
        analyzeButton.disabled = false;

        console.error(err);

        alert("Unable to connect to backend.");

    }

});


/* ------------------------------------------------------- */
/* Result */
/* ------------------------------------------------------- */

function showResult(result) {

    resultSection.classList.remove("hidden");

    trustScore.innerHTML = result.trust_score + "%";

    trustLabel.innerHTML = result.trust_level;

    progressFill.style.width = result.trust_score + "%";

    processingTime.innerHTML =
        "Completed in " +
        result.processing_time +
        " sec";

    jsonViewer.textContent =
        JSON.stringify(
            result.candidate,
            null,
            4
        );

    explanationViewer.textContent =
        JSON.stringify(
            result.explanation,
            null,
            4
        );

}


/* ------------------------------------------------------- */
/* Copy */
/* ------------------------------------------------------- */

copyButton.onclick = () => {

    navigator.clipboard.writeText(
        jsonViewer.textContent
    );

    alert("JSON copied.");

};


/* ------------------------------------------------------- */
/* Download */
/* ------------------------------------------------------- */

downloadButton.onclick = () => {

    if (!latestResult)
        return;

    const blob = new Blob(

        [
            JSON.stringify(
                latestResult.candidate,
                null,
                4
            )
        ],

        {
            type: "application/json"
        }

    );

    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");

    a.href = url;

    a.download = "candidate.json";

    document.body.appendChild(a);

    a.click();

    document.body.removeChild(a);

    URL.revokeObjectURL(url);

};


/* ------------------------------------------------------- */
/* Drag & Drop */
/* ------------------------------------------------------- */

setupDropZone(
    "resumeDropZone",
    resumeFiles,
    renderResumeFiles,
    "pdf"
);

setupDropZone(
    "structuredDropZone",
    structuredFiles,
    renderStructuredFiles,
    "structured"
);

function setupDropZone(id, fileArray, render, type) {

    const zone = document.getElementById(id);

    zone.addEventListener("dragover", e => {

        e.preventDefault();

        zone.classList.add("dragover");

    });

    zone.addEventListener("dragleave", () => {

        zone.classList.remove("dragover");

    });

    zone.addEventListener("drop", e => {

        e.preventDefault();

        zone.classList.remove("dragover");

        [...e.dataTransfer.files].forEach(file => {

            let valid = false;

            if (type === "pdf")
                valid = file.name.endsWith(".pdf");

            if (type === "structured")
                valid =
                    file.name.endsWith(".csv") ||
                    file.name.endsWith(".json");

            if (!valid)
                return;

            const exists = fileArray.some(
                f =>
                    f.name === file.name &&
                    f.size === file.size
            );

            if (!exists)
                fileArray.push(file);

        });

        render();

    });

}