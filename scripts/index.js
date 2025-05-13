// Don't redeclare TERMINAL_PROMPT since it's already in common.js
let typing = false;

window.typechars = function(e) {
  e.preventDefault();

  if (e.target.classList.contains("active")) return;
  if (typing) return;
  typing = true;

  // Clear active class from all links
  const topics = document.querySelectorAll(".topic a");
  topics.forEach((t) => {
    t.classList.remove("active");
    t.style.color = "";
  });

  // Add active class to clicked link
  e.target.classList.add("active");

  const repoName = e.target.textContent;
  const terminalText = ` ${repoName}`;
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
}

function renderRepoDescription(repoLink) {
  const postsContainer = document.getElementById("repos");
  const repoId = repoLink.getAttribute("data-repo-id");
  const repoName = repoLink.textContent;
  
  // Clear the posts container
  postsContainer.innerHTML = "";
  
  // Fetch the repository data for this repo
  fetch(`/api/repo/${repoId}`)
    .then(response => response.json())
    .then(repo => {
      // Create a post element
      const post = document.createElement("div");
      post.classList.add("post");
      
      // Create the description text
      const descriptionText = document.createElement("div");
      descriptionText.textContent = repo.description || "No description available";
      descriptionText.style.textDecoration = "none";
      
      post.appendChild(descriptionText);
      
      // Add the clone URL to the same post
      const cloneUrl = document.createElement("div");
      cloneUrl.style.marginTop = "15px";
      cloneUrl.innerHTML = `<code>git clone git.barrettruth.com/${repoName}.git</code>`;
      
      post.appendChild(cloneUrl);
      
      // Add the post to the container
      postsContainer.appendChild(post);
    })
    .catch(error => {
      console.error("Error fetching repo data:", error);
      const errorElement = document.createElement("div");
      errorElement.classList.add("post");
      errorElement.textContent = "Error loading repository information";
      postsContainer.appendChild(errorElement);
    });
}

document.addEventListener("DOMContentLoaded", function () {
  // No need to add click listeners here, the onclick attribute in the HTML handles it
});