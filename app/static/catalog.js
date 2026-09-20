"use strict";

const bookSelect = document.getElementById("book-id");
const copyForm = document.getElementById("copy-form");
const copyButton = copyForm.querySelector("button");

function showMessage(feedback, message, error = false) {
  feedback.textContent = message;
  feedback.classList.toggle("error", error);
}

function appendRow(listId, countId, emptyId, id, title, subtitle = "") {
  const list = document.getElementById(listId);
  const row = document.createElement("li");
  const number = document.createElement("span");
  number.className = "book-number";
  number.textContent = `#${id}`;
  const details = document.createElement("div");
  const heading = document.createElement("h3");
  heading.textContent = title;
  details.append(heading);
  if (subtitle) {
    const description = document.createElement("p");
    description.textContent = subtitle;
    details.append(description);
  }
  row.append(number, details);
  list.append(row);
  document.getElementById(emptyId).hidden = true;
  document.getElementById(countId).textContent = list.children.length;
}

function bindForm(formId, feedbackId, onCreated) {
  const form = document.getElementById(formId);
  const button = form.querySelector("button");
  const feedback = document.getElementById(feedbackId);
  const buttonLabel = button.textContent;
  button.disabled = form === copyForm && bookSelect.disabled;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (button.disabled) return;
    const payload = {};
    for (const input of form.querySelectorAll("input, select")) {
      const value = input.value.trim();
      if (!value) {
        showMessage(feedback, "Bitte alle Felder ausfüllen. Leerzeichen allein reichen nicht.", true);
        input.focus();
        return;
      }
      payload[input.name] = input.name === "book_id" ? Number(value) : value;
    }

    const controls = form.querySelectorAll("input, select");
    for (const control of controls) control.disabled = true;
    button.disabled = true;
    button.textContent = "Wird gespeichert …";
    showMessage(feedback, "");
    try {
      const response = await fetch(form.action, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const messages = {
          400: "Bitte die Eingaben prüfen. Texte müssen 1–200 Zeichen enthalten.",
          404: "Das gewählte Buch ist nicht mehr vorhanden. Bitte die Seite neu laden.",
        };
        showMessage(feedback, messages[response.status] || `Speichern fehlgeschlagen (HTTP ${response.status}).`, true);
        return;
      }
      const record = await response.json();
      onCreated(record);
      form.reset();
      showMessage(feedback, "Erfolgreich hinzugefügt.");

    } catch {
      showMessage(feedback, "Keine gültige Antwort erhalten. Lade die Seite neu und prüfe vor einem erneuten Versuch, ob der Eintrag bereits gespeichert wurde.", true);
    } finally {
      for (const control of controls) control.disabled = false;
      form.querySelector("input, select").focus();
      button.disabled = false;
      button.textContent = buttonLabel;
    }
  });
}

bindForm("book-form", "feedback", (book) => {
  appendRow("book-list", "book-count", "empty-state", book.id, book.title, book.author);
  const option = document.createElement("option");
  option.value = book.id;
  option.textContent = `#${book.id} · ${book.title} — ${book.author}`;
  bookSelect.append(option);
  if (bookSelect.options.length === 2) {
    bookSelect.disabled = false;
    copyButton.disabled = false;
  }
  document.getElementById("copy-hint").hidden = true;
});

bindForm("copy-form", "copy-feedback", (copy) => {
  const label = Array.from(bookSelect.options).find((option) => Number(option.value) === copy.book_id).textContent;
  appendRow("copy-list", "copy-count", "copy-empty", copy.id, label, `Buch #${copy.book_id} · Verfügbar`);
});

bindForm("member-form", "member-feedback", (member) => {
  appendRow("member-list", "member-count", "member-empty", member.id, member.name);
});
