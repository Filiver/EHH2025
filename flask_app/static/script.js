"use strict";

const ANALYTES = ["egfr", "pu", "upcr", "uacr", "s_kreatinin"];
const SHOWN_KEYS = ["dob", "age"];

// For presentation only
const IDS = [840, 148090, 587590, 174540, 6680, 12330];

/*
dob
age
egfr (date, value+unit)
average egfr
uacr
average uacr
pu
average pu
upcr
average upcr
s_kreatinin

last_nefrology_visit / not in_neforlogy_care
*/

const NUM2ALPH = {
  1: "A",
  2: "B",
  3: "C",
};

const KVContainer = document.querySelector("#kv-container");
const GFRTable = document.querySelector("#GFR-table");
const alertContainer = document.querySelector("#alert-container");
const patientNum = document.querySelector("#Patient-num");
const patientSelect = document.querySelector("#patient-select");
const kvHTML = (k, v) => `
<ul class="list-group list-group-horizontal">
            <li class="list-group-item flex-fil text-center w-50">${k}</li>
            <li class="list-group-item flex-fill text-center w-50">${v}</li>
          </ul>
`;

const alertHTML = (msg) => `
<div class="alert alert-danger" role="alert">
          ${msg}
        </div>`;

const patientSelectHTML = (patientID) => `
<option value="${patientID}">Patient ${patientID}</option>`;

function handleNull(value) {
  let new_val = value === null || value === undefined ? "N/A" : value;
  return new_val;
}

function extractAnalyte(data, analyte) {
  const analyteUnit = handleNull(data[analyte + "_unit"]);
  const analyteValue = handleNull(data[analyte]);
  const analyteDate = handleNull(data[analyte + "_date"]);
  const analyteAverage = handleNull(data["average_" + analyte]);
  return {
    analyte,
    analyteUnit,
    analyteValue,
    analyteDate,
    analyteAverage,
  };
}

// const fetchedData = showMessage();
document.addEventListener("DOMContentLoaded", () => {
  patientSelect.innerHTML = "";

  patientSelect.addEventListener("change", (e) => {
    loadPatient(e.target.value);
  });

  IDS.forEach((id) => {
    patientSelect.insertAdjacentHTML("beforeend", patientSelectHTML(id));
    console.log(id);
  });
  // patientSelect.addEventListener("change", (e) => {
  //   loadPatient(e.target.value);
  // });

  loadPatient(IDS[0]);
});

function markColumn(table, columnAlphabet) {
  for (let i = 1; i < 7; i++) {
    const id = `${columnAlphabet}${i}`;
    const cell = table.querySelector(`#${id}`);
    cell.classList.add("active-cell");
  }
}

function markRow(table, rowNumber) {
  for (let i = 1; i <= 3; i++) {
    const id = `${NUM2ALPH[i]}${rowNumber}`;
    const cell = table.querySelector(`#${id}`);
    cell.classList.add("active-cell");
  }
}

function markCell(table, rowNumber, columnAlphabet) {
  const id = `${rowNumber}${columnAlphabet}`;
  const cell = table.querySelector(`#${id}`);
  cell.classList.add("active-cell");
}

function formatAnalyte(analyte) {
  return {
    key: `${analyte.analyte} (${analyte.analyteDate})`,
    value: `${analyte.analyteValue} ${analyte.analyteUnit}`,
    keyAverage: `Average ${analyte.analyte}`,
    valueAverage: `${analyte.analyteAverage} ${analyte.analyteUnit}`,
  };
}

function markGFR(uacr_cat, gfr_cat) {
  if (uacr_cat == null && gfr_cat == null) {
    return;
  } else if (uacr_cat == null) {
    markRow(GFRTable, gfr_cat);
  } else if (gfr_cat == null) {
    markColumn(GFRTable, NUM2ALPH[uacr_cat]);
  } else {
    markCell(GFRTable, NUM2ALPH[uacr_cat], gfr_cat);
  }
}

async function loadPatient(patient_id) {
  clear();
  // markColumn(GFRTable, "C");
  const data = await getData(patient_id);
  console.log(data);

  if (data["error"]) {
    alert("Error fetching data");
    return;
  }
  markGFR(data["uacr_category"], data["gfr_category"]);

  if (data["in_nefrology_care"]) {
    KVContainer.insertAdjacentHTML(
      "beforeend",
      kvHTML("Last Nefrology Visit", data["last_nefrology_visit"])
    );
  }

  SHOWN_KEYS.forEach((key) => {
    const value = handleNull(data[key]);
    KVContainer.insertAdjacentHTML("beforeend", kvHTML(key, value));
  });
  ANALYTES.forEach((analyte) => {
    const extracted = extractAnalyte(data, analyte);
    const formatted = formatAnalyte(extracted);
    KVContainer.insertAdjacentHTML(
      "beforeend",
      kvHTML(formatted.key, parseFloat(formatted.value).toFixed(3))
    );
    KVContainer.insertAdjacentHTML(
      "beforeend",
      kvHTML(
        formatted.keyAverage,
        parseFloat(formatted.valueAverage).toFixed(3)
      )
    );
  });
  patientNum.innerHTML = `Patient: ${data.patient_id}`;
  data["alerts"].forEach((alert) => {
    alertContainer.insertAdjacentHTML("beforeend", alertHTML(alert));
  });
}

function clear() {
  KVContainer.innerHTML = "";
  GFRTable.querySelectorAll("tr").forEach((tr, i) => {
    tr.querySelectorAll("td").forEach((td, j) => {
      td.classList.remove("active-cell");
    });
  });
  alertContainer.innerHTML = "";
  patientNum.innerHTML = "Patient: ";
}

async function getData(patient_id) {
  const data = await fetch(`/api/data/${patient_id}`);
  const jsonData = await data.json();
  return jsonData;
}
