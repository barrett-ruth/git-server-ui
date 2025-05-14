let typing = false;

window.typechars = function (e) {
  e.preventDefault();

  if (e.target.classList.contains("active")) return;
  if (typing) return;
  typing = true;

  const topics = document.querySelectorAll(".topic a");
  topics.forEach((t) => {
    t.classList.remove("active");
    t.style.color = "";
  });

  e.target.classList.add("active");

  const repoName = e.target.textContent;
  const terminalText = ` /${repoName}`;
  const terminalPrompt = document.querySelector(".terminal-prompt");
  const delay = 250;

  clearPrompt(delay, () => {
    let i = 0;
    function typechar() {
      if (i < terminalText.length) {
        terminalPrompt.innerHTML += terminalText.charAt(i++);
        setTimeout(typechar, delay / terminalText.length);
      } else {
        renderRepoDescription(e.target);
        typing = false;
      }
    }

    typechar();
  });
};

function renderRepoDescription(repoLink) {
  const postsContainer = document.getElementById("repos");
  const repoId = repoLink.getAttribute("data-repo-id");
  let repoName = repoLink.textContent;
  if (repoName.toLowerCase().endsWith('.git')) {
    repoName = repoName.slice(0, -4);
  }

  postsContainer.innerHTML = "";

  fetch(`/api/repo/${repoId}`)
    .then((response) => response.json())
    .then((repo) => {
      const post = document.createElement("div");
      post.classList.add("post");

      const descriptionText = document.createElement("div");
      descriptionText.textContent =
        repo.description || "No description available";
      descriptionText.style.textDecoration = "none";

      post.appendChild(descriptionText);

      const cloneUrl = document.createElement("div");
      cloneUrl.style.marginTop = "15px";
      cloneUrl.innerHTML = `<code>git clone \nhttps://git.barrettruth.com/git/${repoName}</code>`;

      post.appendChild(cloneUrl);
      const viewNote = document.createElement("div");
      viewNote.style.marginTop = "15px";
      viewNote.style.fontSize = "0.8em";
      viewNote.style.fontStyle = "italic";
      viewNote.textContent = "Code should not be viewed in a browser.";
      post.appendChild(viewNote);

      postsContainer.appendChild(post);
    })
    .catch((error) => {
      console.error("Error fetching repo data:", error);
      const errorElement = document.createElement("div");
      errorElement.classList.add("post");
      errorElement.textContent = "Error loading repository information";
      postsContainer.appendChild(errorElement);
    });
}
