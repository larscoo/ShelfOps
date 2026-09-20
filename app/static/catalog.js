"use strict";

const form = document.getElementById("book-form");
const button = document.getElementById("save-button");
const feedback = document.getElementById("feedback");
const list = document.getElementById("book-list");
const titleInput = document.getElementById("title");
const authorInput = document.getElementById("author");
button.disabled = false;

function showMessage(message, error = false) {
  feedback.textContent = message;
  feedback.classList.toggle("error", error);
}

function appendBook(book) {
  const row = document.createElement("li");
  const number = document.createElement("span");
  number.className = "book-number";
  number.textContent = `#${book.id}`;
  const details = document.createElement("div");
  const title = document.createElement("h3");
  const author = document.createElement("p");
  title.textContent = book.title;
  author.textContent = book.author;
  details.append(title, author);
  row.append(number, details);
  list.append(row);
  document.getElementById("empty-state").hidden = true;
  document.getElementById("book-count").textContent = list.children.length;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (button.disabled) return;

  const title = titleInput.value.trim();
  const author = authorInput.value.trim();
  if (!title || !author) {
    showMessage("Bitte Titel und Autor ausfüllen. Leerzeichen allein reichen nicht.", true);
    (!title ? titleInput : authorInput).focus();
    return;
  }

  button.disabled = true;
  button.textContent = "Wird gespeichert …";
  showMessage("");
  try {
    const response = await fetch(form.action, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, author }),
    });
    if (!response.ok) {
      showMessage(
        response.status === 400
          ? "Bitte die Eingaben prüfen: Titel und Autor dürfen je 1–200 Zeichen enthalten."
          : `Speichern fehlgeschlagen (HTTP ${response.status}). Bitte später erneut versuchen.`,
        true,
      );
      return;
    }
    const book = await response.json();
    appendBook(book);
    form.reset();
    showMessage(`„${book.title}“ wurde hinzugefügt.`);
    titleInput.focus();
  } catch {
    showMessage(
      "Keine gültige Antwort erhalten. Lade die Seite neu und prüfe vor einem erneuten Versuch, ob das Buch bereits gespeichert wurde.",
      true,
    );
  } finally {
    button.disabled = false;
    button.textContent = "Buch hinzufügen";
  }
});
