document.addEventListener("DOMContentLoaded", function () {

  // Profile Dropdown Toggle
  const userMenuButton = document.getElementById("user-menu-button");
  const dropdownMenu = document.getElementById("profile_menu");

  userMenuButton?.addEventListener("click", function () {
    const isExpanded =
      userMenuButton.getAttribute("aria-expanded") === "true" || false;
    userMenuButton.setAttribute("aria-expanded", !isExpanded);
    if (dropdownMenu) {
      dropdownMenu.classList.toggle("hidden");
    }
  });

  // Close dropdown when clicking outside
  document.addEventListener("click", function (event) {
    event.stopPropagation()
    if (
      !userMenuButton?.contains(event.target) &&
      !dropdownMenu?.contains(event.target)
    ) {
      dropdownMenu?.classList.add("hidden");
      userMenuButton?.setAttribute("aria-expanded", "false");
    }
  });

  const comments = document.querySelectorAll(".comment");
  const replies = document.querySelectorAll(".reply");
  const showMoreCommentsBtn = document.getElementById("show-more-comments");
  const commentModal = document.getElementById("comment-modal");

  // Initially hide extra comments and replies
  if (comments.length > 3) {
    comments.forEach((comment, index) => {
      if (index >= 3) comment.classList.add("hidden");
    });
  }

  document.querySelectorAll(".show-replies").forEach((element) =>
    element.addEventListener("click", function () {
      const repliesElement = this.closest("div.stats").nextElementSibling;
      repliesElement.classList.toggle("hidden");
    })
  );

  // Show more comments
  showMoreCommentsBtn?.addEventListener("click", () => {
    comments.forEach((comment, index) => {
      if (index >= 3) {
        comment.classList.toggle("hidden");
      }
    });
    showMoreCommentsBtn.innerText =
      showMoreCommentsBtn.innerText === "Show more comments"
        ? "Show less comments"
        : "Show more comments";
  });

  // Open/Close modal for writing comments/replies
  window.openCommentModal = (type) => {
    commentModal.classList.remove("hidden");
    setTimeout(() => commentModal.classList.remove("opacity-0"), 10); // Smooth transition
  };

  window.closeCommentModal = () => {
    commentModal.classList.add("opacity-0");
    setTimeout(() => commentModal.classList.add("hidden"), 300); // Smooth transition
  };

  // Open the modal
});
function openModal(target) {
  document.getElementById(target).classList.remove("hidden");
  document.getElementById(target).classList.remove("opacity-0");
}

// Close the modal
function closeModal(target) {
  document.getElementById(target).classList.add("hidden");
  document.getElementById(target).classList.add("opacity-0");
}

// Form validation and submission
document.getElementById("updateForm")?.addEventListener("submit", function (event) {
    event.preventDefault();

    const oldPassword = document.getElementById("oldPassword").value;
    const newPassword = document.getElementById("newPassword").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    if (newPassword === oldPassword && newPassword.length >= 8) {
      alert("New password cannot be the same as the old password.");
      return;
    }

    if (newPassword !== confirmPassword) {
      alert("New password and confirm password do not match.");
      return;
    }

    closeModal("editModal");
  });

  function submitForm(id){
    document.getElementById(id)?.submit();
  }

  // content counter
  const contentField = document.getElementById('content')
  const words = document.getElementById('words')
  const characters = document.getElementById('characters')

  contentField?.addEventListener('input', function(){
    const text = contentField.value.trim()

    const characterCount = text.length;

    const wordCount = text.split(/\s+/).filter(word => word.length > 0).length;

    words.textContent  = wordCount + " words"
    characters.textContent = characterCount + " characters"
  })



  // tags interaction
  document.getElementById('tag-input')?.addEventListener('keydown', function (event) {
    if (event.key === ',') {
        event.preventDefault();
        addTag(this.value.trim());
        this.value = '';
    }
});

function addTag(tag) {
    if (tag === '') return;

    const tagContainer = document.getElementById('tag-container');
    const tagPill = document.createElement('div');
    tagPill.className = 'tag-pill';
    tagPill.textContent = tag;
    tagPill.addEventListener('click', function () {
        tagContainer.removeChild(tagPill);
        updateTagsInput();
    });

    tagContainer.appendChild(tagPill);
    updateTagsInput();
}

function updateTagsInput() {
    const tags = [];
    document.querySelectorAll('#tag-container .tag-pill').forEach(function (tagPill) {
        tags.push(tagPill.textContent);
    });

    document.getElementById('tags').value = tags.join(',');
    console.log(document.getElementById('tags').value)
}

document.querySelectorAll('.flash-message .close-flash').forEach(button => {
  button.addEventListener('click', function() {
      this.closest('.flash-message').style.display = 'none';
  });
});

function previewImage(event) {
  const file = event.target.files[0];
  const reader = new FileReader();

  reader.onload = function() {
      const previewImage = document.getElementById('profilePicture');
      previewImage.src = reader.result;
  };

  if (file) {
      reader.readAsDataURL(file);
  }
}

function formAction(action) {
  var statusInput = document.getElementById("status");
  var form = document.getElementById("blogForm");

  if (statusInput) {
    statusInput.value = action;
  }

  if (form) {
    document.getElementById('submit')?.click()
  }
}

document.getElementById('draft')?.addEventListener('click', function() {
  formAction('DF');
});

document.getElementById('publish')?.addEventListener('click', function() {
  formAction('PB');
});

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('static/service-worker.js')
      .then(registration => {
        console.log('ServiceWorker registration successful with scope: ', registration.scope);
      })
      .catch(error => {
        console.log('ServiceWorker registration failed: ', error);
      });
  });
}