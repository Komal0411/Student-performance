(() => {
  const bg = document.body;
  // subtle mouse-based tint (non-distracting)
  document.addEventListener('mousemove', e => {
    const x = (e.clientX / window.innerWidth) - 0.5;
    const y = (e.clientY / window.innerHeight) - 0.5;
    bg.style.background = `radial-gradient(circle at ${50 + x*5}% ${20 + y*5}%, rgba(10,20,30,0.6), rgba(5,8,12,1))`;
  });

  // refresh live graph on index (if present) every 5s
  if (window.location.pathname === '/') {
    setInterval(() => {
      const img = document.getElementById('liveGraph');
      if (img) img.src = '/static/graph.png?v=' + Date.now();
    }, 5000);
  }

  // Theme toggle
  const toggle = document.getElementById("themeToggle");
  const body = document.body;

  // Load saved theme
  if (localStorage.getItem("theme") === "dark") {
    body.classList.add("dark-mode");
  }

  // Only attach listener if the toggle exists on the page
  if (toggle) {
    toggle.addEventListener("click", () => {
      body.classList.toggle("dark-mode");
      
      // Save theme
      if (body.classList.contains("dark-mode")) {
        localStorage.setItem("theme", "dark");
      } else {
        localStorage.setItem("theme", "light");
      }
    });
  }
})();
