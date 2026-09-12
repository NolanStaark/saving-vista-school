// Mobile hamburger nav toggle -- shared across every page's header.
// Desktop layout (>1099px, see style.css) is untouched by this script;
// it only matters once .nav-toggle becomes visible at the mobile breakpoint.
(function () {
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('primary-nav');
  if (!toggle || !nav) return;

  function closeNav() {
    nav.classList.remove('nav-open');
    toggle.setAttribute('aria-expanded', 'false');
  }

  function openNav() {
    nav.classList.add('nav-open');
    toggle.setAttribute('aria-expanded', 'true');
  }

  toggle.addEventListener('click', function () {
    if (nav.classList.contains('nav-open')) {
      closeNav();
    } else {
      openNav();
    }
  });

  // Close after choosing a link (each link navigates to a different page,
  // but this avoids a flash of the open menu on pages using the back button).
  nav.addEventListener('click', function (event) {
    if (event.target.tagName === 'A') {
      closeNav();
    }
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      closeNav();
    }
  });

  // If the window is resized (or rotated) past the mobile breakpoint while
  // the menu is open, reset so it doesn't stay stuck open on desktop.
  window.addEventListener('resize', function () {
    if (window.innerWidth > 1099) {
      closeNav();
    }
  });
})();
