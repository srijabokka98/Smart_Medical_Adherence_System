const quotes = [
    "Your health is your wealth.",
    "Every dose brings you closer to recovery.",
    "Small habits build strong health.",
    "Consistency is key to wellness.",
    "Take care of yourself, you're worth it!"
];

const quoteElem = document.getElementById("quote");
quoteElem.textContent = quotes[Math.floor(Math.random() * quotes.length)];