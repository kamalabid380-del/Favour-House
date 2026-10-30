(() => {
  "use strict";

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const fine = window.matchMedia("(pointer: fine)").matches;

  /* ---------- header state ---------- */
  const heads = Array.from(document.querySelectorAll("[data-head]"));
  const setHead = () => {
    const solid = window.scrollY > 40;
    heads.forEach((head) => head.classList.toggle("is-solid", solid));
  };

  /* ---------- mobile menu ---------- */
  const menu = document.querySelector("[data-menu]");
  const openBtn = document.querySelector("[data-menu-open]");
  const closeBtn = document.querySelector("[data-menu-close]");

  const setMenu = (open) => {
    if (!menu) return;
    menu.classList.toggle("is-open", open);
    menu.setAttribute("aria-hidden", String(!open));
    document.body.classList.toggle("is-locked", open);
    if (openBtn) openBtn.setAttribute("aria-expanded", String(open));
  };

  if (openBtn) openBtn.addEventListener("click", () => setMenu(true));
  if (closeBtn) closeBtn.addEventListener("click", () => setMenu(false));

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") setMenu(false);
  });

  /* ---------- ticking marquee ---------- */
  document.querySelectorAll("[data-marquee]").forEach((track) => {
    track.innerHTML += track.innerHTML;
  });

  /* ---------- hero ---------- */
  const hero = document.querySelector("[data-hero]");
  if (hero) {
    const figures = Array.from(hero.querySelectorAll(".hero__slide"));
    const dataEl = document.getElementById("hero-data");
    const payload = dataEl ? JSON.parse(dataEl.textContent) : [];
    const copy = hero.querySelector("[data-hero-copy]");
    const eyebrowEl = hero.querySelector("[data-hero-eyebrow]");
    const titleEl = hero.querySelector("[data-hero-title]");
    const subEl = hero.querySelector("[data-hero-sub]");
    const ctaEl = hero.querySelector("[data-hero-cta]");
    const indexEl = hero.querySelector("[data-hero-index]");
    const bar = hero.querySelector("[data-hero-progress]");
    const barWrap = hero.querySelector(".hero__bar");
    const stage = hero.querySelector("[data-hero-stage]");
    const interval = Number(hero.dataset.interval || 7200);
    const pad = (n) => String(n + 1).padStart(2, "0");
    let index = 0;
    let timer = null;

    if (figures.length > 1) {
      const splitTitle = (text) => {
        if (!titleEl) return;
        titleEl.textContent = "";
        const words = String(text || "").trim().split(/\s+/).filter(Boolean);
        words.forEach((word, i) => {
          const outer = document.createElement("span");
          outer.className = "word";
          outer.style.setProperty("--d", `${i * 70}ms`);
          const inner = document.createElement("span");
          inner.textContent = word;
          outer.appendChild(inner);
          titleEl.appendChild(outer);
          if (i < words.length - 1) titleEl.appendChild(document.createTextNode(" "));
        });
        titleEl.classList.remove("is-live");
        void titleEl.offsetWidth;
        titleEl.classList.add("is-live");
      };

      const restartBar = () => {
        if (!bar) return;
        if (barWrap) barWrap.style.setProperty("--dur", `${interval}ms`);
        bar.style.animation = "none";
        void bar.offsetWidth;
        bar.style.animation = "";
      };

      const schedule = () => {
        if (timer) clearTimeout(timer);
        timer = setTimeout(() => go(index + 1, true), interval);
      };

      const go = (next, animate) => {
        index = (next + figures.length) % figures.length;
        figures.forEach((figure, i) => figure.classList.toggle("is-active", i === index));
        const slide = payload[index] || {};
        if (animate && copy) copy.classList.add("is-out");
        const paint = () => {
          if (eyebrowEl) eyebrowEl.textContent = slide.eyebrow || "";
          splitTitle(slide.title || "");
          if (subEl) subEl.textContent = slide.subtitle || "";
          if (ctaEl) {
            const label = slide.cta_label || "";
            ctaEl.textContent = label;
            ctaEl.href = slide.cta_url || "#";
            ctaEl.classList.toggle("is-hidden", !label);
          }
          if (copy) copy.classList.remove("is-out");
        };
        if (animate) setTimeout(paint, 260);
        else paint();
        if (indexEl) indexEl.textContent = pad(index);
        restartBar();
        schedule();
      };

      const step = (dir) => go(index + dir, true);

      const prevBtn = hero.querySelector("[data-hero-prev]");
      const nextBtn = hero.querySelector("[data-hero-next]");
      if (prevBtn) prevBtn.addEventListener("click", () => step(-1));
      if (nextBtn) nextBtn.addEventListener("click", () => step(1));

      document.addEventListener("keydown", (event) => {
        if (event.key === "ArrowRight") step(1);
        if (event.key === "ArrowLeft") step(-1);
      });

      let touchX = null;
      hero.addEventListener(
        "touchstart",
        (event) => {
          touchX = event.touches[0].clientX;
        },
        { passive: true }
      );
      hero.addEventListener(
        "touchend",
        (event) => {
          if (touchX === null) return;
          const delta = event.changedTouches[0].clientX - touchX;
          if (Math.abs(delta) > 45) step(delta < 0 ? 1 : -1);
          touchX = null;
        },
        { passive: true }
      );

      document.addEventListener("visibilitychange", () => {
        if (document.hidden) {
          if (timer) clearTimeout(timer);
        } else {
          restartBar();
          schedule();
        }
      });

      // arm the first title and the progress line
      splitTitle(payload[0] && payload[0].title ? payload[0].title : "");
      restartBar();
      schedule();
    }

    /* hero scroll zoom */
    if (stage && !reduce) {
      let raf = null;
      const onScroll = () => {
        if (raf) return;
        raf = requestAnimationFrame(() => {
          const height = hero.offsetHeight || 1;
          const progress = Math.min(window.scrollY / height, 1);
          stage.style.transform = `translate3d(0, ${progress * 46}px, 0) scale(${1 + progress * 0.16})`;
          if (copy) copy.style.opacity = String(Math.max(0, 1 - progress * 1.45));
          raf = null;
        });
      };
      window.addEventListener("scroll", onScroll, { passive: true });
      onScroll();
    }
  }

  /* ---------- reveal on scroll ---------- */
  const revealItems = Array.from(document.querySelectorAll("[data-reveal]"));
  if ("IntersectionObserver" in window && revealItems.length) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-in");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -6% 0px" }
    );
    revealItems.forEach((el) => io.observe(el));
  } else {
    revealItems.forEach((el) => el.classList.add("is-in"));
  }

  /* ---------- parallax ---------- */
  const parallaxItems = Array.from(document.querySelectorAll("[data-parallax]"));
  if (parallaxItems.length && !reduce) {
    let raf = null;
    const move = () => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        const vh = window.innerHeight;
        parallaxItems.forEach((el) => {
          const rect = el.getBoundingClientRect();
          if (rect.bottom < -120 || rect.top > vh + 120) return;
          const progress = (rect.top + rect.height / 2 - vh / 2) / vh;
          const amount = parseFloat(el.dataset.parallax || "7");
          el.style.transform = `translate3d(0, ${(-progress * amount).toFixed(2)}%, 0)`;
        });
        raf = null;
      });
    };
    window.addEventListener("scroll", move, { passive: true });
    window.addEventListener("resize", move);
    move();
  }

  /* ---------- custom cursor ---------- */
  if (fine && !reduce) {
    const cursor = document.querySelector("[data-cursor]");
    if (cursor) {
      let x = window.innerWidth / 2;
      let y = window.innerHeight / 2;
      let cx = x;
      let cy = y;
      let seen = false;
      const loop = () => {
        cx += (x - cx) * 0.16;
        cy += (y - cy) * 0.16;
        cursor.style.left = `${cx}px`;
        cursor.style.top = `${cy}px`;
        requestAnimationFrame(loop);
      };
      window.addEventListener(
        "mousemove",
        (event) => {
          x = event.clientX;
          y = event.clientY;
          if (!seen) {
            seen = true;
            cursor.classList.add("is-on");
          }
        },
        { passive: true }
      );
      document.querySelectorAll("a, button, [data-viewer]").forEach((el) => {
        el.addEventListener("mouseenter", () => cursor.classList.add("is-hot"));
        el.addEventListener("mouseleave", () => cursor.classList.remove("is-hot"));
      });
      loop();
    }
  }

  /* ---------- collection filter ---------- */
  const pills = Array.from(document.querySelectorAll("[data-filter]"));
  const cards = Array.from(document.querySelectorAll("[data-product]"));
  if (pills.length && cards.length) {
    const countEl = document.querySelector("[data-count]");
    const emptyEl = document.querySelector("[data-empty]");
    const setCount = (n) => {
      if (!countEl) return;
      countEl.textContent = `${n} ${countEl.dataset.pieces || ""}`.trim();
    };
    pills.forEach((pill) => {
      pill.addEventListener("click", () => {
        const filter = pill.dataset.filter;
        pills.forEach((p) => p.classList.toggle("is-active", p === pill));
        let shown = 0;
        cards.forEach((card) => {
          const show = filter === "all" || card.dataset.category === filter;
          card.classList.toggle("is-filtered", !show);
          if (show) {
            shown += 1;
            card.style.animation = "none";
            void card.offsetWidth;
            card.style.animation = "";
          }
        });
        setCount(shown);
        if (emptyEl) emptyEl.hidden = shown !== 0;
      });
    });
  }

  /* ---------- product viewer ---------- */
  const viewer = document.querySelector("[data-viewer]");
  if (viewer) {
    const main = viewer.querySelector("[data-main-image]");
    const thumbs = Array.from(document.querySelectorAll("[data-thumb]"));

    thumbs.forEach((thumb) => {
      thumb.addEventListener("click", () => {
        thumbs.forEach((t) => t.classList.toggle("is-active", t === thumb));
        if (!main || !thumb.dataset.src) return;
        main.style.opacity = "0";
        window.setTimeout(() => {
          main.src = thumb.dataset.src;
          main.style.opacity = "1";
        }, 170);
      });
    });

    if (fine && !reduce) {
      viewer.addEventListener("mousemove", (event) => {
        const rect = viewer.getBoundingClientRect();
        const px = ((event.clientX - rect.left) / rect.width) * 100;
        const py = ((event.clientY - rect.top) / rect.height) * 100;
        if (main) main.style.transformOrigin = `${px}% ${py}%`;
      });
      viewer.addEventListener("mouseenter", () => viewer.classList.add("is-zooming"));
      viewer.addEventListener("mouseleave", () => viewer.classList.remove("is-zooming"));
    }
  }

  /* ---------- scroll listener ---------- */
  window.addEventListener("scroll", setHead, { passive: true });
  setHead();
})();
