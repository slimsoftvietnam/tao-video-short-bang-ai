    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });

      /* Every cue is in RECORDED seconds (syl-times.json). autoAlpha sits in the TO vars:
         GSAP re-applies a completed tween's end state on every seek. */
      function pop(sel, t, d, s) {
        tl.fromTo(sel, { autoAlpha: 0, scale: s || 0.7, transformOrigin: "50% 50%" },
                       { autoAlpha: 1, scale: 1, duration: d || 0.5, ease: "back.out(1.6)", transformOrigin: "50% 50%" }, t);
      }
      function show(sel, t, d, y) {
        tl.fromTo(sel, { autoAlpha: 0, y: y === undefined ? 36 : y },
                       { autoAlpha: 1, y: 0, duration: d || 0.5, ease: "power3.out" }, t);
      }
      function bump(sel, t, k, base) {
        var b = base === undefined ? 1 : base;
        tl.to(sel, { scale: b * k, duration: 0.12, ease: "power2.out" }, t);
        tl.to(sel, { scale: b, duration: 0.3, ease: "back.out(2)" }, t + 0.12);
      }
      function gone(sel, t, d) {
        tl.to(sel, { autoAlpha: 0, duration: d || 0.25, ease: "power1.out" }, t);
      }
      function lift(sel, t) {
        tl.to(sel, { autoAlpha: 0, y: -40, duration: 0.3, ease: "power2.in" }, t);
      }
      function draw(sel, t, d, stagger) {
        tl.fromTo(sel, { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: d || 0.4, ease: "power2.out", stagger: stagger || 0 }, t);
      }
      function sweep(sel, t, d) {
        tl.fromTo(sel, { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: d || 0.45, ease: "power2.out", transformOrigin: "0% 50%" }, t);
      }
      function flash(t, a) {
        tl.fromTo("#flash", { autoAlpha: a }, { autoAlpha: 0, duration: 0.4, ease: "power2.out", immediateRender: false }, t);
      }
      function ids(prefix, n) {
        var a = [];
        for (var k = 0; k < n; k++) a.push("#" + prefix + k);
        return a;
      }
      /* a ring that marks a control on the evidence, then lets go */
      function ring(sel, t, off) {
        tl.fromTo(sel, { autoAlpha: 0, scale: 1.08, transformOrigin: "50% 50%" },
                       { autoAlpha: 1, scale: 1, duration: 0.3, ease: "power3.out", transformOrigin: "50% 50%" }, t);
        if (off) gone(sel, off, 0.2);
      }
      /* a click lands: the violet ripple at page point (X, Y) */
      function pulse(sel, t, X, Y) {
        tl.fromTo(sel, { autoAlpha: 1, x: X, y: Y, scale: 0.3 },
          { autoAlpha: 0, x: X, y: Y, scale: 1.6, duration: 0.45, ease: "power2.out", immediateRender: false }, t);
      }
      /* the house cursor: its tip sits 23,13 px into the 100 px glyph */
      function click(cur, cp, t, X, Y) {
        tl.to(cur, { scale: 0.84, duration: 0.08, ease: "power2.in", transformOrigin: "23% 13%" }, t - 0.04);
        tl.to(cur, { scale: 1, duration: 0.2, ease: "power2.out", transformOrigin: "23% 13%" }, t + 0.06);
        pulse(cp, t, X, Y);
      }

      /* @geo */

      /* The three steps. A step opens on its tile; when the step has been named the tile flies up into
         its slot in the tracker and lights it (violet ring); the step before it is ticked done. */
      function done(k, t) {
        tl.to("#tk" + k + "-r", { autoAlpha: 0, duration: 0.2, ease: "power1.out" }, t);
        pop("#tk" + k + "-dn", t + 0.05, 0.35, 0.3);
      }
      function lit(k, t) {
        tl.to("#tk" + k, { opacity: 1, duration: 0.15, ease: "none" }, t);
        tl.fromTo("#tk" + k + "-r", { autoAlpha: 0, scale: 1.3 }, { autoAlpha: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }, t);
        bump("#tk" + k, t + 0.02, 1.14);
        if (k > 0) done(k - 1, t);
      }
      function opener(p, k, tIn, tNum, tFly, cx, cy, size) {
        tl.fromTo(p + "-t", { autoAlpha: 0, scale: 0.5, rotation: -12 },
          { autoAlpha: 1, scale: 1, rotation: 0, duration: 0.5, ease: "back.out(1.6)" }, tIn);
        pop(p + "-n", tNum, 0.4, 0.3);
        tl.to(p + "-t", { x: GEO.tk[k] + 56 - cx, y: 148 - cy, scale: 112 / size, duration: 0.45, ease: "power3.inOut" }, tFly);
        tl.set(p + "-t", { autoAlpha: 0 }, tFly + 0.45);
        lit(k, tFly + 0.44);
      }

      // <seams:auto>
      // </seams:auto>

      /* ══ EXAMPLE TIMELINE — every time below is a placeholder for the example SCRIPT.md. Rewrite each cue
         at the syllable time of its word (syl-times.json); scene cuts live in scripts/build.py SC. ═══════ */

      /* ── h1 · "Đây là cách tạo video ngắn bằng AI cực kỳ đơn giản, ai cũng làm được." — the clip in a
         glass window that turns to the viewer while the riser climbs; dead stop on the last word ─────── */
      tl.fromTo("#h1-glow", { autoAlpha: 0, scale: 0.8 }, { autoAlpha: 1, scale: 1, duration: 1.0, ease: "power2.out" }, 0);
      tl.fromTo("#h1-win", { autoAlpha: 0, y: 90, rotationY: -30, rotationX: 14, scale: 0.8, transformPerspective: 1700, transformOrigin: "50% 50%" },
        { autoAlpha: 1, y: 0, rotationY: -20, rotationX: 9, scale: 0.88, duration: 0.6, ease: "power3.out", transformPerspective: 1700, transformOrigin: "50% 50%" }, 0.04);
      tl.to("#h1-win", { rotationY: 0, rotationX: 0, scale: 1, duration: 3.7, ease: "power1.inOut", transformPerspective: 1700 }, 0.64);
      pop("#h1-gpt", 1.42, 0.45, 0.5);                                   // "bằng AI": the agents' marks
      pop("#h1-cl", 1.52, 0.45, 0.5);
      /* the paper darkens and the light behind the window swells while the riser climbs */
      tl.fromTo("#vig", { autoAlpha: 0 }, { autoAlpha: 1, duration: 2.7, ease: "power1.in" }, 1.60);
      tl.to("#h1-glow", { scale: 1.14, duration: 2.8, ease: "power1.in" }, 1.60);
      /* "được." — dead stop: a flash, the window snaps (the riser's peak, add-sfx.py RISER, lands here) */
      flash(4.40, 0.6);
      tl.to("#vig", { autoAlpha: 0, duration: 0.3, ease: "power1.out" }, 4.40);
      tl.to("#h1-win", { scale: 0.97, duration: 0.08, ease: "power2.out" }, 4.40);
      tl.to("#h1-win", { scale: 1, duration: 0.3, ease: "back.out(2)" }, 4.49);
      bump(["#h1-gpt", "#h1-cl"], 4.40, 1.12);

      /* ── s1 · 1 · "Đầu tiên, anh em cài một AI Agent về máy, ví dụ ChatGPT hoặc Claude." ────────────── */
      tl.set(ids("tk", GEO.tk.length), { opacity: 0.4 }, 0);
      tl.fromTo("#trk", { autoAlpha: 0, y: -30 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: "power3.out" }, 4.66);
      opener("#s1", 0, 4.62, 4.80, 6.90, 540, 670, 300);                 // tile on the cut, flies on "về máy"
      bump("#s1-t", 5.00, 1.08);                                         // "Đầu tiên"
      lift("#s1-n", 6.90);
      tl.fromTo("#s1-lap", { autoAlpha: 0, y: 60, scale: 0.9 }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.4, ease: "back.out(1.4)" }, 7.10);
      pop("#s1-gpt", 8.30, 0.45, 0.5);                                   // "ChatGPT"
      pop("#s1-cl", 9.00, 0.45, 0.5);                                    // "Claude"
      pop("#s1-ok", 9.40, 0.45, 0.4);

      /* ── p1 · "Sau đó gửi cho nó file giọng đọc và đúng một câu lệnh: Hãy dựng cho tôi …" ─────────────── */
      show("#p1-pc", 9.95, 0.45, 60);
      pop("#p1-one", 12.40, 0.45, 0.4);                                  // "một câu lệnh" (shutter, add-sfx CLICK)
      /* the prompt lights word by word (build.py PROMPTS -> @pwords below); sent on its last word */
      bump("#p1-snd", 17.30, 0.86);

      /* ── cta · "Anh em nào cần hướng dẫn đầy đủ, comment VIDEO, mình gửi cho nhé." ─────────────────── */
      show("#cta-cb", 17.60, 0.4, 30);
      tl.set("#cta-ph", { autoAlpha: 0 }, 19.80);
      for (var c = 0; c < GEO.cta; c++) tl.set("#cta-c" + c, { display: "inline" }, 19.84 + c * 0.075);   // "VIDEO"
      bump("#cta-snd", 21.20, 0.86);                                     // "gửi"
      tl.fromTo("#cta-pl", { autoAlpha: 0, x: 0, y: 0 }, { autoAlpha: 1, x: 60, y: -60, duration: 0.2, ease: "power2.out" }, 21.30);
      tl.to("#cta-pl", { x: 220, y: -260, autoAlpha: 0, duration: 0.5, ease: "power2.in" }, 21.52);
      gone("#trk", 24.04, 0.16);

      /* @pwords */

      /* ── end card — house bookend at 2x speed (as on the previous videos): every time and
         duration of the standard card scaled by K; 5.5 s -> 2.75 s ─────────────────── */
      var EC = @@start:ec@@, K = 0.5;
      tl.fromTo("#slimai-logo", { autoAlpha: 0, scale: 0.92 },
        { autoAlpha: 1, scale: 1, duration: 0.7 * K, ease: "power3.out" }, EC + 0.12 * K);
      tl.fromTo("#cursor2", { autoAlpha: 0, y: 1150 }, { autoAlpha: 1, duration: 0.12 * K }, EC + 0.9 * K);
      tl.to("#cursor2", { y: 0, duration: 0.9 * K, ease: "power3.out" }, EC + 0.9 * K);
      tl.to("#cursor2", { scale: 0.84, duration: 0.1 * K,  ease: "power2.in",  transformOrigin: "21% 14%" }, EC + 1.95 * K);
      tl.to("#cursor2", { scale: 1,    duration: 0.22 * K, ease: "power2.out", transformOrigin: "21% 14%" }, EC + 2.06 * K);
      tl.to("#slimai-logo", { scale: 0.97, duration: 0.1 * K, ease: "power2.in" },  EC + 1.95 * K);
      tl.to("#slimai-logo", { scale: 1,    duration: 0.3 * K, ease: "back.out(2)" }, EC + 2.06 * K);
      tl.fromTo("#slimai-ring", { opacity: 0.85, scale: 0.9 },
        { opacity: 0, scale: 1.18, duration: 0.75 * K, ease: "power2.out", immediateRender: false }, EC + 1.98 * K);
      tl.fromTo("#slimai-slogan", { autoAlpha: 0, y: 18 },
        { autoAlpha: 1, y: 0, duration: 0.55 * K, ease: "power3.out" }, EC + 2.1 * K);
      tl.to("#cursor2", { y: 1150, duration: 0.6 * K, ease: "power2.in" }, EC + 2.7 * K);
      tl.to("#cursor2", { autoAlpha: 0, duration: 0.1 * K }, EC + 3.25 * K);

      tl.set({}, {}, @@end@@);   /* hold the card; never cut to black */
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
