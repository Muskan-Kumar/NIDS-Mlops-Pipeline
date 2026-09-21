const fileInput=document.getElementById("fileInput");
const browseBtn=document.getElementById("browseBtn");
const dropZone=document.getElementById("dropZone");
const selectedFile=document.getElementById("selectedFile");
const fileName=document.getElementById("fileName");
const fileSize=document.getElementById("fileSize");
const removeFile=document.getElementById("removeFile");
const analyzeBtn=document.getElementById("analyzeBtn");
const uploadError=document.getElementById("uploadError");
const resultsContainer=document.getElementById("resultsContainer");
const emptyState=document.getElementById("emptyState");
const predictionTable=document.getElementById("predictionTable");
const clearResults=document.getElementById("clearResults");
const apiStatus=document.getElementById("apiStatus");
const apiCardStatus=document.getElementById("apiCardStatus");
const toast=document.getElementById("toast");
const toastMessage=document.getElementById("toastMessage");

let selectedCsv=null;

browseBtn.addEventListener("click",function(e){
    e.stopPropagation();
    fileInput.click();
});

dropZone.addEventListener("click",function(){
    fileInput.click();
});

fileInput.addEventListener("change",function(){
    if(this.files.length>0){
        handleFile(this.files[0]);
    }
});

["dragenter","dragover"].forEach(eventName=>{
    dropZone.addEventListener(eventName,function(e){
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add("dragover");
    });
});

["dragleave","drop"].forEach(eventName=>{
    dropZone.addEventListener(eventName,function(e){
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove("dragover");
    });
});

dropZone.addEventListener("drop",function(e){
    const files=e.dataTransfer.files;
    if(files.length>0){
        handleFile(files[0]);
    }
});

removeFile.addEventListener("click",function(){
    resetFile();
});

function handleFile(file){
    uploadError.textContent="";

    if(!file.name.toLowerCase().endsWith(".csv")){
        showError("Please select a CSV file.");
        return;
    }

    selectedCsv=file;

    fileName.textContent=file.name;
    fileSize.textContent=formatFileSize(file.size);

    selectedFile.classList.add("show");
    analyzeBtn.disabled=false;

    showToast("CSV file selected successfully");
}

function resetFile(){
    selectedCsv=null;
    fileInput.value="";
    selectedFile.classList.remove("show");
    analyzeBtn.disabled=true;
    uploadError.textContent="";
}

function formatFileSize(bytes){
    if(bytes===0) return "0 Bytes";

    const units=["Bytes","KB","MB","GB"];
    const index=Math.floor(Math.log(bytes)/Math.log(1024));

    return `${(bytes/Math.pow(1024,index)).toFixed(index===0?0:2)} ${units[index]}`;
}

function showError(message){
    uploadError.textContent=message;
    showToast(message);
}

function showToast(message){
    toastMessage.textContent=message;
    toast.classList.add("show");

    setTimeout(()=>{
        toast.classList.remove("show");
    },3000);
}

analyzeBtn.addEventListener("click",async function(){

    if(!selectedCsv){
        showError("Please select a CSV file first.");
        return;
    }

    analyzeBtn.classList.add("loading");
    analyzeBtn.disabled=true;
    uploadError.textContent="";

    const formData=new FormData();
    formData.append("file",selectedCsv);

    try{

        const response=await fetch("/predict",{
            method:"POST",
            body:formData
        });

        if(!response.ok){
            throw new Error(`Prediction failed (${response.status})`);
        }

        const html=await response.text();

        processPredictionResponse(html);

        showToast("Network traffic analysis completed");

    }catch(error){

        console.error(error);

        showError(
            "Unable to analyze the file. Make sure FastAPI and the ML model are running."
        );

    }finally{

        analyzeBtn.classList.remove("loading");
        analyzeBtn.disabled=false;
    }
});

function processPredictionResponse(html){

    const parser=new DOMParser();
    const documentData=parser.parseFromString(html,"text/html");

    const table=documentData.querySelector("table");

    if(!table){
        throw new Error("Prediction table was not returned by the API.");
    }

    predictionTable.innerHTML="";
    predictionTable.appendChild(table);

    analyzeTable(table);

    emptyState.style.display="none";
    resultsContainer.style.display="block";

    document.getElementById("results").scrollIntoView({
        behavior:"smooth",
        block:"start"
    });
}

function analyzeTable(table){

    const rows=[...table.querySelectorAll("tbody tr")];

    let total=rows.length;
    let benign=0;
    let threats=0;

    rows.forEach(row=>{

        const cells=[...row.querySelectorAll("td")];

        if(cells.length===0){
            return;
        }

        const prediction=cells[cells.length-1].textContent.trim().toLowerCase();

        if(prediction==="benign"){
            benign++;
        }else{
            threats++;
        }
    });

    document.getElementById("totalRecords").textContent=total.toLocaleString();
    document.getElementById("benignCount").textContent=benign.toLocaleString();
    document.getElementById("threatCount").textContent=threats.toLocaleString();

    const resultTitle=document.getElementById("resultTitle");
    const resultDescription=document.getElementById("resultDescription");
    const resultBadge=document.getElementById("resultBadge");
    const overallResult=document.getElementById("overallResult");
    const resultSymbol=overallResult.querySelector(".result-symbol");

    if(threats>0){

        resultTitle.textContent="Threats Detected";
        resultDescription.textContent=
            `${threats.toLocaleString()} suspicious network record(s) detected.`;

        resultBadge.textContent="THREAT DETECTED";

        resultBadge.style.color="var(--danger)";
        resultBadge.style.background="rgba(255,93,108,.08)";
        resultBadge.style.borderColor="rgba(255,93,108,.2)";

        resultSymbol.textContent="!";
        resultSymbol.style.color="var(--danger)";
        resultSymbol.style.background="rgba(255,93,108,.08)";

    }else{

        resultTitle.textContent="Traffic Appears Benign";
        resultDescription.textContent=
            "No malicious traffic was detected in the analyzed records.";

        resultBadge.textContent="NO THREATS";

        resultBadge.style.color="var(--primary)";
        resultBadge.style.background="rgba(53,211,154,.07)";
        resultBadge.style.borderColor="rgba(53,211,154,.2)";

        resultSymbol.textContent="✓";
        resultSymbol.style.color="var(--primary)";
        resultSymbol.style.background="rgba(53,211,154,.09)";
    }
}

clearResults.addEventListener("click",function(){

    predictionTable.innerHTML="";
    resultsContainer.style.display="none";
    emptyState.style.display="flex";

    document.getElementById("totalRecords").textContent="0";
    document.getElementById("benignCount").textContent="0";
    document.getElementById("threatCount").textContent="0";

    showToast("Results cleared");
});

async function checkApi(){

    try{

        const response=await fetch("/docs",{
            method:"GET"
        });

        if(response.ok){

            apiStatus.innerHTML=
                '<span class="status-dot"></span><span>API Connected</span>';

            apiCardStatus.textContent="Online";

        }else{

            setApiOffline();
        }

    }catch(error){

        setApiOffline();
    }
}

function setApiOffline(){

    apiStatus.innerHTML=
        '<span class="status-dot" style="background:var(--danger);box-shadow:0 0 12px rgba(255,93,108,.7)"></span><span>API Offline</span>';

    apiCardStatus.textContent="Offline";
}

checkApi();
