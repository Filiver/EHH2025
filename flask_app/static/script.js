"use strict";

async function showMessage() {
  const data = await fetch("/api/data");
  const jsonData = await data.json();
  console.log(jsonData);
}
