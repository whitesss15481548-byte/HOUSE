const header = document.querySelector("[data-header]");
const nav = document.querySelector("[data-nav]");
const navToggle = document.querySelector("[data-nav-toggle]");
const revealItems = document.querySelectorAll(".reveal");
const consultForm = document.querySelector(".consult-form");

const setHeaderState = () => {
  header.classList.toggle("is-scrolled", window.scrollY > 24);
};

setHeaderState();
window.addEventListener("scroll", setHeaderState, { passive: true });

navToggle.addEventListener("click", () => {
  const isOpen = nav.classList.toggle("is-open");
  navToggle.classList.toggle("is-active", isOpen);
  navToggle.setAttribute("aria-expanded", String(isOpen));
  document.body.classList.toggle("nav-open", isOpen);
});

nav.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => {
    nav.classList.remove("is-open");
    navToggle.classList.remove("is-active");
    navToggle.setAttribute("aria-expanded", "false");
    document.body.classList.remove("nav-open");
  });
});

const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        revealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.16, rootMargin: "0px 0px -40px 0px" }
);

revealItems.forEach((item) => revealObserver.observe(item));

consultForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const button = consultForm.querySelector("button");
  const originalText = button.textContent;
  button.textContent = "已收到，將盡快與您聯繫";
  button.disabled = true;

  window.setTimeout(() => {
    button.textContent = originalText;
    button.disabled = false;
    consultForm.reset();
  }, 2200);
});
