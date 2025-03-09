"use strict";

// const fetchedData = showMessage();
document.addEventListener("DOMContentLoaded", async () => {});

async function showMessage() {
  const data = await fetch("/api/data");
  const jsonData = await data.json();
  return jsonData;
}
