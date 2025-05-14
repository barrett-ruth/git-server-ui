const TERMINAL_PROMPT = "git@git.barrettruth.com:~$ ";
let clearing = false;

class SiteHeader extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <header>
        <a href="/" style="text-decoration: none; color: inherit">
          <div class="terminal-container">
            <span class="terminal-prompt">${TERMINAL_PROMPT}</span>
            <span class="terminal-cursor"></span>
          </div>
        </a>
        <div class="header-links">
          <a target="_blank" href="https://barrettruth.com">website</a>
        </div>
      </header>
    `;
  }
}

class SiteFooter extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <footer>
        <span class="greek-delta">&Delta;</span>
        <div class="footer-links">
          <a target="_blank" href="mailto:br.barrettruth@gmail.com">email</a>
        </div>
      </footer>
    `;
  }
}

customElements.define("site-header", SiteHeader);
customElements.define("site-footer", SiteFooter);

document.addEventListener("DOMContentLoaded", function () {
  if (!document.querySelector("style#dynamic-styles")) {
    const style = document.createElement("style");
    style.id = "dynamic-styles";
    style.innerHTML = `
      footer {
        padding: 20px;
        font-size: 1.5em;
        display: flex;
        align-items: center;
        justify-content: space-between;
      }

      .greek-delta {
        font-family: "Times New Roman", Times, serif;
        font-size: 1.5em;
      }

      .header-links a,
      .footer-links a {
        margin-left: 25px;
        text-decoration: none;
      }
    `;
    document.head.appendChild(style);
  }
});

function clearPrompt(delay, callback) {
  if (clearing) return;
  clearing = true;

  const terminalPrompt = document.querySelector(".terminal-prompt");
  const topicLength = terminalPrompt.innerHTML.length - TERMINAL_PROMPT.length;
  let i = 0;

  function removeChar() {
    if (i++ < topicLength) {
      terminalPrompt.textContent = terminalPrompt.textContent.slice(0, -1);
      setTimeout(removeChar, delay / topicLength);
    } else {
      i = 0;
      terminalPrompt.innerHTML = TERMINAL_PROMPT;
      clearing = false;
      callback && callback();
    }
  }

  removeChar();
}
